#!/usr/bin/env python3
"""
NVIAS Voting System - Production Startup Script
This script ensures proper system startup and prevents database loss issues.
"""

import os
import sys
import subprocess
import json
import time
import shutil
from pathlib import Path
from datetime import datetime

class ProductionStartup:
    def __init__(self):
        self.project_root = Path.cwd()
        self.data_dir = self.project_root / "data"
        self.backup_dir = self.project_root / "backups"
        self.logs_dir = self.project_root / "logs"
        
        # Configuration files
        self.env_file = self.project_root / ".env"
        self.docker_compose_file = self.project_root / "docker-compose.yml"
        self.production_compose_file = self.project_root / "docker-compose.production.yml"
        
        print("🗳️  NVIAS Voting System - Production Startup")
        print("=" * 50)
        
    def check_prerequisites(self):
        """Check if all prerequisites are met"""
        print("🔍 Checking prerequisites...")
        
        issues = []
        
        # Check Docker
        try:
            result = subprocess.run(["docker", "--version"], capture_output=True, text=True, check=True)
            print(f"✅ Docker: {result.stdout.strip()}")
        except (subprocess.CalledProcessError, FileNotFoundError):
            issues.append("Docker is not installed or not accessible")
        
        # Check Docker Compose
        try:
            result = subprocess.run(["docker-compose", "--version"], capture_output=True, text=True, check=True)
            print(f"✅ Docker Compose: {result.stdout.strip()}")
        except (subprocess.CalledProcessError, FileNotFoundError):
            issues.append("Docker Compose is not installed or not accessible")
        
        # Check environment file
        if not self.env_file.exists():
            issues.append(f"Environment file not found: {self.env_file}")
        else:
            print(f"✅ Environment file: {self.env_file}")
            
        # Check required files
        required_files = [
            "server.py",
            "models.py",
            "requirements.txt",
            "Dockerfile"
        ]
        
        for file_name in required_files:
            file_path = self.project_root / file_name
            if not file_path.exists():
                issues.append(f"Required file missing: {file_name}")
            else:
                print(f"✅ Found: {file_name}")
        
        if issues:
            print("\n❌ Prerequisites check failed:")
            for issue in issues:
                print(f"  - {issue}")
            return False
        
        print("✅ All prerequisites met!")
        return True
    
    def setup_directories(self):
        """Create and setup necessary directories"""
        print("\n📁 Setting up directories...")
        
        directories = [
            self.data_dir,
            self.data_dir / "postgres",
            self.data_dir / "app", 
            self.backup_dir,
            self.backup_dir / "wal_archive",
            self.logs_dir
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            print(f"✅ Created/verified: {directory}")
            
            # Set proper permissions
            try:
                os.chmod(directory, 0o755)
            except Exception as e:
                print(f"⚠️  Warning: Could not set permissions for {directory}: {e}")
    
    def check_environment_config(self):
        """Validate environment configuration"""
        print("\n⚙️  Checking environment configuration...")
        
        if not self.env_file.exists():
            print("❌ .env file not found")
            return False
        
        # Read environment variables
        env_vars = {}
        with open(self.env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key] = value
        
        # Check critical variables
        critical_vars = [
            'POSTGRES_DB',
            'POSTGRES_USER', 
            'POSTGRES_PASSWORD',
            'SECRET_KEY',
            'WEB_DOMAIN'
        ]
        
        missing_vars = []
        for var in critical_vars:
            if var not in env_vars:
                missing_vars.append(var)
            else:
                # Don't print sensitive values
                if 'PASSWORD' in var or 'SECRET' in var:
                    print(f"✅ {var}: [HIDDEN]")
                else:
                    print(f"✅ {var}: {env_vars[var]}")
        
        if missing_vars:
            print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
            return False
        
        # Validate SECRET_KEY
        secret_key = env_vars.get('SECRET_KEY', '')
        if secret_key in ['your-production-secret-key-change-this', 'your-very-secure-secret-key-change-this']:
            print("⚠️  WARNING: Using default SECRET_KEY. Please change this for production!")
        
        # Validate database password
        db_password = env_vars.get('POSTGRES_PASSWORD', '')
        if db_password == 'password':
            print("⚠️  WARNING: Using default database password. Please change this for production!")
        
        return True
    
    def backup_existing_data(self):
        """Create backup of existing data before startup"""
        print("\n💾 Checking for existing data...")
        
        postgres_data = self.data_dir / "postgres"
        if postgres_data.exists() and any(postgres_data.iterdir()):
            print("📦 Found existing PostgreSQL data, creating backup...")
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"postgres_data_backup_{timestamp}"
            backup_path = self.backup_dir / backup_name
            
            try:
                shutil.copytree(postgres_data, backup_path)
                print(f"✅ Data backed up to: {backup_path}")
                
                # Create backup metadata
                metadata = {
                    "backup_type": "postgres_data",
                    "timestamp": timestamp,
                    "source": str(postgres_data),
                    "destination": str(backup_path),
                    "created_at": datetime.now().isoformat()
                }
                
                metadata_file = backup_path.parent / f"{backup_name}.json"
                with open(metadata_file, 'w') as f:
                    json.dump(metadata, f, indent=2)
                
                return backup_path
                
            except Exception as e:
                print(f"⚠️  Warning: Could not backup existing data: {e}")
                return None
        else:
            print("✅ No existing data found")
            return None
    
    def stop_existing_containers(self):
        """Stop any existing containers"""
        print("\n🛑 Stopping existing containers...")
        
        try:
            # Stop with both possible compose files
            subprocess.run(["docker-compose", "down"], check=False, capture_output=True)
            subprocess.run(["docker-compose", "-f", str(self.production_compose_file), "down"], 
                         check=False, capture_output=True)
            print("✅ Existing containers stopped")
        except Exception as e:
            print(f"⚠️  Warning: Could not stop existing containers: {e}")
    
    def start_production_services(self):
        """Start production services"""
        print("\n🚀 Starting production services...")
        
        # Determine which compose file to use
        compose_files = ["-f", str(self.docker_compose_file)]
        if self.production_compose_file.exists():
            compose_files.extend(["-f", str(self.production_compose_file)])
            print(f"✅ Using production compose file: {self.production_compose_file}")
        
        try:
            # Pull latest images
            print("📥 Pulling latest images...")
            subprocess.run(["docker-compose"] + compose_files + ["pull"], 
                         check=True, capture_output=True)
            
            # Build application
            print("🔨 Building application...")
            subprocess.run(["docker-compose"] + compose_files + ["build"], 
                         check=True, capture_output=True)
            
            # Start services
            print("▶️  Starting services...")
            subprocess.run(["docker-compose"] + compose_files + ["up", "-d"], 
                         check=True)
            
            print("✅ Services started successfully!")
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to start services: {e}")
            return False
        
        return True
    
    def wait_for_database(self, timeout=120):
        """Wait for database to be ready"""
        print(f"\n⏳ Waiting for database (timeout: {timeout}s)...")
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                result = subprocess.run([
                    "docker-compose", "exec", "-T", "db", 
                    "pg_isready", "-U", "postgres", "-d", "voting_db"
                ], capture_output=True, text=True, check=True, timeout=10)
                
                if "accepting connections" in result.stdout:
                    print("✅ Database is ready!")
                    return True
                    
            except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
                pass
            
            print(".", end="", flush=True)
            time.sleep(2)
        
        print(f"\n❌ Database did not become ready within {timeout} seconds")
        return False
    
    def initialize_database(self):
        """Initialize database schema and data"""
        print("\n🗄️  Initializing database...")
        
        try:
            # Run database initialization
            result = subprocess.run([
                "docker-compose", "exec", "-T", "voting-app",
                "python", "init_db.py"
            ], capture_output=True, text=True, check=True)
            
            print("✅ Database initialized successfully!")
            print(result.stdout)
            
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Database initialization failed: {e}")
            if e.stdout:
                print(f"Output: {e.stdout}")
            if e.stderr:
                print(f"Error: {e.stderr}")
            return False
    
    def verify_application(self):
        """Verify that application is working"""
        print("\n🧪 Verifying application...")
        
        # Wait a moment for application to start
        time.sleep(5)
        
        try:
            # Test health endpoint
            result = subprocess.run([
                "docker-compose", "exec", "-T", "voting-app",
                "curl", "-f", "http://localhost:5000/api/v1/health"
            ], capture_output=True, text=True, check=True, timeout=30)
            
            health_data = json.loads(result.stdout)
            if health_data.get('status') == 'healthy':
                print("✅ Health check passed!")
                
                # Test database connectivity through API
                result = subprocess.run([
                    "docker-compose", "exec", "-T", "voting-app",
                    "curl", "-f", "http://localhost:5000/get_votings"
                ], capture_output=True, text=True, check=True, timeout=30)
                
                print("✅ Database connectivity verified!")
                return True
            else:
                print(f"❌ Health check failed: {health_data}")
                return False
                
        except (subprocess.CalledProcessError, json.JSONDecodeError, subprocess.TimeoutExpired) as e:
            print(f"❌ Application verification failed: {e}")
            return False
    
    def show_access_info(self):
        """Show access information"""
        print("\n🌐 Access Information:")
        print("=" * 30)
        
        # Read environment to get domain
        try:
            with open(self.env_file) as f:
                env_content = f.read()
                
            web_domain = None
            for line in env_content.split('\n'):
                if line.startswith('WEB_DOMAIN='):
                    web_domain = line.split('=', 1)[1].strip()
                    break
            
            if web_domain:
                print(f"🌍 Main Application: https://{web_domain}")
                print(f"📊 Admin Panel: https://{web_domain}")
                print(f"🔗 API Health: https://{web_domain}/api/v1/health")
            else:
                print("🌍 Main Application: Check your WEB_DOMAIN in .env")
                
        except Exception:
            print("🌍 Main Application: Check your configuration")
        
        print(f"📁 Data Directory: {self.data_dir}")
        print(f"💾 Backups Directory: {self.backup_dir}")
        print(f"📝 Logs Directory: {self.logs_dir}")
        
        print("\n🔧 Management Commands:")
        print("  docker-compose logs -f                    # View logs")
        print("  docker-compose exec voting-app python init_db.py  # Reinitialize DB")
        print("  python backup_recovery.py --backup       # Create backup")
        print("  python monitor_system.py --report        # System health")
        
    def run_startup_sequence(self):
        """Run the complete startup sequence"""
        try:
            # Step 1: Prerequisites
            if not self.check_prerequisites():
                return False
            
            # Step 2: Setup directories
            self.setup_directories()
            
            # Step 3: Check configuration
            if not self.check_environment_config():
                return False
            
            # Step 4: Backup existing data
            self.backup_existing_data()
            
            # Step 5: Stop existing containers
            self.stop_existing_containers()
            
            # Step 6: Start services
            if not self.start_production_services():
                return False
            
            # Step 7: Wait for database
            if not self.wait_for_database():
                return False
            
            # Step 8: Initialize database
            if not self.initialize_database():
                return False
            
            # Step 9: Verify application
            if not self.verify_application():
                return False
            
            # Step 10: Show access info
            self.show_access_info()
            
            print("\n🎉 Production startup completed successfully!")
            print("🔄 The system is now running and ready for use.")
            
            return True
            
        except KeyboardInterrupt:
            print("\n\n🛑 Startup cancelled by user")
            return False
        except Exception as e:
            print(f"\n❌ Unexpected error during startup: {e}")
            return False

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="NVIAS Voting System Production Startup")
    parser.add_argument("--skip-verification", action="store_true", 
                       help="Skip application verification step")
    parser.add_argument("--backup-only", action="store_true",
                       help="Only create backup without starting services")
    
    args = parser.parse_args()
    
    startup = ProductionStartup()
    
    if args.backup_only:
        startup.setup_directories()
        startup.backup_existing_data()
        print("✅ Backup completed")
        return
    
    success = startup.run_startup_sequence()
    
    if not success:
        print("\n❌ Startup failed. Please check the errors above and try again.")
        sys.exit(1)
    else:
        print("\n✅ System is ready for production use!")

if __name__ == "__main__":
    main()
