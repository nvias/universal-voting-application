#!/usr/bin/env python3
"""
Simple startup script for the voting system
"""

import os
import sys

def main():
    print("🗳️  Voting System Startup")
    print("=" * 30)
    
    # Check if database is ready
    try:
        from server import create_app
        from models import db
        
        app = create_app()
        with app.app_context():
            # Test database connection
            db.engine.execute('SELECT 1')
            
            # Check if tables exist
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            
            if not tables:
                print("⚠️  Database is empty. Setting up...")
                from fix_database import fix_database, create_sample_voting, create_nase_firmy_sample
                fix_database()
                create_sample_voting()
                create_nase_firmy_sample()
                print("✅ Database setup completed!")
            else:
                print("✅ Database is ready!")
    
    except Exception as e:
        print(f"❌ Database issue detected: {e}")
        print("🔧 Running database fix...")
        try:
            from fix_database import fix_database
            fix_database()
            print("✅ Database fixed!")
        except Exception as fix_error:
            print(f"❌ Could not fix database: {fix_error}")
            print("💡 Please run: python fix_database.py")
            return
    
    # Start the application
    print("\n🚀 Starting application...")
    print("📱 Admin interface: http://localhost:5000")
    print("🔍 API health: http://localhost:5000/api/v1/health")
    print("📚 Press Ctrl+C to stop")
    print("-" * 50)
    
    from server import app
    app.run(host="0.0.0.0", port=5000, debug=True)

if __name__ == "__main__":
    main()
