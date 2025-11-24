"""
Authentication forms for user registration and login
"""

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, TextAreaField, BooleanField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from app.models.user import User

class LoginForm(FlaskForm):
    """User login form"""
    email = StringField('Email', validators=[
        DataRequired(message='Email is required.'),
        Email(message='Please enter a valid email address.')
    ])
    password = PasswordField('Password', validators=[
        DataRequired(message='Password is required.')
    ])
    remember_me = BooleanField('Remember Me')

class RegistrationForm(FlaskForm):
    """User registration form"""
    username = StringField('Username', validators=[
        DataRequired(message='Username is required.'),
        Length(min=3, max=20, message='Username must be between 3 and 20 characters.')
    ])
    
    email = StringField('Email', validators=[
        DataRequired(message='Email is required.'),
        Email(message='Please enter a valid email address.')
    ])
    
    password = PasswordField('Password', validators=[
        DataRequired(message='Password is required.'),
        Length(min=6, message='Password must be at least 6 characters long.')
    ])
    
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(message='Please confirm your password.'),
        EqualTo('password', message='Passwords must match.')
    ])
    
    user_type = SelectField('I am a', choices=[
        ('donor', 'Food Donor (Restaurant, Household, Store)'),
        ('ngo', 'NGO (Charity, Food Bank, Organization)')
    ], validators=[DataRequired(message='Please select your user type.')])
    
    full_name = StringField('Full Name', validators=[
        DataRequired(message='Full name is required.'),
        Length(min=2, max=100, message='Name must be between 2 and 100 characters.')
    ])
    
    phone = StringField('Phone Number', validators=[
        Length(max=20, message='Phone number cannot exceed 20 characters.')
    ])
    
    address = TextAreaField('Address', validators=[
        Length(max=500, message='Address cannot exceed 500 characters.')
    ])
    
    city = StringField('City', validators=[
        Length(max=50, message='City name cannot exceed 50 characters.')
    ])
    
    # NGO-specific fields
    organization_name = StringField('Organization Name', validators=[
        Length(max=100, message='Organization name cannot exceed 100 characters.')
    ])
    
    registration_number = StringField('Registration Number', validators=[
        Length(max=50, message='Registration number cannot exceed 50 characters.')
    ])
    
    def validate_username(self, field):
        """Check if username is already taken"""
        if User.query.filter_by(username=field.data.lower()).first():
            raise ValidationError('Username is already taken. Please choose a different one.')
    
    def validate_email(self, field):
        """Check if email is already registered"""
        if User.query.filter_by(email=field.data.lower()).first():
            raise ValidationError('Email is already registered. Please use a different email or login.')
    
    def validate_organization_name(self, field):
        """Validate organization name for NGOs"""
        if self.user_type.data == 'ngo' and not field.data:
            raise ValidationError('Organization name is required for NGOs.')
    
    def validate_registration_number(self, field):
        """Validate registration number for NGOs"""
        if self.user_type.data == 'ngo' and not field.data:
            raise ValidationError('Registration number is required for NGOs.')

class ProfileForm(FlaskForm):
    """User profile update form"""
    full_name = StringField('Full Name', validators=[
        DataRequired(message='Full name is required.'),
        Length(min=2, max=100, message='Name must be between 2 and 100 characters.')
    ])
    
    phone = StringField('Phone Number', validators=[
        Length(max=20, message='Phone number cannot exceed 20 characters.')
    ])
    
    address = TextAreaField('Address', validators=[
        Length(max=500, message='Address cannot exceed 500 characters.')
    ])
    
    city = StringField('City', validators=[
        Length(max=50, message='City name cannot exceed 50 characters.')
    ])
    
    organization_name = StringField('Organization Name', validators=[
        Length(max=100, message='Organization name cannot exceed 100 characters.')
    ])
    
    def validate_organization_name(self, field):
        """Validate organization name for NGOs"""
        from flask_login import current_user
        if current_user.user_type == 'ngo' and not field.data:
            raise ValidationError('Organization name is required for NGOs.')

class ChangePasswordForm(FlaskForm):
    """Change password form"""
    current_password = PasswordField('Current Password', validators=[
        DataRequired(message='Current password is required.')
    ])
    
    new_password = PasswordField('New Password', validators=[
        DataRequired(message='New password is required.'),
        Length(min=6, message='Password must be at least 6 characters long.')
    ])
    
    confirm_password = PasswordField('Confirm New Password', validators=[
        DataRequired(message='Please confirm your new password.'),
        EqualTo('new_password', message='Passwords must match.')
    ])
    
    def validate_current_password(self, field):
        """Validate current password"""
        from flask_login import current_user
        if not current_user.check_password(field.data):
            raise ValidationError('Current password is incorrect.')