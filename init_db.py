#!/usr/bin/env python3
"""
Database initialization script for the voting application.
Run this script to create all database tables and add sample data.
"""

import os
import sys
from datetime import datetime
import argparse
from sqlalchemy import inspect, text
from sqlalchemy.exc import SQLAlchemyError, OperationalError

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from server import create_app
from models import db, VotingSession, Question, Team, Vote, Voter, QuestionTemplate


def check_database_connection():
    """Check if database connection is working"""
    app = create_app()

    with app.app_context():
        try:
            # Try to execute a simple query
            db.session.execute(text('SELECT 1'))
            print("✓ Database connection successful")
            return True
        except OperationalError as e:
            print(f"✗ Database connection failed: {e}")
            return False
        except Exception as e:
            print(f"✗ Unexpected error connecting to database: {e}")
            return False


def check_tables_exist():
    """Check which tables already exist in the database"""
    app = create_app()

    with app.app_context():
        try:
            inspector = inspect(db.engine)
            existing_tables = inspector.get_table_names()

            # Expected tables from our models
            expected_tables = ['voting_sessions', 'questions', 'teams', 'votes', 'voters', 'question_templates']

            print(f"Existing tables: {existing_tables}")

            missing_tables = [table for table in expected_tables if table not in existing_tables]
            extra_tables = [table for table in existing_tables if table not in expected_tables]

            if missing_tables:
                print(f"Missing tables: {missing_tables}")
            else:
                print("✓ All expected tables exist")

            if extra_tables:
                print(f"Extra tables found: {extra_tables}")

            return existing_tables, missing_tables

        except Exception as e:
            print(f"✗ Error checking tables: {e}")
            return [], []


def create_tables_if_needed(force_recreate=False):
    """Create database tables if they don't exist"""
    app = create_app()

    with app.app_context():
        try:
            if force_recreate:
                print("⚠ Dropping all tables and recreating...")
                db.drop_all()
                db.create_all()
                print("✓ All tables recreated successfully")
            else:
                existing_tables, missing_tables = check_tables_exist()

                if missing_tables:
                    print(f"Creating missing tables: {missing_tables}")
                    db.create_all()
                    print("✓ Missing tables created successfully")
                else:
                    print("✓ All tables already exist, skipping creation")

            return True

        except SQLAlchemyError as e:
            print(f"✗ SQLAlchemy error creating tables: {e}")
            return False
        except Exception as e:
            print(f"✗ Unexpected error creating tables: {e}")
            return False


def init_database(force_recreate=False):
    """Initialize the database with tables and sample data"""
    print("=== Database Initialization ===")

    # Check database connection first
    if not check_database_connection():
        print("Cannot proceed without database connection")
        return False

    # Create tables if needed
    if not create_tables_if_needed(force_recreate):
        print("Failed to create tables")
        return False

    app = create_app()

    with app.app_context():
        try:
            # Create sample question templates if they don't exist
            templates = [
                QuestionTemplate(
                    name="Rating Scale 1-5",
                    description="Rate from 1 (worst) to 5 (best)",
                    question_type="rating",
                    options=['1', '2', '3', '4', '5']
                ),
                QuestionTemplate(
                    name="Yes/No Question",
                    description="Simple yes or no answer",
                    question_type="multiple_choice",
                    options=['Yes', 'No']
                ),
                QuestionTemplate(
                    name="Multiple Choice",
                    description="Choose one option from multiple choices",
                    question_type="multiple_choice",
                    options=['Option A', 'Option B', 'Option C', 'Option D']
                ),
                QuestionTemplate(
                    name="Team Selection",
                    description="Select a team (for Naše firmy competitions)",
                    question_type="team_selection",
                    options=[]
                )
            ]

            templates_added = 0
            for template in templates:
                existing = QuestionTemplate.query.filter_by(name=template.name).first()
                if not existing:
                    db.session.add(template)
                    templates_added += 1
                    print(f"Added template: {template.name}")
                else:
                    print(f"Template already exists: {template.name}")

            if templates_added > 0:
                db.session.commit()
                print(f"✓ {templates_added} new templates added")
            else:
                print("✓ All templates already exist")

            print_database_statistics()
            print("✓ Database initialization completed successfully!")
            return True

        except SQLAlchemyError as e:
            print(f"✗ SQLAlchemy error during initialization: {e}")
            db.session.rollback()
            return False
        except Exception as e:
            print(f"✗ Unexpected error during initialization: {e}")
            db.session.rollback()
            return False


def print_database_statistics():
    """Print current database statistics"""
    try:
        print(f"\n=== Database Statistics ===")
        print(f"Question Templates: {QuestionTemplate.query.count()}")
        print(f"Voting Sessions: {VotingSession.query.count()}")
        print(f"Questions: {Question.query.count()}")
        print(f"Teams: {Team.query.count()}")
        print(f"Voters: {Voter.query.count()}")
        print(f"Votes: {Vote.query.count()}")
    except Exception as e:
        print(f"✗ Error getting database statistics: {e}")


def create_sample_nase_firmy_session():
    """Create a sample 'Naše firmy' voting session for testing"""
    print("=== Creating Sample Session ===")

    app = create_app()

    with app.app_context():
        try:
            # Check if sample session already exists
            existing = VotingSession.query.filter_by(name="Nase firmy 2025").first()
            if existing:
                print("✓ Sample 'Nase firmy 2025' session already exists!")
                print(f"Session ID: {existing.unique_id}")
                print(f"Voting URL: /hlasovani/{existing.unique_id}")
                print(f"QR Code URL: /presentation/{existing.unique_id}")
                return True

            print("Creating sample 'Nase firmy 2025' session...")

            # Create voting session
            session = VotingSession(
                unique_id="655662",
                name="Nase firmy 2025",
                description="Annual company competition",
                started=True,
                ended=False
            )
            db.session.add(session)
            db.session.flush()

            # Add questions (categories)
            categories = ['MASKA', 'KOLA', 'SKELET', 'PLAKAT', 'MARKETING']
            for idx, category in enumerate(categories):
                question = Question(
                    session_id=session.id,
                    text=category,
                    question_type='team_selection',
                    options=[],
                    order_index=idx
                )
                db.session.add(question)

            # Add teams
            teams = ['Tym Alpha', 'Tym Beta', 'Tym Gamma', 'Tym Delta']
            for team_name in teams:
                team = Team(
                    session_id=session.id,
                    name=team_name
                )
                db.session.add(team)

            db.session.commit()
            print("✓ Sample session created successfully!")
            print(f"Session ID: {session.unique_id}")
            print(f"Voting URL: /hlasovani/{session.unique_id}")
            print(f"QR Code URL: /presentation/{session.unique_id}")
            return True

        except SQLAlchemyError as e:
            print(f"✗ SQLAlchemy error creating sample session: {e}")
            db.session.rollback()
            return False
        except Exception as e:
            print(f"✗ Unexpected error creating sample session: {e}")
            db.session.rollback()
            return False


def main():
    """Main function with command line argument handling"""
    parser = argparse.ArgumentParser(description='Initialize the voting application database')
    parser.add_argument('--sample', action='store_true',
                        help='Create sample Nase firmy session')
    parser.add_argument('--force-recreate', action='store_true',
                        help='Drop and recreate all tables (WARNING: destroys existing data)')
    parser.add_argument('--check-only', action='store_true',
                        help='Only check database connection and table status')
    parser.add_argument('--stats', action='store_true',
                        help='Show database statistics only')

    args = parser.parse_args()

    if args.check_only:
        print("=== Database Check ===")
        check_database_connection()
        check_tables_exist()
        return

    if args.stats:
        if check_database_connection():
            app = create_app()
            with app.app_context():
                print_database_statistics()
        return

    if args.force_recreate:
        response = input("⚠ WARNING: This will delete all existing data. Are you sure? (yes/no): ")
        if response.lower() != 'yes':
            print("Operation cancelled")
            return

    # Initialize database
    if not init_database(force_recreate=args.force_recreate):
        print("Database initialization failed")
        sys.exit(1)

    # Create sample session if requested
    if args.sample:
        if not create_sample_nase_firmy_session():
            print("Sample session creation failed")
            sys.exit(1)


if __name__ == '__main__':
    main()