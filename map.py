from flask import Blueprint, render_template

# Create a Blueprint for the map routes
map_bp = Blueprint('map', __name__)

# Route to display the map page
@map_bp.route('/map')
def map_page():
    return render_template('map.html')

# Route to start the password checker minigame
@map_bp.route('/minigame/password')
def launch_password_game():
    return render_template('pswd_checker.html')
