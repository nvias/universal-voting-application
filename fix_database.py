#!/usr/bin/env python3
"""
Database migration and fix script for voting application
This script handles migration from old schema to new schema with proper fixes
"""

import os
import sys
from datetime import datetime

def fix_database():
    """Fix database schema and migrate existing data"""
    try:
        from server import create_app
        from models import db, VotingSession, Question, Team, Vote, Voter, QuestionTemplate
        
        print("🔧 Starting database migration and fix...")
        
        # Create app with current configuration
        app = create_app()
        
        with app.app_context():
            # Drop all tables and recreate (this is the safest approach for development)
            print("⚠️  Dropping existing tables...")
            db.drop_all()
            
            print("✅ Creating new database schema...")
            db.create_all()
            
            # Create default question templates
            print("📝 Creating default question templates...")
            create_default_templates()
            
            print("🎉 Database migration completed successfully!")
            print("\n📋 Next steps:")
            print("1. Start your application: python server.py")
            print("2. Create voting sessions through the admin interface")
            print("3. Use the new team selection feature in voting")
            
    except Exception as e:
        print(f"❌ Error during database migration: {e}")
        print("\n🔍 Troubleshooting steps:")
        print("1. Check your database connection string in .env or environment variables")
        print("2. Ensure PostgreSQL is running")
        print("3. Verify you have proper database permissions")
        sys.exit(1)

def create_default_templates():
    """Create default question templates"""
    from models import db, QuestionTemplate
    
    templates = [
        {
            'name': 'Rating Scale 1-5',
            'description': 'Rate from 1 (worst) to 5 (best)',
            'question_type': 'rating',
            'options': ['1', '2', '3', '4', '5']
        },
        {
            'name': 'Rating Scale 1-10',
            'description': 'Rate from 1 (worst) to 10 (best)',
            'question_type': 'rating',
            'options': ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10']
        },
        {
            'name': 'Yes/No Question',
            'description': 'Simple yes or no answer',
            'question_type': 'multiple_choice',
            'options': ['Yes', 'No']
        },
        {
            'name': 'Agree/Disagree Scale',
            'description': 'Level of agreement',
            'question_type': 'multiple_choice',
            'options': ['Strongly Disagree', 'Disagree', 'Neutral', 'Agree', 'Strongly Agree']
        },
        {
            'name': 'Quality Rating',
            'description': 'Quality assessment',
            'question_type': 'multiple_choice',
            'options': ['Poor', 'Fair', 'Good', 'Very Good', 'Excellent']
        },
        {
            'name': 'Multiple Choice A-D',
            'description': 'Choose one option from four choices',
            'question_type': 'multiple_choice',
            'options': ['Option A', 'Option B', 'Option C', 'Option D']
        },
        {
            'name': 'Naše firmy',
            'description': 'Competition voting template where teams vote for other teams in specific categories. Each team selects one team per category (MASKA, KOLA, SKELET, PLAKÁT, MARKETING).',
            'question_type': 'team_selection',
            'options': []  # Options will be the teams themselves
        }
    ]
    
    for template_data in templates:
        existing = QuestionTemplate.query.filter_by(name=template_data['name']).first()
        if not existing:
            template = QuestionTemplate(
                name=template_data['name'],
                description=template_data['description'],
                question_type=template_data['question_type'],
                options=template_data['options']
            )
            db.session.add(template)
            print(f"  ✅ Created template: {template_data['name']}")
        else:
            print(f"  ⚡ Template already exists: {template_data['name']}")
    
    db.session.commit()

def create_sample_voting():
    """Create a sample voting session for testing"""
    from models import db, VotingSession, Question, Team
    from api_blueprint import generate_unique_id
    
    print("\n📊 Creating sample voting session...")
    
    # Create sample voting session
    session = VotingSession(
        unique_id=generate_unique_id(),
        name="Sample Team Rating",
        description="Sample voting session for testing the new interface"
    )
    db.session.add(session)
    db.session.flush()
    
    # Add sample teams
    team_names = ["Development Team", "Design Team", "Marketing Team", "Sales Team"]
    for team_name in team_names:
        team = Team(
            session_id=session.id,
            name=team_name,
            external_id=team_name.lower().replace(" ", "_")
        )
        db.session.add(team)
    
    # Add sample questions
    questions_data = [
        {"text": "How would you rate the team's communication?", "type": "rating"},
        {"text": "Did the team meet project deadlines?", "type": "multiple_choice"},
        {"text": "Overall team performance", "type": "rating"}
    ]
    
    for idx, q_data in enumerate(questions_data):
        if q_data["type"] == "rating":
            options = ['1', '2', '3', '4', '5']
        else:
            options = ['Yes', 'No', 'Partially']
            
        question = Question(
            session_id=session.id,
            text=q_data["text"],
            question_type=q_data["type"],
            options=options,
            order_index=idx
        )
        db.session.add(question)
    
    db.session.commit()
    
    print(f"  ✅ Sample voting created with ID: {session.unique_id}")
    print(f"  🗳️  Voting URL: /hlasovani/{session.unique_id}")
    print(f"  📱 QR Code URL: /presentation/{session.unique_id}")

def create_nase_firmy_sample():
    """Create a sample Naše firmy voting session"""
    from models import db, VotingSession, Question, Team
    from api_blueprint import generate_unique_id
    
    print("\n🏆 Creating sample 'Naše firmy' voting session...")
    
    # Create Naše firmy voting session
    session = VotingSession(
        unique_id=generate_unique_id(),
        name="Naše firmy 2025",
        description="Sample competition voting - teams vote for other teams in specific categories"
    )
    db.session.add(session)
    db.session.flush()
    
    # Add sample teams
    team_names = ["Tým Alpha", "Tým Beta", "Tým Gamma", "Tým Delta", "Tým Omega"]
    for team_name in team_names:
        team = Team(
            session_id=session.id,
            name=team_name,
            external_id=team_name.lower().replace(" ", "_").replace("ý", "y")
        )
        db.session.add(team)
    
    # Add Naše firmy categories
    categories = ["MASKA", "KOLA", "SKELET", "PLAKÁT", "MARKETING"]
    
    for idx, category in enumerate(categories):
        question = Question(
            session_id=session.id,
            text=category,
            question_type="team_selection",
            options=[],  # Teams will be the options
            order_index=idx
        )
        db.session.add(question)
    
    db.session.commit()
    
def create_nase_firmy_sample():
    """Create a sample Naše firmy voting session"""
    from models import db, VotingSession, Question, Team
    import random
    
    def generate_unique_id():
        """Generate a unique 6-digit ID for voting sessions"""
        while True:
            unique_id = str(random.randint(100000, 999999))
            if not VotingSession.query.filter_by(unique_id=unique_id).first():
                return unique_id
    
    print("\n🏆 Creating sample 'Naše firmy' voting session...")
    
    # Create Naše firmy voting session
    session = VotingSession(
        unique_id=generate_unique_id(),
        name="Naše firmy 2025",
        description="Sample competition voting - teams vote for other teams in specific categories"
    )
    db.session.add(session)
    db.session.flush()
    
    # Add sample teams
    team_names = ["Tým Alpha", "Tým Beta", "Tým Gamma", "Tým Delta", "Tým Omega"]
    for team_name in team_names:
        team = Team(
            session_id=session.id,
            name=team_name,
            external_id=team_name.lower().replace(" ", "_").replace("ý", "y")
        )
        db.session.add(team)
    
    # Add Naše firmy categories
    categories = ["MASKA", "KOLA", "SKELET", "PLAKÁT", "MARKETING"]
    
    for idx, category in enumerate(categories):
        question = Question(
            session_id=session.id,
            text=category,
            question_type="team_selection",
            options=[],  # Teams will be the options
            order_index=idx
        )
        db.session.add(question)
    
    db.session.commit()
    
    print(f"  ✅ Naše firmy voting created with ID: {session.unique_id}")
    print(f"  🗳️  Voting URL: /hlasovani/{session.unique_id}")
    print(f"  📱 QR Code URL: /presentation/{session.unique_id}")
    print(f"  📊 Categories: {', '.join(categories)}")
    print(f"  👥 Teams: {', '.join(team_names)}")unique_id}")
    print(f"  🗳️  Voting URL: /hlasovani/{session.unique_id}")
    print(f"  📱 QR Code URL: /presentation/{session.unique_id}")
    print(f"  📊 Categories: {', '.join(categories)}")
    print(f"  👥 Teams: {', '.join(team_names)}")

def check_database_health():
    """Check if database is properly configured and accessible"""
    try:
        from server import create_app
        from models import db
        
        app = create_app()
        with app.app_context():
            # Try to connect to database
            db.engine.execute('SELECT 1')
            print("✅ Database connection: OK")
            
            # Check if tables exist
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            
            expected_tables = ['voting_sessions', 'questions', 'teams', 'votes', 'voters', 'question_templates']
            missing_tables = [t for t in expected_tables if t not in tables]
            
            if missing_tables:
                print(f"⚠️  Missing tables: {', '.join(missing_tables)}")
                return False
            else:
                print("✅ All required tables exist")
                return True
                
    except Exception as e:
        print(f"❌ Database health check failed: {e}")
        return False

def main():
    """Main function with interactive options"""
    print("🗳️  Voting System Database Migration Tool")
    print("=" * 50)
    
    while True:
        print("\nSelect an option:")
        print("1. Fix/Reset database (⚠️  This will delete all existing data)")
        print("2. Check database health")
        print("3. Create sample voting sessions")
        print("4. Create sample 'Naše firmy' voting")
        print("5. Exit")
        
        choice = input("\nEnter your choice (1-5): ").strip()
        
        if choice == '1':
            confirm = input("\n⚠️  This will DELETE ALL existing data. Continue? (yes/no): ").strip().lower()
            if confirm in ['yes', 'y']:
                fix_database()
            else:
                print("Operation cancelled.")
        
        elif choice == '2':
            print("\n🔍 Checking database health...")
            if check_database_health():
                print("🎉 Database is healthy!")
            else:
                print("💔 Database has issues. Consider running option 1 to fix.")
        
        elif choice == '3':
            if check_database_health():
                create_sample_voting()
            else:
                print("❌ Database not ready. Fix database first (option 1).")
        
        elif choice == '4':
            if check_database_health():
                create_nase_firmy_sample()
            else:
                print("❌ Database not ready. Fix database first (option 1).")
        
        elif choice == '5':
            print("👋 Goodbye!")
            break
        
        else:
            print("❌ Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
