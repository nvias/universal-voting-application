-- Initial database setup for voting application
-- This script runs when the PostgreSQL container starts for the first time

-- Create database if it doesn't exist (optional, as it's created by POSTGRES_DB)
CREATE DATABASE IF NOT EXISTS voting_db;

-- Create extension for UUID generation (optional)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE voting_db TO postgres;

-- Set timezone (optional)
SET timezone = 'UTC';
