"""
User model for authentication and user management
"""

from flask_login import UserMixin
from flask_bcrypt import check_password_hash, generate_password_hash
from datetime import datetime
from app import db

class User(UserMixin, db.Model):
    """User model for both Donors and NGOs"""
    
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    user_type = db.Column(db.Enum('donor', 'ngo', name='user_types'), nullable=False, index=True)
    full_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    city = db.Column(db.String(50))
    
    # NGO specific fields
    organization_name = db.Column(db.String(100))  # Required for NGOs
    registration_number = db.Column(db.String(50))  # Required for NGOs
    
    # Account status
    is_active = db.Column(db.Boolean, default=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    food_donations = db.relationship('FoodDonation', backref='donor', lazy='dynamic', cascade='all, delete-orphan')
    claims = db.relationship('Claim', backref='ngo', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<User {self.username} ({self.user_type}))>'
    
    def set_password(self, password):
        """Set password hash"""
        self.password_hash = generate_password_hash(password).decode('utf-8')
    
    def check_password(self, password):
        """Check if provided password matches hash"""
        return check_password_hash(self.password_hash, password)
    
    def is_donor(self):
        """Check if user is a donor"""
        return self.user_type == 'donor'
    
    def is_ngo(self):
        """Check if user is an NGO"""
        return self.user_type == 'ngo'
    
    def get_display_name(self):
        """Get display name for the user"""
        if self.is_ngo() and self.organization_name:
            return self.organization_name
        return self.full_name
    
    def to_dict(self):
        """Convert user to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'user_type': self.user_type,
            'full_name': self.full_name,
            'phone': self.phone,
            'city': self.city,
            'organization_name': self.organization_name,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    @staticmethod
    def validate_ngo_fields(organization_name, registration_number):
        """Validate required NGO fields"""
        if not organization_name or not organization_name.strip():
            return False, "Organization name is required for NGOs"
        if not registration_number or not registration_number.strip():
            return False, "Registration number is required for NGOs"
        return True, "Valid"