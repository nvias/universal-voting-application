# NVIAS Voting System - Troubleshooting Guide

## 🚨 Common Issues and Solutions

### Issue 1: Database Deleting Itself in Production

**Symptoms:**
- Database data disappears after container restarts
- Voting sessions lost randomly
- Empty database after server reboot

**Root Causes:**
- Improper Docker volume configuration
- Container restart policies
- Missing data directory binding
- Database not using persistent storage

**Solutions:**

#### Immediate Fix:
```bash
# 1. Run the production fixes script
python3 fix_production_issues.py

# 2. Use the persistence configuration
docker-compose -f docker-compose.yml -f docker-compose.persistence.yml up -d

# 3. Verify data directories exist
ls -la data/postgres/
```

#### Preventive Measures:
```bash
# 1. Always use bind mounts for production
# Update docker-compose.yml volumes section:
volumes:
  - ./data/postgres:/var/lib/postgresql/data
  - ./backups:/backups

# 2. Set proper restart policies
restart: always  # Instead of unless-stopped

# 3. Regular backups
./create_backup.sh  # Every 6 hours recommended
```

### Issue 2: Home Page Not Working

**Symptoms:**
- Admin panel shows errors
- API calls fail
- Voting interface not loading
- 404 errors on main functionality

**Root Causes:**
- API endpoint mismatches
- Missing error handling
- Frontend/backend communication issues
- Database connection problems

**Solutions:**

#### Check System Status:
```bash
# 1. Run health check
./health_check.sh

# 2. Check container logs
docker-compose logs voting-app
docker-compose logs db

# 3. Test API endpoints
curl http://localhost:5000/api/v1/health
curl http://localhost:5000/get_votings
```

#### Fix Admin Interface:
```bash
# 1. The admin.html has been updated with fixes
# 2. Clear browser cache
# 3. Check browser console for JavaScript errors
# 4. Verify API endpoints are responding
```

### Issue 3: Container Won't Start

**Symptoms:**
- Docker containers exit immediately
- "Connection refused" errors
- Services not accessible

**Debugging Steps:**
```bash
# 1. Check container status
docker-compose ps

# 2. View detailed logs
docker-compose logs --tail=50 voting-app
docker-compose logs --tail=50 db

# 3. Check resource usage
docker stats

# 4. Verify configuration
docker-compose config
```

**Common Fixes:**
```bash
# 1. Stop and rebuild
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# 2. Check permissions
chmod -R 755 data/
chmod -R 755 backups/

# 3. Remove conflicting containers
docker system prune -f
```

### Issue 4: Database Connection Errors

**Symptoms:**
- "Connection to database failed"
- SQLAlchemy errors
- Timeouts during database operations

**Solutions:**
```bash
# 1. Verify database is running
docker-compose exec db pg_isready -U postgres -d voting_db

# 2. Check database logs
docker-compose logs db | tail -20

# 3. Test connection manually
docker-compose exec db psql -U postgres -d voting_db -c "SELECT 1;"

# 4. Reset database if needed
docker-compose exec voting-app python init_db.py
```

### Issue 5: Voting Interface Problems

**Symptoms:**
- Users can't submit votes
- Vote counts not updating
- QR code page shows wrong statistics

**Solutions:**
```bash
# 1. Check if voting session is active
# Access admin panel and verify session status

# 2. Test vote submission API
curl -X POST http://localhost:5000/api/submit-vote/SESSION_ID \
  -H "Content-Type: application/json" \
  -d '{"votes": []}'

# 3. Clear browser cache and cookies
# 4. Check for JavaScript errors in browser console
```

## 🔧 Diagnostic Commands

### System Health Check
```bash
# Quick health check
./health_check.sh

# Comprehensive system report
python3 monitor_system.py --report

# Continuous monitoring
python3 monitor_system.py --monitor --interval 300
```

### Database Diagnostics
```bash
# Check database size
docker-compose exec db psql -U postgres -d voting_db -c "
SELECT pg_size_pretty(pg_database_size('voting_db')) as db_size;"

# Count records in tables
docker-compose exec db psql -U postgres -d voting_db -c "
SELECT 'voting_sessions' as table_name, COUNT(*) FROM voting_sessions
UNION ALL
SELECT 'votes', COUNT(*) FROM votes
UNION ALL
SELECT 'voters', COUNT(*) FROM voters;"

# Check for database errors
docker-compose logs db | grep -i error
```

### Application Diagnostics
```bash
# Check application logs
docker-compose logs voting-app | tail -50

# Test API endpoints
curl -s http://localhost:5000/api/v1/health | jq
curl -s http://localhost:5000/get_votings | jq

# Check resource usage
docker stats voting-app db
```

## 🛠️ Recovery Procedures

### Complete System Recovery
```bash
# 1. Stop all services
docker-compose down

# 2. Backup current state (if any data exists)
python3 backup_recovery.py --backup

# 3. Clean start with fixes
python3 fix_production_issues.py

# 4. Start with persistence
./quick_start.sh

# 5. Verify functionality
./health_check.sh
```

### Database Recovery
```bash
# 1. List available backups
python3 backup_recovery.py --list

# 2. Restore from backup
python3 backup_recovery.py --restore

# 3. Reinitialize if no backups
docker-compose exec voting-app python init_db.py
```

### Configuration Reset
```bash
# 1. Reset to default configuration
cp .env.production .env

# 2. Update for your environment
nano .env

# 3. Rebuild and restart
docker-compose down
docker-compose build
docker-compose up -d
```

## 📋 Preventive Maintenance

### Daily Tasks
```bash
# Check system status
./health_check.sh

# Monitor logs for errors
docker-compose logs --since 24h | grep -i error
```

### Weekly Tasks
```bash
# Create backup
./create_backup.sh

# System health report
python3 monitor_system.py --report

# Clean old logs
docker-compose logs --since 168h > weekly_logs.txt
```

### Monthly Tasks
```bash
# Update system
docker-compose pull
docker-compose up -d

# Clean old backups
python3 backup_recovery.py --cleanup --days 30

# Full system health check
python3 monitor_system.py --report
```

## 🚀 Performance Optimization

### Database Performance
```bash
# Check database performance
docker-compose exec db psql -U postgres -d voting_db -c "
SELECT query, calls, total_time, mean_time 
FROM pg_stat_statements 
ORDER BY total_time DESC LIMIT 10;"

# Optimize database
docker-compose exec db psql -U postgres -d voting_db -c "VACUUM ANALYZE;"
```

### Container Resource Limits
```yaml
# Add to docker-compose.yml
services:
  db:
    deploy:
      resources:
        limits:
          memory: 512M
          cpus: '0.5'
        reservations:
          memory: 256M

  voting-app:
    deploy:
      resources:
        limits:
          memory: 256M
          cpus: '0.3'
```

## 📞 Getting Help

### Log Collection
```bash
# Collect all relevant logs
mkdir -p debug_logs
docker-compose logs > debug_logs/docker_logs.txt
python3 monitor_system.py --report > debug_logs/system_report.json
cp .env debug_logs/env_config.txt
tar -czf nvias_debug_$(date +%Y%m%d_%H%M%S).tar.gz debug_logs/
```

### Contact Information
When reporting issues, please include:
1. System report (`python3 monitor_system.py --report`)
2. Docker logs (`docker-compose logs`)
3. Error messages from browser console
4. Steps to reproduce the issue
5. System configuration (OS, Docker version)

## 🔍 Advanced Debugging

### Enable Debug Mode
```bash
# Add to .env file
FLASK_ENV=development
FLASK_DEBUG=1

# Restart application
docker-compose restart voting-app
```

### Database Query Debugging
```bash
# Enable query logging in PostgreSQL
docker-compose exec db psql -U postgres -d voting_db -c "
ALTER SYSTEM SET log_statement = 'all';
SELECT pg_reload_conf();"

# View query logs
docker-compose logs db | grep -i "statement:"
```

### Network Debugging
```bash
# Check network connectivity
docker network ls
docker network inspect nvias-voting_local

# Test internal communication
docker-compose exec voting-app curl http://db:5432
docker-compose exec db netstat -ln
```

This troubleshooting guide should help you resolve most issues with the NVIAS Voting System. For persistent problems, run the diagnostic commands and collect logs for further analysis.
