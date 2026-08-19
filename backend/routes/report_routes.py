import os
from flask import Blueprint, request, jsonify, send_from_directory
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from config import Config
from models import ExportJob, Notification, User
from database import db
from routes.auth_routes import admin_required, user_required
import tasks

report_bp = Blueprint('report_bp', __name__)

@report_bp.route('/trigger-export', methods=['POST'])
@user_required
def trigger_export_csv():
    """User triggers async Celery job to export booking history as CSV"""
    user_id = int(get_jwt_identity())
    
    # Try triggering via Celery async, or fallback to synchronous execution if Celery worker is offline
    try:
        async_task = tasks.export_user_bookings_csv.delay(user_id)
        task_id = async_task.id
        # Record pending job
        job = ExportJob(
            task_id=task_id,
            user_id=user_id,
            status='PENDING'
        )
        db.session.add(job)
        db.session.commit()
        return jsonify({
            'message': 'Export job initiated. You will receive an alert once ready.',
            'task_id': task_id,
            'status': 'PENDING'
        }), 202
    except Exception as e:
        # Fallback to direct synchronous execution
        print(f"[CELERY FALLBACK] Executing export directly: {e}")
        dummy_task_id = f"sync_export_{user_id}_{int(datetime.utcnow().timestamp())}"
        
        result = tasks.export_user_bookings_csv(user_id, dummy_task_id)
        return jsonify({
            'message': 'Export completed successfully!',
            'task_id': dummy_task_id,
            'status': 'SUCCESS',
            'download_url': result.get('download_url'),
            'file_name': result.get('file_name')
        }), 200


@report_bp.route('/export-status/<task_id>', methods=['GET'])
@jwt_required()
def get_export_status(task_id):
    """Check status of an ongoing export job"""
    job = ExportJob.query.filter_by(task_id=task_id).first()
    if not job:
        return jsonify({'error': 'Export job not found'}), 404
    return jsonify({'job': job.to_dict()}), 200


@report_bp.route('/my-exports', methods=['GET'])
@jwt_required()
def list_my_exports():
    """Get list of user's past exports"""
    user_id = get_jwt_identity()
    jobs = ExportJob.query.filter_by(user_id=user_id).order_by(ExportJob.created_at.desc()).all()
    return jsonify({'exports': [j.to_dict() for j in jobs]}), 200


@report_bp.route('/download-export/<filename>', methods=['GET'])
def download_export_file(filename):
    """Download exported CSV file"""
    return send_from_directory(Config.EXPORTS_DIR, filename, as_attachment=True)


@report_bp.route('/generate-monthly-report', methods=['POST'])
@admin_required
def trigger_monthly_report():
    """Admin triggers or schedules monthly activity report"""
    data = request.get_json() or {}
    month = data.get('month')
    year = data.get('year')

    try:
        res = tasks.generate_monthly_activity_report.delay(month, year)
        return jsonify({
            'message': 'Monthly Activity Report generation task queued via Celery.',
            'task_id': res.id
        }), 202
    except Exception as e:
        # Fallback to direct synchronous generation
        print(f"[CELERY FALLBACK] Generating monthly report directly: {e}")
        res = tasks.generate_monthly_activity_report(month, year)
        return jsonify({
            'message': 'Monthly Activity Report generated successfully!',
            'result': res
        }), 200


@report_bp.route('/monthly-reports', methods=['GET'])
@admin_required
def list_monthly_reports():
    """List all generated monthly activity reports (HTML and PDF)"""
    files = []
    if os.path.exists(Config.REPORTS_DIR):
        for f in os.listdir(Config.REPORTS_DIR):
            if f.endswith('.pdf') or f.endswith('.html'):
                f_path = os.path.join(Config.REPORTS_DIR, f)
                files.append({
                    'filename': f,
                    'file_type': 'PDF' if f.endswith('.pdf') else 'HTML',
                    'size_bytes': os.path.getsize(f_path),
                    'download_url': f"/api/reports/download-monthly/{f}",
                    'created_at': datetime.fromtimestamp(os.path.getctime(f_path)).strftime('%Y-%m-%d %H:%M:%S')
                })
    files.sort(key=lambda x: x['created_at'], reverse=True)
    return jsonify({'reports': files}), 200


@report_bp.route('/download-monthly/<filename>', methods=['GET'])
def download_monthly_report(filename):
    """View/Download monthly report HTML or PDF"""
    as_attach = request.args.get('download', 'false').lower() == 'true'
    return send_from_directory(Config.REPORTS_DIR, filename, as_attachment=as_attach)


@report_bp.route('/trigger-daily-reminders', methods=['POST'])
@admin_required
def trigger_daily_reminders():
    """Manually test/run daily reminders scheduled task"""
    try:
        res = tasks.send_daily_reminders.delay()
        return jsonify({'message': 'Daily reminders job dispatched via Celery', 'task_id': res.id}), 202
    except Exception as e:
        res = tasks.send_daily_reminders()
        return jsonify({'message': 'Daily reminders executed directly', 'result': res}), 200


@report_bp.route('/notifications', methods=['GET'])
@jwt_required()
def get_user_notifications():
    """Fetch user's in-app notifications"""
    user_id = get_jwt_identity()
    notifs = Notification.query.filter_by(user_id=user_id).order_by(Notification.created_at.desc()).all()
    unread_count = Notification.query.filter_by(user_id=user_id, is_read=False).count()
    return jsonify({
        'notifications': [n.to_dict() for n in notifs],
        'unread_count': unread_count
    }), 200


@report_bp.route('/notifications/<int:notif_id>/read', methods=['PUT'])
@jwt_required()
def mark_notification_read(notif_id):
    """Mark a notification as read"""
    user_id = get_jwt_identity()
    notif = Notification.query.filter_by(id=notif_id, user_id=user_id).first()
    if not notif:
        return jsonify({'error': 'Notification not found'}), 404
    notif.is_read = True
    db.session.commit()
    return jsonify({'message': 'Notification marked as read'}), 200


@report_bp.route('/notifications/read-all', methods=['PUT'])
@jwt_required()
def mark_all_notifications_read():
    """Mark all user notifications as read"""
    user_id = get_jwt_identity()
    Notification.query.filter_by(user_id=user_id, is_read=False).update({'is_read': True})
    db.session.commit()
    return jsonify({'message': 'All notifications marked as read'}), 200
