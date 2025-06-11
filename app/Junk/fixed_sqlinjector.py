import time
import sqlite3
from flask import Blueprint, render_template, request, session, redirect, url_for
from flask_login import login_required, current_user

sqlinjector_bp = Blueprint('sqlinjector', __name__, template_folder='templates')

LEVELS = {
    1: "Bypass login with ' OR '1'='1",
    2: "Bypass login using comment '--",
    3: "Bypass login injecting in the password only"
}

def save_progress(user_id, score, completed):
    """Save progress to SQLite"""
    conn = sqlite3.connect('game.db')
    cursor = conn.cursor()
    
    # Get current progress
    cursor.execute('SELECT best_score, total_attempts FROM game_progress WHERE user_id = ? AND game_name = ?', 
                   (user_id, 'sqlinjector'))
    current = cursor.fetchone()
    
    if current:
        best_score = max(current[0], score)
        total_attempts = current[1] + 1
        cursor.execute('''
            UPDATE game_progress 
            SET is_completed = ?, best_score = ?, total_attempts = ?
            WHERE user_id = ? AND game_name = ?
        ''', (completed, best_score, total_attempts, user_id, 'sqlinjector'))
    else:
        cursor.execute('''
            INSERT INTO game_progress (user_id, game_name, is_completed, best_score, total_attempts)
            VALUES (?, ?, ?, ?, 1)
        ''', (user_id, 'sqlinjector', completed, score))
    
    # Update user total score if completed for first time
    if completed:
        cursor.execute('''
            UPDATE users 
            SET total_score = total_score + ?, games_completed = games_completed + 1
            WHERE id = ? AND id NOT IN (
                SELECT user_id FROM game_progress 
                WHERE user_id = ? AND game_name = ? AND is_completed = 1
            )
        ''', (score, user_id, user_id, 'sqlinjector'))
    
    conn.commit()
    conn.close()

@sqlinjector_bp.route("/", methods=["GET", "POST"])
@login_required
def index():
    if "sql_level" not in session:
        session["sql_level"] = 1
        session["sql_attempts"] = 0
        session["sql_start_time"] = time.time()

    success = False
    query = None
    level = session["sql_level"]
    hint = LEVELS[level]

    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}';"
        session["sql_attempts"] += 1

        if level == 1 and ("' OR '1'='1" in username or "' OR '1'='1" in password):
            success = True
        elif level == 2 and ("--" in username or "--" in password):
            success = True
        elif level == 3 and "' OR '1'='1" in password:
            success = True

        if success:
            session["sql_level"] += 1
            completed = session["sql_level"] > len(LEVELS)

            if completed:
                # Calculate completion time
                start_time = session.get("sql_start_time", time.time())
                completion_time = time.time() - start_time
                
                # Save progress
                save_progress(current_user.id, len(LEVELS), True)
                
                session["sql_level"] = 1  # reset after completion
                result = "🎉 All levels completed! You're now an SQL Injection expert!"
            else:
                result = "✅ Injection successful! Moving to next level."
        else:
            result = "❌ Injection failed. Try again!"

        return render_template("sqlinjector.html", 
                             query=query, 
                             success=success, 
                             result=result, 
                             level=level, 
                             hint=hint,
                             total_levels=len(LEVELS)
                             )

    return render_template("sqlinjector.html", 
                         query=query, 
                         success=success, 
                         level=level, 
                         hint=hint,
                         total_levels=len(LEVELS)
                        )

@sqlinjector_bp.route("/reset")
@login_required
def reset_levels():
    session.pop("sql_level", None)
    session.pop("sql_attempts", None)
    session.pop("sql_start_time", None)
    return redirect(url_for('sqlinjector.index'))

@sqlinjector_bp.route("/defender", methods=["GET", "POST"])
@login_required
def defender():
    options = [
        "Use parameterized queries (prepared statements)",
        "Escape user input manually",
        "Trust user input, it's harmless"
    ]
    correct = "Use parameterized queries (prepared statements)"
    result = None
    completed = False

    if request.method == "POST":
        choice = request.form.get("defense_choice")
        completed = choice == correct
        
        if completed:
            result = "✅ Correct! Always use prepared statements."
            # Save defender completion
            save_defender_progress(current_user.id)
        else:
            result = "❌ Wrong. The safest way is to use parameterized queries."

    return render_template("defender.html", 
                         options=options, 
                         result=result,
                         completed=completed)

def save_defender_progress(user_id):
    """Save SQL defender progress"""
    conn = sqlite3.connect('game.db')
    cursor = conn.cursor()
    
    # Check if already completed
    cursor.execute('SELECT id FROM game_progress WHERE user_id = ? AND game_name = ? AND is_completed = 1', 
                   (user_id, 'sqldefender'))
    if not cursor.fetchone():
        cursor.execute('''
            INSERT OR REPLACE INTO game_progress (user_id, game_name, is_completed, best_score, total_attempts)
            VALUES (?, ?, 1, 1, 1)
        ''', (user_id, 'sqldefender'))
        
        # Update user score
        cursor.execute('UPDATE users SET total_score = total_score + 15, games_completed = games_completed + 1 WHERE id = ?', 
                       (user_id,))
    
    conn.commit()
    conn.close()