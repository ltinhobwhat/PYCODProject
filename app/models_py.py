from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
import json

db = SQLAlchemy()

class User(UserMixin, db.Model):
    """User model for authentication with Flask-Login"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    password_hash = db.Column(db.String(128), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)
    
    # Relationship to game saves
    game_saves = db.relationship('GameSave', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<User {self.username}>'

class GameSave(db.Model):
    """Model for storing complete game states"""
    __tablename__ = 'game_saves'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    save_name = db.Column(db.String(100), nullable=False, default='Autosave')
    save_data = db.Column(db.JSON, nullable=False)  # Stores the complete game state
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Composite unique constraint to prevent duplicate save names per user
    __table_args__ = (
        db.UniqueConstraint('user_id', 'save_name', name='unique_user_save_name'),
    )
    
    def __repr__(self):
        return f'<GameSave {self.save_name} - User {self.user_id}>'
    
    def to_dict(self):
        """Convert save to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'save_name': self.save_name,
            'save_data': self.save_data,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @property
    def game_progress(self):
        """Easy access to game progress data"""
        return self.save_data.get('game_progress', {})
    
    @property
    def current_level(self):
        """Easy access to current level"""
        return self.save_data.get('current_level', 1)
    
    @property
    def total_score(self):
        """Easy access to total score"""
        return self.save_data.get('total_score', 0)
    
    @property
    def completed_games(self):
        """Easy access to completed games list"""
        return self.save_data.get('completed_games', [])
    
    @property
    def session_data(self):
        """Easy access to session data for individual games"""
        return self.save_data.get('session_data', {})
    
    def get_game_data(self, game_name):
        """Get specific game's session data"""
        return self.session_data.get(game_name, {})
    
    def get_game_progress(self, game_name):
        """Get specific game's progress data"""
        return self.game_progress.get(game_name, {})