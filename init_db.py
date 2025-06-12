#!/usr/bin/env python3
"""
Database initialization script for the voting application
"""

from server import create_app
from models import db, QuestionTemplate
import os

def create_sample_templates():
    """Create sample question templates"""
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
            print(f"Created template: {template_data['name']}")
        else:
            print(f"Template already exists: {template_data['name']}")

def main():
    """Initialize the database"""
    # Set environment for database creation
    os.environ.setdefault('FLASK_ENV', 'development')
    
    app = create_app()
    
    with app.app_context():
        print("Creating database tables...")
        db.create_all()
        print("Database tables created successfully!")
        
        print("\nCreating sample question templates...")
        create_sample_templates()
        db.session.commit()
        print("Sample templates created successfully!")
        
        print("\n✅ Database initialization completed!")
        print("\nTo start the application:")
        print("python server.py")
        print("\nOr with environment variables:")
        print("FLASK_ENV=docker python server.py")

if __name__ == '__main__':
    main()
