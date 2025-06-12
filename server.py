from flask import Flask, render_template, request, jsonify, make_response, redirect
from flask_migrate import Migrate
from flask_cors import CORS
import os
from datetime import datetime

# Import configurations and models
from config import config
from models import db, VotingSession, Question, Team, Vote, Voter, QuestionTemplate
from api_blueprint import api_bp

def create_app(config_name=None):
    """Application factory pattern"""
    app = Flask(__name__, template_folder="./site")
    
    # Configuration
    config_name = config_name or os.environ.get('FLASK_ENV', 'default')
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    migrate = Migrate(app, db)
    CORS(app, origins=app.config['CORS_ORIGINS'])
    
    # Register blueprints
    app.register_blueprint(api_bp)
    
    return app

app = create_app()

# Default route
@app.route('/')
def home():
    return render_template('admin.html')

# Admin functionality (legacy support)
@app.route('/create_voting', methods=['POST', 'GET']) 
def create_voting():
    """Legacy endpoint - now uses database"""
    try:
        data = request.get_json()
        
        if not data or 'teams' not in data or 'questions' not in data:
            return jsonify({'error': 'Invalid request format'}), 400
        
        # Create voting session
        from api_blueprint import generate_unique_id
        session = VotingSession(
            unique_id=generate_unique_id(),
            name=data.get("name", "Unnamed Session")
        )
        db.session.add(session)
        db.session.flush()
        
        # Add questions
        for idx, question_text in enumerate(data['questions']):
            question = Question(
                session_id=session.id,
                text=question_text,
                question_type='rating',
                options=['1', '2', '3', '4', '5'],
                order_index=idx
            )
            db.session.add(question)
        
        # Add teams
        for team_data in data['teams']:
            team_name = list(team_data.keys())[0]  # Get team name from legacy format
            team = Team(
                session_id=session.id,
                name=team_name
            )
            db.session.add(team)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Voting pool saved',
            'id': session.unique_id
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/get_votings', methods=['GET'])
def get_votings():
    """Get all voting sessions - updated for database"""
    sessions = VotingSession.query.all()
    result = {}
    
    for session in sessions:
        teams_data = []
        for team in session.teams:
            team_questions = {}
            for question in session.questions:
                votes = Vote.query.filter_by(team_id=team.id, question_id=question.id).count()
                team_questions[str(question.order_index + 1)] = votes
            teams_data.append({team.name: [team_questions]})
        
        result[session.unique_id] = {
            'unique_id': session.unique_id,
            'started': session.started,
            'name': session.name,
            'teams': teams_data,
            'questions': [q.text for q in session.questions],
            'created_at': session.created_at.strftime("%Y-%m-%d %H:%M:%S")
        }
    
    return jsonify(result)

@app.route('/get_voting/<votingid>', methods=['GET'])
def get_voting(votingid):
    """Get specific voting session"""
    session = VotingSession.query.filter_by(unique_id=votingid).first()
    if not session:
        return jsonify({'error': 'Voting session not found'}), 404
    
    # Build legacy format response
    teams_data = []
    for team in session.teams:
        team_questions = {}
        for question in session.questions:
            votes = Vote.query.filter_by(team_id=team.id, question_id=question.id).count()
            team_questions[str(question.order_index + 1)] = votes
        teams_data.append({team.name: [team_questions]})
    
    voting_data = {
        'unique_id': session.unique_id,
        'started': session.started,
        'name': session.name,
        'teams': teams_data,
        'questions': [q.text for q in session.questions],
        'created_at': session.created_at.strftime("%Y-%m-%d %H:%M:%S")
    }
    
    return jsonify(voting_data)

@app.route('/admin', methods=['POST', 'GET']) 
def process_login():
    """Process admin login"""
    data = request.form.to_dict(flat=False)
    resp = make_response(render_template('admin.html'))
    resp.set_cookie('login', str(data["name"][0]), httponly=False)
    resp.set_cookie('password', str(data["pass"][0]), httponly=False)
    return resp

@app.route('/start_voting/<voting_id>', methods=['POST'])
def start_voting(voting_id):
    """Start voting session"""
    session = VotingSession.query.filter_by(unique_id=voting_id).first()
    if not session:
        return jsonify({"error": "Voting not found"}), 404
    
    session.started = True
    session.updated_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify({"message": f"Voting {voting_id} has started!"})

@app.route('/stop_voting/<voting_id>', methods=['POST'])
def stop_voting(voting_id):
    """Stop voting session"""
    session = VotingSession.query.filter_by(unique_id=voting_id).first()
    if not session:
        return jsonify({"error": "Voting not found"}), 404
    
    session.ended = True
    session.updated_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify({"message": f"Voting {voting_id} has been stopped!"})

@app.route('/login')
def admin_login():
    """Admin login page"""
    return render_template('login.html')

@app.route('/api/config')
def get_app_config():
    """Get application configuration for frontend"""
    return jsonify({
        'app_url': app.config.get('APP_URL', request.host_url.rstrip('/'))
    })

@app.route('/presentation/<id>')
def projected_site(id):
    """QR code presentation page"""
    session = VotingSession.query.filter_by(unique_id=id).first()
    if not session:
        return "Voting session not found", 404
    
    return render_template('qr.html', voting_id=id, session_name=session.name)

@app.route('/hlasovani/<voteid>')
def voting_site_menu(voteid):
    """Voting page for users"""
    session = VotingSession.query.filter_by(unique_id=voteid).first()
    if not session:
        return "Voting session not found", 404
    
    if not session.started or session.ended:
        return "Voting session is not active", 400
    
    return render_template('voting.html')

# API endpoint to get voting data for frontend
@app.route('/api/voting-data/<voteid>')
def get_voting_data_for_frontend(voteid):
    """Get voting session data for the frontend voting interface"""
    session = VotingSession.query.filter_by(unique_id=voteid).first()
    if not session:
        return jsonify({'error': 'Voting session not found'}), 404
    
    questions = [{
        'id': q.id,
        'text': q.text,
        'question_type': q.question_type,
        'options': q.options,
        'order_index': q.order_index
    } for q in session.questions]
    
    teams = [{
        'id': t.id,
        'name': t.name
    } for t in session.teams]
    
    return jsonify({
        'session': {
            'id': session.unique_id,
            'name': session.name,
            'started': session.started,
            'ended': session.ended
        },
        'questions': questions,
        'teams': teams
    })

# API endpoint to submit votes from frontend
@app.route('/api/submit-vote/<voteid>', methods=['POST'])
def submit_vote_frontend(voteid):
    """Submit vote from frontend"""
    session = VotingSession.query.filter_by(unique_id=voteid).first()
    if not session:
        return jsonify({'error': 'Voting session not found'}), 404
    
    if not session.started or session.ended:
        return jsonify({'error': 'Voting session is not active'}), 400
    
    data = request.get_json()
    
    try:
        # Create voter identifier from IP and user agent
        voter_identifier = f"{request.remote_addr}_{hash(request.headers.get('User-Agent', ''))}"
        
        # Get or create voter
        voter = Voter.query.filter_by(
            session_id=session.id, 
            identifier=voter_identifier
        ).first()
        
        if not voter:
            voter = Voter(
                session_id=session.id,
                identifier=voter_identifier,
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent')
            )
            db.session.add(voter)
            db.session.flush()
        
        # Process votes for each question
        votes_submitted = 0
        for vote_data in data.get('votes', []):
            question_id = vote_data.get('question_id')
            team_id = vote_data.get('team_id')
            voter_team_id = vote_data.get('voter_team_id')  # Team that voter represents
            
            # Check if vote already exists
            existing_vote = Vote.query.filter_by(
                question_id=question_id,
                voter_id=voter.id
            ).first()
            
            if existing_vote:
                continue  # Skip if already voted
            
            # Create vote
            vote = Vote(
                session_id=session.id,
                question_id=question_id,
                team_id=team_id,
                voter_id=voter.id,
                voter_team_id=voter_team_id,
                option_selected=vote_data.get('option_selected'),
                numeric_value=vote_data.get('numeric_value'),
                text_value=vote_data.get('text_value')
            )
            
            db.session.add(vote)
            votes_submitted += 1
        
        voter.last_vote_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': f'{votes_submitted} votes submitted successfully',
            'votes_submitted': votes_submitted
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Database initialization
@app.cli.command()
def init_db():
    """Initialize the database with tables and sample data"""
    db.create_all()
    
    # Create sample question templates
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
        )
    ]
    
    for template in templates:
        existing = QuestionTemplate.query.filter_by(name=template.name).first()
        if not existing:
            db.session.add(template)
    
    db.session.commit()
    print("Database initialized successfully!")

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)
