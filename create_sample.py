#!/usr/bin/env python3
"""
Create sample 'Nase firmy 2025' session
"""

import sys
sys.path.insert(0, '.')

from server import create_app
from models import db, VotingSession, Question, Team

def create_sample():
    app = create_app()
    with app.app_context():
        # Check if sample session exists
        existing = VotingSession.query.filter_by(name='Nase firmy 2025').first()
        if existing:
            print(f'Sample session already exists! ID: {existing.unique_id}')
            return existing.unique_id
        
        print('Creating sample "Nase firmy 2025" session...')
        
        # Create voting session
        session = VotingSession(
            unique_id='655662',
            name='Nase firmy 2025',
            description='Annual company competition',
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
        print('Sample session created successfully!')
        print(f'Session ID: {session.unique_id}')
        print(f'Voting URL: http://localhost:5000/hlasovani/{session.unique_id}')
        print(f'QR Code URL: http://localhost:5000/presentation/{session.unique_id}')
        
        return session.unique_id

if __name__ == '__main__':
    create_sample()
