# quiz.py
from flask import Blueprint, render_template, request

quiz_bp = Blueprint('quiz', __name__, template_folder='templates')

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

@quiz_bp.route('/', methods=["GET", "POST"])
def index():
    if request.method == "POST":
        score = 0
        for i, q in enumerate(QUESTIONS):
            selected = request.form.getlist(f"q{i}")
            if set(selected) == set(q["answers"]):
                score += 1
        return render_template("quiz.html", questions=QUESTIONS, score=score, total=len(QUESTIONS))
    return render_template("quiz.html", questions=QUESTIONS)
