"""
Main routes for homepage and general pages
"""

from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from flask_login import current_user
from app.models.food_donation import FoodDonation, Category
from app.models.claim import Claim
from app.models.user import User
from app.forms.donation import SearchDonationsForm
from datetime import date

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Homepage"""
    # Get some statistics for the homepage
    stats = {
        'total_donations': FoodDonation.query.count(),
        'available_donations': FoodDonation.query.filter_by(status='available').filter(FoodDonation.expiry_date >= date.today()).count(),
        'completed_donations': FoodDonation.query.filter_by(status='completed').count(),
        'total_donors': User.query.filter_by(user_type='donor').count(),
        'total_ngos': User.query.filter_by(user_type='ngo').count()
    }
    
    # Get recent available donations for showcase
    recent_donations = FoodDonation.query.filter_by(status='available')\
        .filter(FoodDonation.expiry_date >= date.today())\
        .order_by(FoodDonation.created_at.desc())\
        .limit(6).all()
    
    return render_template('main/index.html', stats=stats, recent_donations=recent_donations)

@main_bp.route('/about')
def about():
    """About page"""
    return render_template('main/about.html')

@main_bp.route('/how-it-works')
def how_it_works():
    """How it works page"""
    return render_template('main/how_it_works.html')

@main_bp.route('/browse')
def browse_donations():
    """Browse available food donations"""
    form = SearchDonationsForm()
    
    # Get query parameters
    search = request.args.get('search', '')
    category_id = request.args.get('category_id', 0, type=int)
    city = request.args.get('city', '')
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
    per_page = 12
    donations = query.paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    # Get categories for filter
    categories = Category.query.order_by(Category.name).all()
    
    return render_template('main/browse.html', 
                         donations=donations, 
                         form=form, 
                         categories=categories,
                         current_filters={
                             'search': search,
                             'category_id': category_id,
                             'city': city,
                             'dietary_info': dietary_info
                         })

@main_bp.route('/dashboard')
def dashboard():
    """Dashboard - redirects based on user type"""
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))
    
    if current_user.is_donor():
        return redirect(url_for('donor.dashboard'))
    elif current_user.is_ngo():
        return redirect(url_for('ngo.dashboard'))
    else:
        return redirect(url_for('main.index'))

@main_bp.route('/api/stats')
def api_stats():
    """API endpoint for site statistics"""
    stats = {
        'total_donations': FoodDonation.query.count(),
        'available_donations': FoodDonation.query.filter_by(status='available').filter(FoodDonation.expiry_date >= date.today()).count(),
        'completed_donations': FoodDonation.query.filter_by(status='completed').count(),
        'total_users': User.query.count(),
        'active_claims': Claim.query.filter(Claim.status.in_(['claimed', 'scheduled', 'picked_up'])).count()
    }
    return jsonify(stats)

@main_bp.route('/contact')
def contact():
    """Contact page"""
    return render_template('main/contact.html')

@main_bp.route('/privacy')
def privacy():
    """Privacy policy page"""
    return render_template('main/privacy.html')

@main_bp.route('/terms')
def terms():
    """Terms of service page"""
    return render_template('main/terms.html')