"""
Routes for NGOs - browsing and claiming food donations
"""

from flask import Blueprint, render_template, request, flash, redirect, url_for, abort
from flask_login import login_required, current_user
from app import db
from app.models.food_donation import FoodDonation
from app.models.claim import Claim
from app.forms.donation import SearchDonationsForm, ClaimForm, UpdateClaimForm
from datetime import date, timedelta

ngo_bp = Blueprint('ngo', __name__)

def ngo_required(f):
    """Decorator to require NGO user type"""
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_ngo():
            flash('Access denied. NGO account required.', 'error')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@ngo_bp.route('/dashboard')
@login_required
@ngo_required
def dashboard():
    """NGO dashboard"""
    # Get NGO's claim statistics
    total_claims = Claim.query.filter_by(ngo_id=current_user.id).count()
    active_claims = Claim.query.filter_by(ngo_id=current_user.id)\
        .filter(Claim.status.in_(['claimed', 'scheduled', 'picked_up'])).count()
    completed_claims = Claim.query.filter_by(ngo_id=current_user.id, status='completed').count()
    
    # Available donations in user's city
    available_nearby = 0
    if current_user.city:
        available_nearby = FoodDonation.query.filter_by(status='available')\
            .filter(FoodDonation.pickup_city.ilike(f'%{current_user.city}%'))\
            .filter(FoodDonation.expiry_date >= date.today()).count()
    
    # Recent claims
    recent_claims = Claim.query.filter_by(ngo_id=current_user.id)\
        .order_by(Claim.claimed_at.desc()).limit(5).all()
    
    # Urgent donations (expiring soon)
    urgent_donations = FoodDonation.query.filter_by(status='available')\
        .filter(FoodDonation.expiry_date >= date.today())\
        .filter(FoodDonation.expiry_date <= date.today() + timedelta(days=2))\
        .limit(5).all()
    
    stats = {
        'total_claims': total_claims,
        'active_claims': active_claims,
        'completed_claims': completed_claims,
        'available_nearby': available_nearby
    }
    
    return render_template('ngo/dashboard.html', 
                         stats=stats, 
                         recent_claims=recent_claims,
                         urgent_donations=urgent_donations)

@ngo_bp.route('/browse')
@login_required
@ngo_required
def browse_donations():
    """Browse available food donations"""
    form = SearchDonationsForm()
    
    # Get query parameters
    search = request.args.get('search', '')
    category_id = request.args.get('category_id', 0, type=int)
    city = request.args.get('city', current_user.city or '')  # Default to NGO's city
    dietary_info = request.args.get('dietary_info', '')
    page = request.args.get('page', 1, type=int)
    
    # Build query
    query = FoodDonation.get_available_donations(
        city=city if city else None,
        category_id=category_id if category_id > 0 else None,
        search=search if search else None
    )
    
    # Add dietary filter if specified
    if dietary_info:
        query = query.filter(FoodDonation.dietary_info == dietary_info)
    
    # Paginate results
    donations = query.paginate(
        page=page, per_page=12, error_out=False
    )
    
    return render_template('ngo/browse.html', 
                         donations=donations, 
                         form=form,
                         current_filters={
                             'search': search,
                             'category_id': category_id,
                             'city': city,
                             'dietary_info': dietary_info
                         })

@ngo_bp.route('/donation/<int:id>')
@login_required
@ngo_required
def view_donation(id):
    """View donation details"""
    donation = FoodDonation.query.get_or_404(id)
    
    # Check if donation is available or if NGO already claimed it
    can_claim = donation.can_be_claimed()
    already_claimed = False
    
    if donation.claim and donation.claim.ngo_id == current_user.id:
        already_claimed = True
    
    return render_template('ngo/view_donation.html', 
                         donation=donation, 
                         can_claim=can_claim,
                         already_claimed=already_claimed)

@ngo_bp.route('/claim-donation/<int:id>', methods=['GET', 'POST'])
@login_required
@ngo_required
def claim_donation(id):
    """Claim a food donation"""
    donation = FoodDonation.query.get_or_404(id)
    
    if not donation.can_be_claimed():
        flash('This donation is no longer available for claiming.', 'error')
        return redirect(url_for('ngo.view_donation', id=id))
    
    # Check if already claimed by someone
    if donation.claim:
        flash('This donation has already been claimed by another NGO.', 'error')
        return redirect(url_for('ngo.view_donation', id=id))
    
    form = ClaimForm()
    
    if form.validate_on_submit():
        claim = Claim(
            donation_id=donation.id,
            ngo_id=current_user.id,
            notes=form.notes.data.strip() if form.notes.data else None
        )
        
        # Update donation status
        donation.status = 'claimed'
        
        try:
            db.session.add(claim)
            db.session.commit()
            flash(f'Successfully claimed "{donation.title}"! Please coordinate pickup with the donor.', 'success')
            return redirect(url_for('ngo.view_claim', id=claim.id))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while claiming the donation.', 'error')
    
    return render_template('ngo/claim_donation.html', donation=donation, form=form)

@ngo_bp.route('/my-claims')
@login_required
@ngo_required
def my_claims():
    """View NGO's claims"""
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', '')
    
    query = Claim.get_claims_for_ngo(current_user.id)
    
    if status_filter:
        query = query.filter_by(status=status_filter)
    
    claims = query.paginate(
        page=page, per_page=10, error_out=False
    )
    
    return render_template('ngo/my_claims.html', 
                         claims=claims, 
                         status_filter=status_filter)

@ngo_bp.route('/claim/<int:id>')
@login_required
@ngo_required
def view_claim(id):
    """View claim details"""
    claim = Claim.query.filter_by(id=id, ngo_id=current_user.id).first_or_404()
    
    return render_template('ngo/view_claim.html', claim=claim)

@ngo_bp.route('/update-claim/<int:id>', methods=['GET', 'POST'])
@login_required
@ngo_required
def update_claim(id):
    """Update claim status"""
    claim = Claim.query.filter_by(id=id, ngo_id=current_user.id).first_or_404()
    
    form = UpdateClaimForm(obj=claim)
    
    if form.validate_on_submit():
        old_status = claim.status
        claim.status = form.status.data
        claim.notes = form.notes.data.strip() if form.notes.data else claim.notes
        
        # Handle status-specific updates
        if form.status.data == 'completed' and old_status != 'completed':
            claim.mark_as_completed()
        elif form.status.data == 'cancelled':
            claim.cancel_claim(form.notes.data)
        
        try:
            db.session.commit()
            flash('Claim status updated successfully!', 'success')
            return redirect(url_for('ngo.view_claim', id=id))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while updating the claim.', 'error')
    
    return render_template('ngo/update_claim.html', form=form, claim=claim)

@ngo_bp.route('/cancel-claim/<int:id>', methods=['POST'])
@login_required
@ngo_required
def cancel_claim(id):
    """Cancel a claim"""
    claim = Claim.query.filter_by(id=id, ngo_id=current_user.id).first_or_404()
    
    if not claim.can_be_cancelled():
        flash('This claim cannot be cancelled at its current status.', 'error')
        return redirect(url_for('ngo.view_claim', id=id))
    
    reason = request.form.get('reason', 'Cancelled by NGO')
    claim.cancel_claim(reason)
    
    try:
        db.session.commit()
        flash('Claim has been cancelled successfully.', 'info')
    except Exception as e:
        db.session.rollback()
        flash('An error occurred while cancelling the claim.', 'error')
    
    return redirect(url_for('ngo.my_claims'))

@ngo_bp.route('/complete-pickup/<int:id>', methods=['POST'])
@login_required
@ngo_required
def complete_pickup(id):
    """Mark a claim as completed (pickup finished)"""
    claim = Claim.query.filter_by(id=id, ngo_id=current_user.id).first_or_404()
    
    if claim.status == 'completed':
        flash('This claim is already marked as completed.', 'info')
        return redirect(url_for('ngo.my_claims'))
    
    # Mark claim as completed
    claim.mark_as_completed()
    
    try:
        db.session.commit()
        flash(f'Successfully marked pickup of "{claim.donation.title}" as completed!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('An error occurred while updating the claim status.', 'error')
    
    return redirect(url_for('ngo.my_claims'))