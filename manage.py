#!/usr/bin/env python3
"""
Management script for the voting application
"""

import click
from flask.cli import with_appcontext
from server import create_app
from models import db, QuestionTemplate
import os

@click.group()
def cli():
    """Voting System Management Commands"""
    pass

@cli.command()
@click.option('--sample-data', is_flag=True, help='Include sample question templates')
def init_db(sample_data):
    """Initialize the database"""
    app = create_app()
    with app.app_context():
        click.echo('Creating database tables...')
        db.create_all()
        click.echo('✅ Database tables created!')
        
        if sample_data:
            from init_db import create_sample_templates
            click.echo('Creating sample templates...')
            create_sample_templates()
            db.session.commit()
            click.echo('✅ Sample templates created!')

@cli.command()
@click.argument('name')
@click.option('--description', default='', help='Template description')
@click.option('--type', 'question_type', default='multiple_choice', 
              type=click.Choice(['rating', 'multiple_choice', 'yes_no']),
              help='Question type')
@click.option('--options', default='', help='Comma-separated options')
def create_template(name, description, question_type, options):
    """Create a new question template"""
    app = create_app()
    with app.app_context():
        # Parse options
        if options:
            option_list = [opt.strip() for opt in options.split(',')]
        elif question_type == 'rating':
            option_list = ['1', '2', '3', '4', '5']
        elif question_type == 'yes_no':
            option_list = ['Yes', 'No']
        else:
            option_list = ['Option A', 'Option B', 'Option C']
        
        template = QuestionTemplate(
            name=name,
            description=description,
            question_type=question_type,
            options=option_list
        )
        
        db.session.add(template)
        db.session.commit()
        
        click.echo(f'✅ Template "{name}" created with ID {template.id}')

@cli.command()
def list_templates():
    """List all question templates"""
    app = create_app()
    with app.app_context():
        templates = QuestionTemplate.query.all()
        
        if not templates:
            click.echo('No templates found.')
            return
        
        click.echo('\nQuestion Templates:')
        click.echo('-' * 60)
        for t in templates:
            click.echo(f'ID: {t.id}')
            click.echo(f'Name: {t.name}')
            click.echo(f'Type: {t.question_type}')
            click.echo(f'Options: {", ".join(t.options)}')
            click.echo('-' * 60)

@cli.command()
@click.option('--host', default='0.0.0.0', help='Host to bind to')
@click.option('--port', default=5000, help='Port to bind to')
@click.option('--debug', is_flag=True, help='Enable debug mode')
def run(host, port, debug):
    """Run the application"""
    app = create_app()
    app.run(host=host, port=port, debug=debug)

@cli.command()
def reset_db():
    """Reset the database (WARNING: This will delete all data!)"""
    if click.confirm('This will delete all data. Are you sure?'):
        app = create_app()
        with app.app_context():
            db.drop_all()
            db.create_all()
            click.echo('✅ Database reset completed!')

@cli.command()
def check_health():
    """Check application health"""
    try:
        app = create_app()
        with app.app_context():
            # Test database connection
            result = db.session.execute(db.text('SELECT 1')).fetchone()
            click.echo('✅ Database connection: OK')
            
            # Check tables exist
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            expected_tables = ['voting_sessions', 'questions', 'teams', 'votes', 'voters', 'question_templates']
            missing_tables = [t for t in expected_tables if t not in tables]
            
            if missing_tables:
                click.echo(f'❌ Missing tables: {", ".join(missing_tables)}')
                click.echo('Run "python manage.py init-db" to create tables')
            else:
                click.echo('✅ Database tables: OK')
                
            click.echo('✅ Application health check passed!')
                
    except Exception as e:
        click.echo(f'❌ Health check failed: {e}')

if __name__ == '__main__':
    cli()
