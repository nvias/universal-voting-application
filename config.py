import os
from datetime import timedelta

class Config:
    # Database Configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'postgresql://username:password@localhost:5432/voting_db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Security
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here'
    
    # CORS
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '*').split(',')
    
    # API Configuration
    API_TITLE = 'Voting System API'
    API_VERSION = 'v1'
    
    # Application URL for QR codes
    APP_URL = os.environ.get('APP_URL') or 'http://localhost:5000'
    
    # Session timeout
    PERMANENT_SESSION_LIFETIME = timedelta(hours=5)

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_ECHO = True

class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_ECHO = False

class DockerConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'postgresql://postgres:password@db:5432/voting_db'

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'docker': DockerConfig,
    'default': DevelopmentConfig
}
