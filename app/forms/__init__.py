"""
Forms package for Flask-WTF forms
"""

from .auth import LoginForm, RegistrationForm, ProfileForm, ChangePasswordForm
from .donation import FoodDonationForm, SearchDonationsForm, ClaimForm, UpdateClaimForm, CategoryForm

__all__ = [
    'LoginForm', 'RegistrationForm', 'ProfileForm', 'ChangePasswordForm',
    'FoodDonationForm', 'SearchDonationsForm', 'ClaimForm', 'UpdateClaimForm', 'CategoryForm'
]