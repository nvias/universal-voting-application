#!/usr/bin/env python3
"""
Verification script to check if all updates are working correctly
"""

import os
import requests
import time

def check_file_content():
    """Check if files have been updated correctly"""
    print("📁 Checking file updates...")
    
    # Check voting.html for new design
    try:
        with open('site/voting.html', 'r', encoding='utf-8') as f:
            content = f.read()
            if 'Inter' in content and '--primary-color' in content:
                print("  ✅ voting.html has new modern design")
            else:
                print("  ❌ voting.html still has old design")
                return False
    except Exception as e:
        print(f"  ❌ Could not read voting.html: {e}")
        return False
    
    # Check models.py for new fields
    try:
        with open('models.py', 'r', encoding='utf-8') as f:
            content = f.read()
            if 'voter_team_id' in content:
                print("  ✅ models.py has new voter_team_id field")
            else:
                print("  ❌ models.py missing voter_team_id field")
                return False
    except Exception as e:
        print(f"  ❌ Could not read models.py: {e}")
        return False
    
    return True

def check_database():
    """Check database schema"""
    print("\n🗄️  Checking database...")
    
    try:
        from server import create_app
        from models import db, VotingSession, QuestionTemplate
        
        app = create_app()
        with app.app_context():
            # Test connection
            db.engine.execute('SELECT 1')
            print("  ✅ Database connection working")
            
            # Check tables exist
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            
            expected_tables = ['voting_sessions', 'questions', 'teams', 'votes', 'voters', 'question_templates']
            missing = [t for t in expected_tables if t not in tables]
            
            if missing:
                print(f"  ❌ Missing tables: {missing}")
                return False
            else:
                print("  ✅ All required tables exist")
            
            # Check for "Naše firmy" template
            nase_firmy = QuestionTemplate.query.filter_by(name='Naše firmy').first()
            if nase_firmy:
                print("  ✅ 'Naše firmy' template exists")
            else:
                print("  ⚠️  'Naše firmy' template missing")
            
            return True
            
    except Exception as e:
        print(f"  ❌ Database check failed: {e}")
        return False

def check_api_endpoints():
    """Check if API endpoints are working"""
    print("\n🔌 Checking API endpoints...")
    
    base_url = "http://localhost:5000"
    
    # Start server in background for testing
    import subprocess
    import threading
    import time
    
    def start_server():
        try:
            from server import app
            app.run(host="localhost", port=5000, debug=False, use_reloader=False)
        except:
            pass
    
    # Start server in thread
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    time.sleep(3)  # Wait for server to start
    
    try:
        # Test health endpoint
        response = requests.get(f"{base_url}/api/v1/health", timeout=5)
        if response.status_code == 200:
            print("  ✅ Health endpoint working")
        else:
            print(f"  ❌ Health endpoint failed: {response.status_code}")
            return False
        
        # Test config endpoint
        response = requests.get(f"{base_url}/api/config", timeout=5)
        if response.status_code == 200:
            config = response.json()
            print(f"  ✅ Config endpoint working (APP_URL: {config.get('app_url', 'not set')})")
        else:
            print(f"  ❌ Config endpoint failed: {response.status_code}")
        
        # Test templates endpoint
        response = requests.get(f"{base_url}/api/v1/templates", timeout=5)
        if response.status_code == 200:
            templates = response.json()
            nase_firmy_found = any(t['name'] == 'Naše firmy' for t in templates)
            if nase_firmy_found:
                print("  ✅ Templates endpoint working with 'Naše firmy'")
            else:
                print("  ⚠️  Templates endpoint working but missing 'Naše firmy'")
        else:
            print(f"  ❌ Templates endpoint failed: {response.status_code}")
        
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"  ❌ Could not connect to server: {e}")
        print("  💡 Make sure to start the server first: python start.py")
        return False

def check_frontend():
    """Check if frontend files are accessible"""
    print("\n🌐 Checking frontend...")
    
    try:
        # Check if voting page loads
        response = requests.get("http://localhost:5000/", timeout=5)
        if response.status_code == 200:
            print("  ✅ Admin page loads")
        else:
            print(f"  ❌ Admin page failed: {response.status_code}")
            return False
            
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"  ❌ Could not check frontend: {e}")
        return False

def main():
    """Run all verification checks"""
    print("🔍 Voting System Verification")
    print("=" * 40)
    
    all_good = True
    
    # Check files
    if not check_file_content():
        all_good = False
    
    # Check database
    if not check_database():
        all_good = False
    
    # Check API (only if server is running)
    print("\n⚠️  Note: Start the server with 'python start.py' to test API endpoints")
    
    # Summary
    print("\n" + "=" * 40)
    if all_good:
        print("🎉 All core components verified successfully!")
        print("\n📋 Next steps:")
        print("1. Start server: python start.py")
        print("2. Open admin: http://localhost:5000")
        print("3. Create and test voting sessions")
        print("4. Test the new modern UI")
    else:
        print("❌ Some issues found. Please fix them:")
        print("1. Run: python fix_database.py")
        print("2. Choose option 1 to reset database")
        print("3. Run this verification again")
        print("4. Check the SETUP_GUIDE.md for detailed instructions")

if __name__ == "__main__":
    main()
