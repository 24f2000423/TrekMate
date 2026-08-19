from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import User, Trek, Booking
from database import db, cache
from routes.auth_routes import staff_required

staff_bp = Blueprint('staff_bp', __name__)

@staff_bp.route('/treks', methods=['GET'])
@staff_required
def get_staff_assigned_treks():
    """List all treks assigned to current staff member"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    if user.role == 'admin':
        treks = Trek.query.all()
    else:
        treks = Trek.query.filter_by(assigned_staff_id=user.id).all()

    results = []
    for t in treks:
        t_dict = t.to_dict()
        t_dict['registered_users_count'] = Booking.query.filter_by(trek_id=t.id, status='Booked').count()
        results.append(t_dict)

    return jsonify({'treks': results}), 200


@staff_bp.route('/treks/<int:trek_id>/participants', methods=['GET'])
@staff_required
def get_trek_participants(trek_id):
    """View list of registered users/participants for an assigned trek"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    trek = Trek.query.get(trek_id)

    if not trek:
        return jsonify({'error': 'Trek not found'}), 404

    if user.role == 'staff' and trek.assigned_staff_id != user.id:
        return jsonify({'error': 'Access denied: You are not assigned to this trek'}), 403

    bookings = Booking.query.filter_by(trek_id=trek_id).order_by(Booking.booking_date.desc()).all()
    participants = []
    for b in bookings:
        participants.append({
            'booking_id': b.id,
            'user_id': b.user_id,
            'name': b.user.name if b.user else 'Unknown',
            'email': b.user.email if b.user else 'Unknown',
            'contact_no': b.user.contact_no if b.user else 'N/A',
            'seats': b.seats,
            'status': b.status,
            'payment_status': b.payment_status,
            'booking_date': b.booking_date.strftime('%Y-%m-%d %H:%M:%S') if b.booking_date else None,
            'special_notes': b.special_notes
        })

    return jsonify({
        'trek': trek.to_dict(),
        'participants': participants,
        'total_registered': len([p for p in participants if p['status'] == 'Booked'])
    }), 200


@staff_bp.route('/treks/<int:trek_id>/status', methods=['PUT'])
@staff_required
def update_trek_operational_status(trek_id):
    """Staff updates slots, marks trek as Open / Closed / Started / Completed"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    trek = Trek.query.get(trek_id)

    if not trek:
        return jsonify({'error': 'Trek not found'}), 404

    if user.role == 'staff' and trek.assigned_staff_id != user.id:
        return jsonify({'error': 'Access denied: You are not assigned to this trek'}), 403

    data = request.get_json() or {}
    if 'status' in data:
        new_status = data['status']
        if new_status not in ['Pending', 'Approved', 'Open', 'Closed', 'Started', 'Completed']:
            return jsonify({'error': 'Invalid status'}), 400
        trek.status = new_status

    if 'available_slots' in data:
        new_slots = int(data['available_slots'])
        if new_slots < 0 or new_slots > trek.total_slots:
            return jsonify({'error': f'Available slots must be between 0 and {trek.total_slots}'}), 400
        trek.available_slots = new_slots

    db.session.commit()
    try:
        cache.clear()
    except Exception:
        pass

    return jsonify({
        'message': f"Trek '{trek.name}' operational status updated",
        'trek': trek.to_dict()
    }), 200
