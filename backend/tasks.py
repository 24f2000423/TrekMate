import os
import csv
from datetime import datetime, date, timedelta
from celery_app import celery_app
from config import Config
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

# Ensure export & report directories exist
os.makedirs(Config.EXPORTS_DIR, exist_ok=True)
os.makedirs(Config.REPORTS_DIR, exist_ok=True)


def get_flask_app():
    from app import create_app
    return create_app()


@celery_app.task(name='tasks.send_daily_reminders')
def send_daily_reminders():
    """
    Scheduled Job (Daily):
    Finds upcoming treks starting within the next 3 days and sends reminder notifications
    to registered trekkers via notifications / email / webhook simulation.
    """
    app = get_flask_app()
    with app.app_context():
        from database import db
        from models import Trek, Booking, Notification, User

        today = date.today()
        upcoming_threshold = today + timedelta(days=3)

        # Find active treks starting soon
        upcoming_treks = Trek.query.filter(
            Trek.start_date >= today,
            Trek.start_date <= upcoming_threshold,
            Trek.status.in_(['Open', 'Closed', 'Approved'])
        ).all()

        reminders_sent = 0
        logs = []

        for trek in upcoming_treks:
            # Active bookings for this trek
            bookings = Booking.query.filter_by(trek_id=trek.id, status='Booked').all()
            for b in bookings:
                user = User.query.get(b.user_id)
                if not user or not user.is_active:
                    continue

                days_left = (trek.start_date - today).days
                time_str = "tomorrow!" if days_left == 1 else f"in {days_left} days ({trek.start_date.strftime('%d %b %Y')})"

                msg = (
                    f"Reminder: Your booked trek '{trek.name}' at {trek.location} starts {time_str}. "
                    f"Difficulty: {trek.difficulty}. Duration: {trek.duration_days} days. "
                    f"Assigned Staff: {trek.assigned_staff.name if trek.assigned_staff else 'TMA Guide Team'}. "
                    f"Please pack appropriate gear and stay hydrated!"
                )

                # 1. Create DB in-app Notification
                notif = Notification(
                    user_id=user.id,
                    title=f"Upcoming Trek Reminder: {trek.name}",
                    message=msg,
                    type='reminder'
                )
                db.session.add(notif)
                reminders_sent += 1

                log_entry = f"Reminder sent to {user.email} ({user.name}) for trek '{trek.name}'"
                logs.append(log_entry)
                print(f"[CELERY DAILY REMINDER] {log_entry}")

        db.session.commit()
        return {
            'status': 'SUCCESS',
            'reminders_sent': reminders_sent,
            'logs': logs,
            'timestamp': datetime.utcnow().isoformat()
        }


@celery_app.task(name='tasks.generate_monthly_activity_report')
def generate_monthly_activity_report(month=None, year=None):
    """
    Scheduled Job (Monthly):
    Generates a comprehensive Monthly Trekking Activity Report for Admin
    in both HTML and PDF formats.
    """
    app = get_flask_app()
    with app.app_context():
        from database import db
        from models import Trek, Booking, User, Notification
        from sqlalchemy import func

        today = date.today()
        if not month:
            # Report for previous or current month
            target_date = today.replace(day=1)
            target_month = target_date.month
            target_year = target_date.year
        else:
            target_month = int(month)
            target_year = int(year) if year else today.year

        month_name = datetime(target_year, target_month, 1).strftime('%B %Y')

        # 1. Aggregations
        total_treks = Trek.query.count()
        total_users = User.query.filter_by(role='user').count()
        total_staff = User.query.filter_by(role='staff').count()
        
        all_bookings = Booking.query.all()
        total_bookings = len(all_bookings)
        active_bookings = len([b for b in all_bookings if b.status == 'Booked'])
        completed_bookings = len([b for b in all_bookings if b.status == 'Completed'])
        cancelled_bookings = len([b for b in all_bookings if b.status == 'Cancelled'])
        total_revenue = sum(b.total_amount for b in all_bookings if b.status in ['Booked', 'Completed'])

        # Popular treks
        treks = Trek.query.all()
        trek_stats = []
        for t in treks:
            b_count = Booking.query.filter_by(trek_id=t.id).count()
            rev = sum(b.total_amount for b in Booking.query.filter_by(trek_id=t.id, status='Booked').all())
            trek_stats.append({
                'name': t.name,
                'location': t.location,
                'difficulty': t.difficulty,
                'bookings': b_count,
                'revenue': rev,
                'status': t.status
            })
        trek_stats.sort(key=lambda x: x['bookings'], reverse=True)

        # 2. Generate HTML Report
        html_filename = f"monthly_report_{target_year}_{target_month:02d}.html"
        html_path = os.path.join(Config.REPORTS_DIR, html_filename)

        popular_rows_html = "".join([
            f"<tr><td>{ts['name']}</td><td>{ts['location']}</td><td>{ts['difficulty']}</td>"
            f"<td>{ts['bookings']}</td><td>₹{ts['revenue']:.2f}</td><td>{ts['status']}</td></tr>"
            for ts in trek_stats[:10]
        ])

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Monthly Activity Report - {month_name}</title>
            <style>
                body {{ font-family: 'Segoe UI', Arial, sans-serif; margin: 40px; color: #333; background: #fdfdfd; }}
                h1 {{ color: #198754; border-bottom: 2px solid #198754; padding-bottom: 8px; }}
                h2 {{ color: #0d6efd; margin-top: 30px; }}
                .summary-grid {{ display: flex; flex-wrap: wrap; gap: 20px; margin: 20px 0; }}
                .summary-card {{ background: #f8f9fa; border: 1px solid #dee2e6; border-radius: 8px; padding: 15px 25px; min-width: 180px; }}
                .summary-card h3 {{ margin: 0; font-size: 14px; color: #6c757d; text-transform: uppercase; }}
                .summary-card p {{ margin: 5px 0 0 0; font-size: 24px; font-weight: bold; color: #212529; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 15px; background: #fff; }}
                th, td {{ border: 1px solid #dee2e6; padding: 10px 14px; text-align: left; }}
                th {{ background-color: #f1f3f5; font-weight: 600; }}
                tr:nth-child(even) {{ background-color: #fafbfc; }}
                .footer {{ margin-top: 50px; font-size: 12px; color: #888; border-top: 1px solid #eee; padding-top: 10px; }}
            </style>
        </head>
        <body>
            <h1>Trekking Management Application (TMA) - Monthly Activity Report</h1>
            <p><strong>Reporting Period:</strong> {month_name} | <strong>Generated on:</strong> {datetime.utcnow().strftime('%d %B %Y, %H:%M UTC')}</p>
            
            <h2>Executive Summary</h2>
            <div class="summary-grid">
                <div class="summary-card"><h3>Total Treks</h3><p>{total_treks}</p></div>
                <div class="summary-card"><h3>Total Trekkers</h3><p>{total_users}</p></div>
                <div class="summary-card"><h3>Staff Members</h3><p>{total_staff}</p></div>
                <div class="summary-card"><h3>Total Bookings</h3><p>{total_bookings}</p></div>
                <div class="summary-card"><h3>Total Revenue</h3><p>₹{total_revenue:.2f}</p></div>
            </div>

            <h2>Booking Breakdown</h2>
            <table>
                <thead><tr><th>Active Bookings</th><th>Completed</th><th>Cancelled</th></tr></thead>
                <tbody><tr><td>{active_bookings}</td><td>{completed_bookings}</td><td>{cancelled_bookings}</td></tr></tbody>
            </table>

            <h2>Top Performing & Popular Treks</h2>
            <table>
                <thead><tr><th>Trek Name</th><th>Location</th><th>Difficulty</th><th>Bookings</th><th>Revenue</th><th>Status</th></tr></thead>
                <tbody>{popular_rows_html}</tbody>
            </table>

            <div class="footer">
                <p>Generated automatically by Trekking Management Application Celery Scheduler &copy; {target_year}</p>
            </div>
        </body>
        </html>
        """
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

        # 3. Generate PDF Report using ReportLab
        pdf_filename = f"monthly_report_{target_year}_{target_month:02d}.pdf"
        pdf_path = os.path.join(Config.REPORTS_DIR, pdf_filename)
        doc = SimpleDocTemplate(pdf_path, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
        
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'ReportTitle',
            parent=styles['Heading1'],
            fontSize=20,
            leading=24,
            textColor=colors.HexColor('#198754')
        )
        subtitle_style = ParagraphStyle(
            'ReportSubtitle',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#6c757d'),
            spaceAfter=15
        )
        h2_style = ParagraphStyle(
            'H2',
            parent=styles['Heading2'],
            fontSize=14,
            leading=18,
            textColor=colors.HexColor('#0d6efd'),
            spaceBefore=12,
            spaceAfter=8
        )

        elements = []
        elements.append(Paragraph("TMA Monthly Activity Report", title_style))
        elements.append(Paragraph(f"Reporting Period: <b>{month_name}</b> | Generated on: {datetime.utcnow().strftime('%d %b %Y %H:%M UTC')}", subtitle_style))
        elements.append(Spacer(1, 10))

        elements.append(Paragraph("Executive Summary Metrics", h2_style))
        summary_data = [
            ["Metric", "Value", "Metric", "Value"],
            ["Total Treks", str(total_treks), "Total Registered Trekkers", str(total_users)],
            ["Total Staff Members", str(total_staff), "Total Bookings", str(total_bookings)],
            ["Active Bookings", str(active_bookings), "Completed Bookings", str(completed_bookings)],
            ["Cancelled Bookings", str(cancelled_bookings), "Total Revenue Generated", f"INR {total_revenue:.2f}"]
        ]
        t_summary = Table(summary_data, colWidths=[130, 130, 150, 130])
        t_summary.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e9ecef')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#212529')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#dee2e6')),
        ]))
        elements.append(t_summary)
        elements.append(Spacer(1, 15))

        elements.append(Paragraph("Top Popular Treks", h2_style))
        trek_table_data = [["Trek Name", "Location", "Difficulty", "Bookings", "Status"]]
        for ts in trek_stats[:8]:
            trek_table_data.append([
                ts['name'][:25],
                ts['location'][:20],
                ts['difficulty'],
                str(ts['bookings']),
                ts['status']
            ])
        t_treks = Table(trek_table_data, colWidths=[150, 140, 90, 80, 80])
        t_treks.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#198754')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#dee2e6')),
        ]))
        elements.append(t_treks)

        doc.build(elements)

        # Notify Admin in database
        admins = User.query.filter_by(role='admin').all()
        for admin in admins:
            notif = Notification(
                user_id=admin.id,
                title=f"Monthly Activity Report Ready: {month_name}",
                message=f"The monthly activity report for {month_name} has been generated. Total Bookings: {total_bookings}, Revenue: ₹{total_revenue:.2f}.",
                type='report'
            )
            db.session.add(notif)
        db.session.commit()

        return {
            'status': 'SUCCESS',
            'month': month_name,
            'html_file': html_filename,
            'pdf_file': pdf_filename,
            'total_bookings': total_bookings,
            'total_revenue': total_revenue
        }


@celery_app.task(name='tasks.export_user_bookings_csv')
def export_user_bookings_csv(user_id, task_id=None):
    """
    User-Triggered Async Job:
    Exports user booking history as CSV with task status tracking and in-app notification.
    """
    app = get_flask_app()
    with app.app_context():
        from database import db
        from models import Booking, User, ExportJob, Notification

        user = User.query.get(user_id)
        if not user:
            return {'status': 'FAILURE', 'error': 'User not found'}

        if not task_id:
            task_id = f"export_{user_id}_{int(datetime.utcnow().timestamp())}"
        
        # Check or create ExportJob record
        job = ExportJob.query.filter_by(task_id=task_id).first()
        if not job:
            job = ExportJob(
                task_id=task_id,
                user_id=user_id,
                status='PENDING'
            )
            db.session.add(job)
            db.session.commit()

        # Fetch bookings
        bookings = Booking.query.filter_by(user_id=user_id).order_by(Booking.booking_date.desc()).all()

        filename = f"booking_history_user_{user_id}_{int(datetime.utcnow().timestamp())}.csv"
        filepath = os.path.join(Config.EXPORTS_DIR, filename)

        with open(filepath, mode='w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([
                'Booking ID',
                'User ID',
                'User Name',
                'User Email',
                'Trek ID',
                'Trek Name',
                'Location',
                'Difficulty',
                'Start Date',
                'End Date',
                'Duration (Days)',
                'Seats Booked',
                'Booking Status',
                'Payment Status',
                'Total Amount (INR)',
                'Booking Date',
                'Special Notes'
            ])

            for b in bookings:
                t = b.trek
                writer.writerow([
                    b.id,
                    user.id,
                    user.name,
                    user.email,
                    t.id if t else 'N/A',
                    t.name if t else 'Unknown',
                    t.location if t else 'N/A',
                    t.difficulty if t else 'N/A',
                    t.start_date.strftime('%Y-%m-%d') if t and t.start_date else 'N/A',
                    t.end_date.strftime('%Y-%m-%d') if t and t.end_date else 'N/A',
                    t.duration_days if t else 'N/A',
                    b.seats,
                    b.status,
                    b.payment_status,
                    b.total_amount,
                    b.booking_date.strftime('%Y-%m-%d %H:%M:%S') if b.booking_date else '',
                    b.special_notes or ''
                ])

        download_url = f"/api/reports/download-export/{filename}"
        job.status = 'SUCCESS'
        job.file_name = filename
        job.file_path = filepath
        job.download_url = download_url
        job.completed_at = datetime.utcnow()

        # Add in-app notification
        notif = Notification(
            user_id=user_id,
            title="Trekking History CSV Ready",
            message=f"Your booking history export ({len(bookings)} records) is ready for download!",
            type='system'
        )
        db.session.add(notif)
        db.session.commit()

        return {
            'status': 'SUCCESS',
            'task_id': task_id,
            'file_name': filename,
            'download_url': download_url,
            'records_count': len(bookings)
        }
