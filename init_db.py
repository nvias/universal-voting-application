#!/usr/bin/env python3
"""
Database initialization script for the voting application.
Run this script to create all database tables and add sample data.
"""

import os
import sys
from datetime import datetime

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from server import create_app
from models import db, VotingSession, Question, Team, Vote, Voter, QuestionTemplate

def init_database():
    """Initialize the database with tables and sample data"""
    app = create_app()
    
    with app.app_context():
        print("Creating database tables...")
        db.create_all()
        
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
        
        for template in templates:
            existing = QuestionTemplate.query.filter_by(name=template.name).first()
            if not existing:
                db.session.add(template)
                print(f"Added template: {template.name}")
        
        db.session.commit()
        print("Database initialized successfully!")
        
        # Print database statistics
        print(f"\nDatabase Statistics:")
        print(f"Question Templates: {QuestionTemplate.query.count()}")
        print(f"Voting Sessions: {VotingSession.query.count()}")
        print(f"Questions: {Question.query.count()}")
        print(f"Teams: {Team.query.count()}")
        print(f"Voters: {Voter.query.count()}")
        print(f"Votes: {Vote.query.count()}")

def create_sample_nase_firmy_session():
    """Create a sample 'Naše firmy' voting session for testing"""
    app = create_app()
    
    with app.app_context():
        # Check if sample session already exists
        existing = VotingSession.query.filter_by(name="Nase firmy 2025").first()
        if existing:
            print("Sample 'Nase firmy 2025' session already exists!")
            return
        
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
        print("Sample session created successfully!")
        print(f"Session ID: {session.unique_id}")
        print(f"Voting URL: /hlasovani/{session.unique_id}")
        print(f"QR Code URL: /presentation/{session.unique_id}")

if __name__ == '__main__':
    # The script is now non-interactive.
    # To create the sample session, run from your host machine:
    # docker-compose exec voting-app python init_db.py --sample
    if len(sys.argv) > 1 and sys.argv[1] == '--sample':
        create_sample_nase_firmy_session()
    else:
        init_database()
