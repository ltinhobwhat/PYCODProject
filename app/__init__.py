from flask import Flask, render_template, redirect, url_for
from flask_login import LoginManager, login_required, current_user
import sqlite3

def create_app():
    app = Flask(__name__)
    app.secret_key = "supersecretkey"
    
    # Home Route
    @app.route('/')
    def home():
        if current_user.is_authenticated:
            return redirect(url_for('menu.menu'))
        else:
            return redirect(url_for('auth.login'))
    
    # Login Manager Setup
    login_manager = LoginManager(app)
    login_manager.login_view = 'auth.login'
    
    @login_manager.user_loader
    def load_user(user_id):
        conn = sqlite3.connect('game.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        user_data = cursor.fetchone()
        conn.close()
        
        if user_data:
            from .simple_user import SimpleUser
            return SimpleUser(user_data)
        return None
    
    # Register all blueprints with the fixed versions
    try:
        from .auth import auth_bp
        app.register_blueprint(auth_bp, url_prefix='/auth')
        print("✅ Auth blueprint loaded")
    except Exception as e:
        print(f"❌ Auth blueprint failed: {e}")
    
    try:
        from .menu import menu_bp
        app.register_blueprint(menu_bp, url_prefix='/menu')
        print("✅ Menu blueprint loaded")
    except Exception as e:
        print(f"❌ Menu blueprint failed: {e}")
    
    try:
        from .map import map_bp
        app.register_blueprint(map_bp, url_prefix='/map')
        print("✅ Map blueprint loaded")
    except Exception as e:
        print(f"❌ Map blueprint failed: {e}")
    
    # FIXED GAMES - Use the new SQLite versions
    try:
        from .fixed_pswdChecker import pswd_app
        app.register_blueprint(pswd_app, url_prefix='/pswdChecker')
        print("✅ Fixed Password checker loaded")
    except Exception as e:
        print(f"❌ Password checker failed: {e}")
    
    try:
        from .fixed_quiz import quiz_bp
        app.register_blueprint(quiz_bp, url_prefix='/quiz')
        print("✅ Fixed Quiz loaded")
    except Exception as e:
        print(f"❌ Quiz failed: {e}")
    
    try:
        from .fixed_vigenere import vigenere_bp
        app.register_blueprint(vigenere_bp, url_prefix='/vigenere')
        print("✅ Fixed Vigenere loaded")
    except Exception as e:
        print(f"❌ Vigenere failed: {e}")
    
    try:
        from .fixed_hashgame import hashgame_bp
        app.register_blueprint(hashgame_bp, url_prefix='/hashgame')
        print("✅ Fixed Hash game loaded")
    except Exception as e:
        print(f"❌ Hash game failed: {e}")
    
    try:
        from .fixed_sqlinjector import sqlinjector_bp
        app.register_blueprint(sqlinjector_bp, url_prefix='/sqlinjector')
        print("✅ Fixed SQL injector loaded")
    except Exception as e:
        print(f"❌ SQL injector failed: {e}")
    # Add this to your __init__.py file after the SQL injector blueprint registration:

    try:
        from .social_engineering import social_bp
        app.register_blueprint(social_bp, url_prefix='/social')
        print("✅ Social Engineering loaded")
    except Exception as e:
        print(f"❌ Social Engineering failed: {e}")
    # Optional: Leaderboard (will create this next if needed)
    try:
        from .leaderboard import leaderboard_bp
        app.register_blueprint(leaderboard_bp, url_prefix='/leaderboard')
        print("✅ Leaderboard blueprint loaded")
    except Exception as e:
        print(f"❌ Leaderboard blueprint failed: {e}")
    try:
        from .sql_defender import sqldefender_bp
        app.register_blueprint(sqldefender_bp, url_prefix='/sqldefender')
        print("✅ SQL Defender loaded")
    except Exception as e:
        print(f"❌ SQL Defender failed: {e}")
    return app