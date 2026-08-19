from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from models import Trek, User
from database import db, cache
from routes.auth_routes import admin_required, staff_required

trek_bp = Blueprint('trek_bp', __name__)

def invalidate_trek_cache():
    try:
        cache.clear()
    except Exception as e:
        print(f"[CACHE CLEAR WARNING] {e}")


@trek_bp.route('', methods=['GET'])
@trek_bp.route('/', methods=['GET'])
def get_treks():
    """
    Search and filter treks with Redis caching.
    Supported filters: search query, difficulty, location, min_duration, max_duration, min_price, max_price, status
    """
    search_query = request.args.get('search', '').strip()
    difficulty = request.args.get('difficulty', '').strip()
    location = request.args.get('location', '').strip()
    status = request.args.get('status', '').strip()
    min_duration = request.args.get('min_duration', type=int)
    max_duration = request.args.get('max_duration', type=int)
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)

    # Build cache key based on query parameters
    cache_key = f"treks_list_{search_query}_{difficulty}_{location}_{status}_{min_duration}_{max_duration}_{min_price}_{max_price}"
    
    cached_data = None
    try:
        cached_data = cache.get(cache_key)
    except Exception:
        pass

    if cached_data is not None:
        return jsonify({'treks': cached_data, 'cached': True}), 200

    query = Trek.query

    if search_query:
        query = query.filter(
            (Trek.name.ilike(f'%{search_query}%')) |
            (Trek.location.ilike(f'%{search_query}%')) |
            (Trek.description.ilike(f'%{search_query}%'))
        )
    if difficulty:
        query = query.filter(Trek.difficulty == difficulty)
    if location:
        query = query.filter(Trek.location.ilike(f'%{location}%'))
    if status:
        query = query.filter(Trek.status == status)
    if min_duration is not None:
        query = query.filter(Trek.duration_days >= min_duration)
    if max_duration is not None:
        query = query.filter(Trek.duration_days <= max_duration)
    if min_price is not None:
        query = query.filter(Trek.price >= min_price)
    if max_price is not None:
        query = query.filter(Trek.price <= max_price)

    treks = query.order_by(Trek.start_date.asc()).all()
    results = [t.to_dict() for t in treks]

    try:
        cache.set(cache_key, results, timeout=120)  # 2 min TTL
    except Exception:
        pass

    return jsonify({'treks': results, 'cached': False}), 200


@trek_bp.route('/<int:trek_id>', methods=['GET'])
def get_trek(trek_id):
    """Retrieve details for a single trek with caching"""
    cache_key = f"trek_detail_{trek_id}"
    try:
        cached_trek = cache.get(cache_key)
        if cached_trek:
            return jsonify({'trek': cached_trek, 'cached': True}), 200
    except Exception:
        pass

    trek = Trek.query.get(trek_id)
    if not trek:
        return jsonify({'error': 'Trek not found'}), 404

    data = trek.to_dict()
    try:
        cache.set(cache_key, data, timeout=300)
    except Exception:
        pass

    return jsonify({'trek': data, 'cached': False}), 200


@trek_bp.route('', methods=['POST'])
@trek_bp.route('/', methods=['POST'])
@admin_required
def create_trek():
    """Admin creates a new trek route and event"""
    data = request.get_json() or {}
    
    name = data.get('name', '').strip()
    location = data.get('location', '').strip()
    difficulty = data.get('difficulty', 'Moderate')
    duration_days = data.get('duration_days', 1)
    total_slots = data.get('total_slots', 20)
    start_date_str = data.get('start_date')
    end_date_str = data.get('end_date')
    price = data.get('price', 0.0)
    description = data.get('description', '')
    image_url = data.get('image_url', '')
    assigned_staff_id = data.get('assigned_staff_id')
    status = data.get('status', 'Open')

    if not name or not location or not start_date_str or not end_date_str:
        return jsonify({'error': 'Name, location, start date, and end date are required'}), 400

    try:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        if end_date < start_date:
            return jsonify({'error': 'End date cannot be before start date'}), 400
    except ValueError:
        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400

    if assigned_staff_id:
        staff_user = User.query.filter_by(id=assigned_staff_id, role='staff').first()
        if not staff_user:
            return jsonify({'error': 'Assigned staff member not found or invalid role'}), 400

    new_trek = Trek(
        name=name,
        location=location,
        difficulty=difficulty,
        duration_days=int(duration_days),
        total_slots=int(total_slots),
        available_slots=int(total_slots),
        assigned_staff_id=assigned_staff_id,
        status=status,
        start_date=start_date,
        end_date=end_date,
        description=description,
        price=float(price),
        image_url=image_url
    )

    db.session.add(new_trek)
    db.session.commit()

    invalidate_trek_cache()
    return jsonify({'message': 'Trek created successfully', 'trek': new_trek.to_dict()}), 201


@trek_bp.route('/<int:trek_id>', methods=['PUT'])
@jwt_required()
def update_trek(trek_id):
    """Admin or assigned Staff updates trek information"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    trek = Trek.query.get(trek_id)
    if not trek:
        return jsonify({'error': 'Trek not found'}), 404

    # Staff permission check
    if user.role == 'staff' and trek.assigned_staff_id != user.id:
        return jsonify({'error': 'Permission denied: You can only update treks assigned to you'}), 403

    if user.role not in ['admin', 'staff']:
        return jsonify({'error': 'Unauthorized'}), 403

    data = request.get_json() or {}

    if user.role == 'admin':
        # Admin can update everything
        if 'name' in data: trek.name = data['name'].strip()
        if 'location' in data: trek.location = data['location'].strip()
        if 'difficulty' in data: trek.difficulty = data['difficulty']
        if 'duration_days' in data: trek.duration_days = int(data['duration_days'])
        if 'total_slots' in data:
            new_total = int(data['total_slots'])
            booked = trek.total_slots - trek.available_slots
            trek.total_slots = new_total
            trek.available_slots = max(0, new_total - booked)
        if 'assigned_staff_id' in data:
            staff_id = data['assigned_staff_id']
            if staff_id:
                staff_user = User.query.filter_by(id=staff_id, role='staff').first()
                if not staff_user:
                    return jsonify({'error': 'Assigned staff not found'}), 400
            trek.assigned_staff_id = staff_id
        if 'price' in data: trek.price = float(data['price'])
        if 'image_url' in data: trek.image_url = data['image_url']
        if 'description' in data: trek.description = data['description']
        if 'start_date' in data and data['start_date']:
            trek.start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
        if 'end_date' in data and data['end_date']:
            trek.end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date()

    # Staff can update slots and status
    if 'status' in data:
        trek.status = data['status']
    if 'available_slots' in data:
        new_avail = int(data['available_slots'])
        if new_avail < 0 or new_avail > trek.total_slots:
            return jsonify({'error': f'Available slots must be between 0 and {trek.total_slots}'}), 400
        trek.available_slots = new_avail

    db.session.commit()
    invalidate_trek_cache()
    return jsonify({'message': 'Trek updated successfully', 'trek': trek.to_dict()}), 200


@trek_bp.route('/<int:trek_id>', methods=['DELETE'])
@admin_required
def delete_trek(trek_id):
    """Admin removes a trek route"""
    trek = Trek.query.get(trek_id)
    if not trek:
        return jsonify({'error': 'Trek not found'}), 404

    db.session.delete(trek)
    db.session.commit()

    invalidate_trek_cache()
    return jsonify({'message': f"Trek '{trek.name}' deleted successfully"}), 200
