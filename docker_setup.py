#!/usr/bin/env python3
"""
Simple Docker setup script for voting system
"""

import subprocess
import time
import requests

def run_cmd(cmd):
    """Run command and return success status"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def main():
    print("🐳 Simple Docker Setup for Voting System")
    print("=" * 45)
    
    # Step 1: Stop existing containers
    print("\n1️⃣  Stopping existing containers...")
    run_cmd("docker-compose down -v")
    print("   ✅ Containers stopped")
    
    # Step 2: Build and start
    print("\n2️⃣  Building and starting services...")
    success, stdout, stderr = run_cmd("docker-compose up -d --build")
    if not success:
        print(f"   ❌ Failed to start: {stderr}")
        return False
    print("   ✅ Services started")
    
    # Step 3: Wait for services
    print("\n3️⃣  Waiting for services to be ready...")
    for i in range(30):  # Wait up to 30 seconds
        try:
            response = requests.get("http://localhost:5000/api/v1/health", timeout=2)
            if response.status_code == 200:
                print("   ✅ Application is ready!")
                break
        except:
            pass
        print(f"   ⏳ Waiting... ({i+1}/30)")
        time.sleep(1)
    else:
        print("   ❌ Timeout waiting for application")
        return False
    
    # Step 4: Setup database
    print("\n4️⃣  Setting up database...")
    success, stdout, stderr = run_cmd(
        'docker-compose exec -T voting-app python -c "from fix_database import run_all_setup; run_all_setup()"'
    )
    if success:
        print("   ✅ Database setup completed")
    else:
        print(f"   ❌ Database setup failed")
        print(f"   Error: {stderr}")
        return False
    
    # Step 5: Test endpoints
    print("\n5️⃣  Testing key endpoints...")
    endpoints = [
        ("/", "Admin page"),
        ("/api/v1/health", "Health check"),
        ("/api/v1/templates", "Templates"),
    ]
    
    for endpoint, name in endpoints:
        try:
            response = requests.get(f"http://localhost:5000{endpoint}", timeout=5)
            if response.status_code == 200:
                print(f"   ✅ {name}: OK")
            else:
                print(f"   ❌ {name}: {response.status_code}")
        except Exception as e:
            print(f"   ❌ {name}: {e}")
    
    # Success!
    print("\n🎉 Setup completed successfully!")
    print("\n📋 Access Information:")
    print("   🏠 Admin Interface: http://localhost:5000")
    print("   🔍 API Health: http://localhost:5000/api/v1/health")
    print("   🗄️  Database Admin: http://localhost:8080 (admin@example.com / admin)")
    
    print("\n📝 What's been created:")
    print("   • Sample team rating voting")
    print("   • 'Naše firmy' competition voting")
    print("   • All question templates")
    
    print("\n🧪 Test the new features:")
    print("   1. Open admin interface and start a voting session")
    print("   2. Visit voting URL - you'll see modern UI with team selection")
    print("   3. Test 'Naše firmy' voting with 5 categories")
    print("   4. Use stop voting functionality")
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        print("\n💥 Setup failed. Check the errors above.")
        print("   💡 Try running: docker-compose logs")
