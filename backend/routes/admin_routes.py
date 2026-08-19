from flask import Blueprint, request, jsonify
from datetime import datetime
from models import User, Trek, Booking, Notification
from database import db
from routes.auth_routes import admin_required

admin_bp = Blueprint('admin_bp', __name__)

@admin_bp.route('/stats', methods=['GET'])
@admin_required
def get_dashboard_stats():
    """Aggregates analytics and metrics for Admin dashboard and Chart.js"""
    total_treks = Trek.query.count()
    open_treks = Trek.query.filter_by(status='Open').count()
    completed_treks = Trek.query.filter_by(status='Completed').count()

    total_users = User.query.filter_by(role='user').count()
    total_staff = User.query.filter_by(role='staff').count()
    active_users = User.query.filter_by(role='user', is_active=True, is_blacklisted=False).count()

    all_bookings = Booking.query.all()
    total_bookings = len(all_bookings)
    active_bookings = len([b for b in all_bookings if b.status == 'Booked'])
    cancelled_bookings = len([b for b in all_bookings if b.status == 'Cancelled'])
    completed_bookings = len([b for b in all_bookings if b.status == 'Completed'])
    total_revenue = sum(b.total_amount for b in all_bookings if b.status in ['Booked', 'Completed'])

    # Difficulty distribution
    difficulty_counts = {
        'Easy': Trek.query.filter_by(difficulty='Easy').count(),
        'Moderate': Trek.query.filter_by(difficulty='Moderate').count(),
        'Hard': Trek.query.filter_by(difficulty='Hard').count()
    }

    # Top popular treks
    treks = Trek.query.all()
    popular_treks = []
    for t in treks:
        b_count = Booking.query.filter_by(trek_id=t.id, status='Booked').count()
        popular_treks.append({
            'name': t.name,
            'location': t.location,
            'bookings_count': b_count,
            'available_slots': t.available_slots,
            'total_slots': t.total_slots
        })
    popular_treks.sort(key=lambda x: x['bookings_count'], reverse=True)

    return jsonify({
        'metrics': {
            'total_treks': total_treks,
            'open_treks': open_treks,
            'completed_treks': completed_treks,
            'total_users': total_users,
            'total_staff': total_staff,
            'active_users': active_users,
            'total_bookings': total_bookings,
            'active_bookings': active_bookings,
            'cancelled_bookings': cancelled_bookings,
            'completed_bookings': completed_bookings,
            'total_revenue': total_revenue
        },
        'charts': {
            'difficulty_distribution': difficulty_counts,
            'popular_treks': popular_treks[:6],
            'booking_status': {
                'Booked': active_bookings,
                'Completed': completed_bookings,
                'Cancelled': cancelled_bookings
            }
        }
    }), 200


@admin_bp.route('/staff', methods=['GET'])
@admin_required
def list_staff():
    """List all staff members and their assigned treks"""
    staff_members = User.query.filter_by(role='staff').all()
    results = []
    for s in staff_members:
        treks = Trek.query.filter_by(assigned_staff_id=s.id).all()
        s_dict = s.to_dict()
        s_dict['assigned_treks_list'] = [{'id': t.id, 'name': t.name, 'location': t.location, 'status': t.status} for t in treks]
        s_dict['treks_count'] = len(treks)
        results.append(s_dict)
    return jsonify({'staff': results}), 200


@admin_bp.route('/staff', methods=['POST'])
@admin_required
def create_staff():
    """Admin creates a new trek staff account"""
    data = request.get_json() or {}
    username = data.get('username', '').strip()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '').strip()
    name = data.get('name', '').strip()
    contact_no = data.get('contact_no', '').strip()
    specialization = data.get('specialization', '').strip()
    experience_years = data.get('experience_years', 0)

    if not username or not email or not password or not name:
        return jsonify({'error': 'Username, email, password, and name are required'}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({'error': 'Username already exists'}), 409

    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already registered'}), 409

    new_staff = User(
        username=username,
        email=email,
        name=name,
        contact_no=contact_no,
        role='staff',
        specialization=specialization,
        experience_years=int(experience_years) if experience_years else 0,
        is_active=True,
        is_blacklisted=False
    )
    new_staff.set_password(password)

    db.session.add(new_staff)
    db.session.commit()

    return jsonify({'message': 'Trek Staff onboarded successfully', 'staff': new_staff.to_dict()}), 201


@admin_bp.route('/users', methods=['GET'])
@admin_required
def list_users():
    """Search and view all users and staff"""
    search = request.args.get('search', '').strip()
    role = request.args.get('role', '').strip()

    query = User.query
    if search:
        query = query.filter(
            (User.name.ilike(f'%{search}%')) |
            (User.email.ilike(f'%{search}%')) |
            (User.username.ilike(f'%{search}%'))
        )
    if role:
        query = query.filter_by(role=role)

    users = query.order_by(User.created_at.desc()).all()
    return jsonify({'users': [u.to_dict() for u in users]}), 200


@admin_bp.route('/users/<int:user_id>/status', methods=['PUT'])
@admin_required
def update_user_status(user_id):
    """Deactivate or blacklist user/staff"""
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    if user.role == 'admin':
        return jsonify({'error': 'Cannot deactivate or blacklist superuser Admin'}), 400

    data = request.get_json() or {}
    if 'is_active' in data:
        user.is_active = bool(data['is_active'])
    if 'is_blacklisted' in data:
        user.is_blacklisted = bool(data['is_blacklisted'])

    db.session.commit()
    return jsonify({'message': f"User status updated for {user.name}", 'user': user.to_dict()}), 200


@admin_bp.route('/assign-staff', methods=['POST'])
@admin_required
def assign_staff_to_trek():
    """Assign or reassign a staff member to a trek"""
    data = request.get_json() or {}
    trek_id = data.get('trek_id')
    staff_id = data.get('staff_id')

    trek = Trek.query.get(trek_id)
    if not trek:
        return jsonify({'error': 'Trek not found'}), 404

    if staff_id:
        staff = User.query.filter_by(id=staff_id, role='staff').first()
        if not staff:
            return jsonify({'error': 'Staff member not found'}), 404
        trek.assigned_staff_id = staff.id
    else:
        trek.assigned_staff_id = None

    db.session.commit()
    return jsonify({'message': 'Staff assigned successfully', 'trek': trek.to_dict()}), 200


@admin_bp.route('/bookings', methods=['GET'])
@admin_required
def list_all_bookings():
    """Admin views all historical and active bookings"""
    trek_id = request.args.get('trek_id', type=int)
    status = request.args.get('status', '').strip()

    query = Booking.query
    if trek_id:
        query = query.filter_by(trek_id=trek_id)
    if status:
        query = query.filter_by(status=status)

    bookings = query.order_by(Booking.booking_date.desc()).all()
    return jsonify({'bookings': [b.to_dict() for b in bookings]}), 200
