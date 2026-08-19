from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from functools import wraps
from models import User
from database import db

auth_bp = Blueprint('auth_bp', __name__)

def role_required(allowed_roles):
    """Decorator to enforce role-based access control"""
    def decorator(fn):
        @wraps(fn)
        @jwt_required()
        def wrapper(*args, **kwargs):
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            if not user:
                return jsonify({'error': 'User not found'}), 404
            if not user.is_active or user.is_blacklisted:
                return jsonify({'error': 'Your account is deactivated or blacklisted. Contact Admin.'}), 403
            if user.role not in allowed_roles:
                return jsonify({'error': f'Access denied: {user.role} is not authorized for this resource'}), 403
            return fn(*args, **kwargs)
        return wrapper
    return decorator

def admin_required(fn):
    return role_required(['admin'])(fn)

def staff_required(fn):
    return role_required(['admin', 'staff'])(fn)

def user_required(fn):
    return role_required(['user'])(fn)


@auth_bp.route('/register', methods=['POST'])
def register():
    """Trekker self-registration only. Admin and Staff cannot register here."""
    data = request.get_json() or {}
    username = data.get('username', '').strip()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '').strip()
    name = data.get('name', '').strip()
    contact_no = data.get('contact_no', '').strip()

    if not username or not email or not password or not name:
        return jsonify({'error': 'Username, email, password, and full name are required'}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({'error': 'Username is already taken'}), 409

    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email is already registered'}), 409

    # Strictly role='user'
    new_user = User(
        username=username,
        email=email,
        name=name,
        contact_no=contact_no,
        role='user',
        is_active=True,
        is_blacklisted=False
    )
    new_user.set_password(password)

    db.session.add(new_user)
    db.session.commit()

    access_token = create_access_token(identity=str(new_user.id))
    return jsonify({
        'message': 'Registration successful! Welcome to TMA.',
        'access_token': access_token,
        'user': new_user.to_dict()
    }), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    """Unified login for Admin, Staff, and Trekkers"""
    data = request.get_json() or {}
    identifier = data.get('identifier', '').strip()  # email or username
    password = data.get('password', '').strip()

    if not identifier or not password:
        return jsonify({'error': 'Please provide email/username and password'}), 400

    user = User.query.filter((User.email == identifier.lower()) | (User.username == identifier)).first()

    if not user or not user.check_password(password):
        return jsonify({'error': 'Invalid email/username or password'}), 401

    if not user.is_active:
        return jsonify({'error': 'Account has been deactivated. Please contact the administrator.'}), 403

    if user.is_blacklisted:
        return jsonify({'error': 'Account is blacklisted. Access denied.'}), 403

    access_token = create_access_token(identity=str(user.id))
    return jsonify({
        'message': f'Welcome back, {user.name}!',
        'access_token': access_token,
        'user': user.to_dict()
    }), 200


@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    return jsonify({'user': user.to_dict()}), 200


@auth_bp.route('/me', methods=['PUT'])
@jwt_required()
def update_profile():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    data = request.get_json() or {}
    if 'name' in data and data['name'].strip():
        user.name = data['name'].strip()
    if 'contact_no' in data:
        user.contact_no = data['contact_no'].strip()
    if 'specialization' in data and user.role == 'staff':
        user.specialization = data['specialization']
    if 'experience_years' in data and user.role == 'staff':
        try:
            user.experience_years = int(data['experience_years'])
        except ValueError:
            pass

    db.session.commit()
    return jsonify({'message': 'Profile updated successfully', 'user': user.to_dict()}), 200


@auth_bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    data = request.get_json() or {}
    old_password = data.get('old_password', '')
    new_password = data.get('new_password', '')

    if not old_password or not new_password:
        return jsonify({'error': 'Both old and new passwords are required'}), 400

    if not user.check_password(old_password):
        return jsonify({'error': 'Current password does not match'}), 400

    if len(new_password) < 6:
        return jsonify({'error': 'New password must be at least 6 characters'}), 400

    user.set_password(new_password)
    db.session.commit()
    return jsonify({'message': 'Password changed successfully'}), 200
