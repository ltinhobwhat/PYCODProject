from flask import Blueprint, render_template, request, redirect, session, url_for
import random

quiz_bp = Blueprint("quiz", __name__, template_folder="templates/quiz")

# QUESTIONS = [...]  # Remplace ça par l'import ou la liste de tes questions
from .questions_pool import QUESTIONS

NUM_QUESTIONS = 10

@quiz_bp.route("/", methods=["GET", "POST"])
def index():
    if "quiz_questions" not in session or "quiz_index" not in session:
        num_to_pick = min(NUM_QUESTIONS, len(QUESTIONS))
        session["quiz_questions"] = random.sample(QUESTIONS, num_to_pick)
        session["quiz_index"] = 0
        session["score"] = 0
        session["answers"] = []

    quiz_questions = session["quiz_questions"]
    index = session.get("quiz_index", 0)
    total = len(quiz_questions)


    if request.method == "POST":
        user_answers = request.form.getlist("answer")
        correct_answers = quiz_questions[index]["answers"]
        if set(user_answers) == set(correct_answers):
            session["score"] += 1
        session["answers"].append(user_answers)
        session["quiz_index"] += 1
        index += 1

        if index >= total:
            return redirect(url_for("quiz.result"))

    question = quiz_questions[index]
    return render_template("quiz_question.html", question=question, index=index + 1, total=total)

@quiz_bp.route("/result")
def result():
    score = session.get("score", 0)
    total = len(session.get("quiz_questions", []))
    session.clear()  # facultatif pour reset le quiz
    return render_template("quiz_result.html", score=score, total=total)
