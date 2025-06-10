import hashlib
import time
import sqlite3
from flask import Blueprint, render_template, request, session
from flask_login import login_required, current_user

pswd_app = Blueprint('pswd_app', __name__)  

sites = ["Banque SecurePlus", "Réseau Social ChatterBox", "Forum GeekZone"]

def evaluate_password_strength(password):
    score = 0
    if len(password) >= 8: score += 1
    if any(c.isupper() for c in password): score += 1
    if any(c.isdigit() for c in password): score += 1
    if any(c in "!@#$%^&*()-_+=<>?/;:" for c in password): score += 1
    levels = ["💀 Très faible", "⚠️ Faible", "😐 Moyen", "🔐 Fort", "🔥 Très Fort"]
    return levels[score]

def simulate_crack(password):
    common_passwords = ["123456", "password", "qwerty", "azerty", "admin"]
    time.sleep(1)
    if password in common_passwords:
        return "💀 Mot de passe CRACKÉ en 0.01s !"
    elif len(password) < 6:
        return "😬 Mot de passe trop court, cracké en 1 seconde."
    else:
        return "✅ Mot de passe sécurisé, crackage estimé : plusieurs années."

def save_progress(user_id, score, completed):
    """Save password game progress to SQLite"""
    conn = sqlite3.connect('game.db')
    cursor = conn.cursor()
    
    # Get current progress
    cursor.execute('SELECT best_score, total_attempts FROM game_progress WHERE user_id = ? AND game_name = ?', 
                   (user_id, 'pswd'))
    current = cursor.fetchone()
    
    if current:
        best_score = max(current[0], score)
        total_attempts = current[1] + 1
        cursor.execute('''
            UPDATE game_progress 
            SET is_completed = ?, best_score = ?, total_attempts = ?
            WHERE user_id = ? AND game_name = ?
        ''', (completed, best_score, total_attempts, user_id, 'pswd'))
    else:
        cursor.execute('''
            INSERT INTO game_progress (user_id, game_name, is_completed, best_score, total_attempts)
            VALUES (?, ?, ?, ?, 1)
        ''', (user_id, 'pswd', completed, score))
    
    # Update user total score if completed for first time
    if completed:
        cursor.execute('''
            UPDATE users 
            SET total_score = total_score + ?, games_completed = games_completed + 1
            WHERE id = ? AND id NOT IN (
                SELECT user_id FROM game_progress 
                WHERE user_id = ? AND game_name = ? AND is_completed = 1
            )
        ''', (score, user_id, user_id, 'pswd'))
    
    conn.commit()
    conn.close()

@pswd_app.route("/", methods=["GET", "POST"])
@login_required
def index():
    # Initialize game start time for progress tracking
    if 'pswd_start_time' not in session:
        session['pswd_start_time'] = time.time()
    
    if request.method == "POST":
        passwords = {}
        evaluations = {}
        crack_results = {}
        for site in sites:
            password = request.form.get(site)
            passwords[site] = hashlib.sha256(password.encode()).hexdigest()
            evaluations[site] = evaluate_password_strength(password)
            crack_results[site] = simulate_crack(password)
        session['passwords'] = passwords
        session['password_evaluations'] = evaluations
        session['crack_results'] = crack_results
        session['memory_test'] = False
        return render_template("memory_test.html", sites=sites)
    
    return render_template("password_checker.html", sites=sites)

@pswd_app.route("/memory_test", methods=["POST"])
@login_required
def memory_test():
    passwords = session.get('passwords', {})
    score = 0
    results = {}
    for site in sites:
        attempt = request.form.get(site)
        if hashlib.sha256(attempt.encode()).hexdigest() == passwords.get(site):
            results[site] = "✅ Mot de passe correct !"
            score += 1
        else:
            results[site] = "❌ Mot de passe incorrect."
    
    # Calculate completion time
    start_time = session.get('pswd_start_time', time.time())
    completion_time = time.time() - start_time
    
    # Update progress
    completed = score == len(sites)  # Perfect score required for completion
    save_progress(current_user.id, score, completed)
    
    # Clean up session
    session.pop('passwords', None)
    session.pop('password_evaluations', None)
    session.pop('crack_results', None)
    session.pop('pswd_start_time', None)
    
    return render_template("result.html", 
                         results=results, 
                         score=score, 
                         total=len(sites),
                         completed=completed)