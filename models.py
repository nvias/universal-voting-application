from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()

class QuestionTemplate(db.Model):
    __tablename__ = 'question_templates'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    question_type = db.Column(db.String(50), nullable=False)  # 'multiple_choice', 'rating', 'yes_no', 'ranking', 'team_selection'
    options_json = db.Column(db.Text)  # JSON string of available options
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    questions = db.relationship('Question', backref='template', lazy=True)
    
    @property
    def options(self):
        return json.loads(self.options_json) if self.options_json else []
    
    @options.setter
    def options(self, value):
        self.options_json = json.dumps(value)

class VotingSession(db.Model):
    __tablename__ = 'voting_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    unique_id = db.Column(db.String(10), unique=True, nullable=False)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    started = db.Column(db.Boolean, default=False)
    ended = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    questions = db.relationship('Question', backref='session', lazy=True, cascade='all, delete-orphan')
    teams = db.relationship('Team', backref='session', lazy=True, cascade='all, delete-orphan')
    votes = db.relationship('Vote', backref='session', lazy=True, cascade='all, delete-orphan')
    voters = db.relationship('Voter', backref='session', lazy=True, cascade='all, delete-orphan')

class Question(db.Model):
    __tablename__ = 'questions'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('voting_sessions.id'), nullable=False)
    template_id = db.Column(db.Integer, db.ForeignKey('question_templates.id'), nullable=True)
    text = db.Column(db.Text, nullable=False)
    question_type = db.Column(db.String(50), nullable=False)
    options_json = db.Column(db.Text)
    order_index = db.Column(db.Integer, default=0)
    
    # Relationships
    votes = db.relationship('Vote', backref='question', lazy=True, cascade='all, delete-orphan')
    
    @property
    def options(self):
        return json.loads(self.options_json) if self.options_json else []
    
    @options.setter
    def options(self, value):
        self.options_json = json.dumps(value)

class Team(db.Model):
    __tablename__ = 'teams'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('voting_sessions.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    external_id = db.Column(db.String(100))  # ID from external application
    description = db.Column(db.Text)
    
    # Relationships for votes
    votes_received = db.relationship('Vote', foreign_keys='Vote.team_id', backref='team', lazy=True)
    votes_given = db.relationship('Vote', foreign_keys='Vote.voter_team_id', backref='voter_team', lazy=True)

class Voter(db.Model):
    __tablename__ = 'voters'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('voting_sessions.id'), nullable=False)
    identifier = db.Column(db.String(100), nullable=False)  # Could be IP, session ID, etc.
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.Text)
    first_vote_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_vote_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    votes = db.relationship('Vote', backref='voter', lazy=True)

class Vote(db.Model):
    __tablename__ = 'votes'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('voting_sessions.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False)
    team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=False)  # Team being voted FOR
    voter_id = db.Column(db.Integer, db.ForeignKey('voters.id'), nullable=False)
    voter_team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=True)  # Team that the voter represents
    option_selected = db.Column(db.String(200))  # Selected option text/value
    numeric_value = db.Column(db.Float)  # For rating/numeric questions
    text_value = db.Column(db.Text)  # For text responses
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Unique constraint to prevent duplicate votes (one vote per question per voter)
    __table_args__ = (db.UniqueConstraint('question_id', 'voter_id', name='unique_vote_per_question'),)
