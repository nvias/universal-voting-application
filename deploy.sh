#!/bin/bash

# NVIAS Voting System Deployment Script
# This script helps deploy the voting system with proper configuration

set -e

echo "========================================="
echo "   NVIAS Voting System Deployment"
echo "========================================="
echo ""

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check dependencies
echo "Checking dependencies..."

if ! command_exists docker; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command_exists docker-compose; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

echo "✅ Docker and Docker Compose are installed"
echo ""

# Check deployment type
echo "Select deployment type:"
echo "1) Local Development (localhost:5000)"
echo "2) Production with Traefik (custom domain)"
echo ""
read -p "Enter your choice (1 or 2): " DEPLOYMENT_TYPE

case $DEPLOYMENT_TYPE in
    1)
        echo ""
        echo "🔧 Setting up LOCAL DEVELOPMENT deployment..."
        
        # Copy development environment file
        if [ ! -f .env ]; then
            cp .env.example .env
            echo "✅ Created .env file from .env.example"
        else
            echo "⚠️  .env file already exists, skipping creation"
        fi
        
        # Start services
        echo ""
        echo "🚀 Starting development services..."
        docker-compose up -d
        
        # Wait for services to be ready
        echo ""
        echo "⏳ Waiting for services to be ready..."
        sleep 10
        
        # Initialize database
        echo ""
        echo "🗄️  Initializing database..."
        docker-compose exec voting-app python init_db.py || echo "⚠️  Database initialization failed, but continuing..."
        
        echo ""
        echo "🎉 Local development deployment complete!"
        echo ""
        echo "📋 Access URLs:"
        echo "   Main App: http://localhost:5000"
        echo "   PgAdmin:  http://localhost:8080 (admin@example.com / admin)"
        echo ""
        echo "🔧 To customize settings, edit the .env file"
        ;;
        
    2)
        echo ""
        echo "🔧 Setting up PRODUCTION deployment with Traefik..."
        
        # Copy production environment template
        if [ ! -f .env ]; then
            cp .env.production .env
            echo "✅ Created .env file from production template"
            echo ""
            echo "⚠️  IMPORTANT: Please edit .env file with your configuration:"
            echo "   - WEB_DOMAIN: Your domain name"
            echo "   - SECRET_KEY: Generate a secure secret key"
            echo "   - POSTGRES_PASSWORD: Set a secure database password"
            echo "   - APP_URL: Your full application URL"
            echo ""
            read -p "Press Enter after you've configured the .env file..."
        else
            echo "⚠️  .env file already exists"
        fi
        
        # Check if Traefik network exists
        if ! docker network ls | grep -q "traefik_proxy"; then
            echo ""
            echo "⚠️  Traefik proxy network not found."
            echo "   Please ensure Traefik is running with a network named 'traefik_proxy'"
            echo "   Or modify docker-compose.yml to match your Traefik setup"
            echo ""
            read -p "Continue anyway? (y/N): " CONTINUE
            if [[ ! $CONTINUE =~ ^[Yy]$ ]]; then
                echo "Deployment cancelled."
                exit 1
            fi
        fi
        
        # Remove override file if it exists (for production)
        if [ -f docker-compose.override.yml ]; then
            echo "🔧 Backing up docker-compose.override.yml as docker-compose.override.yml.bak"
            mv docker-compose.override.yml docker-compose.override.yml.bak
        fi
        
        # Start production services
        echo ""
        echo "🚀 Starting production services..."
        docker-compose up -d
        
        # Wait for services to be ready
        echo ""
        echo "⏳ Waiting for services to be ready..."
        sleep 15
        
        # Initialize database
        echo ""
        echo "🗄️  Initializing database..."
        docker-compose exec voting-app python init_db.py || echo "⚠️  Database initialization failed, but continuing..."
        
        # Source the .env file to get the domain
        if [ -f .env ]; then
            export $(cat .env | grep -v '^#' | xargs)
        fi
        
        echo ""
        echo "🎉 Production deployment complete!"
        echo ""
        echo "📋 Access URLs:"
        echo "   Main App: ${APP_URL:-https://your-domain.com}"
        if [ "${PGADMIN_ENABLE:-false}" = "true" ]; then
            echo "   PgAdmin:  https://${PGADMIN_DOMAIN:-pgadmin.your-domain.com}"
        fi
        echo ""
        echo "🔧 To customize settings, edit the .env file and restart services"
        ;;
        
    *)
        echo "❌ Invalid choice. Please run the script again."
        exit 1
        ;;
esac

echo ""
echo "📚 Additional commands:"
echo "   View logs:     docker-compose logs -f"
echo "   Stop services: docker-compose down"
echo "   Update app:    docker-compose pull && docker-compose up -d"
echo "   Database shell: docker-compose exec db psql -U postgres -d voting_db"
echo ""
echo "🆘 For help, check README.md or run: docker-compose logs voting-app"
