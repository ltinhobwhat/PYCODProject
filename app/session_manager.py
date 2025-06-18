# app/session_manager.py - Gestionnaire de sessions pour les jeux
from flask import session
from flask_login import current_user

class GameSession:
    """Gestionnaire de session pour chaque jeu"""
    
    def __init__(self, game_name):
        self.game_name = game_name
        self.user_id = current_user.id if current_user.is_authenticated else None
    
    def _get_key(self, key):
        """Génère une clé unique par utilisateur et par jeu"""
        return f"{self.game_name}_{key}_{self.user_id}"
    
    def get(self, key, default=None):
        """Récupère une valeur de session"""
        return session.get(self._get_key(key), default)
    
    def set(self, key, value):
        """Définit une valeur de session"""
        session[self._get_key(key)] = value
    
    def pop(self, key, default=None):
        """Supprime et retourne une valeur de session"""
        return session.pop(self._get_key(key), default)
    
    def clear(self):
        """Efface toutes les données de session pour ce jeu et cet utilisateur"""
        keys_to_remove = []
        prefix = f"{self.game_name}_"
        suffix = f"_{self.user_id}"
        
        for key in session.keys():
            if key.startswith(prefix) and key.endswith(suffix):
                keys_to_remove.append(key)
        
        for key in keys_to_remove:
            session.pop(key, None)
    
    def exists(self, key):
        """Vérifie si une clé existe"""
        return self._get_key(key) in session

# Exemple d'utilisation dans un jeu :
"""
from app.session_manager import GameSession

@quiz_bp.route("/", methods=["GET", "POST"])
@login_required
def index():
    # Créer une instance de GameSession pour ce jeu
    game_session = GameSession('quiz')
    
    # Utiliser game_session au lieu de session directement
    if not game_session.exists("questions"):
        selected_questions = random.sample(QUESTIONS, NUM_QUESTIONS)
        game_session.set("questions", selected_questions)
        game_session.set("index", 0)
        game_session.set("score", 0)
    
    current_index = game_session.get("index", 0)
    questions = game_session.get("questions", [])
    
    # etc...
"""