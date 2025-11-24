"""
Food donation and category models
"""

from datetime import datetime, date
from app import db

class Category(db.Model):
    """Food category model"""
    
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    food_donations = db.relationship('FoodDonation', backref='category', lazy='dynamic')
    
    def __repr__(self):
        return f'<Category {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description
        }

class FoodDonation(db.Model):
    """Food donation model"""
    
    __tablename__ = 'food_donations'
    
    id = db.Column(db.Integer, primary_key=True)
    donor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    
    # Food details
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    quantity = db.Column(db.Integer, nullable=False)
    unit = db.Column(db.String(20), nullable=False)  # kg, pieces, liters, etc.
    expiry_date = db.Column(db.Date, nullable=False, index=True)
    
    # Pickup details
    pickup_address = db.Column(db.Text, nullable=False)
    pickup_city = db.Column(db.String(50), nullable=False, index=True)
    pickup_instructions = db.Column(db.Text)
    
    # Status and metadata
    status = db.Column(
        db.Enum('available', 'claimed', 'completed', 'expired', name='donation_status'),
        default='available',
        nullable=False,
        index=True
    )
    is_perishable = db.Column(db.Boolean, default=True)
    dietary_info = db.Column(db.String(100))  # vegetarian, vegan, gluten-free, etc.
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    claim = db.relationship('Claim', backref='donation', uselist=False, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<FoodDonation {self.title} by {self.donor.username}>'
    
    def is_available(self):
        """Check if donation is available for claiming"""
        return self.status == 'available' and not self.is_expired()
    
    def is_expired(self):
        """Check if donation has expired"""
        return self.expiry_date < date.today()
    
    def days_until_expiry(self):
        """Get number of days until expiry"""
        delta = self.expiry_date - date.today()
        return delta.days
    
    def is_urgent(self):
        """Check if donation expires within 2 days"""
        return self.days_until_expiry() <= 2
    
    def get_status_class(self):
        """Get CSS class for status display"""
        status_classes = {
            'available': 'success' if not self.is_urgent() else 'warning',
            'claimed': 'info',
            'completed': 'secondary',
            'expired': 'danger'
        }
        return status_classes.get(self.status, 'secondary')
    
    def can_be_edited(self):
        """Check if donation can be edited by donor"""
        return self.status == 'available'
    
    def can_be_claimed(self):
        """Check if donation can be claimed by NGO"""
        return self.status == 'available' and not self.is_expired()
    
    def update_status_if_expired(self):
        """Update status to expired if past expiry date"""
        if self.is_expired() and self.status == 'available':
            self.status = 'expired'
            return True
        return False
    
    def to_dict(self, include_donor=False):
        """Convert donation to dictionary for JSON serialization"""
        data = {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'quantity': self.quantity,
            'unit': self.unit,
            'expiry_date': self.expiry_date.isoformat(),
            'pickup_address': self.pickup_address,
            'pickup_city': self.pickup_city,
            'pickup_instructions': self.pickup_instructions,
            'status': self.status,
            'is_perishable': self.is_perishable,
            'dietary_info': self.dietary_info,
            'created_at': self.created_at.isoformat(),
            'category': self.category.to_dict() if self.category else None,
            'days_until_expiry': self.days_until_expiry(),
            'is_urgent': self.is_urgent()
        }
        
        if include_donor and self.donor:
            data['donor'] = {
                'id': self.donor.id,
                'name': self.donor.get_display_name(),
                'phone': self.donor.phone
            }
        
        return data
    
    @staticmethod
    def get_available_donations(city=None, category_id=None, search=None):
        """Get available donations with optional filters"""
        query = FoodDonation.query.filter_by(status='available')
        
        # Filter by city
        if city:
            query = query.filter(FoodDonation.pickup_city.ilike(f'%{city}%'))
        
        # Filter by category
        if category_id:
            query = query.filter_by(category_id=category_id)
        
        # Search in title and description
        if search:
            search_term = f'%{search}%'
            query = query.filter(
                db.or_(
                    FoodDonation.title.ilike(search_term),
                    FoodDonation.description.ilike(search_term)
                )
            )
        
        # Exclude expired donations and order by urgency
        query = query.filter(FoodDonation.expiry_date >= date.today())
        query = query.order_by(FoodDonation.expiry_date.asc(), FoodDonation.created_at.desc())
        
        return query