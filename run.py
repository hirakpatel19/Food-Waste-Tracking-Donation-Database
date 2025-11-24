#!/usr/bin/env python3
"""
Food Waste Tracking & Donation Database
Main application entry point
"""

import os
from app import create_app, db
from app.models.user import User
from app.models.food_donation import FoodDonation, Category
from app.models.claim import Claim

# Create Flask application
app = create_app(os.getenv('FLASK_CONFIG') or 'default')

@app.shell_context_processor
def make_shell_context():
    """Make database models available in Flask shell"""
    return {
        'db': db,
        'User': User,
        'FoodDonation': FoodDonation,
        'Category': Category,
        'Claim': Claim
    }

@app.cli.command()
def init_db():
    """Initialize the database with sample data"""
    with app.app_context():
        db.create_all()
        
        # Create categories if they don't exist
        categories = [
            ('Fruits & Vegetables', 'Fresh produce, fruits, and vegetables'),
            ('Bakery Items', 'Bread, pastries, and baked goods'),
            ('Dairy Products', 'Milk, cheese, yogurt, and dairy items'),
            ('Meat & Seafood', 'Fresh and cooked meat, poultry, and seafood'),
            ('Prepared Meals', 'Ready-to-eat meals and cooked food'),
            ('Dry Goods', 'Rice, pasta, cereals, and non-perishable items'),
            ('Beverages', 'Juices, soft drinks, and other beverages'),
            ('Other', 'Miscellaneous food items')
        ]
        
        for name, description in categories:
            category = Category.query.filter_by(name=name).first()
            if not category:
                category = Category(name=name, description=description)
                db.session.add(category)
        
        db.session.commit()
        print('Database initialized successfully!')

def init_database_standalone():
    """Initialize database without running Flask server"""
    app_instance = create_app()
    with app_instance.app_context():
        db.create_all()
        
        # Create categories if they don't exist
        categories = [
            ('Fruits & Vegetables', 'Fresh produce, fruits, and vegetables'),
            ('Bakery Items', 'Bread, pastries, and baked goods'),
            ('Dairy Products', 'Milk, cheese, yogurt, and dairy items'),
            ('Meat & Seafood', 'Fresh and cooked meat, poultry, and seafood'),
            ('Prepared Meals', 'Ready-to-eat meals and cooked food'),
            ('Dry Goods', 'Rice, pasta, cereals, and non-perishable items'),
            ('Beverages', 'Juices, soft drinks, and other beverages'),
            ('Other', 'Miscellaneous food items')
        ]
        
        for name, description in categories:
            category = Category.query.filter_by(name=name).first()
            if not category:
                category = Category(name=name, description=description)
                db.session.add(category)
        
        db.session.commit()
        print('✅ Database initialized successfully!')
        return True

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == 'init-db':
        init_database_standalone()
    else:
        # Try to find an available port
        import socket
        def find_free_port():
            ports_to_try = [5000, 5001, 5002, 8000, 8080, 3000]
            for port in ports_to_try:
                try:
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                        s.bind(('', port))
                        return port
                except OSError:
                    continue
            return 5000  # fallback
        
        port = find_free_port()
        print(f"Starting server on port {port}...")
        app.run(debug=True, host='0.0.0.0', port=port)