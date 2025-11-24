#!/usr/bin/env python3
"""
Setup script for Food Waste Tracking & Donation Database
SDG Innovators - Group 10
"""

import os
import sys
import subprocess
from pathlib import Path

def create_virtual_environment():
    """Create Python virtual environment"""
    print("Creating virtual environment...")
    try:
        subprocess.run([sys.executable, '-m', 'venv', 'venv'], check=True)
        print("✅ Virtual environment created successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error creating virtual environment: {e}")
        return False

def install_dependencies():
    """Install Python dependencies"""
    print("Installing dependencies...")
    
    # Determine pip path based on OS
    if os.name == 'nt':  # Windows
        pip_path = os.path.join('venv', 'Scripts', 'pip')
    else:  # macOS/Linux
        pip_path = os.path.join('venv', 'bin', 'pip')
    
    try:
        subprocess.run([pip_path, 'install', '-r', 'requirements.txt'], check=True)
        print("✅ Dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing dependencies: {e}")
        return False

def setup_environment():
    """Setup environment variables"""
    print("Setting up environment variables...")
    
    env_file = Path('.env')
    env_example = Path('.env.example')
    
    if not env_file.exists() and env_example.exists():
        try:
            import shutil
            shutil.copy('.env.example', '.env')
            print("✅ Environment file (.env) created from template")
            print("ℹ️  Please edit .env file to configure your settings")
            return True
        except Exception as e:
            print(f"❌ Error creating .env file: {e}")
            return False
    elif env_file.exists():
        print("✅ Environment file (.env) already exists")
        return True
    else:
        print("⚠️  No .env.example file found")
        return True

def initialize_database():
    """Initialize the database"""
    print("Initializing database...")
    
    # Determine python path based on OS
    if os.name == 'nt':  # Windows
        python_path = os.path.join('venv', 'Scripts', 'python')
    else:  # macOS/Linux
        python_path = os.path.join('venv', 'bin', 'python')
    
    try:
        # Initialize database with sample data using the standalone function
        env = os.environ.copy()
        env['FLASK_CONFIG'] = 'development'
        subprocess.run([python_path, 'run.py', 'init-db'], 
                      check=True, env=env, cwd=os.getcwd())
        print("✅ Database initialized successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error initializing database: {e}")
        print("ℹ️  You can initialize it manually later with: python run.py init-db")
        return False

def print_instructions():
    """Print final setup instructions"""
    print("\n" + "="*60)
    print("🎉 SETUP COMPLETE!")
    print("="*60)
    print()
    print("To start the application:")
    print()
    
    if os.name == 'nt':  # Windows
        print("1. Activate virtual environment:")
        print("   venv\\Scripts\\activate")
        print()
        print("2. Run the application:")
        print("   python run.py")
    else:  # macOS/Linux
        print("1. Activate virtual environment:")
        print("   source venv/bin/activate")
        print()
        print("2. Run the application:")
        print("   python run.py")
    
    print()
    print("3. Open your browser and go to: http://localhost:5000")
    print()
    print("📝 Notes:")
    print("- Edit .env file to configure your settings")
    print("- Default database: SQLite (food_waste_tracker.db)")
    print("- Check README.md for detailed documentation")
    print("="*60)

def main():
    """Main setup function"""
    print("Food Waste Tracking & Donation Database - Setup")
    print("SDG Innovators - Group 10")
    print("="*60)
    
    # Check if Python version is adequate
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required!")
        sys.exit(1)
    
    success = True
    
    # Step 1: Create virtual environment
    if not os.path.exists('venv'):
        success &= create_virtual_environment()
    else:
        print("✅ Virtual environment already exists")
    
    # Step 2: Install dependencies
    if success:
        success &= install_dependencies()
    
    # Step 3: Setup environment
    if success:
        success &= setup_environment()
    
    # Step 4: Initialize database
    if success:
        success &= initialize_database()
    
    # Print final instructions
    if success:
        print_instructions()
    else:
        print("\n❌ Setup completed with some errors. Please check the messages above.")
        sys.exit(1)

if __name__ == '__main__':
    main()