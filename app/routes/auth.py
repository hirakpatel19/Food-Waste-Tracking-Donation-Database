"""
Authentication routes for user registration, login, and profile management
"""

from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models.user import User
from app.forms.auth import LoginForm, RegistrationForm, ProfileForm, ChangePasswordForm

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = LoginForm()
    
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        
        if user and user.check_password(form.password.data):
            if not user.is_active:
                flash('Your account has been deactivated. Please contact support.', 'error')
                return redirect(url_for('auth.login'))
            
            login_user(user, remember=form.remember_me.data)
            flash(f'Welcome back, {user.get_display_name()}!', 'success')
            
            # Redirect to next page or dashboard
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            return redirect(url_for('main.dashboard'))
        else:
            flash('Invalid email or password. Please try again.', 'error')
    
    return render_template('auth/login.html', form=form)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = RegistrationForm()
    
    if form.validate_on_submit():
        # Create new user
        user = User(
            username=form.username.data.lower().strip(),
            email=form.email.data.lower().strip(),
            user_type=form.user_type.data,
            full_name=form.full_name.data.strip(),
            phone=form.phone.data.strip() if form.phone.data else None,
            address=form.address.data.strip() if form.address.data else None,
            city=form.city.data.strip() if form.city.data else None
        )
        
        # Set password
        user.set_password(form.password.data)
        
        # Add NGO-specific fields if applicable
        if form.user_type.data == 'ngo':
            user.organization_name = form.organization_name.data.strip()
            user.registration_number = form.registration_number.data.strip()
        
        try:
            db.session.add(user)
            db.session.commit()
            
            flash(f'Registration successful! Welcome to Food Waste Tracker, {user.get_display_name()}.', 'success')
            login_user(user)
            return redirect(url_for('main.dashboard'))
        
        except Exception as e:
            db.session.rollback()
            flash('An error occurred during registration. Please try again.', 'error')
    
    return render_template('auth/register.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    """User logout"""
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('main.index'))

@auth_bp.route('/profile')
@login_required
def profile():
    """View user profile"""
    return render_template('auth/profile.html', user=current_user)

@auth_bp.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    """Edit user profile"""
    form = ProfileForm(obj=current_user)
    
    if form.validate_on_submit():
        current_user.full_name = form.full_name.data.strip()
        current_user.phone = form.phone.data.strip() if form.phone.data else None
        current_user.address = form.address.data.strip() if form.address.data else None
        current_user.city = form.city.data.strip() if form.city.data else None
        
        # Update NGO-specific fields
        if current_user.is_ngo():
            current_user.organization_name = form.organization_name.data.strip()
        
        try:
            db.session.commit()
            flash('Your profile has been updated successfully.', 'success')
            return redirect(url_for('auth.profile'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while updating your profile.', 'error')
    
    return render_template('auth/edit_profile.html', form=form)

@auth_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """Change user password"""
    form = ChangePasswordForm()
    
    if form.validate_on_submit():
        current_user.set_password(form.new_password.data)
        
        try:
            db.session.commit()
            flash('Your password has been changed successfully.', 'success')
            return redirect(url_for('auth.profile'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while changing your password.', 'error')
    
    return render_template('auth/change_password.html', form=form)

@auth_bp.route('/deactivate', methods=['POST'])
@login_required
def deactivate_account():
    """Deactivate user account"""
    current_user.is_active = False
    
    try:
        db.session.commit()
        logout_user()
        flash('Your account has been deactivated.', 'info')
        return redirect(url_for('main.index'))
    except Exception as e:
        db.session.rollback()
        flash('An error occurred while deactivating your account.', 'error')
        return redirect(url_for('auth.profile'))