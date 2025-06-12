# Voting System Application

A modern Flask-based voting system with PostgreSQL backend, designed for team evaluations and surveys with flexible question types and comprehensive analytics.

## Features

### Core Functionality
- **Flexible Voting System**: Support for rating scales, multiple choice, yes/no questions
- **Team-based Voting**: Users vote for different teams across multiple questions
- **Real-time Results**: Comprehensive analytics and result aggregation
- **Mobile-Responsive**: Works seamlessly on desktop and mobile devices

### API Integration
- **RESTful API**: Complete API for external application integration
- **Question Templates**: Reusable question templates for consistent surveys
- **External Team Management**: Import teams from external systems
- **Flexible Results Export**: SQL-based result queries for custom analytics

### Technical Features
- **PostgreSQL Database**: Robust data storage with complex query capabilities
- **Docker Ready**: Complete containerization with Docker Compose
- **Environment Configuration**: Flexible configuration for different environments
- **Database Migrations**: Version-controlled database schema changes

## Quick Start with Docker

### Prerequisites
- Docker and Docker Compose installed
- Git

### 1. Clone and Start
```bash
git clone <your-repo-url>
cd voting-app

# Start the application stack
docker-compose up -d
```

### 2. Initialize Database
```bash
# Initialize database with sample data
docker-compose exec voting-app python init_db.py
```

### 3. Access the Application
- **Main App**: http://localhost:5000
- **API Health Check**: http://localhost:5000/api/v1/health
- **PgAdmin** (optional): http://localhost:8080 (admin@example.com / admin)

## Development Setup

### Prerequisites
- Python 3.11+
- PostgreSQL 15+
- Git

### 1. Setup Environment
```bash
# Clone repository
git clone <your-repo-url>
cd voting-app

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Database
```bash
# Copy environment template
cp .env.example .env

# Edit .env with your database credentials
DATABASE_URL=postgresql://username:password@localhost:5432/voting_db
SECRET_KEY=your-secret-key
```

### 3. Initialize Database
```bash
# Create database tables and sample data
python init_db.py

# Or use migrations (recommended for production)
python create_migrations.py
```

### 4. Run Application
```bash
python server.py
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

### Start Voting Session
```bash
curl -X POST http://localhost:5000/api/v1/voting/{voting_id}/start
```

### Get Results
```bash
curl http://localhost:5000/api/v1/voting/{voting_id}/results
```

## Project Structure

```
voting-app/
├── server.py              # Main Flask application
├── models.py              # Database models
├── api_blueprint.py       # API endpoints
├── config.py              # Configuration classes
├── init_db.py            # Database initialization
├── create_migrations.py   # Migration helper
├── requirements.txt       # Python dependencies
├── Dockerfile            # Container definition
├── docker-compose.yml    # Multi-container setup
├── site/                 # Frontend templates
│   ├── admin.html
│   ├── login.html
│   ├── voting.html
│   └── qr.html
├── database/             # Legacy JSON files (deprecated)
└── migrations/           # Database migrations (auto-generated)
```

## Database Schema

### Core Tables
- **voting_sessions**: Main voting sessions
- **questions**: Questions within sessions
- **teams**: Teams being evaluated
- **votes**: Individual votes cast
- **voters**: Voter tracking
- **question_templates**: Reusable question templates

### Key Relationships
- Sessions contain multiple questions and teams
- Votes link questions, teams, and voters
- Flexible schema supports various question types and aggregation methods

## Configuration

### Environment Variables
```bash
# Flask Configuration
FLASK_ENV=development|production|docker
SECRET_KEY=your-secret-key

# Database
DATABASE_URL=postgresql://user:pass@host:port/db

# CORS (comma-separated origins)
CORS_ORIGINS=*
```

### Docker Environment
The application automatically configures for Docker when `FLASK_ENV=docker`.

## Deployment

### Production Deployment with Docker
```bash
# Set production environment
export FLASK_ENV=production
export SECRET_KEY=your-very-secure-key
export DATABASE_URL=postgresql://user:pass@prod-db:5432/voting_db

# Deploy
docker-compose -f docker-compose.yml up -d
```

### Portainer Stack Deployment
1. Copy `docker-compose.yml` to Portainer
2. Set environment variables in Portainer UI
3. Deploy stack

### Environment-Specific Configurations
- **Development**: SQLite fallback, debug mode, detailed logging
- **Production**: PostgreSQL required, security headers, optimized settings
- **Docker**: Container-optimized settings, health checks

## API Documentation

Complete API documentation is available in `API_DOCUMENTATION.md`, including:
- All endpoint specifications
- Request/response examples
- Error handling
- Integration examples
- Advanced SQL query examples

## Security Considerations

### Current Security Features
- CORS configuration
- SQL injection prevention (SQLAlchemy ORM)
- Input validation
- Error handling without information disclosure

### Recommended Production Security
- Implement API authentication (JWT/API keys)
- Add rate limiting
- Use HTTPS with proper certificates
- Regular security updates
- Database connection encryption
- Environment variable security

## Performance Optimization

### Database
- Indexed foreign keys
- Efficient query patterns
- Connection pooling
- Query optimization for large datasets

### Application
- SQLAlchemy ORM optimization
- Caching strategies for templates
- Async capabilities for high concurrency

## Monitoring and Logging

### Health Checks
- Application health endpoint: `/api/v1/health`
- Database connectivity checks
- Docker health checks configured

### Logging
- Structured logging for production
- Error tracking and monitoring
- Performance metrics collection

## Contributing

### Development Workflow
1. Fork the repository
2. Create feature branch
3. Implement changes with tests
4. Update documentation
5. Submit pull request

### Code Standards
- PEP 8 compliance
- Type hints where appropriate
- Comprehensive docstrings
- Unit test coverage

## Troubleshooting

### Common Issues

#### Database Connection Errors
```bash
# Check database status
docker-compose logs db

# Verify connection string
python -c "from server import create_app; app=create_app(); app.app_context().push(); from models import db; db.create_all()"
```

#### Port Conflicts
```bash
# Change ports in docker-compose.yml if needed
ports:
  - "5001:5000"  # Change external port
```

#### Permission Issues
```bash
# Fix file permissions
sudo chown -R $USER:$USER .
```

### Logs and Debugging
```bash
# View application logs
docker-compose logs voting-app

# View database logs
docker-compose logs db

# Access container for debugging
docker-compose exec voting-app bash
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:
1. Check the troubleshooting section
2. Review API documentation
3. Check Docker logs for error details
4. Open an issue with detailed error information

## Roadmap

### Upcoming Features
- [ ] Real-time voting updates via WebSocket
- [ ] Advanced analytics dashboard
- [ ] Email notifications
- [ ] Bulk import/export functionality
- [ ] Multi-language support
- [ ] Advanced authentication system
- [ ] Audit logging
- [ ] API rate limiting
- [ ] Caching layer implementation
- [ ] Mobile app API extensions
