from flask import Blueprint, request, jsonify
from models import db, VotingSession, Question, Team, Vote, Voter, QuestionTemplate
from datetime import datetime
import random
import json

api_bp = Blueprint('api', __name__, url_prefix='/api/v1')

def generate_unique_id():
    """Generate a unique 6-digit ID for voting sessions"""
    while True:
        unique_id = str(random.randint(100000, 999999))
        if not VotingSession.query.filter_by(unique_id=unique_id).first():
            return unique_id

@api_bp.route('/health', methods=['GET'])
def health_check():
    """API health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '1.0'
    })

@api_bp.route('/templates', methods=['GET'])
def get_question_templates():
    """Get all question templates"""
    templates = QuestionTemplate.query.all()
    return jsonify([{
        'id': t.id,
        'name': t.name,
        'description': t.description,
        'question_type': t.question_type,
        'options': t.options
    } for t in templates])

@api_bp.route('/templates', methods=['POST'])
def create_question_template():
    """Create a new question template"""
    data = request.get_json()
    
    if not data or not all(k in data for k in ['name', 'question_type']):
        return jsonify({'error': 'Missing required fields: name, question_type'}), 400
    
    template = QuestionTemplate(
        name=data['name'],
        description=data.get('description'),
        question_type=data['question_type'],
        options=data.get('options', [])
    )
    
    db.session.add(template)
    db.session.commit()
    
    return jsonify({
        'id': template.id,
        'message': 'Template created successfully'
    }), 201

@api_bp.route('/voting', methods=['POST'])
def create_voting_session():
    """Create a new voting session from external application"""
    try:
        data = request.get_json(force=True)
        
        if not data or 'name' not in data:
            return jsonify({'error': 'Missing required field: name'}), 400
        
        # Create voting session
        session = VotingSession(
            unique_id=generate_unique_id(),
            name=data['name'],
            description=data.get('description', '')
        )
        db.session.add(session)
        db.session.flush()  # Get the ID
        
        # Add questions
        questions_data = data.get('questions', [])
        for idx, q_data in enumerate(questions_data):
            question = Question(
                session_id=session.id,
                template_id=q_data.get('template_id'),
                text=q_data['text'],
                question_type=q_data.get('question_type', 'multiple_choice'),
                options=q_data.get('options', []),
                order_index=idx
            )
            db.session.add(question)
        
        # Add teams
        teams_data = data.get('teams', [])
        for team_data in teams_data:
            team = Team(
                session_id=session.id,
                name=team_data['name'],
                external_id=team_data.get('external_id'),
                description=team_data.get('description')
            )
            db.session.add(team)
        
        db.session.commit()
        
        return jsonify({
            'id': session.unique_id,
            'message': 'Voting session created successfully',
            'voting_url': f'/hlasovani/{session.unique_id}',
            'qr_url': f'/presentation/{session.unique_id}'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@api_bp.route('/voting/<voting_id>', methods=['GET'])
def get_voting_session(voting_id):
    """Get voting session details"""
    session = VotingSession.query.filter_by(unique_id=voting_id).first()
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
        'name': t.name,
        'external_id': t.external_id,
        'description': t.description
    } for t in session.teams]
    
    return jsonify({
        'id': session.unique_id,
        'name': session.name,
        'description': session.description,
        'started': session.started,
        'ended': session.ended,
        'created_at': session.created_at.isoformat(),
        'questions': questions,
        'teams': teams
    })

@api_bp.route('/voting/<voting_id>/teams', methods=['POST'])
def update_teams(voting_id):
    """Update teams for a voting session"""
    session = VotingSession.query.filter_by(unique_id=voting_id).first()
    if not session:
        return jsonify({'error': 'Voting session not found'}), 404
    
    data = request.get_json()
    teams_data = data.get('teams', [])
    
    try:
        # Remove existing teams
        Team.query.filter_by(session_id=session.id).delete()
        
        # Add new teams
        for team_data in teams_data:
            team = Team(
                session_id=session.id,
                name=team_data['name'],
                external_id=team_data.get('external_id'),
                description=team_data.get('description')
            )
            db.session.add(team)
        
        db.session.commit()
        return jsonify({'message': 'Teams updated successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@api_bp.route('/voting/<voting_id>/start', methods=['POST'])
def start_voting_session(voting_id):
    """Start a voting session"""
    session = VotingSession.query.filter_by(unique_id=voting_id).first()
    if not session:
        return jsonify({'error': 'Voting session not found'}), 404
    
    session.started = True
    session.updated_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify({'message': f'Voting session {voting_id} started successfully'})

@api_bp.route('/voting/<voting_id>/stop', methods=['POST'])
def stop_voting_session(voting_id):
    """Stop a voting session"""
    session = VotingSession.query.filter_by(unique_id=voting_id).first()
    if not session:
        return jsonify({'error': 'Voting session not found'}), 404
    
    session.ended = True
    session.updated_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify({'message': f'Voting session {voting_id} stopped successfully'})

@api_bp.route('/voting/<voting_id>/vote', methods=['POST'])
def submit_vote(voting_id):
    """Submit a vote"""
    session = VotingSession.query.filter_by(unique_id=voting_id).first()
    if not session:
        return jsonify({'error': 'Voting session not found'}), 404
    
    if not session.started or session.ended:
        return jsonify({'error': 'Voting session is not active'}), 400
    
    data = request.get_json()
    required_fields = ['question_id', 'team_id', 'voter_identifier']
    if not all(field in data for field in required_fields):
        return jsonify({'error': f'Missing required fields: {required_fields}'}), 400
    
    try:
        # Get or create voter
        voter = Voter.query.filter_by(
            session_id=session.id, 
            identifier=data['voter_identifier']
        ).first()
        
        if not voter:
            voter = Voter(
                session_id=session.id,
                identifier=data['voter_identifier'],
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent')
            )
            db.session.add(voter)
            db.session.flush()
        
        # Check if vote already exists
        existing_vote = Vote.query.filter_by(
            question_id=data['question_id'],
            voter_id=voter.id
        ).first()
        
        if existing_vote:
            return jsonify({'error': 'Vote already submitted for this question'}), 400
        
        # Create vote
        vote = Vote(
            session_id=session.id,
            question_id=data['question_id'],
            team_id=data['team_id'],
            voter_id=voter.id,
            voter_team_id=data.get('voter_team_id'),  # Team that the voter represents
            option_selected=data.get('option_selected'),
            numeric_value=data.get('numeric_value'),
            text_value=data.get('text_value')
        )
        
        db.session.add(vote)
        voter.last_vote_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({'message': 'Vote submitted successfully'}), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@api_bp.route('/voting/<voting_id>/results', methods=['GET'])
def get_voting_results(voting_id):
    """Get voting results with flexible aggregation"""
    session = VotingSession.query.filter_by(unique_id=voting_id).first()
    if not session:
        return jsonify({'error': 'Voting session not found'}), 404
    
    # Basic aggregation - can be customized based on requirements
    results = []
    
    for question in session.questions:
        question_results = {
            'question_id': question.id,
            'question_text': question.text,
            'question_type': question.question_type,
            'teams': {}
        }
        
        for team in session.teams:
            team_votes = Vote.query.filter_by(
                question_id=question.id,
                team_id=team.id
            ).all()
            
            if question.question_type == 'rating':
                avg_rating = sum(v.numeric_value for v in team_votes if v.numeric_value) / len(team_votes) if team_votes else 0
                question_results['teams'][team.name] = {
                    'vote_count': len(team_votes),
                    'average_rating': round(avg_rating, 2)
                }
            else:
                # Count votes by option
                option_counts = {}
                for vote in team_votes:
                    option = vote.option_selected or 'no_option'
                    option_counts[option] = option_counts.get(option, 0) + 1
                
                question_results['teams'][team.name] = {
                    'vote_count': len(team_votes),
                    'option_counts': option_counts
                }
        
        results.append(question_results)
    
    return jsonify({
        'session_id': voting_id,
        'session_name': session.name,
        'total_voters': len(session.voters),
        'results': results
    })

@api_bp.route('/voting/<voting_id>/results/nase-firmy', methods=['GET'])
def get_nase_firmy_results(voting_id):
    """Get specialized results for 'Naše firmy' template"""
    session = VotingSession.query.filter_by(unique_id=voting_id).first()
    if not session:
        return jsonify({'error': 'Voting session not found'}), 404
    
    # Check if this session uses "Naše firmy" template
    nase_firmy_questions = [q for q in session.questions if q.question_type == 'team_selection']
    if not nase_firmy_questions:
        return jsonify({'error': 'This session does not use Naše firmy template'}), 400
    
    categories = {
        'MASKA': [],
        'KOLA': [],
        'SKELET': [],
        'PLAKÁT': [],
        'MARKETING': []
    }
    
    # Group questions by category
    category_questions = {}
    for question in nase_firmy_questions:
        category = question.text.upper()
        if category in categories:
            category_questions[category] = question
    
    results = {}
    
    for category, question in category_questions.items():
        # Get all votes for this category
        votes = Vote.query.filter_by(question_id=question.id).all()
        
        # Count votes for each team (including self-votes)
        team_votes = {}
        voting_teams = {}  # Teams that gave votes
        self_votes = {}  # Track self-votes separately
        
        for vote in votes:
            voted_team = Team.query.get(vote.team_id)
            voter_team = Team.query.get(vote.voter_team_id) if vote.voter_team_id else None
            
            if voted_team.name not in team_votes:
                team_votes[voted_team.name] = {
                    'votes': 0,
                    'voting_teams': [],
                    'self_votes': 0
                }
            
            team_votes[voted_team.name]['votes'] += 1
            if voter_team:
                team_votes[voted_team.name]['voting_teams'].append(voter_team.name)
                
                # Track self-votes
                if voter_team.id == voted_team.id:
                    team_votes[voted_team.name]['self_votes'] += 1
        
        # Find team with most votes
        if team_votes:
            winner = max(team_votes.items(), key=lambda x: x[1]['votes'])
            results[category] = {
                'winning_team': winner[0],
                'votes_received': winner[1]['votes'],
                'voting_teams': list(set(winner[1]['voting_teams'])),  # Remove duplicates
                'self_votes': winner[1]['self_votes']
            }
        else:
            results[category] = {
                'winning_team': None,
                'votes_received': 0,
                'voting_teams': [],
                'self_votes': 0
            }
    
    return jsonify({
        'session_id': voting_id,
        'session_name': session.name,
        'template': 'Naše firmy',
        'results': results
    })

@api_bp.route('/voting', methods=['GET'])
def get_all_voting_sessions():
    """Get all voting sessions"""
    sessions = VotingSession.query.all()
    return jsonify([{
        'id': s.unique_id,
        'name': s.name,
        'started': s.started,
        'ended': s.ended,
        'created_at': s.created_at.isoformat(),
        'question_count': len(s.questions),
        'team_count': len(s.teams),
        'vote_count': len(s.votes)
    } for s in sessions])

# Error handlers
@api_bp.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@api_bp.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return jsonify({'error': 'Internal server error'}), 500
