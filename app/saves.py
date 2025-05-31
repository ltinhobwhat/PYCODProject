# saves.py
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from models import db, GameSave
import json

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
    
    if existing_save:
        existing_save.save_data = get_game_state()
    else:
        new_save = GameSave(
            user_id=current_user.id,
            save_name=save_name,
            save_data=get_game_state()
        )
        db.session.add(new_save)
    
    db.session.commit()
    return jsonify({'status': 'success'})

@saves_bp.route('/load/<int:save_id>', methods=['GET'])
@login_required
def load_game(save_id):
    save = GameSave.query.filter_by(
        id=save_id,
        user_id=current_user.id
    ).first_or_404()
    
    # Restore all game state
    for game, data in save.save_data.items():
        if game == 'current_levels':
            for game_name, level in data.items():
                session[game_name + '_level'] = level
        else:
            session[game_name] = data
    
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