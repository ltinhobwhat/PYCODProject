# app/simple_user.py
from flask_login import UserMixin

class SimpleUser(UserMixin):
    def __init__(self, user_data):
        self.id = user_data[0]
        self.username = user_data[1]
        self.email = user_data[2]
        self.password_hash = user_data[3]
        self.total_score = user_data[4] if len(user_data) > 4 else 0
        self.games_completed = user_data[5] if len(user_data) > 5 else 0
    
    def get_id(self):
        return str(self.id)