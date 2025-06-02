from flask import Flask
from flask_login import LoginManager
from .models import db, User

def create_app():
    app = Flask(__name__)
    app.secret_key = "supersecretkey"
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///game.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    login_manager = LoginManager(app)
    login_manager.login_view = 'auth.login'

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    # Blueprints (importe les autres fichiers .py du projet)
    from .pswdChecker import pswd_app
    from .menu import menu_bp
    from .map import map_bp
    from .quiz import quiz_bp
    from .vigenere import vigenere_bp
    from .hashgame import hashgame_bp
    from .sqlinjector import sqlinjector_bp
    from .auth import auth_bp
    from .saves import saves_bp

    app.register_blueprint(menu_bp)
    app.register_blueprint(pswd_app, url_prefix='/pswdChecker')
    app.register_blueprint(map_bp, url_prefix='/map')
    app.register_blueprint(quiz_bp, url_prefix='/quiz')
    app.register_blueprint(vigenere_bp, url_prefix='/vigenere')
    app.register_blueprint(hashgame_bp, url_prefix='/hashgame')
    app.register_blueprint(sqlinjector_bp, url_prefix='/sqlinjector')
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(saves_bp)

    with app.app_context():
        db.create_all()

    return app
