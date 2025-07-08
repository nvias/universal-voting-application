-- Initial database setup for voting application
-- This script runs when the PostgreSQL container starts for the first time

-- The database is created by the POSTGRES_DB environment variable in docker-compose.
CREATE DATABASE voting_db;

-- Create extension for UUID generation (optional)
CREATE EXTENSION "uuid-ossp";

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE voting_db TO postgres;

-- Set timezone (optional)
SET timezone = 'UTC';
