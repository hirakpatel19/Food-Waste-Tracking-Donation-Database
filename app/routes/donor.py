"""
Routes for food donors - managing food donations
"""

from flask import Blueprint, render_template, request, flash, redirect, url_for, abort
from flask_login import login_required, current_user
from app import db
from app.models.food_donation import FoodDonation
from app.models.claim import Claim
from app.forms.donation import FoodDonationForm
from datetime import date

donor_bp = Blueprint('donor', __name__)

def donor_required(f):
    """Decorator to require donor user type"""
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_donor():
            flash('Access denied. Donor account required.', 'error')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@donor_bp.route('/dashboard')
@login_required
@donor_required
def dashboard():
    """Donor dashboard"""
    # Get donor's donations statistics
    total_donations = FoodDonation.query.filter_by(donor_id=current_user.id).count()
    available_donations = FoodDonation.query.filter_by(
        donor_id=current_user.id, 
        status='available'
    ).filter(FoodDonation.expiry_date >= date.today()).count()
    
    claimed_donations = FoodDonation.query.filter_by(
        donor_id=current_user.id, 
        status='claimed'
    ).count()
    
    completed_donations = FoodDonation.query.filter_by(
        donor_id=current_user.id, 
        status='completed'
    ).count()
    
    # Get recent donations
    recent_donations = FoodDonation.query.filter_by(donor_id=current_user.id)\
        .order_by(FoodDonation.created_at.desc()).limit(5).all()
    
    # Update expired donations
    expired_count = 0
    for donation in FoodDonation.query.filter_by(donor_id=current_user.id, status='available'):
        if donation.update_status_if_expired():
            expired_count += 1
    
    if expired_count > 0:
        db.session.commit()
    
    stats = {
        'total': total_donations,
        'available': available_donations,
        'claimed': claimed_donations,
        'completed': completed_donations
    }
    
    return render_template('donor/dashboard.html', 
                         stats=stats, 
                         recent_donations=recent_donations)

@donor_bp.route('/donations')
@login_required
@donor_required
def my_donations():
    """View all donor's donations"""
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', '')
    
    query = FoodDonation.query.filter_by(donor_id=current_user.id)
    
    if status_filter:
        query = query.filter_by(status=status_filter)
    
    donations = query.order_by(FoodDonation.created_at.desc()).paginate(
        page=page, per_page=10, error_out=False
    )
    
    return render_template('donor/donations.html', 
                         donations=donations, 
                         status_filter=status_filter)

@donor_bp.route('/add-donation', methods=['GET', 'POST'])
@login_required
@donor_required
def add_donation():
    """Add new food donation"""
    form = FoodDonationForm()
    
    if form.validate_on_submit():
        donation = FoodDonation(
            donor_id=current_user.id,
            category_id=form.category_id.data,
            title=form.title.data.strip(),
            description=form.description.data.strip() if form.description.data else None,
            quantity=form.quantity.data,
            unit=form.unit.data,
            expiry_date=form.expiry_date.data,
            pickup_address=form.pickup_address.data.strip(),
            pickup_city=form.pickup_city.data.strip(),
            pickup_instructions=form.pickup_instructions.data.strip() if form.pickup_instructions.data else None,
            is_perishable=form.is_perishable.data,
            dietary_info=form.dietary_info.data if form.dietary_info.data else None
        )
        
        try:
            db.session.add(donation)
            db.session.commit()
            flash(f'Food donation "{donation.title}" has been added successfully!', 'success')
            return redirect(url_for('donor.dashboard'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while adding the donation.', 'error')
    
    return render_template('donor/add_donation.html', form=form)

@donor_bp.route('/edit-donation/<int:id>', methods=['GET', 'POST'])
@login_required
@donor_required
def edit_donation(id):
    """Edit existing food donation"""
    donation = FoodDonation.query.filter_by(id=id, donor_id=current_user.id).first_or_404()
    
    if not donation.can_be_edited():
        flash('This donation cannot be edited as it has already been claimed.', 'error')
        return redirect(url_for('donor.view_donation', id=id))
    
    form = FoodDonationForm(obj=donation)
    
    if form.validate_on_submit():
        donation.category_id = form.category_id.data
        donation.title = form.title.data.strip()
        donation.description = form.description.data.strip() if form.description.data else None
        donation.quantity = form.quantity.data
        donation.unit = form.unit.data
        donation.expiry_date = form.expiry_date.data
        donation.pickup_address = form.pickup_address.data.strip()
        donation.pickup_city = form.pickup_city.data.strip()
        donation.pickup_instructions = form.pickup_instructions.data.strip() if form.pickup_instructions.data else None
        donation.is_perishable = form.is_perishable.data
        donation.dietary_info = form.dietary_info.data if form.dietary_info.data else None
        
        try:
            db.session.commit()
            flash(f'Donation "{donation.title}" has been updated successfully!', 'success')
            return redirect(url_for('donor.view_donation', id=id))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while updating the donation.', 'error')
    
    return render_template('donor/edit_donation.html', form=form, donation=donation)

@donor_bp.route('/donation/<int:id>')
@login_required
@donor_required
def view_donation(id):
    """View single donation details"""
    donation = FoodDonation.query.filter_by(id=id, donor_id=current_user.id).first_or_404()
    
    # Update status if expired
    if donation.update_status_if_expired():
        db.session.commit()
    
    return render_template('donor/view_donation.html', donation=donation)

@donor_bp.route('/delete-donation/<int:id>', methods=['POST'])
@login_required
@donor_required
def delete_donation(id):
    """Delete food donation"""
    donation = FoodDonation.query.filter_by(id=id, donor_id=current_user.id).first_or_404()
    
    if not donation.can_be_edited():
        flash('This donation cannot be deleted as it has already been claimed.', 'error')
        return redirect(url_for('donor.view_donation', id=id))
    
    title = donation.title
    
    try:
        db.session.delete(donation)
        db.session.commit()
        flash(f'Donation "{title}" has been deleted successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('An error occurred while deleting the donation.', 'error')
    
    return redirect(url_for('donor.my_donations'))

@donor_bp.route('/claims')
@login_required
@donor_required
def view_claims():
    """View claims on donor's food donations"""
    page = request.args.get('page', 1, type=int)
    
    claims = Claim.get_claims_for_donor(current_user.id).paginate(
        page=page, per_page=10, error_out=False
    )
    
    return render_template('donor/claims.html', claims=claims)