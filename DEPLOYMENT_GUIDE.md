# 🚀 NVIAS Voting System - Complete Deployment Guide

This guide covers all deployment scenarios for the NVIAS Voting System, from local development to production with Traefik reverse proxy and SSL certificates.

## 📋 Overview

The system now supports:
- **Local Development**: Simple localhost setup for development and testing
- **Production with Traefik**: Full production deployment with SSL certificates and custom domains
- **Standalone Production**: Production without Traefik (manual SSL/proxy setup)

## 🏗️ Architecture

### Docker Services
- **voting-app**: Main Flask application (port 5000)
- **db**: PostgreSQL database (port 5432)
- **pgadmin**: Database management interface (port 80/8080)

### Networks
- **local**: Internal communication between services
- **proxy**: External Traefik network (production only)

### Volumes
- **postgres_data**: Database persistence
- **pgadmin_data**: PgAdmin configuration
- **voting_data**: Application data storage

## 🚀 Quick Start

### One-Command Deployment
```bash
# Clone and deploy in one go
git clone <your-repo-url> && cd voting-app
chmod +x deploy.sh && ./deploy.sh
```

The script will guide you through:
1. **Option 1**: Local development setup
2. **Option 2**: Production setup with Traefik

## 🔧 Manual Setup Options

### Option 1: Local Development

Perfect for testing, development, and local demonstrations.

```bash
# 1. Setup environment
cp .env.example .env

# 2. Start services (uses docker-compose.override.yml automatically)
docker-compose up -d

# 3. Initialize database
docker-compose exec voting-app python init_db.py

# 4. Access application
echo "Application ready at http://localhost:5000"
```

**What you get:**
- Main app: http://localhost:5000
- PgAdmin: http://localhost:8080 (admin@example.com / admin)
- Full development environment with hot reloading
- No SSL/domain configuration needed

### Option 2: Production with Traefik

For production deployments with automatic SSL certificates.

```bash
# 1. Setup production environment
cp .env.production .env

# 2. Configure your settings in .env
nano .env
# Required changes:
# - WEB_DOMAIN=your-domain.com
# - SECRET_KEY=generate-secure-key
# - POSTGRES_PASSWORD=secure-password
# - APP_URL=https://your-domain.com

# 3. Remove development overrides
mv docker-compose.override.yml docker-compose.override.yml.bak

# 4. Ensure Traefik network exists
docker network create traefik_proxy

# 5. Start production services
docker-compose up -d

# 6. Initialize database
docker-compose exec voting-app python init_db.py
```

**What you get:**
- Custom domain with SSL certificates
- Automatic HTTP to HTTPS redirect
- Production-optimized configuration
- Optional PgAdmin with subdomain
- Full Traefik integration

### Option 3: Standalone Production

For production without Traefik (you handle SSL/proxy externally).

```bash
# 1. Modify docker-compose.yml to add port mapping
# Add under voting-app service:
#   ports:
#     - "5000:5000"

# 2. Remove Traefik labels (optional)
# Edit docker-compose.yml and remove all "traefik.*" labels

# 3. Deploy
cp .env.production .env
nano .env  # Configure your settings
docker-compose up -d
```

## 📂 Configuration Files

### Environment Files
- **.env.example**: Local development template
- **.env.production**: Production template with Traefik
- **.env**: Your actual configuration (created from templates)

### Docker Files
- **docker-compose.yml**: Main configuration with Traefik support
- **docker-compose.override.yml**: Local development overrides
- **Dockerfile**: Application container definition

### Key Environment Variables

```bash
# Project Identity
COMPOSE_PROJECT_NAME=nvias-voting        # Docker compose project name
WEB_DOMAIN=voting.yourdomain.com         # Your domain
APP_URL=https://voting.yourdomain.com    # Full app URL

# Security
SECRET_KEY=your-very-secure-secret-key   # Flask secret key
POSTGRES_PASSWORD=secure-db-password     # Database password

# Features
CORS_ORIGINS=https://voting.yourdomain.com  # Allowed origins
PGADMIN_ENABLE=true                      # Enable PgAdmin
CERT_RESOLVER=main-resolver              # Traefik cert resolver
```

## 🌐 Traefik Integration

### Prerequisites
- Traefik running with network named `traefik_proxy`
- DNS pointing to your server
- Certificate resolver configured in Traefik

### Automatic Features
- **SSL Certificates**: Automatic Let's Encrypt certificates
- **HTTP Redirect**: Automatic HTTP to HTTPS redirect
- **Load Balancing**: Built-in load balancing capabilities
- **Health Checks**: Application health monitoring

### Traefik Labels Explained
```yaml
# Enable Traefik
traefik.enable=true
traefik.docker.network=traefik_proxy

# HTTP Router (redirects to HTTPS)
traefik.http.routers.web_${COMPOSE_PROJECT_NAME}.entrypoints=web
traefik.http.routers.web_${COMPOSE_PROJECT_NAME}.rule=Host(`${WEB_DOMAIN}`)
traefik.http.routers.web_${COMPOSE_PROJECT_NAME}.middlewares=web_${COMPOSE_PROJECT_NAME}_https

# HTTPS Router (main application)
traefik.http.routers.web_${COMPOSE_PROJECT_NAME}-https.entrypoints=websecure
traefik.http.routers.web_${COMPOSE_PROJECT_NAME}-https.rule=Host(`${WEB_DOMAIN}`)
traefik.http.routers.web_${COMPOSE_PROJECT_NAME}-https.tls=true
traefik.http.routers.web_${COMPOSE_PROJECT_NAME}-https.tls.certresolver=main-resolver
```

## 🗄️ Database Management

### Access Database
```bash
# Database shell
docker-compose exec db psql -U postgres -d voting_db

# Via PgAdmin (if enabled)
# Local: http://localhost:8080
# Production: https://pgadmin.yourdomain.com
```

### Database Operations
```bash
# Initialize/reset database
docker-compose exec voting-app python init_db.py

# Create sample data
docker-compose exec voting-app python init_db.py --sample

# Test database connection
docker-compose exec voting-app python test_db.py

# Database backup
docker-compose exec db pg_dump -U postgres voting_db > backup.sql

# Database restore
docker-compose exec -T db psql -U postgres voting_db < backup.sql
```

## 📊 Monitoring and Maintenance

### Health Checks
```bash
# Application health
curl http://localhost:5000/api/v1/health

# Service status
docker-compose ps

# View logs
docker-compose logs -f voting-app
```

### Updates and Maintenance
```bash
# Update application
docker-compose pull
docker-compose up -d

# Restart specific service
docker-compose restart voting-app

# Scale services (if needed)
docker-compose up -d --scale voting-app=2
```

## 🚨 Troubleshooting

### Common Issues

#### "Traefik network not found"
```bash
# Create the network
docker network create traefik_proxy

# Or check existing networks
docker network ls
```

#### "Port already in use"
```bash
# Check what's using the port
sudo lsof -i :5000

# Change port in docker-compose.override.yml
ports:
  - "5001:5000"
```

#### "Database connection failed"
```bash
# Check database logs
docker-compose logs db

# Verify database is running
docker-compose ps db

# Test connection
docker-compose exec voting-app python -c "from server import create_app; create_app()"
```

#### "SSL Certificate issues"
```bash
# Check Traefik logs
docker logs traefik

# Verify DNS
nslookup your-domain.com

# Check certificate resolver
# Ensure Traefik has proper ACME configuration
```

### Debug Mode
```bash
# Enable debug logging
echo "FLASK_ENV=development" >> .env
docker-compose restart voting-app

# View detailed logs
docker-compose logs -f voting-app
```

## 🔒 Security Considerations

### Production Security Checklist
- [ ] Change default SECRET_KEY
- [ ] Set strong POSTGRES_PASSWORD
- [ ] Configure proper CORS_ORIGINS
- [ ] Use HTTPS in production
- [ ] Disable debug mode (FLASK_ENV=production)
- [ ] Regular security updates
- [ ] Monitor application logs
- [ ] Backup database regularly

### Network Security
- Internal services communicate via `local` network
- Only necessary ports exposed to public
- Traefik handles SSL termination
- Database not directly accessible from internet

## 🚀 Advanced Deployment

### Multiple Environments
```bash
# Development
cp .env.example .env.dev
docker-compose --env-file .env.dev up -d

# Staging
cp .env.production .env.staging
# Edit staging-specific settings
docker-compose --env-file .env.staging up -d

# Production
cp .env.production .env.prod
# Edit production settings
docker-compose --env-file .env.prod up -d
```

### Custom Traefik Configuration
```yaml
# Add custom middleware
labels:
  - "traefik.http.middlewares.auth.basicauth.users=admin:$$2y$$10$$..."
  - "traefik.http.routers.web_${COMPOSE_PROJECT_NAME}-https.middlewares=auth"
```

### Load Balancing
```bash
# Scale application instances
docker-compose up -d --scale voting-app=3

# Traefik automatically load balances between instances
```

## 📋 Deployment Checklist

### Pre-deployment
- [ ] Server requirements met (Docker, Docker Compose)
- [ ] Domain DNS configured
- [ ] Traefik running (for production)
- [ ] Environment variables configured
- [ ] Backup existing data (if upgrading)

### Deployment
- [ ] Clone repository
- [ ] Configure environment (.env)
- [ ] Start services (docker-compose up -d)
- [ ] Initialize database
- [ ] Test application functionality
- [ ] Verify SSL certificates (production)

### Post-deployment
- [ ] Monitor logs for errors
- [ ] Test all functionality
- [ ] Setup monitoring/alerting
- [ ] Document custom configurations
- [ ] Plan backup strategy

## 🎯 Summary

The NVIAS Voting System now supports flexible deployment options:

1. **Local Development**: Quick setup for testing and development
2. **Production with Traefik**: Full production deployment with SSL
3. **Standalone Production**: Production without Traefik dependency

Choose the option that best fits your infrastructure and requirements. The automated deployment script (`./deploy.sh`) makes setup simple for both scenarios.

For questions or issues, check the troubleshooting section or review the Docker logs for detailed error information.
