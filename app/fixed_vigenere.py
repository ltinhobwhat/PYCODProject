import random
import time
import sqlite3
from flask import Blueprint, render_template, request, session, redirect, url_for
from flask_login import login_required, current_user

vigenere_bp = Blueprint('vigenere', __name__, template_folder='templates')

WORDS = ["network", "security", "password", "cipher", "encryption", "attack", "firewall"]
KEYS = ["key", "cipher", "alpha", "secure"]

def vigenere_encrypt(text, key):
    encrypted = ""
    key = key.lower()
    for i, c in enumerate(text.lower()):
        if c.isalpha():
            shift = ord(key[i % len(key)]) - ord('a')
            encrypted += chr((ord(c) - ord('a') + shift) % 26 + ord('a'))
        else:
            encrypted += c
    return encrypted

def save_progress(user_id, score, completed):
    """Save progress to SQLite instead of SQLAlchemy"""
    conn = sqlite3.connect('game.db')
    cursor = conn.cursor()
    
    # Get current progress
    cursor.execute('SELECT best_score, total_attempts FROM game_progress WHERE user_id = ? AND game_name = ?', 
                   (user_id, 'vigenere'))
    current = cursor.fetchone()
    
    if current:
        best_score = max(current[0], score)
        total_attempts = current[1] + 1
        cursor.execute('''
            UPDATE game_progress 
            SET is_completed = ?, best_score = ?, total_attempts = ?
            WHERE user_id = ? AND game_name = ?
        ''', (completed, best_score, total_attempts, user_id, 'vigenere'))
    else:
        cursor.execute('''
            INSERT INTO game_progress (user_id, game_name, is_completed, best_score, total_attempts)
            VALUES (?, ?, ?, ?, 1)
        ''', (user_id, 'vigenere', completed, score))
    
    # Update user total score if completed for first time
    if completed:
        cursor.execute('SELECT games_completed FROM users WHERE id = ?', (user_id,))
        user_data = cursor.fetchone()
        if user_data:
            cursor.execute('''
                UPDATE users 
                SET total_score = total_score + ?, games_completed = games_completed + 1
                WHERE id = ? AND id NOT IN (
                    SELECT user_id FROM game_progress 
                    WHERE user_id = ? AND game_name = ? AND is_completed = 1
                )
            ''', (score, user_id, user_id, 'vigenere'))
    
    conn.commit()
    conn.close()

@vigenere_bp.route("/", methods=["GET", "POST"])
@login_required
def index():
    if "vigenere_score" not in session:
        session["vigenere_score"] = 0
        session["vigenere_total"] = 0
        session["vigenere_start_time"] = time.time()

    result = None

    if request.method == "POST":
        user_guess = request.form.get("guess", "").lower()
        original = request.form.get("original")
        key = request.form.get("key")
        encrypted = request.form.get("encrypted")
        session["vigenere_total"] += 1

        if user_guess == original:
            session["vigenere_score"] += 1
            result = "✅ Correct!"
        else:
            result = f"❌ Wrong. The correct word was: <strong>{original}</strong>"
        
        # Check completion (5 correct answers)
        completed = session["vigenere_score"] >= 5
        
        if completed or session["vigenere_total"] >= 10:
            # Calculate completion time
            start_time = session.get("vigenere_start_time", time.time())
            completion_time = time.time() - start_time
            
            # Save progress to database
            save_progress(current_user.id, session["vigenere_score"], completed)
            
            if completed:
                result += " 🎉 Congratulations! You've mastered the Vigenère cipher!"

    # Generate new challenge
    word = random.choice(WORDS)
    key = random.choice(KEYS)
    encrypted = vigenere_encrypt(word, key)

    return render_template("vigenere.html",
                           encrypted=encrypted,
                           original=word,
                           key=key,
                           result=result,
                           score=session.get("vigenere_score", 0),
                           total=session.get("vigenere_total", 0))

@vigenere_bp.route("/reset")
@login_required
def reset_score():
    session.pop("vigenere_score", None)
    session.pop("vigenere_total", None)
    session.pop("vigenere_start_time", None)
    return redirect(url_for('vigenere.index'))