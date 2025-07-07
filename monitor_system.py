#!/usr/bin/env python3
"""
System Monitoring and Diagnostic Tool for NVIAS Voting Application
This script monitors database health, prevents data loss, and provides diagnostics.
"""

import os
import sys
import subprocess
import json
import time
import psutil
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('system_monitor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SystemMonitor:
    def __init__(self):
        self.data_dir = Path("./data")
        self.logs_dir = Path("./logs")
        self.backup_dir = Path("./backups")
        self.container_prefix = "nvias-voting"
        
        # Ensure directories exist
        self.data_dir.mkdir(exist_ok=True)
        self.logs_dir.mkdir(exist_ok=True)
        self.backup_dir.mkdir(exist_ok=True)
        
        # Monitoring thresholds
        self.disk_threshold = 85  # % disk usage
        self.memory_threshold = 85  # % memory usage
        self.db_size_threshold = 1000  # MB
        
    def get_docker_containers(self) -> List[Dict]:
        """Get information about running Docker containers"""
        try:
            result = subprocess.run([
                "docker", "ps", "--format", 
                "{{.Names}}\t{{.Status}}\t{{.Image}}\t{{.Ports}}"
            ], capture_output=True, text=True, check=True)
            
            containers = []
            for line in result.stdout.strip().split('\n'):
                if line and self.container_prefix in line:
                    parts = line.split('\t')
                    containers.append({
                        'name': parts[0],
                        'status': parts[1] if len(parts) > 1 else 'Unknown',
                        'image': parts[2] if len(parts) > 2 else 'Unknown',
                        'ports': parts[3] if len(parts) > 3 else 'None'
                    })
            
            return containers
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to get Docker containers: {e}")
            return []
    
    def check_container_health(self, container_name: str) -> Dict:
        """Check health of a specific container"""
        try:
            # Get container stats
            stats_result = subprocess.run([
                "docker", "stats", container_name, "--no-stream", 
                "--format", "table {{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}\t{{.BlockIO}}"
            ], capture_output=True, text=True, check=True)
            
            # Get container logs (last 50 lines)
            logs_result = subprocess.run([
                "docker", "logs", "--tail", "50", container_name
            ], capture_output=True, text=True, check=True)
            
            # Check if container is healthy
            inspect_result = subprocess.run([
                "docker", "inspect", container_name, 
                "--format", "{{.State.Health.Status}}"
            ], capture_output=True, text=True, check=True)
            
            health_status = inspect_result.stdout.strip()
            
            return {
                'container': container_name,
                'health_status': health_status,
                'stats': stats_result.stdout.strip(),
                'recent_logs': logs_result.stdout.strip().split('\n')[-10:],  # Last 10 lines
                'timestamp': datetime.now().isoformat()
            }
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to check container health for {container_name}: {e}")
            return {
                'container': container_name,
                'health_status': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def check_database_health(self) -> Dict:
        """Comprehensive database health check"""
        db_container = None
        
        # Find database container
        containers = self.get_docker_containers()
        for container in containers:
            if 'db' in container['name']:
                db_container = container['name']
                break
        
        if not db_container:
            return {
                'status': 'error',
                'message': 'Database container not found'
            }
        
        try:
            # Check database connectivity
            conn_result = subprocess.run([
                "docker", "exec", db_container,
                "pg_isready", "-U", "postgres", "-d", "voting_db"
            ], capture_output=True, text=True, check=True)
            
            # Get database size
            size_result = subprocess.run([
                "docker", "exec", db_container,
                "psql", "-U", "postgres", "-d", "voting_db", "-t", "-c",
                "SELECT pg_size_pretty(pg_database_size('voting_db'));"
            ], capture_output=True, text=True, check=True)
            
            # Count records in main tables
            tables_result = subprocess.run([
                "docker", "exec", db_container,
                "psql", "-U", "postgres", "-d", "voting_db", "-t", "-c",
                """
                SELECT 
                    'voting_sessions', COUNT(*) FROM voting_sessions
                UNION ALL
                SELECT 
                    'teams', COUNT(*) FROM teams  
                UNION ALL
                SELECT 
                    'questions', COUNT(*) FROM questions
                UNION ALL
                SELECT 
                    'votes', COUNT(*) FROM votes
                UNION ALL
                SELECT 
                    'voters', COUNT(*) FROM voters;
                """
            ], capture_output=True, text=True, check=True)
            
            # Get active connections
            connections_result = subprocess.run([
                "docker", "exec", db_container,
                "psql", "-U", "postgres", "-d", "voting_db", "-t", "-c",
                "SELECT count(*) FROM pg_stat_activity WHERE datname = 'voting_db';"
            ], capture_output=True, text=True, check=True)
            
            # Parse results
            db_size = size_result.stdout.strip()
            active_connections = int(connections_result.stdout.strip())
            
            table_counts = {}
            for line in tables_result.stdout.strip().split('\n'):
                if '|' in line:
                    parts = line.split('|')
                    if len(parts) >= 2:
                        table_name = parts[0].strip()
                        count = parts[1].strip()
                        table_counts[table_name] = int(count) if count.isdigit() else 0
            
            return {
                'status': 'healthy',
                'database_size': db_size,
                'active_connections': active_connections,
                'table_counts': table_counts,
                'container': db_container,
                'timestamp': datetime.now().isoformat()
            }
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Database health check failed: {e}")
            return {
                'status': 'error',
                'message': str(e),
                'container': db_container,
                'timestamp': datetime.now().isoformat()
            }
    
    def check_system_resources(self) -> Dict:
        """Check system resource usage"""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            
            # Network I/O
            network = psutil.net_io_counters()
            
            # Process count
            process_count = len(psutil.pids())
            
            return {
                'cpu_percent': cpu_percent,
                'memory_percent': memory_percent,
                'memory_total_gb': round(memory.total / 1024**3, 2),
                'memory_used_gb': round(memory.used / 1024**3, 2),
                'disk_percent': disk_percent,
                'disk_total_gb': round(disk.total / 1024**3, 2),
                'disk_used_gb': round(disk.used / 1024**3, 2),
                'network_bytes_sent': network.bytes_sent,
                'network_bytes_recv': network.bytes_recv,
                'process_count': process_count,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"System resource check failed: {e}")
            return {
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def check_data_integrity(self) -> Dict:
        """Check data directory integrity and permissions"""
        issues = []
        
        # Check if data directories exist and have correct permissions
        critical_dirs = [
            self.data_dir / "postgres",
            self.data_dir / "app",
            self.backup_dir,
            self.logs_dir
        ]
        
        for dir_path in critical_dirs:
            if not dir_path.exists():
                issues.append(f"Missing directory: {dir_path}")
            elif not os.access(dir_path, os.R_OK | os.W_OK):
                issues.append(f"Permission issue: {dir_path}")
            else:
                # Check disk space in directory
                if dir_path.exists():
                    try:
                        stat = os.statvfs(str(dir_path))
                        free_bytes = stat.f_bavail * stat.f_frsize
                        total_bytes = stat.f_blocks * stat.f_frsize
                        free_percent = (free_bytes / total_bytes) * 100
                        
                        if free_percent < 10:  # Less than 10% free
                            issues.append(f"Low disk space in {dir_path}: {free_percent:.1f}% free")
                    except OSError:
                        pass
        
        # Check PostgreSQL data directory size
        postgres_data = self.data_dir / "postgres"
        if postgres_data.exists():
            try:
                total_size = sum(f.stat().st_size for f in postgres_data.rglob('*') if f.is_file())
                size_mb = total_size / 1024**2
                
                if size_mb > self.db_size_threshold:
                    issues.append(f"Large database size: {size_mb:.1f} MB")
            except Exception as e:
                issues.append(f"Could not calculate database size: {e}")
        
        return {
            'status': 'ok' if not issues else 'warning',
            'issues': issues,
            'timestamp': datetime.now().isoformat()
        }
    
    def generate_health_report(self) -> Dict:
        """Generate comprehensive health report"""
        logger.info("Generating system health report...")
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'docker_containers': self.get_docker_containers(),
            'database_health': self.check_database_health(),
            'system_resources': self.check_system_resources(),
            'data_integrity': self.check_data_integrity()
        }
        
        # Check individual containers
        report['container_health'] = {}
        for container in report['docker_containers']:
            container_name = container['name']
            report['container_health'][container_name] = self.check_container_health(container_name)
        
        # Overall system status
        critical_issues = []
        warnings = []
        
        # Database issues
        if report['database_health']['status'] != 'healthy':
            critical_issues.append("Database health check failed")
        
        # Resource issues
        resources = report['system_resources']
        if 'memory_percent' in resources and resources['memory_percent'] > self.memory_threshold:
            warnings.append(f"High memory usage: {resources['memory_percent']:.1f}%")
        
        if 'disk_percent' in resources and resources['disk_percent'] > self.disk_threshold:
            critical_issues.append(f"High disk usage: {resources['disk_percent']:.1f}%")
        
        # Data integrity issues
        if report['data_integrity']['status'] != 'ok':
            warnings.extend(report['data_integrity']['issues'])
        
        # Container health issues
        for container_name, health in report['container_health'].items():
            if health.get('health_status') not in ['healthy', '']:
                warnings.append(f"Container {container_name} health: {health.get('health_status', 'unknown')}")
        
        report['overall_status'] = {
            'status': 'critical' if critical_issues else ('warning' if warnings else 'healthy'),
            'critical_issues': critical_issues,
            'warnings': warnings,
            'summary': f"{len(critical_issues)} critical, {len(warnings)} warnings"
        }
        
        return report
    
    def save_report(self, report: Dict, filename: Optional[str] = None) -> str:
        """Save health report to file"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"health_report_{timestamp}.json"
        
        report_path = self.logs_dir / filename
        
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"Health report saved to {report_path}")
        return str(report_path)
    
    def monitor_continuous(self, interval: int = 300):
        """Run continuous monitoring with specified interval (seconds)"""
        logger.info(f"Starting continuous monitoring (interval: {interval}s)")
        
        while True:
            try:
                report = self.generate_health_report()
                
                # Save report
                self.save_report(report)
                
                # Log status
                status = report['overall_status']
                if status['status'] == 'critical':
                    logger.error(f"CRITICAL: {status['summary']}")
                    for issue in status['critical_issues']:
                        logger.error(f"  - {issue}")
                elif status['status'] == 'warning':
                    logger.warning(f"WARNING: {status['summary']}")
                    for warning in status['warnings']:
                        logger.warning(f"  - {warning}")
                else:
                    logger.info("System status: HEALTHY")
                
                # Sleep until next check
                time.sleep(interval)
                
            except KeyboardInterrupt:
                logger.info("Monitoring stopped by user")
                break
            except Exception as e:
                logger.error(f"Monitoring error: {e}")
                time.sleep(60)  # Wait 1 minute before retrying
    
    def cleanup_old_reports(self, days: int = 7):
        """Clean up old health reports"""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        deleted_count = 0
        for report_file in self.logs_dir.glob("health_report_*.json"):
            try:
                file_time = datetime.fromtimestamp(report_file.stat().st_mtime)
                if file_time < cutoff_date:
                    report_file.unlink()
                    deleted_count += 1
            except Exception as e:
                logger.error(f"Failed to delete old report {report_file}: {e}")
        
        if deleted_count > 0:
            logger.info(f"Cleaned up {deleted_count} old health reports")

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="NVIAS Voting System Monitor")
    parser.add_argument("--report", action="store_true", help="Generate one-time health report")
    parser.add_argument("--monitor", action="store_true", help="Run continuous monitoring")
    parser.add_argument("--interval", type=int, default=300, help="Monitoring interval in seconds")
    parser.add_argument("--cleanup", action="store_true", help="Clean up old reports")
    parser.add_argument("--days", type=int, default=7, help="Days to keep reports")
    
    args = parser.parse_args()
    
    monitor = SystemMonitor()
    
    print("🔍 NVIAS Voting System Monitor")
    print("=" * 40)
    
    if args.cleanup:
        monitor.cleanup_old_reports(args.days)
    elif args.monitor:
        monitor.monitor_continuous(args.interval)
    elif args.report:
        report = monitor.generate_health_report()
        report_path = monitor.save_report(report)
        
        # Print summary
        status = report['overall_status']
        print(f"\n📊 System Status: {status['status'].upper()}")
        print(f"📈 Summary: {status['summary']}")
        
        if status['critical_issues']:
            print("\n🚨 Critical Issues:")
            for issue in status['critical_issues']:
                print(f"  - {issue}")
        
        if status['warnings']:
            print("\n⚠️  Warnings:")
            for warning in status['warnings']:
                print(f"  - {warning}")
        
        print(f"\n📄 Full report saved to: {report_path}")
    else:
        print("Available commands:")
        print("  --report      Generate health report")
        print("  --monitor     Run continuous monitoring")
        print("  --cleanup     Clean up old reports")
        print()
        print("Example usage:")
        print("  python monitor_system.py --report")
        print("  python monitor_system.py --monitor --interval 600")

if __name__ == "__main__":
    main()
