# quiz.py

import random
from flask import Blueprint, render_template, request, session, redirect, url_for
from flask import Blueprint
quiz_bp = Blueprint("quiz", __name__, template_folder="templates/quiz")
from questions_pool import QUESTIONS

quiz_bp = Blueprint('quiz', __name__, template_folder='templates')
NUM_QUESTIONS = 10  # nombre de questions à tirer au hasard

@quiz_bp.route("/quiz/", methods=["GET", "POST"])
def index():
    if "quiz_questions" not in session:
        # Choisir les questions au début
        num_to_pick = min(NUM_QUESTIONS, len(QUESTIONS))
        session["quiz_questions"] = random.sample(QUESTIONS, num_to_pick)
        session["quiz_index"] = 0
        session["score"] = 0
        session["answers"] = []

    quiz_questions = session["quiz_questions"]
    index = session["quiz_index"]
    total = len(quiz_questions)

    if request.method == "POST":
        # Récupère les réponses de l'utilisateur
        user_answers = request.form.getlist("answer")
        correct_answers = quiz_questions[index]["answers"]
        if set(user_answers) == set(correct_answers):
            session["score"] += 1
        session["answers"].append(user_answers)
        session["quiz_index"] += 1
        index += 1

        if index >= total:
            return redirect(url_for("quiz.result"))

    # Affiche la question actuelle
    questions = quiz_questions[index:index+2]
    return render_template("quiz_question.html", question=question, index=index + 1, total=total)
@quiz_bp.route("/quiz/result")
def result():
    score = session.get("score", 0)
    total = len(session.get("quiz_questions", []))
    return render_template("quiz_result.html", score=score, total=total)
