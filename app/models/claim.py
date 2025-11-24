"""
Claim model for tracking NGO food donation claims
"""

from datetime import datetime
from app import db

class Claim(db.Model):
    """Claim model to track NGO claims on food donations"""
    
    __tablename__ = 'claims'
    
    id = db.Column(db.Integer, primary_key=True)
    donation_id = db.Column(
        db.Integer, 
        db.ForeignKey('food_donations.id'), 
        nullable=False, 
        unique=True,  # One donation can only have one claim
        index=True
    )
    ngo_id = db.Column(
        db.Integer, 
        db.ForeignKey('users.id'), 
        nullable=False, 
        index=True
    )
    
    # Claim status and timing
    status = db.Column(
        db.Enum('claimed', 'scheduled', 'picked_up', 'completed', 'cancelled', name='claim_status'),
        default='claimed',
        nullable=False,
        index=True
    )
    
    # Timestamps
    claimed_at = db.Column(db.DateTime, default=datetime.utcnow)
    pickup_scheduled_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    
    # Additional notes
    notes = db.Column(db.Text)
    
    def __repr__(self):
        return f'<Claim {self.ngo.username} -> {self.donation.title}>'
    
    def is_active(self):
        """Check if claim is still active (not completed or cancelled)"""
        return self.status not in ['completed', 'cancelled']
    
    def can_be_cancelled(self):
        """Check if claim can be cancelled"""
        return self.status in ['claimed', 'scheduled']
    
    def get_status_class(self):
        """Get CSS class for status display"""
        status_classes = {
            'claimed': 'info',
            'scheduled': 'primary',
            'picked_up': 'warning',
            'completed': 'success',
            'cancelled': 'danger'
        }
        return status_classes.get(self.status, 'secondary')
    
    def mark_as_completed(self):
        """Mark claim as completed and update donation status"""
        self.status = 'completed'
        self.completed_at = datetime.utcnow()
        
        # Update donation status
        if self.donation:
            self.donation.status = 'completed'
    
    def cancel_claim(self, reason=None):
        """Cancel the claim and make donation available again"""
        self.status = 'cancelled'
        if reason:
            self.notes = f"Cancelled: {reason}"
        
        # Make donation available again
        if self.donation:
            self.donation.status = 'available'
    
    def schedule_pickup(self, scheduled_time, notes=None):
        """Schedule pickup for the claim"""
        self.status = 'scheduled'
        self.pickup_scheduled_at = scheduled_time
        if notes:
            self.notes = notes
    
    def mark_as_picked_up(self, notes=None):
        """Mark as picked up"""
        self.status = 'picked_up'
        if notes:
            self.notes = notes
    
    def to_dict(self, include_donation=False, include_ngo=False):
        """Convert claim to dictionary for JSON serialization"""
        data = {
            'id': self.id,
            'status': self.status,
            'claimed_at': self.claimed_at.isoformat() if self.claimed_at else None,
            'pickup_scheduled_at': self.pickup_scheduled_at.isoformat() if self.pickup_scheduled_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'notes': self.notes
        }
        
        if include_donation and self.donation:
            data['donation'] = self.donation.to_dict()
        
        if include_ngo and self.ngo:
            data['ngo'] = {
                'id': self.ngo.id,
                'name': self.ngo.get_display_name(),
                'phone': self.ngo.phone,
                'email': self.ngo.email
            }
        
        return data
    
    @staticmethod
    def get_claims_for_ngo(ngo_id, status=None):
        """Get claims for a specific NGO"""
        query = Claim.query.filter_by(ngo_id=ngo_id)
        
        if status:
            query = query.filter_by(status=status)
        
        return query.order_by(Claim.claimed_at.desc())
    
    @staticmethod
    def get_claims_for_donor(donor_id, status=None):
        """Get claims for donations by a specific donor"""
        from app.models.food_donation import FoodDonation
        
        query = Claim.query.join(FoodDonation).filter(FoodDonation.donor_id == donor_id)
        
        if status:
            query = query.filter(Claim.status == status)
        
        return query.order_by(Claim.claimed_at.desc())