from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from database import db

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='user')  # 'admin', 'staff', 'user'
    name = db.Column(db.String(100), nullable=False)
    contact_no = db.Column(db.String(20), nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    is_blacklisted = db.Column(db.Boolean, default=False, nullable=False)
    
    # Optional staff profile fields
    experience_years = db.Column(db.Integer, default=0)
    specialization = db.Column(db.String(100), nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    assigned_treks = db.relationship('Trek', back_populates='assigned_staff', foreign_keys='Trek.assigned_staff_id', lazy='dynamic')
    bookings = db.relationship('Booking', back_populates='user', lazy='dynamic', cascade='all, delete-orphan')
    notifications = db.relationship('Notification', back_populates='user', lazy='dynamic', cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'name': self.name,
            'contact_no': self.contact_no,
            'is_active': self.is_active,
            'is_blacklisted': self.is_blacklisted,
            'experience_years': self.experience_years,
            'specialization': self.specialization,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }


class Trek(db.Model):
    __tablename__ = 'treks'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False, index=True)
    location = db.Column(db.String(150), nullable=False, index=True)
    difficulty = db.Column(db.String(20), nullable=False, default='Moderate')  # 'Easy', 'Moderate', 'Hard'
    duration_days = db.Column(db.Integer, nullable=False, default=1)
    total_slots = db.Column(db.Integer, nullable=False, default=20)
    available_slots = db.Column(db.Integer, nullable=False, default=20)
    
    assigned_staff_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    status = db.Column(db.String(20), nullable=False, default='Open')  # 'Pending', 'Approved', 'Open', 'Closed', 'Completed'
    
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Float, default=0.0)
    image_url = db.Column(db.String(500), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    assigned_staff = db.relationship('User', back_populates='assigned_treks', foreign_keys=[assigned_staff_id])
    bookings = db.relationship('Booking', back_populates='trek', lazy='dynamic', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'location': self.location,
            'difficulty': self.difficulty,
            'duration_days': self.duration_days,
            'total_slots': self.total_slots,
            'available_slots': self.available_slots,
            'assigned_staff_id': self.assigned_staff_id,
            'assigned_staff_name': self.assigned_staff.name if self.assigned_staff else 'Unassigned',
            'assigned_staff_email': self.assigned_staff.email if self.assigned_staff else None,
            'assigned_staff_contact': self.assigned_staff.contact_no if self.assigned_staff else None,
            'status': self.status,
            'start_date': self.start_date.strftime('%Y-%m-%d') if self.start_date else None,
            'end_date': self.end_date.strftime('%Y-%m-%d') if self.end_date else None,
            'description': self.description,
            'price': self.price,
            'image_url': self.image_url,
            'booked_count': self.total_slots - self.available_slots,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }


class Booking(db.Model):
    __tablename__ = 'bookings'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    trek_id = db.Column(db.Integer, db.ForeignKey('treks.id'), nullable=False, index=True)
    booking_date = db.Column(db.DateTime, default=datetime.utcnow)
    seats = db.Column(db.Integer, default=1, nullable=False)
    status = db.Column(db.String(20), default='Booked', nullable=False)  # 'Booked', 'Cancelled', 'Completed'
    payment_status = db.Column(db.String(20), default='Paid')  # 'Paid', 'Pending', 'Refunded'
    total_amount = db.Column(db.Float, default=0.0)
    special_notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    user = db.relationship('User', back_populates='bookings')
    trek = db.relationship('Trek', back_populates='bookings')

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'user_name': self.user.name if self.user else None,
            'user_email': self.user.email if self.user else None,
            'user_contact': self.user.contact_no if self.user else None,
            'trek_id': self.trek_id,
            'trek_name': self.trek.name if self.trek else 'Unknown Trek',
            'trek_location': self.trek.location if self.trek else 'Unknown',
            'trek_difficulty': self.trek.difficulty if self.trek else 'Moderate',
            'trek_start_date': self.trek.start_date.strftime('%Y-%m-%d') if self.trek and self.trek.start_date else None,
            'trek_end_date': self.trek.end_date.strftime('%Y-%m-%d') if self.trek and self.trek.end_date else None,
            'trek_status': self.trek.status if self.trek else 'Unknown',
            'assigned_staff_name': self.trek.assigned_staff.name if self.trek and self.trek.assigned_staff else 'Unassigned',
            'booking_date': self.booking_date.strftime('%Y-%m-%d %H:%M:%S') if self.booking_date else None,
            'seats': self.seats,
            'status': self.status,
            'payment_status': self.payment_status,
            'total_amount': self.total_amount,
            'special_notes': self.special_notes,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }


class Notification(db.Model):
    __tablename__ = 'notifications'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    title = db.Column(db.String(150), nullable=False)
    message = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(30), default='reminder')  # 'reminder', 'booking', 'cancellation', 'report', 'system'
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship
    user = db.relationship('User', back_populates='notifications')

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'message': self.message,
            'type': self.type,
            'is_read': self.is_read,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }


class ExportJob(db.Model):
    __tablename__ = 'export_jobs'

    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.String(100), unique=True, nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    status = db.Column(db.String(20), default='PENDING')  # 'PENDING', 'SUCCESS', 'FAILURE'
    file_name = db.Column(db.String(200), nullable=True)
    file_path = db.Column(db.String(300), nullable=True)
    download_url = db.Column(db.String(300), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'task_id': self.task_id,
            'user_id': self.user_id,
            'status': self.status,
            'file_name': self.file_name,
            'download_url': self.download_url,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'completed_at': self.completed_at.strftime('%Y-%m-%d %H:%M:%S') if self.completed_at else None
        }
