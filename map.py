from flask import Blueprint, render_template

map_bp = Blueprint('map', __name__)

@map_bp.route('/')
def map_page():
    return render_template('map.html')

# Route to start the password checker minigame
@map_bp.route('/minigame/password')
def launch_password_game():
    return redirect(url_for('pswd_app.password_checker'))  # Redirect to the password checker route
