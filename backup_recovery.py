#!/usr/bin/env python3
"""
Database Backup and Recovery System for NVIAS Voting Application
This script prevents data loss and provides recovery mechanisms.
"""

import os
import sys
import subprocess
import json
import shutil
from datetime import datetime, timedelta
from pathlib import Path

# Configuration
BACKUP_DIR = Path("./backups")
DATA_DIR = Path("./data")
MAX_BACKUPS = 10  # Keep last 10 backups

def ensure_directories():
    """Create necessary directories"""
    BACKUP_DIR.mkdir(exist_ok=True)
    DATA_DIR.mkdir(exist_ok=True)
    (DATA_DIR / "postgres").mkdir(exist_ok=True)
    (DATA_DIR / "app").mkdir(exist_ok=True)

def get_container_name():
    """Get the PostgreSQL container name"""
    try:
        result = subprocess.run([
            "docker", "ps", "--filter", "name=db", "--format", "{{.Names}}"
        ], capture_output=True, text=True, check=True)
        
        containers = result.stdout.strip().split('\n')
        postgres_containers = [c for c in containers if 'db' in c and c]
        
        if postgres_containers:
            return postgres_containers[0]
        else:
            raise Exception("No PostgreSQL container found")
            
    except subprocess.CalledProcessError:
        raise Exception("Could not find PostgreSQL container")

def create_backup():
    """Create a database backup"""
    print("🔄 Creating database backup...")
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_filename = f"voting_db_backup_{timestamp}.sql"
    backup_path = BACKUP_DIR / backup_filename
    
    try:
        container_name = get_container_name()
        
        # Create SQL dump
        cmd = [
            "docker", "exec", container_name,
            "pg_dump", "-U", "postgres", "-d", "voting_db", "--clean", "--create"
        ]
        
        print(f"📝 Running backup command: {' '.join(cmd)}")
        
        with open(backup_path, 'w') as f:
            result = subprocess.run(cmd, stdout=f, stderr=subprocess.PIPE, text=True, check=True)
        
        # Create metadata file
        metadata = {
            "timestamp": timestamp,
            "filename": backup_filename,
            "size": backup_path.stat().st_size,
            "created_at": datetime.now().isoformat(),
            "container": container_name,
            "database": "voting_db"
        }
        
        metadata_path = BACKUP_DIR / f"voting_db_backup_{timestamp}.json"
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        print(f"✅ Backup created successfully: {backup_filename}")
        print(f"📊 Backup size: {backup_path.stat().st_size / 1024:.2f} KB")
        
        # Clean old backups
        cleanup_old_backups()
        
        return backup_path
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Backup failed: {e}")
        if e.stderr:
            print(f"Error details: {e.stderr}")
        return None
    except Exception as e:
        print(f"❌ Backup error: {e}")
        return None

def list_backups():
    """List available backups"""
    print("\n📋 Available backups:")
    
    backups = []
    for backup_file in BACKUP_DIR.glob("voting_db_backup_*.sql"):
        metadata_file = backup_file.with_suffix('.json')
        
        if metadata_file.exists():
            with open(metadata_file) as f:
                metadata = json.load(f)
            backups.append({
                'file': backup_file,
                'metadata': metadata
            })
        else:
            # Backup without metadata
            stat = backup_file.stat()
            backups.append({
                'file': backup_file,
                'metadata': {
                    'timestamp': backup_file.stem.split('_')[-2] + '_' + backup_file.stem.split('_')[-1],
                    'size': stat.st_size,
                    'created_at': datetime.fromtimestamp(stat.st_mtime).isoformat()
                }
            })
    
    # Sort by timestamp
    backups.sort(key=lambda x: x['metadata']['timestamp'], reverse=True)
    
    if not backups:
        print("No backups found.")
        return []
    
    for i, backup in enumerate(backups, 1):
        metadata = backup['metadata']
        size_kb = metadata['size'] / 1024
        created = metadata.get('created_at', 'Unknown')
        
        print(f"{i:2d}. {backup['file'].name}")
        print(f"    Created: {created}")
        print(f"    Size: {size_kb:.2f} KB")
        print()
    
    return backups

def restore_backup(backup_path=None):
    """Restore database from backup"""
    if backup_path is None:
        backups = list_backups()
        if not backups:
            print("❌ No backups available for restore")
            return False
        
        try:
            choice = int(input("Select backup number to restore: ")) - 1
            if 0 <= choice < len(backups):
                backup_path = backups[choice]['file']
            else:
                print("❌ Invalid selection")
                return False
        except ValueError:
            print("❌ Please enter a valid number")
            return False
    
    print(f"🔄 Restoring database from: {backup_path.name}")
    
    # Confirm restore
    confirm = input("⚠️  This will overwrite the current database. Continue? (yes/no): ")
    if confirm.lower() != 'yes':
        print("Restore cancelled.")
        return False
    
    try:
        container_name = get_container_name()
        
        # Stop the application to prevent conflicts
        print("🛑 Stopping application...")
        subprocess.run(["docker-compose", "stop", "voting-app"], check=False)
        
        # Restore database
        cmd = [
            "docker", "exec", "-i", container_name,
            "psql", "-U", "postgres", "-d", "postgres"
        ]
        
        print("📥 Restoring database...")
        with open(backup_path, 'r') as f:
            result = subprocess.run(cmd, stdin=f, stderr=subprocess.PIPE, text=True, check=True)
        
        # Restart application
        print("🚀 Restarting application...")
        subprocess.run(["docker-compose", "start", "voting-app"], check=False)
        
        print("✅ Database restored successfully!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Restore failed: {e}")
        if e.stderr:
            print(f"Error details: {e.stderr}")
        return False
    except Exception as e:
        print(f"❌ Restore error: {e}")
        return False

def cleanup_old_backups():
    """Remove old backups, keeping only the latest MAX_BACKUPS"""
    backups = list(BACKUP_DIR.glob("voting_db_backup_*.sql"))
    backups.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    
    if len(backups) > MAX_BACKUPS:
        for backup_file in backups[MAX_BACKUPS:]:
            metadata_file = backup_file.with_suffix('.json')
            
            print(f"🗑️  Removing old backup: {backup_file.name}")
            backup_file.unlink()
            
            if metadata_file.exists():
                metadata_file.unlink()

def setup_automatic_backups():
    """Setup automatic backup schedule"""
    print("⏰ Setting up automatic backups...")
    
    # Create backup script
    backup_script = """#!/bin/bash
# Automatic backup script for NVIAS Voting System
cd "$(dirname "$0")"
python3 backup_recovery.py --backup --quiet
"""
    
    script_path = Path("./auto_backup.sh")
    with open(script_path, 'w') as f:
        f.write(backup_script)
    
    os.chmod(script_path, 0o755)
    
    # Create systemd timer (Linux)
    if sys.platform.startswith('linux'):
        print("📅 Creating systemd timer for automatic backups...")
        
        service_content = f"""[Unit]
Description=NVIAS Voting System Backup
After=docker.service

[Service]
Type=oneshot
WorkingDirectory={Path.cwd()}
ExecStart={Path.cwd() / 'auto_backup.sh'}
User={os.getenv('USER', 'root')}
"""
        
        timer_content = """[Unit]
Description=Run NVIAS backup every 6 hours
Requires=nvias-backup.service

[Timer]
OnCalendar=*-*-* 00,06,12,18:00:00
Persistent=true

[Install]
WantedBy=timers.target
"""
        
        print("📝 Systemd service and timer files created.")
        print("To enable automatic backups, run:")
        print("  sudo cp nvias-backup.service nvias-backup.timer /etc/systemd/system/")
        print("  sudo systemctl enable nvias-backup.timer")
        print("  sudo systemctl start nvias-backup.timer")
        
        with open("nvias-backup.service", 'w') as f:
            f.write(service_content)
        with open("nvias-backup.timer", 'w') as f:
            f.write(timer_content)
    
    print("✅ Automatic backup setup completed!")

def check_database_health():
    """Check database health and connection"""
    print("🏥 Checking database health...")
    
    try:
        container_name = get_container_name()
        
        # Check container status
        result = subprocess.run([
            "docker", "inspect", container_name, "--format", "{{.State.Status}}"
        ], capture_output=True, text=True, check=True)
        
        status = result.stdout.strip()
        print(f"📊 Container status: {status}")
        
        if status != "running":
            print("❌ Database container is not running!")
            return False
        
        # Check database connection
        cmd = [
            "docker", "exec", container_name,
            "pg_isready", "-U", "postgres", "-d", "voting_db"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print("✅ Database connection: OK")
        
        # Check data integrity
        cmd = [
            "docker", "exec", container_name,
            "psql", "-U", "postgres", "-d", "voting_db", "-c",
            "SELECT COUNT(*) as total_sessions FROM voting_sessions;"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print(f"📈 Database content check: {result.stdout.strip()}")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Health check failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="NVIAS Voting System Backup & Recovery")
    parser.add_argument("--backup", action="store_true", help="Create a backup")
    parser.add_argument("--restore", action="store_true", help="Restore from backup")
    parser.add_argument("--list", action="store_true", help="List available backups")
    parser.add_argument("--health", action="store_true", help="Check database health")
    parser.add_argument("--setup-auto", action="store_true", help="Setup automatic backups")
    parser.add_argument("--quiet", action="store_true", help="Quiet mode")
    
    args = parser.parse_args()
    
    ensure_directories()
    
    if not args.quiet:
        print("🗳️  NVIAS Voting System - Backup & Recovery Tool")
        print("=" * 50)
    
    if args.backup:
        create_backup()
    elif args.restore:
        restore_backup()
    elif args.list:
        list_backups()
    elif args.health:
        check_database_health()
    elif args.setup_auto:
        setup_automatic_backups()
    else:
        print("Available commands:")
        print("  --backup      Create a database backup")
        print("  --restore     Restore from backup")
        print("  --list        List available backups")
        print("  --health      Check database health")
        print("  --setup-auto  Setup automatic backups")
        print()
        print("Example usage:")
        print("  python backup_recovery.py --backup")
        print("  python backup_recovery.py --health")
        print("  python backup_recovery.py --restore")

if __name__ == "__main__":
    main()
