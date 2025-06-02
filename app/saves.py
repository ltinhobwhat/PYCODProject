from flask import Blueprint, request, jsonify, session  # Added session import
from flask_login import login_required, current_user
from models import db, GameSave

saves_bp = Blueprint('saves', __name__)

@login_required
def get_game_state():
    """Helper function to collect all game state from session"""
    return {
        'pswd_app': session.get('pswd_app', {}),
        'quiz': session.get('quiz', {}),
        'vigenere': session.get('vigenere', {}),
        'hashgame': session.get('hashgame', {}),
        'sqlinjector': session.get('sqlinjector', {}),
        'current_levels': {
            'pswd_app': session.get('level', 1),
            'sqlinjector': session.get('level', 1)
        }
    }

@saves_bp.route('/save', methods=['POST'])
@login_required
def save_game():
    save_name = request.form.get('save_name', 'Autosave')
    
    # Create new save or update existing
    existing_save = GameSave.query.filter_by(
        user_id=current_user.id, 
        save_name=save_name
    ).first()
    
    game_state = get_game_state()
    
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
    return jsonify({'status': 'success'})

@saves_bp.route('/list', methods=['GET'])
@login_required
def list_saves():
    saves = GameSave.query.filter_by(user_id=current_user.id).all()
    return jsonify([{
        'id': save.id,
        'name': save.save_name,
        'date': save.last_updated.strftime('%Y-%m-%d %H:%M')
    } for save in saves])