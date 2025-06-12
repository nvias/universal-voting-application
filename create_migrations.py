#!/usr/bin/env python3
"""
Create Flask-Migrate migrations
"""

from flask_migrate import init, migrate, upgrade
from server import create_app
import os

def main():
    """Initialize Flask-Migrate and create initial migration"""
    app = create_app()
    
    with app.app_context():
        # Initialize migrations if not already done
        if not os.path.exists('migrations'):
            print("Initializing Flask-Migrate...")
            init()
            print("✅ Flask-Migrate initialized")
        
        # Create migration
        print("Creating migration...")
        migrate(message='Initial migration')
        print("✅ Migration created")
        
        # Apply migration
        print("Applying migration...")
        upgrade()
        print("✅ Migration applied")
        
        print("\n🎉 Database migrations completed successfully!")

if __name__ == '__main__':
    main()
