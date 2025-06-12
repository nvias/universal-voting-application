#!/usr/bin/env python3
"""
Reset and reinitialize the database
"""

from server import create_app
from models import db
import os

def reset_database():
    """Reset the database completely"""
    app = create_app()
    
    with app.app_context():
        print("🗑️  Dropping all tables...")
        db.drop_all()
        print("✅ All tables dropped!")
        
        print("🔨 Creating new tables...")
        db.create_all()
        print("✅ All tables created!")
        
        print("📝 Creating sample question templates...")
        from init_db import create_sample_templates
        create_sample_templates()
        db.session.commit()
        print("✅ Sample templates created!")
        
        print("\n🎉 Database reset completed successfully!")

if __name__ == '__main__':
    reset_database()
