from flask import Blueprint, render_template, redirect, url_for

map_bp = Blueprint('map', __name__)

@map_bp.route('/')
def map_page():
    return render_template('map.html')

# Route to start the password checker minigame
@map_bp.route('/minigame/password')
def launch_password_game():
    return redirect(url_for('pswd_app.index')) 

@map_bp.route('/minigame/quiz')
def launch_quiz():
    return redirect(url_for('quiz.index'))

@map_bp.route('/minigame/vigenere')
def launch_vigenere():
    return redirect(url_for('vigenere.index'))

@map_bp.route('/minigame/hashgame')
def launch_hashgame():
    return redirect(url_for('hashgame.index'))

@map_bp.route('/minigame/sqlinjector')
def launch_sqlinjector():
    return redirect(url_for('sqlinjector.index'))

@map_bp.route('/minigame/sqldefender')
def launch_sqldefender():
    return redirect(url_for('sqlinjector.defender'))