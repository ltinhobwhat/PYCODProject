from flask import Blueprint, request, jsonify, session
from flask_login import login_required, current_user
from .save_manager import SaveManager
import logging

logger = logging.getLogger(__name__)

saves_bp = Blueprint('saves', __name__, url_prefix='/saves')

@saves_bp.route('/save', methods=['POST'])
@login_required
def save_game():
    """Save current game state"""
    try:
        save_name = request.form.get('save_name', 'Autosave')
        
        # Use your SaveManager to save the game
        result = SaveManager.save_game(save_name)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Save game error: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@saves_bp.route('/load/<int:save_id>', methods=['POST'])
@login_required
def load_game(save_id):
    """Load game state from save"""
    try:
        result = SaveManager.load_game(save_id)
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Load game error: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@saves_bp.route('/list', methods=['GET'])
@login_required
def list_saves():
    """Get list of user's saves"""
    try:
        from .models import GameSave
        
        saves = GameSave.query.filter_by(user_id=current_user.id).all()
        save_list = []
        
        for save in saves:
            save_list.append({
                'id': save.id,
                'save_name': save.save_name,
                'created_at': save.created_at.strftime('%Y-%m-%d %H:%M'),
                'updated_at': save.updated_at.strftime('%Y-%m-%d %H:%M')
            })
        
        return jsonify({
            'status': 'success',
            'saves': save_list
        })
        
    except Exception as e:
        logger.error(f"List saves error: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@saves_bp.route('/delete/<int:save_id>', methods=['DELETE'])
@login_required
def delete_save(save_id):
    """Delete a save"""
    try:
        from .models import GameSave, db
        
        save = GameSave.query.filter_by(
            id=save_id,
            user_id=current_user.id
        ).first()
        
        if not save:
            return jsonify({
                'status': 'error',
                'message': 'Save not found'
            }), 404
        
        db.session.delete(save)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Save deleted'
        })
        
    except Exception as e:
        logger.error(f"Delete save error: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500