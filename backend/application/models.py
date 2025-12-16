from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from application.database import db

class User(db.Model):
    """User model for both admin and regular users"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='user')  # 'admin' or 'user'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    reservations = db.relationship('Reservation', backref='user', lazy='dynamic')
    
    def __init__(self, username, email, password, role='user'):
        self.username = username
        self.email = email
        self.password = password  # Will be hashed by setter
        self.role = role
    
    @property
    def password(self):
        raise AttributeError('Password is not readable')
    
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def is_admin(self):
        return self.role == 'admin'
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'created_at': self.created_at.isoformat(),
            'is_active': self.is_active
        }
    
    def __repr__(self):
        return f'<User {self.username}>'

class ParkingLot(db.Model):
    """Parking lot model"""
    __tablename__ = 'parking_lots'
    
    id = db.Column(db.Integer, primary_key=True)
    prime_location_name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.Text, nullable=False)
    pin_code = db.Column(db.String(10), nullable=False)
    price_per_hour = db.Column(db.Float, nullable=False)
    number_of_spots = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    parking_spots = db.relationship('ParkingSpot', backref='parking_lot', lazy='dynamic', cascade='all, delete-orphan')
    
    def get_available_spots_count(self):
        """Get count of available parking spots"""
        return self.parking_spots.filter_by(status='A').count()
    
    def get_occupied_spots_count(self):
        """Get count of occupied parking spots"""
        return self.parking_spots.filter_by(status='O').count()
    
    def to_dict(self):
        return {
            'id': self.id,
            'prime_location_name': self.prime_location_name,
            'address': self.address,
            'pin_code': self.pin_code,
            'price_per_hour': self.price_per_hour,
            'number_of_spots': self.number_of_spots,
            'available_spots': self.get_available_spots_count(),
            'occupied_spots': self.get_occupied_spots_count(),
            'created_at': self.created_at.isoformat(),
            'is_active': self.is_active
        }
    
    def __repr__(self):
        return f'<ParkingLot {self.prime_location_name}>'

class ParkingSpot(db.Model):
    """Parking spot model"""
    __tablename__ = 'parking_spots'
    
    id = db.Column(db.Integer, primary_key=True)
    spot_number = db.Column(db.String(10), nullable=False)  # A1, A2, B1, etc.
    status = db.Column(db.Enum('A', 'O', name='spot_status'), default='A', nullable=False)  # A=Available, O=Occupied
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Foreign Keys
    lot_id = db.Column(db.Integer, db.ForeignKey('parking_lots.id'), nullable=False)
    
    # Relationships
    reservations = db.relationship('Reservation', backref='parking_spot', lazy='dynamic')
    
    def get_current_reservation(self):
        """Get current active reservation for this spot"""
        return self.reservations.filter_by(leaving_timestamp=None).first()
    
    def to_dict(self):
        current_reservation = self.get_current_reservation()
        return {
            'id': self.id,
            'spot_number': self.spot_number,
            'status': self.status,
            'lot_id': self.lot_id,
            'current_reservation': current_reservation.to_dict() if current_reservation else None,
            'created_at': self.created_at.isoformat()
        }
    
    def __repr__(self):
        return f'<ParkingSpot {self.spot_number} - {self.status}>'

class Reservation(db.Model):
    """Reservation model for parking spots"""
    __tablename__ = 'reservations'
    
    id = db.Column(db.Integer, primary_key=True)
    parking_timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    leaving_timestamp = db.Column(db.DateTime)
    parking_cost = db.Column(db.Float, default=0.0)
    vehicle_number = db.Column(db.String(20))
    remarks = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Foreign Keys
    spot_id = db.Column(db.Integer, db.ForeignKey('parking_spots.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    def calculate_cost(self):
        """Calculate parking cost based on duration"""
        if self.leaving_timestamp:
            duration_hours = (self.leaving_timestamp - self.parking_timestamp).total_seconds() / 3600
            # Round up to next hour
            duration_hours = max(1, int(duration_hours) + (1 if duration_hours % 1 > 0 else 0))
            self.parking_cost = duration_hours * self.parking_spot.parking_lot.price_per_hour
        return self.parking_cost
    
    def get_duration(self):
        """Get parking duration in hours"""
        if self.leaving_timestamp:
            return (self.leaving_timestamp - self.parking_timestamp).total_seconds() / 3600
        else:
            return (datetime.utcnow() - self.parking_timestamp).total_seconds() / 3600
    
    def is_active(self):
        """Check if reservation is currently active"""
        return self.leaving_timestamp is None
    
    def to_dict(self):
        return {
            'id': self.id,
            'spot_id': self.spot_id,
            'user_id': self.user_id,
            'parking_timestamp': self.parking_timestamp.isoformat(),
            'leaving_timestamp': self.leaving_timestamp.isoformat() if self.leaving_timestamp else None,
            'parking_cost': self.parking_cost,
            'vehicle_number': self.vehicle_number,
            'remarks': self.remarks,
            'duration_hours': round(self.get_duration(), 2),
            'is_active': self.is_active(),
            'created_at': self.created_at.isoformat()
        }
    
    def __repr__(self):
        return f'<Reservation {self.id} - User {self.user_id} - Spot {self.spot_id}>'