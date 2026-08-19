from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from models import Booking, Trek, User, Notification
from database import db, cache
from routes.auth_routes import user_required

booking_bp = Blueprint('booking_bp', __name__)

@booking_bp.route('', methods=['POST'])
@booking_bp.route('/', methods=['POST'])
@user_required
def create_booking():
    """
    User books a trek with validations:
    - Trek exists and is Open
    - No duplicate active booking for the same trek
    - Cannot overbook beyond available slots
    """
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    data = request.get_json() or {}
    trek_id = data.get('trek_id')
    seats = int(data.get('seats', 1))
    special_notes = data.get('special_notes', '').strip()

    if not trek_id or seats <= 0:
        return jsonify({'error': 'Invalid trek ID or number of seats'}), 400

    trek = Trek.query.get(trek_id)
    if not trek:
        return jsonify({'error': 'Trek not found'}), 404

    # 1. Status Check: Booking allowed only when trek status is Open
    if trek.status != 'Open':
        return jsonify({'error': f'Booking closed. This trek is currently {trek.status}.'}), 400

    # 2. Check for duplicate booking
    existing_booking = Booking.query.filter_by(
        user_id=user.id,
        trek_id=trek.id,
        status='Booked'
    ).first()
    if existing_booking:
        return jsonify({'error': 'You already have an active booking for this trek.'}), 400

    # 3. Check Slot Availability (Prevent overbooking)
    if trek.available_slots < seats:
        return jsonify({'error': f'Not enough slots available. Only {trek.available_slots} slot(s) left.'}), 400

    # Calculate total
    total_amount = round(trek.price * seats, 2)

    # Decrement available slots
    trek.available_slots -= seats

    # Create Booking
    booking = Booking(
        user_id=user.id,
        trek_id=trek.id,
        seats=seats,
        status='Booked',
        payment_status='Paid',  # Simulated payment
        total_amount=total_amount,
        special_notes=special_notes
    )
    db.session.add(booking)

    # In-app confirmation notification
    notif = Notification(
        user_id=user.id,
        title=f"Booking Confirmed: {trek.name}",
        message=f"You successfully booked {seats} slot(s) for '{trek.name}' at {trek.location} starting on {trek.start_date.strftime('%d %b %Y')}. Total: ₹{total_amount:.2f}.",
        type='booking'
    )
    db.session.add(notif)
    db.session.commit()

    try:
        cache.clear()
    except Exception:
        pass

    return jsonify({
        'message': 'Trek booked successfully! See you on the trail.',
        'booking': booking.to_dict()
    }), 201


@booking_bp.route('/my-bookings', methods=['GET'])
@jwt_required()
def get_my_bookings():
    """Retrieve all bookings for current user"""
    user_id = get_jwt_identity()
    bookings = Booking.query.filter_by(user_id=user_id).order_by(Booking.booking_date.desc()).all()
    return jsonify({'bookings': [b.to_dict() for b in bookings]}), 200


@booking_bp.route('/history', methods=['GET'])
@jwt_required()
def get_my_trekking_history():
    """Retrieve completed & historical treks for current user"""
    user_id = get_jwt_identity()
    bookings = Booking.query.filter(
        Booking.user_id == user_id,
        Booking.status.in_(['Completed', 'Booked', 'Cancelled'])
    ).order_by(Booking.booking_date.desc()).all()

    return jsonify({'history': [b.to_dict() for b in bookings]}), 200


@booking_bp.route('/<int:booking_id>/cancel', methods=['POST'])
@user_required
def cancel_booking(booking_id):
    """User cancels booking, restores slots"""
    user_id = get_jwt_identity()
    booking = Booking.query.filter_by(id=booking_id, user_id=user_id).first()

    if not booking:
        return jsonify({'error': 'Booking not found'}), 404

    if booking.status != 'Booked':
        return jsonify({'error': f'Cannot cancel booking with status: {booking.status}'}), 400

    trek = Trek.query.get(booking.trek_id)
    if trek:
        # Restore available slots
        trek.available_slots = min(trek.total_slots, trek.available_slots + booking.seats)

    booking.status = 'Cancelled'
    booking.payment_status = 'Refunded'

    # Notification
    notif = Notification(
        user_id=user_id,
        title=f"Booking Cancelled: {trek.name if trek else 'Trek'}",
        message=f"Your booking #{booking.id} for {trek.name if trek else ''} has been cancelled. {booking.seats} seat(s) refunded.",
        type='cancellation'
    )
    db.session.add(notif)
    db.session.commit()

    try:
        cache.clear()
    except Exception:
        pass

    return jsonify({
        'message': 'Booking cancelled successfully. Slots restored.',
        'booking': booking.to_dict()
    }), 200
