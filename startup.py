#!/usr/bin/env python3
"""
Startup script for the NVIAS Voting System
This script initializes the database and starts the application
"""

import os
import sys
import subprocess
import time
from datetime import datetime

def print_banner():
    """Print application banner"""
    print("=" * 60)
    print("       NVIAS VOTING SYSTEM - STARTUP SCRIPT")
    print("=" * 60)
    print()

def check_requirements():
    """Check if all required packages are installed"""
    print("Checking requirements...")
    
    try:
        import flask
        import flask_sqlalchemy
        import psycopg2
        import flask_cors
        print("✓ All required packages are installed")
        return True
    except ImportError as e:
        print(f"✗ Missing package: {e}")
        print("Please run: pip install -r requirements.txt")
        return False

def check_database_config():
    """Check database configuration"""
    print("Checking database configuration...")
    
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        print("✗ DATABASE_URL environment variable not set")
        print("Please set DATABASE_URL in your .env file")
        return False
    
    print(f"✓ Database URL configured: {database_url.split('@')[0]}@[hidden]")
    return True

def initialize_database():
    """Initialize the database"""
    print("Initializing database...")
    
    try:
        from init_db import init_database
        init_database()
        print("✓ Database initialized successfully")
        return True
    except Exception as e:
        print(f"✗ Database initialization failed: {e}")
        return False

def test_database_connection():
    """Test database connection"""
    print("Testing database connection...")
    
    try:
        from tests.test_db import test_database_connection
        if test_database_connection():
            print("✓ Database connection test passed")
            return True
        else:
            print("✗ Database connection test failed")
            return False
    except Exception as e:
        print(f"✗ Database test error: {e}")
        return False

def create_sample_data():
    """Create sample voting session"""
    print("Creating sample data...")
    
    try:
        from init_db import create_sample_nase_firmy_session
        create_sample_nase_firmy_session()
        print("✓ Sample data created")
        return True
    except Exception as e:
        print(f"✗ Sample data creation failed: {e}")
        return False

def start_application():
    """Start the Flask application"""
    print("Starting application...")
    print()
    print("Application starting on http://localhost:5000")
    print("Press Ctrl+C to stop the application")
    print()
    
    try:
        from server import app
        app.run(host="0.0.0.0", port=5000, debug=True)
    except KeyboardInterrupt:
        print("\nApplication stopped by user")
    except Exception as e:
        print(f"Application error: {e}")

def main():
    """Main startup function"""
    print_banner()
    
    # Check requirements
    if not check_requirements():
        sys.exit(1)
    
    # Check database configuration
    if not check_database_config():
        sys.exit(1)
    
    # Initialize database
    if not initialize_database():
        sys.exit(1)
    
    # Test database connection
    if not test_database_connection():
        sys.exit(1)
    
    # Ask about sample data
    response = input("\nCreate sample 'Nase firmy 2025' session? (y/N): ")
    if response.lower() in ['y', 'yes']:
        create_sample_data()
    
    print("\n" + "=" * 60)
    print("       SYSTEM READY - STARTING APPLICATION")
    print("=" * 60)
    print()
    
    # Start application
    start_application()

if __name__ == '__main__':
    main()
