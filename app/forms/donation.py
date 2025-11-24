"""
Forms for food donation management
"""

from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, IntegerField, SelectField, DateField, BooleanField
from wtforms.validators import DataRequired, Length, NumberRange, ValidationError
from datetime import date, timedelta
from app.models.food_donation import Category

class FoodDonationForm(FlaskForm):
    """Form for creating/editing food donations"""
    title = StringField('Food Item Title', validators=[
        DataRequired(message='Title is required.'),
        Length(min=3, max=100, message='Title must be between 3 and 100 characters.')
    ])
    
    description = TextAreaField('Description', validators=[
        Length(max=500, message='Description cannot exceed 500 characters.')
    ])
    
    category_id = SelectField('Category', coerce=int, validators=[
        DataRequired(message='Please select a category.')
    ])
    
    quantity = IntegerField('Quantity', validators=[
        DataRequired(message='Quantity is required.'),
        NumberRange(min=1, max=10000, message='Quantity must be between 1 and 10,000.')
    ])
    
    unit = SelectField('Unit', choices=[
        ('kg', 'Kilograms (kg)'),
        ('lbs', 'Pounds (lbs)'),
        ('pieces', 'Pieces'),
        ('portions', 'Portions/Servings'),
        ('liters', 'Liters'),
        ('bottles', 'Bottles'),
        ('packages', 'Packages'),
        ('boxes', 'Boxes'),
        ('bags', 'Bags'),
        ('other', 'Other')
    ], validators=[DataRequired(message='Please select a unit.')])
    
    expiry_date = DateField('Expiry Date', validators=[
        DataRequired(message='Expiry date is required.')
    ])
    
    pickup_address = TextAreaField('Pickup Address', validators=[
        DataRequired(message='Pickup address is required.'),
        Length(min=10, max=500, message='Address must be between 10 and 500 characters.')
    ])
    
    pickup_city = StringField('City', validators=[
        DataRequired(message='City is required.'),
        Length(min=2, max=50, message='City must be between 2 and 50 characters.')
    ])
    
    pickup_instructions = TextAreaField('Pickup Instructions', validators=[
        Length(max=300, message='Instructions cannot exceed 300 characters.')
    ])
    
    is_perishable = BooleanField('This food is perishable', default=True)
    
    dietary_info = SelectField('Dietary Information', choices=[
        ('', 'No specific dietary restrictions'),
        ('vegetarian', 'Vegetarian'),
        ('vegan', 'Vegan'),
        ('gluten-free', 'Gluten-Free'),
        ('dairy-free', 'Dairy-Free'),
        ('nut-free', 'Nut-Free'),
        ('halal', 'Halal'),
        ('kosher', 'Kosher'),
        ('organic', 'Organic'),
        ('other', 'Other (specify in description)')
    ])
    
    def __init__(self, *args, **kwargs):
        super(FoodDonationForm, self).__init__(*args, **kwargs)
        # Populate category choices from database
        self.category_id.choices = [(c.id, c.name) for c in Category.query.order_by(Category.name).all()]
        if not self.category_id.choices:
            self.category_id.choices = [(0, 'No categories available')]
    
    def validate_expiry_date(self, field):
        """Validate that expiry date is not in the past"""
        if field.data < date.today():
            raise ValidationError('Expiry date cannot be in the past.')
        
        # Warn if expiry date is more than 1 year in future
        if field.data > date.today() + timedelta(days=365):
            raise ValidationError('Expiry date seems too far in the future. Please check the date.')

class SearchDonationsForm(FlaskForm):
    """Form for searching food donations"""
    search = StringField('Search food items...', validators=[
        Length(max=100, message='Search term cannot exceed 100 characters.')
    ])
    
    category_id = SelectField('Category', coerce=int)
    
    city = StringField('City', validators=[
        Length(max=50, message='City cannot exceed 50 characters.')
    ])
    
    dietary_info = SelectField('Dietary Preference', choices=[
        ('', 'Any'),
        ('vegetarian', 'Vegetarian'),
        ('vegan', 'Vegan'),
        ('gluten-free', 'Gluten-Free'),
        ('dairy-free', 'Dairy-Free'),
        ('nut-free', 'Nut-Free'),
        ('halal', 'Halal'),
        ('kosher', 'Kosher'),
        ('organic', 'Organic')
    ])
    
    def __init__(self, *args, **kwargs):
        super(SearchDonationsForm, self).__init__(*args, **kwargs)
        # Populate category choices
        categories = [(0, 'All Categories')] + [(c.id, c.name) for c in Category.query.order_by(Category.name).all()]
        self.category_id.choices = categories

class ClaimForm(FlaskForm):
    """Form for claiming a food donation"""
    notes = TextAreaField('Notes (Optional)', validators=[
        Length(max=300, message='Notes cannot exceed 300 characters.')
    ], description='Any additional information about the pickup or special requirements.')

class UpdateClaimForm(FlaskForm):
    """Form for updating claim status"""
    status = SelectField('Status', choices=[
        ('claimed', 'Claimed'),
        ('scheduled', 'Pickup Scheduled'),
        ('picked_up', 'Picked Up'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ], validators=[DataRequired()])
    
    notes = TextAreaField('Notes', validators=[
        Length(max=300, message='Notes cannot exceed 300 characters.')
    ])

class CategoryForm(FlaskForm):
    """Form for creating/editing categories (admin use)"""
    name = StringField('Category Name', validators=[
        DataRequired(message='Category name is required.'),
        Length(min=2, max=50, message='Name must be between 2 and 50 characters.')
    ])
    
    description = TextAreaField('Description', validators=[
        Length(max=200, message='Description cannot exceed 200 characters.')
    ])
    
    def validate_name(self, field):
        """Check if category name already exists"""
        existing = Category.query.filter_by(name=field.data).first()
        if existing and (not hasattr(self, 'category') or existing.id != self.category.id):
            raise ValidationError('A category with this name already exists.')