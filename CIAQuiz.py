# quiz.py
from flask import Blueprint, render_template, request

quiz_bp = Blueprint('quiz', __name__, template_folder='templates')

# Base de questions : chaque question a une phrase + les bonnes réponses
QUESTIONS = [
    {
        "text": "HTTPS uses encryption to protect data in transit.",
        "answers": ["confidentiality"]
    },
    {
        "text": "Digital signatures help ensure a message hasn't been altered.",
        "answers": ["integrity"]
    },
    {
        "text": "A redundant server ensures service stays available even during failure.",
        "answers": ["availability"]
    },
    {
        "text": "Multi-factor authentication protects access to accounts.",
        "answers": ["confidentiality", "integrity"]
    }
]

@quiz_bp.route('/')
def index():
    return render_template("quiz.html", questions=QUESTIONS)