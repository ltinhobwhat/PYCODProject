# save_manager.py - Centralized save system
from flask import session
from .models import db, GameSave
from flask_login import current_user
import json
import logging

logger = logging.getLogger(__name__)

class SaveManager:
    """Centralized save system for all minigames"""
    
    @staticmethod
    def register_game_progress(game_name, progress_data):
        """Allow minigames to register their progress"""
        if 'game_progress' not in session:
            session['game_progress'] = {}
        
        session['game_progress'][game_name] = progress_data
        session.permanent = True
    
    @staticmethod
    def get_game_progress(game_name):
        """Get specific game progress"""
        return session.get('game_progress', {}).get(game_name, {})
    
    @staticmethod
    def get_full_game_state():
        """Collect all game state for saving"""
        return {
            'game_progress': session.get('game_progress', {}),
            'current_level': session.get('level', 1),
            'total_score': session.get('total_score', 0),
            'completed_games': session.get('completed_games', []),
            'session_data': {
                'pswd_app': session.get('pswd_app', {}),
                'quiz': session.get('quiz', {}),
                'vigenere': session.get('vigenere', {}),
                'hashgame': session.get('hashgame', {}),
                'sqlinjector': session.get('sqlinjector', {})
            }
        }
    
    @staticmethod
    def save_game(save_name='Autosave'):
        """Save current game state"""
        try:
            game_state = SaveManager.get_full_game_state()
            
            # Find existing save or create new one
            existing_save = GameSave.query.filter_by(
                user_id=current_user.id, 
                save_name=save_name
            ).first()
            
            if existing_save:
                existing_save.save_data = game_state
            else:
                new_save = GameSave(
                    user_id=current_user.id,
                    save_name=save_name,
                    save_data=game_state
                )
                db.session.add(new_save)
            
            db.session.commit()
            return {'status': 'success'}
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Save error: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    @staticmethod
    def load_game(save_id):
        """Load game state from save"""
        try:
            save = GameSave.query.filter_by(
                id=save_id,
                user_id=current_user.id
            ).first()
            
            if not save:
                return {'status': 'error', 'message': 'Save not found'}
            
            # Restore all session data
            save_data = save.save_data
            
            # Restore game progress
            session['game_progress'] = save_data.get('game_progress', {})
            session['level'] = save_data.get('current_level', 1)
            session['total_score'] = save_data.get('total_score', 0)
            session['completed_games'] = save_data.get('completed_games', [])
            
            # Restore session data for each game
            session_data = save_data.get('session_data', {})
            for game_name, data in session_data.items():
                session[game_name] = data
            
            session.permanent = True
            return {'status': 'success'}
            
        except Exception as e:
            logger.error(f"Load error: {str(e)}")
            return {'status': 'error', 'message': str(e)}

# Helper functions for minigames
def save_progress(game_name, score=0, completed=False, level=1, **kwargs):
    """Simple interface for minigames to save progress"""
    progress = {
        'score': score,
        'completed': completed,
        'level': level,
        'custom_data': kwargs
    }
    SaveManager.register_game_progress(game_name, progress)
    
    # Update global progress
    if completed and game_name not in session.get('completed_games', []):
        completed_games = session.get('completed_games', [])
        completed_games.append(game_name)
        session['completed_games'] = completed_games
    
    # Update total score
    session['total_score'] = session.get('total_score', 0) + score

def get_progress(game_name):
    """Simple interface for minigames to get their progress"""
    return SaveManager.get_game_progress(game_name)