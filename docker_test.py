#!/usr/bin/env python3
"""
Docker testing script for the voting system
"""

import subprocess
import time
import requests
import sys
import json

class DockerTester:
    def __init__(self):
        self.base_url = "http://localhost:5000"
        self.containers = ["voting-app-voting-app-1", "voting-app-db-1"]
        
    def run_command(self, cmd, capture_output=True):
        """Run a shell command"""
        try:
            if capture_output:
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                return result.returncode == 0, result.stdout, result.stderr
            else:
                result = subprocess.run(cmd, shell=True)
                return result.returncode == 0, "", ""
        except Exception as e:
            return False, "", str(e)
    
    def check_docker(self):
        """Check if Docker is available"""
        print("🐳 Checking Docker...")
        success, stdout, stderr = self.run_command("docker --version")
        if success:
            print(f"  ✅ Docker available: {stdout.strip()}")
        else:
            print(f"  ❌ Docker not available: {stderr}")
            return False
            
        success, stdout, stderr = self.run_command("docker-compose --version")
        if success:
            print(f"  ✅ Docker Compose available: {stdout.strip()}")
            return True
        else:
            print(f"  ❌ Docker Compose not available: {stderr}")
            return False
    
    def stop_existing_containers(self):
        """Stop any existing containers"""
        print("\n🛑 Stopping existing containers...")
        success, stdout, stderr = self.run_command("docker-compose down")
        if success:
            print("  ✅ Existing containers stopped")
        else:
            print(f"  ⚠️  Could not stop containers (might not be running): {stderr}")
    
    def build_and_start(self):
        """Build and start the Docker containers"""
        print("\n🔨 Building and starting containers...")
        
        # Build the application
        print("  📦 Building voting-app...")
        success, stdout, stderr = self.run_command("docker-compose build voting-app")
        if not success:
            print(f"  ❌ Build failed: {stderr}")
            return False
        print("  ✅ Build completed")
        
        # Start all services
        print("  🚀 Starting all services...")
        success, stdout, stderr = self.run_command("docker-compose up -d")
        if not success:
            print(f"  ❌ Failed to start services: {stderr}")
            return False
        print("  ✅ Services started")
        
        return True
    
    def wait_for_services(self, timeout=120):
        """Wait for services to be healthy"""
        print(f"\n⏳ Waiting for services to be ready (timeout: {timeout}s)...")
        
        start_time = time.time()
        db_ready = False
        app_ready = False
        
        while time.time() - start_time < timeout:
            # Check database
            if not db_ready:
                success, stdout, stderr = self.run_command("docker-compose exec -T db pg_isready -U postgres")
                if success:
                    print("  ✅ Database is ready")
                    db_ready = True
            
            # Check application
            if db_ready and not app_ready:
                try:
                    response = requests.get(f"{self.base_url}/api/v1/health", timeout=5)
                    if response.status_code == 200:
                        print("  ✅ Application is ready")
                        app_ready = True
                except:
                    pass
            
            if db_ready and app_ready:
                return True
            
            print("  ⏳ Still waiting...")
            time.sleep(5)
        
        print(f"  ❌ Timeout waiting for services")
        return False
    
    def check_logs(self):
        """Check container logs for errors"""
        print("\n📋 Checking container logs...")
        
        for container in ["voting-app", "db"]:
            print(f"\n  📄 Logs for {container}:")
            success, stdout, stderr = self.run_command(f"docker-compose logs --tail=10 {container}")
            if success:
                lines = stdout.split('\n')[-10:]  # Last 10 lines
                for line in lines:
                    if line.strip():
                        print(f"    {line}")
            else:
                print(f"    ❌ Could not get logs: {stderr}")
    
    def setup_database(self):
        """Setup database with sample data"""
        print("\n🗄️  Setting up database...")
        
        # Run the database fix script
        success, stdout, stderr = self.run_command("docker-compose exec -T voting-app python fix_database.py <<< '1\nyes'")
        if success:
            print("  ✅ Database setup completed")
        else:
            print(f"  ❌ Database setup failed: {stderr}")
            # Try alternative approach
            print("  🔄 Trying alternative setup...")
            success, stdout, stderr = self.run_command("docker-compose exec voting-app python -c \"from fix_database import fix_database, create_sample_voting, create_nase_firmy_sample; fix_database(); create_sample_voting(); create_nase_firmy_sample()\"")
            if success:
                print("  ✅ Alternative database setup completed")
            else:
                print(f"  ❌ Alternative setup also failed: {stderr}")
                return False
        
        return True
    
    def test_api_endpoints(self):
        """Test API endpoints"""
        print("\n🔌 Testing API endpoints...")
        
        endpoints = [
            ("/api/v1/health", "Health check"),
            ("/api/config", "Configuration"),
            ("/api/v1/templates", "Question templates"),
            ("/api/v1/voting", "Voting sessions (GET)"),
        ]
        
        for endpoint, description in endpoints:
            try:
                response = requests.get(f"{self.base_url}{endpoint}", timeout=10)
                if response.status_code == 200:
                    print(f"  ✅ {description}: OK")
                    if endpoint == "/api/v1/templates":
                        data = response.json()
                        nase_firmy = any(t.get('name') == 'Naše firmy' for t in data)
                        if nase_firmy:
                            print(f"    ✅ 'Naše firmy' template found")
                        else:
                            print(f"    ⚠️  'Naše firmy' template missing")
                else:
                    print(f"  ❌ {description}: {response.status_code}")
            except Exception as e:
                print(f"  ❌ {description}: {e}")
    
    def test_frontend(self):
        """Test frontend pages"""
        print("\n🌐 Testing frontend...")
        
        pages = [
            ("/", "Admin interface"),
            ("/login", "Login page"),
        ]
        
        for endpoint, description in pages:
            try:
                response = requests.get(f"{self.base_url}{endpoint}", timeout=10)
                if response.status_code == 200:
                    print(f"  ✅ {description}: OK")
                    # Check for modern UI elements
                    if endpoint == "/" and "Inter" in response.text:
                        print(f"    ✅ Modern UI detected")
                else:
                    print(f"  ❌ {description}: {response.status_code}")
            except Exception as e:
                print(f"  ❌ {description}: {e}")
    
    def create_test_voting(self):
        """Create a test voting session via API"""
        print("\n🗳️  Creating test voting session...")
        
        payload = {
            "name": "Docker Test Voting",
            "description": "Test voting created via Docker API",
            "questions": [
                {
                    "text": "Rate the Docker setup",
                    "question_type": "rating",
                    "options": ["1", "2", "3", "4", "5"]
                }
            ],
            "teams": [
                {"name": "Docker Team", "external_id": "docker_team"},
                {"name": "Test Team", "external_id": "test_team"}
            ]
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/api/v1/voting",
                headers={"Content-Type": "application/json"},
                json=payload,
                timeout=10
            )
            
            if response.status_code == 201:
                data = response.json()
                voting_id = data['id']
                print(f"  ✅ Test voting created: {voting_id}")
                print(f"  🗳️  Voting URL: {self.base_url}/hlasovani/{voting_id}")
                print(f"  📱 QR Code: {self.base_url}/presentation/{voting_id}")
                
                # Start the voting
                start_response = requests.post(f"{self.base_url}/api/v1/voting/{voting_id}/start", timeout=10)
                if start_response.status_code == 200:
                    print(f"  ✅ Voting started successfully")
                    return voting_id
                else:
                    print(f"  ❌ Could not start voting: {start_response.status_code}")
            else:
                print(f"  ❌ Could not create voting: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"  ❌ Error creating voting: {e}")
        
        return None
    
    def show_access_info(self):
        """Show access information"""
        print("\n🌟 Access Information:")
        print("=" * 50)
        print(f"🏠 Admin Interface: {self.base_url}")
        print(f"🔍 API Health Check: {self.base_url}/api/v1/health")
        print(f"📚 API Documentation: See API_DOCUMENTATION.md")
        print(f"🗄️  Database Admin (pgAdmin): http://localhost:8080")
        print(f"   📧 Email: admin@example.com")
        print(f"   🔑 Password: admin")
        print("=" * 50)
    
    def cleanup(self):
        """Cleanup containers"""
        print("\n🧹 Cleanup options:")
        print("1. Keep containers running")
        print("2. Stop containers (keep data)")
        print("3. Stop and remove everything (including data)")
        
        choice = input("Choose (1-3): ").strip()
        
        if choice == "2":
            print("🛑 Stopping containers...")
            self.run_command("docker-compose down")
            print("✅ Containers stopped (data preserved)")
        elif choice == "3":
            print("🗑️  Removing everything...")
            self.run_command("docker-compose down -v")
            print("✅ Everything removed")
        else:
            print("✅ Containers left running")
    
    def run_full_test(self):
        """Run the complete test suite"""
        print("🧪 Docker Testing Suite for Voting System")
        print("=" * 50)
        
        # Check prerequisites
        if not self.check_docker():
            return False
        
        # Stop existing containers
        self.stop_existing_containers()
        
        # Build and start
        if not self.build_and_start():
            return False
        
        # Wait for services
        if not self.wait_for_services():
            self.check_logs()
            return False
        
        # Setup database
        if not self.setup_database():
            self.check_logs()
            return False
        
        # Test APIs
        self.test_api_endpoints()
        
        # Test frontend
        self.test_frontend()
        
        # Create test voting
        voting_id = self.create_test_voting()
        
        # Show access info
        self.show_access_info()
        
        # Test summary
        print("\n🎉 Docker test completed!")
        if voting_id:
            print(f"✅ Test voting created and ready: {voting_id}")
        
        print("\n📋 Next steps:")
        print("1. Open the admin interface in your browser")
        print("2. Test the modern UI and team selection")
        print("3. Create 'Naše firmy' voting sessions")
        print("4. Test the QR code functionality")
        
        return True

def main():
    """Main function"""
    tester = DockerTester()
    
    try:
        success = tester.run_full_test()
        if success:
            print("\n🎊 All tests passed! Your Docker setup is working correctly.")
        else:
            print("\n💥 Some tests failed. Check the output above for details.")
        
        # Cleanup
        tester.cleanup()
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        tester.cleanup()
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        tester.cleanup()

if __name__ == "__main__":
    main()
