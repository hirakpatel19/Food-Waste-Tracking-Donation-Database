"""
Routes package for Flask blueprints
"""

from .main import main_bp
from .auth import auth_bp
from .donor import donor_bp
from .ngo import ngo_bp

__all__ = ['main_bp', 'auth_bp', 'donor_bp', 'ngo_bp']