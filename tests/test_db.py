#!/usr/bin/env python3
"""
Test script to verify database connection and functionality
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from server import create_app
from models import db, VotingSession, Question, Team, Vote, Voter, QuestionTemplate
from sqlalchemy import text

def test_database_connection():
    """Test database connection and basic operations"""
    app = create_app()
    
    with app.app_context():
        try:
            # Test database connection
            with db.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            print("✓ Database connection successful")
            
            # Test table creation
            db.create_all()
            print("✓ Database tables created/verified")
            
            # Test sample data insertion
            test_template = QuestionTemplate(
                name="Test Template",
                description="Test template for database verification",
                question_type="rating",
                options=['1', '2', '3', '4', '5']
            )
            
            db.session.add(test_template)
            db.session.commit()
            print("✓ Sample data insertion successful")
            
            # Clean up test data
            db.session.delete(test_template)
            db.session.commit()
            print("✓ Test data cleanup successful")
            
            # Show database stats
            print("\nDatabase Statistics:")
            print(f"  Question Templates: {QuestionTemplate.query.count()}")
            print(f"  Voting Sessions: {VotingSession.query.count()}")
            print(f"  Questions: {Question.query.count()}")
            print(f"  Teams: {Team.query.count()}")
            print(f"  Voters: {Voter.query.count()}")
            print(f"  Votes: {Vote.query.count()}")
            
            return True
            
        except Exception as e:
            print(f"✗ Database test failed: {e}")
            return False

def show_existing_sessions():
    """Show existing voting sessions"""
    app = create_app()
    
    with app.app_context():
        sessions = VotingSession.query.all()
        
        if not sessions:
            print("No voting sessions found")
            return
        
        print("\nExisting Voting Sessions:")
        for session in sessions:
            status = "Active" if session.started and not session.ended else "Inactive"
            if session.ended:
                status = "Ended"
            
            print(f"  ID: {session.unique_id}")
            print(f"  Name: {session.name}")
            print(f"  Status: {status}")
            print(f"  Teams: {len(session.teams)}")
            print(f"  Questions: {len(session.questions)}")
            print(f"  Votes: {len(session.votes)}")
            print(f"  Created: {session.created_at}")
            print(f"  URL: /hlasovani/{session.unique_id}")
            print(f"  QR: /presentation/{session.unique_id}")
            print("-" * 40)

if __name__ == '__main__':
    print("Testing database connection and functionality...\n")
    
    if test_database_connection():
        print("\n" + "="*50)
        show_existing_sessions()
        print("\nDatabase test completed successfully!")
    else:
        print("\nDatabase test failed!")
        sys.exit(1)
        for session in sessions:
            print(f"  ID: {session.unique_id}")
            print(f"    Name: {session.name}")
            print(f"    Teams: {len(session.teams)}")
            print(f"    Questions: {len(session.questions)}")
            print(f"    Votes: {len(session.votes)}")
            print(f"    Voters: {len(session.voters)}")
            print(f"    Started: {session.started}")
            print(f"    Ended: {session.ended}")
            print()

def show_nase_firmy_details():
    """Show details of Nase firmy 2025 session"""
    app = create_app()
    
    with app.app_context():
        session = VotingSession.query.filter_by(name="Nase firmy 2025").first()
        
        if not session:
            print("Nase firmy 2025 session not found")
            return
        
        print(f"\nNase firmy 2025 Details:")
        print(f"  Session ID: {session.unique_id}")
        print(f"  Started: {session.started}")
        print(f"  Ended: {session.ended}")
        
        print(f"\n  Teams ({len(session.teams)}):")
        for team in session.teams:
            print(f"    - {team.name} (ID: {team.id})")
        
        print(f"\n  Questions ({len(session.questions)}):")
        for q in session.questions:
            print(f"    - {q.text} (Type: {q.question_type}, ID: {q.id})")
        
        print(f"\n  Votes ({len(session.votes)}):")
        for vote in session.votes:
            voter_team = Team.query.get(vote.voter_team_id) if vote.voter_team_id else None
            voted_team = Team.query.get(vote.team_id)
            question = Question.query.get(vote.question_id)
            print(f"    - {voter_team.name if voter_team else 'Unknown'} -> {voted_team.name} for {question.text}")
        
        print(f"\n  Voters ({len(session.voters)}):")
        for voter in session.voters:
            print(f"    - Voter {voter.id} ({voter.identifier[:20]}...)")

if __name__ == '__main__':
    print("Testing database connection and functionality...\n")
    
    if test_database_connection():
        print("\n" + "="*50)
        show_existing_sessions()
        show_nase_firmy_details()
    else:
        print("Database test failed. Please check your database configuration.")
        sys.exit(1)
