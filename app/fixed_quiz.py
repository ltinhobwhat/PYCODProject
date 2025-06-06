import random
import time
import sqlite3
from flask import Blueprint, render_template, request, redirect, session, url_for
from flask_login import login_required, current_user

quiz_bp = Blueprint("quiz", __name__, template_folder="templates")

# Import questions from your existing pool
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
    },
    {
        "text": "Firewalls help filter traffic based on rules.",
        "answers": ["confidentiality"]
    },
    {
        "text": "Phishing attacks aim to steal user credentials.",
        "answers": ["confidentiality"]
    },
    {
        "text": "Hash functions create fixed-size outputs from variable input data.",
        "answers": ["integrity"]
    },
    {
        "text": "Social engineering exploits human psychology for attacks.",
        "answers": ["confidentiality"]
    },
    {
        "text": "Regular software updates help fix security vulnerabilities.",
        "answers": ["availability", "integrity"]
    },
    {
        "text": "Strong passwords reduce the risk of unauthorized access.",
        "answers": ["confidentiality"]
    }
]

NUM_QUESTIONS = 10

def save_progress(user_id, score, completed, percentage):
    """Save quiz progress to SQLite"""
    conn = sqlite3.connect('game.db')
    cursor = conn.cursor()
    
    # Get current progress
    cursor.execute('SELECT best_score, total_attempts FROM game_progress WHERE user_id = ? AND game_name = ?', 
                   (user_id, 'quiz'))
    current = cursor.fetchone()
    
    if current:
        best_score = max(current[0], score)
        total_attempts = current[1] + 1
        cursor.execute('''
            UPDATE game_progress 
            SET is_completed = ?, best_score = ?, total_attempts = ?
            WHERE user_id = ? AND game_name = ?
        ''', (completed, best_score, total_attempts, user_id, 'quiz'))
    else:
        cursor.execute('''
            INSERT INTO game_progress (user_id, game_name, is_completed, best_score, total_attempts)
            VALUES (?, ?, ?, ?, 1)
        ''', (user_id, 'quiz', completed, score))
    
    # Update user total score if completed for first time
    if completed:
        cursor.execute('''
            UPDATE users 
            SET total_score = total_score + ?, games_completed = games_completed + 1
            WHERE id = ? AND id NOT IN (
                SELECT user_id FROM game_progress 
                WHERE user_id = ? AND game_name = ? AND is_completed = 1
            )
        ''', (score, user_id, user_id, 'quiz'))
    
    conn.commit()
    conn.close()

@quiz_bp.route("/", methods=["GET", "POST"])
@login_required
def index():
    if "quiz_questions" not in session or "quiz_index" not in session:
        num_to_pick = min(NUM_QUESTIONS, len(QUESTIONS))
        session["quiz_questions"] = random.sample(QUESTIONS, num_to_pick)
        session["quiz_index"] = 0
        session["quiz_score"] = 0
        session["quiz_answers"] = []
        session["quiz_start_time"] = time.time()

    quiz_questions = session["quiz_questions"]
    index = session.get("quiz_index", 0)
    total = len(quiz_questions)

    if request.method == "POST":
        user_answers = request.form.getlist("answer")
        correct_answers = quiz_questions[index]["answers"]
        if set(user_answers) == set(correct_answers):
            session["quiz_score"] += 1
        session["quiz_answers"].append(user_answers)
        session["quiz_index"] += 1
        index += 1

        if index >= total:
            return redirect(url_for("quiz.result"))

    question = quiz_questions[index]
    return render_template("quiz_question.html", 
                         question=question, 
                         index=index + 1, 
                         total=total)

@quiz_bp.route("/result")
@login_required
def result():
    score = session.get("quiz_score", 0)
    total = len(session.get("quiz_questions", []))
    
    # Calculate percentage and completion time
    percentage = (score / total) * 100 if total > 0 else 0
    completed = percentage >= 70  # Consider 70% as completion threshold
    
    start_time = session.get("quiz_start_time", time.time())
    completion_time = time.time() - start_time
    
    # Save progress
    save_progress(current_user.id, score, completed, percentage)
    
    # Clean up session
    session.pop('quiz_questions', None)
    session.pop('quiz_index', None)
    session.pop('quiz_score', None)
    session.pop('quiz_answers', None)
    session.pop('quiz_start_time', None)
    
    return render_template("quiz_result.html", 
                         score=score, 
                         total=total,
                         percentage=percentage,
                         completed=completed)