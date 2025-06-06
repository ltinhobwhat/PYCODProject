from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime
import json

db = SQLAlchemy(session_options={'autocommit': False, 'autoflush': False})

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)
    
    # Progress tracking
    total_score = db.Column(db.Integer, default=0)
    games_completed = db.Column(db.Integer, default=0)
    current_level = db.Column(db.Integer, default=1)
    
    # Relationships
    game_progress = db.relationship('GameProgress', backref='user', lazy=True, cascade='all, delete-orphan')
    achievements = db.relationship('UserAchievement', backref='user', lazy=True, cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_progress_percentage(self):
        """Calculate overall progress percentage"""
        total_games = 6  # pswd, quiz, vigenere, hashgame, sqlinjector, sqldefender
        return min((self.games_completed / total_games) * 100, 100)
    
    def get_rank(self):
        """Get user's rank based on total score"""
        users_with_higher_score = User.query.filter(User.total_score > self.total_score).count()
        return users_with_higher_score + 1
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'total_score': self.total_score,
            'games_completed': self.games_completed,
            'progress_percentage': self.get_progress_percentage(),
            'rank': self.get_rank(),
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class GameProgress(db.Model):
    """Track individual game progress and scores"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    game_name = db.Column(db.String(50), nullable=False)  # pswd, quiz, vigenere, etc.
    
    # Progress metrics
    is_completed = db.Column(db.Boolean, default=False)
    best_score = db.Column(db.Integer, default=0)
    total_attempts = db.Column(db.Integer, default=0)
    completion_time = db.Column(db.Integer, default=0)  # in seconds
    current_level = db.Column(db.Integer, default=1)
    
    # Timestamps
    first_attempt = db.Column(db.DateTime, default=datetime.utcnow)
    last_attempt = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)
    
    # Additional game-specific data
    session_data = db.Column(db.JSON, default={})
    
    __table_args__ = (
        db.UniqueConstraint('user_id', 'game_name', name='unique_user_game'),
    )
    
    def update_progress(self, score=None, completed=None, level=None, session_data=None):
        """Update game progress"""
        self.total_attempts += 1
        self.last_attempt = datetime.utcnow()
        
        if score is not None and score > self.best_score:
            self.best_score = score
            
        if level is not None:
            self.current_level = level
            
        if completed and not self.is_completed:
            self.is_completed = True
            self.completed_at = datetime.utcnow()
            # Calculate completion time from first attempt
            if self.first_attempt:
                time_diff = datetime.utcnow() - self.first_attempt
                self.completion_time = int(time_diff.total_seconds())
                
        if session_data:
            self.session_data = session_data
            
    def to_dict(self):
        return {
            'game_name': self.game_name,
            'is_completed': self.is_completed,
            'best_score': self.best_score,
            'total_attempts': self.total_attempts,
            'completion_time': self.completion_time,
            'current_level': self.current_level,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'last_attempt': self.last_attempt.isoformat() if self.last_attempt else None
        }

class Achievement(db.Model):
    """Define available achievements"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=False)
    icon = db.Column(db.String(50), default='🏆')
    points = db.Column(db.Integer, default=10)
    condition_type = db.Column(db.String(50), nullable=False)  # score, completion, time, etc.
    condition_value = db.Column(db.JSON, nullable=False)  # achievement criteria
    
    def check_condition(self, user):
        """Check if user meets achievement condition"""
        if self.condition_type == 'complete_game':
            game_name = self.condition_value.get('game_name')
            progress = GameProgress.query.filter_by(user_id=user.id, game_name=game_name).first()
            return progress and progress.is_completed
            
        elif self.condition_type == 'total_score':
            return user.total_score >= self.condition_value.get('min_score', 0)
            
        elif self.condition_type == 'complete_all':
            return user.games_completed >= 6
            
        elif self.condition_type == 'speed_completion':
            game_name = self.condition_value.get('game_name')
            max_time = self.condition_value.get('max_time')
            progress = GameProgress.query.filter_by(user_id=user.id, game_name=game_name).first()
            return progress and progress.is_completed and progress.completion_time <= max_time
            
        return False

class UserAchievement(db.Model):
    """Track user achievements"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    achievement_id = db.Column(db.Integer, db.ForeignKey('achievement.id'), nullable=False)
    earned_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    achievement = db.relationship('Achievement', backref='user_achievements')
    
    __table_args__ = (
        db.UniqueConstraint('user_id', 'achievement_id', name='unique_user_achievement'),
    )