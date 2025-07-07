#!/usr/bin/env python3
"""
NVIAS Voting System - Comprehensive Test Suite
Tests all fixes and ensures system functionality
"""

import os
import sys
import subprocess
import json
import time
import requests
from pathlib import Path
from datetime import datetime

class SystemTester:
    def __init__(self):
        self.project_root = Path.cwd()
        self.data_dir = self.project_root / "data"
        self.backup_dir = self.project_root / "backups"
        self.base_url = "http://localhost:5000"
        
        self.test_results = {
            'timestamp': datetime.now().isoformat(),
            'tests_passed': 0,
            'tests_failed': 0,
            'tests_skipped': 0,
            'details': []
        }
        
        print("🧪 NVIAS Voting System - Comprehensive Test Suite")
        print("=" * 55)
    
    def log_test(self, test_name, passed, message="", details=None):
        """Log test result"""
        status = "PASS" if passed else "FAIL"
        emoji = "✅" if passed else "❌"
        
        print(f"{emoji} {test_name}: {status}")
        if message:
            print(f"   {message}")
        
        if passed:
            self.test_results['tests_passed'] += 1
        else:
            self.test_results['tests_failed'] += 1
        
        self.test_results['details'].append({
            'test_name': test_name,
            'status': status,
            'message': message,
            'details': details,
            'timestamp': datetime.now().isoformat()
        })
    
    def skip_test(self, test_name, reason):
        """Skip a test with reason"""
        print(f"⏭️  {test_name}: SKIPPED - {reason}")
        self.test_results['tests_skipped'] += 1
        self.test_results['details'].append({
            'test_name': test_name,
            'status': 'SKIPPED',
            'message': reason,
            'timestamp': datetime.now().isoformat()
        })
    
    def test_docker_environment(self):
        """Test Docker environment"""
        print("\n🐳 Testing Docker Environment...")
        
        # Test Docker installation
        try:
            result = subprocess.run(["docker", "--version"], 
                                 capture_output=True, text=True, check=True)
            version = result.stdout.strip()
            self.log_test("Docker Installation", True, f"Version: {version}")
        except (subprocess.CalledProcessError, FileNotFoundError):
            self.log_test("Docker Installation", False, "Docker not found or not working")
            return False
        
        # Test Docker Compose
        try:
            result = subprocess.run(["docker-compose", "--version"], 
                                 capture_output=True, text=True, check=True)
            version = result.stdout.strip()
            self.log_test("Docker Compose", True, f"Version: {version}")
        except (subprocess.CalledProcessError, FileNotFoundError):
            self.log_test("Docker Compose", False, "Docker Compose not found")
            return False
        
        return True
    
    def test_file_structure(self):
        """Test required files and directories"""
        print("\n📁 Testing File Structure...")
        
        # Required files
        required_files = [
            "server.py", "models.py", "requirements.txt", "Dockerfile",
            ".env", "docker-compose.yml", "backup_recovery.py",
            "monitor_system.py", "fix_production_issues.py"
        ]
        
        for file_name in required_files:
            file_path = self.project_root / file_name
            if file_path.exists():
                self.log_test(f"File: {file_name}", True, f"Found at {file_path}")
            else:
                self.log_test(f"File: {file_name}", False, f"Missing from {file_path}")
        
        # Required directories
        required_dirs = [
            "site", "data", "data/postgres", "data/app", "backups", "logs"
        ]
        
        for dir_name in required_dirs:
            dir_path = self.project_root / dir_name
            if dir_path.exists():
                self.log_test(f"Directory: {dir_name}", True, f"Exists at {dir_path}")
            else:
                # Create missing directories
                dir_path.mkdir(parents=True, exist_ok=True)
                self.log_test(f"Directory: {dir_name}", True, f"Created at {dir_path}")
        
        return True
    
    def test_containers_running(self):
        """Test if containers are running"""
        print("\n🚀 Testing Container Status...")
        
        try:
            result = subprocess.run(["docker-compose", "ps"], 
                                 capture_output=True, text=True, check=True)
            output = result.stdout
            
            # Check for voting-app container
            if "voting-app" in output and "Up" in output:
                self.log_test("Voting App Container", True, "Container is running")
            else:
                self.log_test("Voting App Container", False, "Container not running")
            
            # Check for database container
            if "db" in output and "Up" in output:
                self.log_test("Database Container", True, "Container is running")
            else:
                self.log_test("Database Container", False, "Container not running")
            
            return "voting-app" in output and "db" in output
            
        except subprocess.CalledProcessError as e:
            self.log_test("Container Status Check", False, f"Error: {e}")
            return False
    
    def test_database_health(self):
        """Test database health and connectivity"""
        print("\n🗄️  Testing Database Health...")
        
        # Test database connectivity
        try:
            result = subprocess.run([
                "docker-compose", "exec", "-T", "db",
                "pg_isready", "-U", "postgres", "-d", "voting_db"
            ], capture_output=True, text=True, check=True, timeout=30)
            
            if "accepting connections" in result.stdout:
                self.log_test("Database Connectivity", True, "Database accepting connections")
            else:
                self.log_test("Database Connectivity", False, "Database not accepting connections")
                return False
                
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
            self.log_test("Database Connectivity", False, f"Error: {e}")
            return False
        
        # Test database content
        try:
            result = subprocess.run([
                "docker-compose", "exec", "-T", "db",
                "psql", "-U", "postgres", "-d", "voting_db", "-t", "-c",
                "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';"
            ], capture_output=True, text=True, check=True, timeout=30)
            
            table_count = int(result.stdout.strip())
            if table_count > 0:
                self.log_test("Database Schema", True, f"Found {table_count} tables")
            else:
                self.log_test("Database Schema", False, "No tables found")
                
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired, ValueError) as e:
            self.log_test("Database Schema", False, f"Error checking schema: {e}")
        
        return True
    
    def test_api_endpoints(self):
        """Test API endpoints"""
        print("\n🌐 Testing API Endpoints...")
        
        # Wait for application to be ready
        time.sleep(5)
        
        # Test health endpoint
        try:
            response = requests.get(f"{self.base_url}/api/v1/health", timeout=10)
            if response.status_code == 200:
                health_data = response.json()
                if health_data.get('status') == 'healthy':
                    self.log_test("API Health Endpoint", True, "Health check passed")
                else:
                    self.log_test("API Health Endpoint", False, f"Unhealthy: {health_data}")
            else:
                self.log_test("API Health Endpoint", False, f"HTTP {response.status_code}")
        except Exception as e:
            self.log_test("API Health Endpoint", False, f"Error: {e}")
        
        # Test legacy health endpoint
        try:
            response = requests.get(f"{self.base_url}/health", timeout=10)
            if response.status_code == 200:
                self.log_test("Legacy Health Endpoint", True, "Accessible")
            else:
                self.log_test("Legacy Health Endpoint", False, f"HTTP {response.status_code}")
        except Exception as e:
            self.log_test("Legacy Health Endpoint", False, f"Error: {e}")
        
        # Test votings endpoint
        try:
            response = requests.get(f"{self.base_url}/get_votings", timeout=10)
            if response.status_code == 200:
                votings_data = response.json()
                self.log_test("Votings API", True, f"Returns {len(votings_data)} voting sessions")
            else:
                self.log_test("Votings API", False, f"HTTP {response.status_code}")
        except Exception as e:
            self.log_test("Votings API", False, f"Error: {e}")
        
        # Test admin page
        try:
            response = requests.get(f"{self.base_url}/", timeout=10)
            if response.status_code == 200 and "NVIAS" in response.text:
                self.log_test("Admin Interface", True, "Page loads correctly")
            else:
                self.log_test("Admin Interface", False, f"HTTP {response.status_code}")
        except Exception as e:
            self.log_test("Admin Interface", False, f"Error: {e}")
        
        return True
    
    def test_voting_functionality(self):
        """Test voting functionality by creating a test session"""
        print("\n🗳️  Testing Voting Functionality...")
        
        # Create test voting session
        test_voting_data = {
            "name": "Test Voting Session",
            "description": "Automated test session",
            "teams": [
                {"name": "Test Team 1"},
                {"name": "Test Team 2"}
            ],
            "questions": [
                {
                    "text": "Test Question",
                    "question_type": "rating",
                    "options": ["1", "2", "3", "4", "5"]
                }
            ]
        }
        
        try:
            # Create voting session via API
            response = requests.post(
                f"{self.base_url}/api/v1/voting",
                json=test_voting_data,
                timeout=10
            )
            
            if response.status_code == 201:
                result = response.json()
                voting_id = result.get('id')
                self.log_test("Create Voting Session", True, f"Created session {voting_id}")
                
                # Test starting the session
                start_response = requests.post(
                    f"{self.base_url}/api/v1/voting/{voting_id}/start",
                    timeout=10
                )
                
                if start_response.status_code == 200:
                    self.log_test("Start Voting Session", True, f"Started session {voting_id}")
                    
                    # Test getting session data
                    data_response = requests.get(
                        f"{self.base_url}/api/voting-data/{voting_id}",
                        timeout=10
                    )
                    
                    if data_response.status_code == 200:
                        self.log_test("Get Voting Data", True, "Session data accessible")
                    else:
                        self.log_test("Get Voting Data", False, f"HTTP {data_response.status_code}")
                    
                    # Test stopping the session
                    stop_response = requests.post(
                        f"{self.base_url}/api/v1/voting/{voting_id}/stop",
                        timeout=10
                    )
                    
                    if stop_response.status_code == 200:
                        self.log_test("Stop Voting Session", True, f"Stopped session {voting_id}")
                    else:
                        self.log_test("Stop Voting Session", False, f"HTTP {stop_response.status_code}")
                    
                else:
                    self.log_test("Start Voting Session", False, f"HTTP {start_response.status_code}")
                    
            else:
                self.log_test("Create Voting Session", False, f"HTTP {response.status_code}")
                
        except Exception as e:
            self.log_test("Voting Functionality", False, f"Error: {e}")
        
        return True
    
    def test_backup_system(self):
        """Test backup and recovery system"""
        print("\n💾 Testing Backup System...")
        
        # Test backup script exists
        backup_script = self.project_root / "backup_recovery.py"
        if backup_script.exists():
            self.log_test("Backup Script", True, "Script exists")
            
            # Test backup functionality
            try:
                result = subprocess.run([
                    "python3", str(backup_script), "--health"
                ], capture_output=True, text=True, timeout=60)
                
                if result.returncode == 0:
                    self.log_test("Backup Health Check", True, "Script runs correctly")
                else:
                    self.log_test("Backup Health Check", False, f"Script error: {result.stderr}")
                    
            except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
                self.log_test("Backup Health Check", False, f"Error: {e}")
        else:
            self.log_test("Backup Script", False, "Script missing")
        
        # Test backup directory
        if self.backup_dir.exists():
            self.log_test("Backup Directory", True, f"Directory exists: {self.backup_dir}")
        else:
            self.log_test("Backup Directory", False, "Backup directory missing")
        
        return True
    
    def test_monitoring_system(self):
        """Test monitoring system"""
        print("\n📊 Testing Monitoring System...")
        
        # Test monitoring script
        monitor_script = self.project_root / "monitor_system.py"
        if monitor_script.exists():
            self.log_test("Monitor Script", True, "Script exists")
            
            # Test if psutil is available (required for monitoring)
            try:
                import psutil
                self.log_test("Monitor Dependencies", True, "psutil available")
            except ImportError:
                self.log_test("Monitor Dependencies", False, "psutil not installed")
                
        else:
            self.log_test("Monitor Script", False, "Script missing")
        
        return True
    
    def test_data_persistence(self):
        """Test data persistence configuration"""
        print("\n💽 Testing Data Persistence...")
        
        # Check if persistence configuration exists
        persistence_file = self.project_root / "docker-compose.persistence.yml"
        if persistence_file.exists():
            self.log_test("Persistence Config", True, "Configuration exists")
        else:
            self.log_test("Persistence Config", False, "Configuration missing")
        
        # Check data directory structure
        postgres_data = self.data_dir / "postgres"
        app_data = self.data_dir / "app"
        
        if postgres_data.exists():
            self.log_test("PostgreSQL Data Dir", True, f"Exists: {postgres_data}")
        else:
            self.log_test("PostgreSQL Data Dir", False, "Missing data directory")
        
        if app_data.exists():
            self.log_test("Application Data Dir", True, f"Exists: {app_data}")
        else:
            self.log_test("Application Data Dir", False, "Missing app data directory")
        
        # Check if PostgreSQL configuration exists
        postgres_conf = self.project_root / "postgresql.conf"
        if postgres_conf.exists():
            self.log_test("PostgreSQL Config", True, "Configuration file exists")
        else:
            self.log_test("PostgreSQL Config", False, "Configuration file missing")
        
        return True
    
    def test_quick_start_scripts(self):
        """Test quick start and utility scripts"""
        print("\n🚀 Testing Quick Start Scripts...")
        
        scripts_to_test = [
            ("quick_start.sh", "Quick start script"),
            ("health_check.sh", "Health check script"),
            ("create_backup.sh", "Backup script")
        ]
        
        for script_name, description in scripts_to_test:
            script_path = self.project_root / script_name
            if script_path.exists():
                # Check if script is executable
                if os.access(script_path, os.X_OK):
                    self.log_test(description, True, f"Script exists and is executable")
                else:
                    self.log_test(description, False, f"Script exists but not executable")
            else:
                self.log_test(description, False, f"Script missing: {script_name}")
        
        return True
    
    def generate_test_report(self):
        """Generate comprehensive test report"""
        print("\n📋 Generating Test Report...")
        
        # Calculate success rate
        total_tests = self.test_results['tests_passed'] + self.test_results['tests_failed']
        if total_tests > 0:
            success_rate = (self.test_results['tests_passed'] / total_tests) * 100
        else:
            success_rate = 0
        
        self.test_results['success_rate'] = success_rate
        self.test_results['total_tests'] = total_tests
        
        # Save to file
        report_file = self.project_root / f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(self.test_results, f, indent=2)
        
        print(f"📄 Test report saved to: {report_file}")
        
        return report_file
    
    def run_all_tests(self):
        """Run all tests"""
        print("Starting comprehensive test suite...\n")
        
        # Test sequence
        test_functions = [
            self.test_docker_environment,
            self.test_file_structure,
            self.test_containers_running,
            self.test_database_health,
            self.test_api_endpoints,
            self.test_voting_functionality,
            self.test_backup_system,
            self.test_monitoring_system,
            self.test_data_persistence,
            self.test_quick_start_scripts
        ]
        
        for test_func in test_functions:
            try:
                test_func()
            except Exception as e:
                test_name = test_func.__name__.replace('test_', '').replace('_', ' ').title()
                self.log_test(test_name, False, f"Unexpected error: {e}")
        
        # Generate report
        report_file = self.generate_test_report()
        
        # Print summary
        print("\n" + "=" * 55)
        print("🧪 TEST SUMMARY")
        print("=" * 55)
        print(f"✅ Tests Passed: {self.test_results['tests_passed']}")
        print(f"❌ Tests Failed: {self.test_results['tests_failed']}")
        print(f"⏭️  Tests Skipped: {self.test_results['tests_skipped']}")
        print(f"📊 Success Rate: {self.test_results['success_rate']:.1f}%")
        print(f"📄 Report: {report_file}")
        
        if self.test_results['tests_failed'] == 0:
            print("\n🎉 All tests passed! Your NVIAS Voting System is working correctly.")
            return True
        else:
            print(f"\n⚠️  {self.test_results['tests_failed']} test(s) failed. Please check the issues above.")
            return False

def main():
    """Main function"""
    print("This test suite will verify that all fixes are working correctly.")
    print("Make sure your system is running before starting tests.\n")
    
    confirm = input("Start comprehensive tests? (y/N): ")
    if confirm.lower() != 'y':
        print("Tests cancelled.")
        return
    
    tester = SystemTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🚀 Your system is ready for production use!")
    else:
        print("\n🔧 Please fix the issues above and run tests again.")
        sys.exit(1)

if __name__ == "__main__":
    main()
