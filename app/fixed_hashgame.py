import random
import hashlib
import time
import sqlite3
from flask import Blueprint, render_template, request, session, redirect, url_for
from flask_login import login_required, current_user

hashgame_bp = Blueprint('hashgame', __name__, template_folder='templates')

WORDS = ["password", "admin", "network", "cyber", "python"]
HASH_ALGOS = {
    "md5": lambda x: hashlib.md5(x.encode()).hexdigest(),
    "sha1": lambda x: hashlib.sha1(x.encode()).hexdigest(),
    "sha256": lambda x: hashlib.sha256(x.encode()).hexdigest(),
}

def save_progress(user_id, score, completed):
    """Save progress to SQLite"""
    conn = sqlite3.connect('game.db')
    cursor = conn.cursor()
    
    # Get current progress
    cursor.execute('SELECT best_score, total_attempts FROM game_progress WHERE user_id = ? AND game_name = ?', 
                   (user_id, 'hashgame'))
    current = cursor.fetchone()
    
    if current:
        best_score = max(current[0], score)
        total_attempts = current[1] + 1
        cursor.execute('''
            UPDATE game_progress 
            SET is_completed = ?, best_score = ?, total_attempts = ?
            WHERE user_id = ? AND game_name = ?
        ''', (completed, best_score, total_attempts, user_id, 'hashgame'))
    else:
        cursor.execute('''
            INSERT INTO game_progress (user_id, game_name, is_completed, best_score, total_attempts)
            VALUES (?, ?, ?, ?, 1)
        ''', (user_id, 'hashgame', completed, score))
    
    # Update user total score if completed for first time
    if completed:
        cursor.execute('''
            UPDATE users 
            SET total_score = total_score + ?, games_completed = games_completed + 1
            WHERE id = ? AND id NOT IN (
                SELECT user_id FROM game_progress 
                WHERE user_id = ? AND game_name = ? AND is_completed = 1
            )
        ''', (score, user_id, user_id, 'hashgame'))
    
    conn.commit()
    conn.close()

def generate_hash_challenge():
    word = random.choice(WORDS)
    algo = random.choice(list(HASH_ALGOS.keys()))
    hashed_word = HASH_ALGOS[algo](word)
    return word, algo, hashed_word

@hashgame_bp.route("/", methods=["GET", "POST"])
@login_required
def index():
    # Initialize session data
    if "hash_score" not in session:
        session["hash_score"] = 0
        session["hash_total"] = 0
        session["hash_start_time"] = time.time()

    if request.method == "POST":
        correct_algo = request.form.get("correct_algo")
        user_choice = request.form.get("algo_choice")
        session["hash_total"] += 1
        
        if user_choice == correct_algo:
            session["hash_score"] += 1
            result = "✅ Correct!"
        else:
            result = f"❌ Wrong. It was {correct_algo.upper()}."
        
        # Check completion (10 correct answers or 15 total attempts)
        completed = session["hash_score"] >= 10
        should_end = completed or session["hash_total"] >= 15
        
        if should_end:
            # Calculate completion time
            start_time = session.get("hash_start_time", time.time())
            completion_time = time.time() - start_time
            
            # Save progress
            save_progress(current_user.id, session["hash_score"], completed)
            
            if completed:
                result += " 🎉 Congratulations! You're a true Hash Detective!"
        
        # Generate new challenge after answer
        word, algo, hashed_word = generate_hash_challenge()
        return render_template("hashgame.html", 
                             hashed_word=hashed_word,
                             correct_algo=algo, 
                             result=result,
                             score=session["hash_score"],
                             total=session["hash_total"],
                             completed=completed if should_end else False
                             )
    
    # First load
    word, algo, hashed_word = generate_hash_challenge()
    return render_template("hashgame.html", 
                         hashed_word=hashed_word,
                         correct_algo=algo,
                         score=session.get("hash_score", 0),
                         total=session.get("hash_total", 0),
                         completed=False
                         )

@hashgame_bp.route("/reset")
@login_required
def reset():
    session.pop("hash_score", None)
    session.pop("hash_total", None)
    session.pop("hash_start_time", None)
    return redirect(url_for('hashgame.index'))