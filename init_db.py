#!/usr/bin/env python3
"""
Standalone database initialization script
Food Waste Tracking & Donation Database
"""

import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def init_database():
    """Initialize the database with sample data"""
    try:
        # Import after adding to path
        from app import create_app, db
        from app.models.food_donation import Category
        
        # Create Flask app
        app = create_app('development')
        
        with app.app_context():
            # Create all tables
            db.create_all()
            
            # Create sample categories
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
            
            # Add categories if they don't exist
            for name, description in categories:
                existing_category = Category.query.filter_by(name=name).first()
                if not existing_category:
                    category = Category(name=name, description=description)
                    db.session.add(category)
            
            # Commit all changes
            db.session.commit()
            
            print("✅ Database initialized successfully!")
            print(f"📍 Database location: {app.config['SQLALCHEMY_DATABASE_URI']}")
            print(f"📊 Created {len(categories)} food categories")
            
            return True
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure you're in the project directory and dependencies are installed.")
        return False
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        return False

if __name__ == '__main__':
    print("🗃️  Initializing Food Waste Tracker Database...")
    print("=" * 50)
    
    success = init_database()
    
    if success:
        print("=" * 50)
        print("🎉 Database setup complete!")
        print()
        print("Next steps:")
        print("1. Activate virtual environment: source venv/bin/activate")
        print("2. Run the application: python run.py")
        print("3. Open browser: http://localhost:5000")
    else:
        print("=" * 50)
        print("❌ Database initialization failed.")
        print("Please check the error messages above.")
        sys.exit(1)