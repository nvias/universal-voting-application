# Voting System Application

A modern Flask-based voting system with PostgreSQL backend, designed for team evaluations and surveys with flexible question types and comprehensive analytics. Features Traefik integration for production deployments with SSL support.

## Features

### Core Functionality
- **Flexible Voting System**: Support for rating scales, multiple choice, yes/no questions, team selection
- **Team-based Voting**: Users vote for different teams across multiple questions
- **Real-time Results**: Comprehensive analytics and result aggregation with detailed voting information
- **Mobile-Responsive**: Works seamlessly on desktop and mobile devices
- **Detailed Voting Tracking**: See which team voted for which team (perfect for competitions)

### API Integration
- **RESTful API**: Complete API for external application integration
- **Question Templates**: Reusable question templates for consistent surveys
- **External Team Management**: Import teams from external systems
- **Flexible Results Export**: SQL-based result queries for custom analytics

### Technical Features
- **PostgreSQL Database**: Robust data storage with complex query capabilities
- **Docker Ready**: Complete containerization with Docker Compose
- **Traefik Integration**: Production-ready reverse proxy with SSL certificates
- **Environment Configuration**: Flexible configuration for different environments
- **Database Migrations**: Version-controlled database schema changes

## Quick Start

### 🚀 One-Command Deployment

```bash
# Clone the repository
git clone <your-repo-url>
cd voting-app

# Run the deployment script (works for both local and production)
chmod +x deploy.sh
./deploy.sh
```

The deployment script will guide you through:
1. **Local Development**: Runs on localhost:5000 with all features
2. **Production Deployment**: Traefik integration with SSL and custom domain

### 🔧 Manual Setup

#### Local Development
```bash
# 1. Copy environment file
cp .env.example .env

# 2. Start services
docker-compose up -d

# 3. Initialize database
docker-compose exec voting-app python init_db.py

# 4. Access application
# Main App: http://localhost:5000
# PgAdmin: http://localhost:8080
```

#### Production with Traefik
```bash
# 1. Copy production environment template
cp .env.production .env

# 2. Edit .env with your domain and settings
nano .env

# 3. Remove development override (if exists)
mv docker-compose.override.yml docker-compose.override.yml.bak

# 4. Start production services
docker-compose up -d

# 5. Initialize database
docker-compose exec voting-app python init_db.py
```

## Configuration

### Environment Variables (.env)

```bash
# Project Settings
COMPOSE_PROJECT_NAME=nvias-voting
WEB_DOMAIN=voting.yourdomain.com
APP_URL=https://voting.yourdomain.com

# Application
FLASK_ENV=production
SECRET_KEY=your-very-secure-secret-key
CORS_ORIGINS=https://voting.yourdomain.com

# Database
POSTGRES_DB=voting_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=secure-password

# Traefik
CERT_RESOLVER=main-resolver

# Optional: PgAdmin
PGADMIN_ENABLE=true
PGADMIN_DOMAIN=pgadmin.yourdomain.com
```

### Docker Compose Files

- **docker-compose.yml**: Production configuration with Traefik
- **docker-compose.override.yml**: Local development overrides (auto-used)
- **.env.example**: Development environment template
- **.env.production**: Production environment template

## Deployment Scenarios

### 1. Local Development
```bash
# Uses docker-compose.override.yml automatically
docker-compose up -d

# Accessible at:
# - Main App: http://localhost:5000
# - PgAdmin: http://localhost:8080
```

### 2. Production with Traefik
```bash
# Remove override file for production
mv docker-compose.override.yml docker-compose.override.yml.bak

# Configure environment
cp .env.production .env
# Edit .env with your settings

# Deploy
docker-compose up -d

# Accessible at your configured domain with SSL
```

### 3. Standalone Production (No Traefik)
```bash
# Modify docker-compose.yml to add port mapping:
# ports:
#   - "5000:5000"

# Remove Traefik labels and deploy
docker-compose up -d
```

## API Usage Examples

### Create a Voting Session
```bash
curl -X POST http://localhost:5000/api/v1/voting \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Team Performance Review",
    "questions": [
      {
        "text": "Rate team communication",
        "question_type": "rating",
        "options": ["1", "2", "3", "4", "5"]
      }
    ],
    "teams": [
      {"name": "Development Team", "external_id": "dev_001"},
      {"name": "Design Team", "external_id": "design_001"}
    ]
  }'
```

### Get Detailed Results (Shows Which Team Voted for Which)
```bash
curl http://localhost:5000/api/v1/voting/{voting_id}/results
```

## Management Commands

```bash
# View logs
docker-compose logs -f voting-app

# Database shell
docker-compose exec db psql -U postgres -d voting_db

# Application shell
docker-compose exec voting-app python

# Initialize/Reset database
docker-compose exec voting-app python init_db.py

# Test application
docker-compose exec voting-app python test_fixes.py

# Stop services
docker-compose down

# Update and restart
docker-compose pull && docker-compose up -d
```

## Special Features

### "Naše firmy" Template
Perfect for company competitions where teams vote for each other:

```bash
# Creates session with categories: MASKA, KOLA, SKELET, PLAKÁT, MARKETING
docker-compose exec voting-app python init_db.py --sample
```

### Detailed Voting Results
See exactly which team voted for which team:
- Admin panel shows voting patterns
- Export includes voter information
- API provides detailed breakdown

### Real-time Statistics
- Live vote counting on presentation screens
- Automatic refresh every 5 seconds
- Manual refresh with visual feedback

## Project Structure

```
voting-app/
├── deploy.sh                 # Deployment script
├── docker-compose.yml        # Production Docker configuration
├── docker-compose.override.yml # Local development overrides
├── .env.example              # Development environment template
├── .env.production           # Production environment template
├── server.py                 # Main Flask application
├── models.py                 # Database models
├── api_blueprint.py          # API endpoints
├── config.py                 # Configuration classes
├── init_db.py               # Database initialization
├── requirements.txt          # Python dependencies
├── site/                     # Frontend templates
│   ├── admin.html           # Admin interface
│   ├── voting.html          # Voting interface
│   ├── qr.html              # QR code presentation
│   └── results.html         # Results visualization
└── docs/                     # Documentation
    ├── FIXES_APPLIED.md
    ├── RESULTS_GUIDE.md
    └── DETAILED_VOTING_GUIDE.md
```

## Monitoring and Logs

### Health Checks
- Application: `http://your-domain/api/v1/health`
- Database connectivity: Built-in Docker health checks
- Traefik integration: Automatic SSL and routing

### Logging
```bash
# View all logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f voting-app
docker-compose logs -f db
```

## Security Features

### Production Security
- Environment-based configuration
- Secret key management
- CORS configuration
- SQL injection prevention (SQLAlchemy ORM)
- Secure database connections

### SSL/TLS Support
- Automatic SSL certificate generation via Traefik
- HTTP to HTTPS redirection
- Secure cookie settings in production

## Performance Optimization

### Database
- Indexed foreign keys
- Efficient query patterns
- Connection pooling support
- Query optimization for large datasets

### Application
- Docker multi-stage builds
- Health checks for reliability
- Graceful shutdown handling
- Static file optimization

## Troubleshooting

### Common Issues

#### Port Conflicts
```bash
# Change external ports in .env or docker-compose.yml
WEB_PORT=5001  # If port 5000 is busy
```

#### Database Connection Issues
```bash
# Check database logs
docker-compose logs db

# Verify connection
docker-compose exec voting-app python test_db.py
```

#### Traefik Issues
```bash
# Verify Traefik network exists
docker network ls | grep traefik_proxy

# Check Traefik labels
docker-compose config
```

#### SSL Certificate Issues
```bash
# Check certificate resolver configuration
# Verify domain DNS points to your server
# Check Traefik logs for certificate generation
```

### Debug Mode
```bash
# Enable debug mode
echo "FLASK_ENV=development" >> .env
docker-compose restart voting-app
```

## API Documentation

Complete API documentation is available in `API_DOCUMENTATION.md`, including:
- All endpoint specifications
- Request/response examples
- Error handling
- Integration examples
- Advanced SQL query examples

## Contributing

### Development Workflow
1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Make changes and test locally: `./deploy.sh` → choice 1
4. Test production setup: `./deploy.sh` → choice 2
5. Submit pull request

### Code Standards
- PEP 8 compliance
- Type hints where appropriate
- Comprehensive docstrings
- Docker compatibility
- Environment variable configuration

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:
1. Check the troubleshooting section
2. Review deployment documentation
3. Check Docker logs: `docker-compose logs`
4. Open an issue with detailed error information

## Roadmap

### Upcoming Features
- [ ] WebSocket integration for real-time updates
- [ ] Advanced analytics dashboard
- [ ] Multi-language support
- [ ] Advanced authentication system
- [ ] Kubernetes deployment support
- [ ] Backup and restore functionality
- [ ] Advanced caching layer
- [ ] Mobile app API extensions
