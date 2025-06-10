import hashlib
import sqlite3
from flask import Blueprint, render_template_string, request, session, redirect, flash
from flask_login import login_required, current_user

pswd_app = Blueprint('pswd_app', __name__)  

# HTML Templates
PASSWORD_INPUT_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Password Strength Test</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #1a1a1a;
            color: #00ff00;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            margin: 0;
            padding: 20px;
        }
        
        .container {
            background-color: #2a2a2a;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 0 20px rgba(0, 255, 0, 0.3);
            max-width: 500px;
            width: 100%;
        }
        
        h1 {
            text-align: center;
            color: #00ff00;
            text-shadow: 0 0 10px rgba(0, 255, 0, 0.5);
            margin-bottom: 30px;
        }
        
        .instruction {
            text-align: center;
            margin-bottom: 30px;
            color: #cccccc;
            line-height: 1.6;
        }
        
        .password-group {
            margin-bottom: 25px;
        }
        
        label {
            display: block;
            margin-bottom: 8px;
            color: #00ff00;
            font-weight: bold;
        }
        
        input[type="password"] {
            width: 100%;
            padding: 12px;
            background-color: #1a1a1a;
            border: 2px solid #00ff00;
            color: #ffffff;
            border-radius: 5px;
            font-size: 16px;
            box-sizing: border-box;
        }
        
        input[type="password"]:focus {
            outline: none;
            border-color: #00ff00;
            box-shadow: 0 0 10px rgba(0, 255, 0, 0.5);
        }
        
        .submit-btn {
            width: 100%;
            padding: 15px;
            background-color: #00ff00;
            color: #000000;
            border: none;
            border-radius: 5px;
            font-size: 18px;
            font-weight: bold;
            cursor: pointer;
            margin-top: 20px;
        }
        
        .submit-btn:hover {
            background-color: #00cc00;
            box-shadow: 0 0 15px rgba(0, 255, 0, 0.7);
        }
        
        .warning {
            color: #ff6347;
            text-align: center;
            margin-top: 15px;
        }
        
        .back-btn {
            display: block;
            width: 200px;
            margin: 20px auto;
            padding: 12px;
            background-color: #333;
            color: #00ff00;
            text-align: center;
            text-decoration: none;
            border-radius: 5px;
            border: 2px solid #00ff00;
        }
        
        .back-btn:hover {
            background-color: #444;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔐 Password Strength Test</h1>
        
        {% if already_completed %}
        <div class="warning">
            <h2>⚠️ You have already completed this challenge!</h2>
            <p>Your score: {{ score }}/3 points</p>
            <a href="/menu/" class="back-btn">Back to Menu</a>
        </div>
        {% else %}
        <div class="instruction">
            <p>Create 3 different passwords and test their strength.</p>
            <p>A strong password contains: uppercase, lowercase, numbers and special characters.</p>
        </div>
        
        <form method="POST">
            <div class="password-group">
                <label for="password1">Password 1:</label>
                <input type="password" id="password1" name="password1" placeholder="Enter your first password" required>
            </div>
            
            <div class="password-group">
                <label for="password2">Password 2:</label>
                <input type="password" id="password2" name="password2" placeholder="Enter your second password" required>
            </div>
            
            <div class="password-group">
                <label for="password3">Password 3:</label>
                <input type="password" id="password3" name="password3" placeholder="Enter your third password" required>
            </div>
            
            <button type="submit" class="submit-btn">Analyze Passwords</button>
        </form>
        {% endif %}
    </div>
</body>
</html>
"""

PASSWORD_RESULTS_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Results - Password Strength Test</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #1a1a1a;
            color: #00ff00;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            margin: 0;
            padding: 20px;
        }
        
        .container {
            background-color: #2a2a2a;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 0 20px rgba(0, 255, 0, 0.3);
            max-width: 600px;
            width: 100%;
        }
        
        h1 {
            text-align: center;
            color: #00ff00;
            text-shadow: 0 0 10px rgba(0, 255, 0, 0.5);
            margin-bottom: 30px;
        }
        
        .result-card {
            background-color: #1a1a1a;
            border: 2px solid #00ff00;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 20px;
        }
        
        .password-number {
            font-size: 18px;
            font-weight: bold;
            margin-bottom: 15px;
            color: #00ff00;
        }
        
        .strength-meter {
            height: 30px;
            background-color: #333333;
            border-radius: 15px;
            overflow: hidden;
            margin: 10px 0;
        }
        
        .strength-fill {
            height: 100%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            color: #000000;
        }
        
        .criteria {
            margin-top: 15px;
        }
        
        .criteria-item {
            margin: 5px 0;
            font-size: 14px;
        }
        
        .criteria-item.met {
            color: #00ff00;
        }
        
        .criteria-item.not-met {
            color: #ff6347;
        }
        
        .similarity-warning {
            background-color: rgba(255, 99, 71, 0.2);
            border: 2px solid #ff6347;
            border-radius: 8px;
            padding: 15px;
            margin: 20px 0;
            text-align: center;
        }
        
        .similarity-warning h3 {
            color: #ff6347;
            margin-top: 0;
        }
        
        .similarity-warning p {
            margin: 5px 0;
            color: #ffaaaa;
        }
        
        .final-score {
            text-align: center;
            margin-top: 30px;
            font-size: 24px;
            font-weight: bold;
            padding: 20px;
            background-color: #1a1a1a;
            border: 3px solid #00ff00;
            border-radius: 10px;
        }
        
        .penalty-info {
            color: #ff6347;
            font-size: 14px;
            margin-top: 10px;
        }
        
        .back-btn {
            display: block;
            width: 200px;
            margin: 30px auto 0;
            padding: 12px;
            background-color: #00ff00;
            color: #000000;
            text-align: center;
            text-decoration: none;
            border-radius: 5px;
            font-weight: bold;
        }
        
        .back-btn:hover {
            background-color: #00cc00;
            box-shadow: 0 0 15px rgba(0, 255, 0, 0.7);
        }
        
        .success-message {
            text-align: center;
            margin-top: 20px;
            color: #00ff00;
            font-size: 18px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 Analysis Results</h1>
        
        {% for result in results %}
        <div class="result-card">
            <div class="password-number">Password {{ result.number }}</div>
            
            <div class="strength-meter">
                <div class="strength-fill" style="width: {{ result.score }}%; background-color: {{ result.color }};">
                    {{ result.score }}%
                </div>
            </div>
            
            <div style="text-align: center; margin: 10px 0; font-size: 20px;">
                {{ result.level }}
            </div>
            
            <div class="criteria">
                <div class="criteria-item {% if result.details.length %}met{% else %}not-met{% endif %}">
                    {% if result.details.length %}✅{% else %}❌{% endif %} Minimum length (8 characters)
                </div>
                <div class="criteria-item {% if result.details.uppercase %}met{% else %}not-met{% endif %}">
                    {% if result.details.uppercase %}✅{% else %}❌{% endif %} Uppercase letters
                </div>
                <div class="criteria-item {% if result.details.lowercase %}met{% else %}not-met{% endif %}">
                    {% if result.details.lowercase %}✅{% else %}❌{% endif %} Lowercase letters
                </div>
                <div class="criteria-item {% if result.details.digits %}met{% else %}not-met{% endif %}">
                    {% if result.details.digits %}✅{% else %}❌{% endif %} Numbers
                </div>
                <div class="criteria-item {% if result.details.special %}met{% else %}not-met{% endif %}">
                    {% if result.details.special %}✅{% else %}❌{% endif %} Special characters
                </div>
            </div>
        </div>
        {% endfor %}
        
        {% if similarity_warnings %}
        <div class="similarity-warning">
            <h3>⚠️ Password Similarity Warning</h3>
            {% for warning in similarity_warnings %}
            <p>{{ warning }}</p>
            {% endfor %}
            <p style="font-weight: bold; margin-top: 10px;">
                Using similar passwords reduces security!
            </p>
        </div>
        {% endif %}
        
        <div class="final-score">
            Final Score: {{ final_score }}/3 points
            {% if penalty > 0 %}
            <div class="penalty-info">
                (Penalty applied: -{{ "%.1f"|format(penalty) }} for password similarity)
            </div>
            {% endif %}
        </div>
        
        <div class="success-message">
            ✅ Challenge completed successfully!<br>
            Your results have been saved.
        </div>
        
        <a href="/menu/" class="back-btn">Back to Menu</a>
    </div>
</body>
</html>
"""

def calculate_similarity(pwd1, pwd2):
    """Calculate similarity percentage between two passwords"""
    # Convert to lowercase for comparison
    pwd1_lower = pwd1.lower()
    pwd2_lower = pwd2.lower()
    
    # Check if one is a substring of the other
    if pwd1_lower in pwd2_lower or pwd2_lower in pwd1_lower:
        # Calculate how much of the longer password is covered
        longer = max(len(pwd1), len(pwd2))
        shorter = min(len(pwd1), len(pwd2))
        return (shorter / longer) * 100
    
    # Calculate Levenshtein distance (simple version)
    if len(pwd1) > len(pwd2):
        pwd1, pwd2 = pwd2, pwd1
    
    distances = range(len(pwd1) + 1)
    for i2, c2 in enumerate(pwd2):
        new_distances = [i2 + 1]
        for i1, c1 in enumerate(pwd1):
            if c1 == c2:
                new_distances.append(distances[i1])
            else:
                new_distances.append(1 + min((distances[i1], distances[i1 + 1], new_distances[-1])))
        distances = new_distances
    
    # Convert distance to similarity percentage
    max_len = max(len(pwd1), len(pwd2))
    similarity = (1 - distances[-1] / max_len) * 100
    return similarity

def check_password_uniqueness(passwords):
    """Check if passwords are sufficiently unique from each other"""
    similarity_warnings = []
    penalty = 0
    
    # Compare each pair of passwords
    for i in range(len(passwords)):
        for j in range(i + 1, len(passwords)):
            similarity = calculate_similarity(passwords[i], passwords[j])
            
            if similarity > 80:
                similarity_warnings.append(f"Password {i+1} and {j+1} are too similar ({similarity:.0f}%)")
                penalty += 1
            elif similarity > 60:
                similarity_warnings.append(f"Password {i+1} and {j+1} are quite similar ({similarity:.0f}%)")
                penalty += 0.5
    
    return similarity_warnings, min(penalty, 2)  # Max penalty of 2 points

def evaluate_password_strength(password):
    """Simple password strength evaluation"""
    score = 0
    details = {
        'length': False,
        'uppercase': False,
        'lowercase': False,
        'digits': False,
        'special': False
    }
    
    # Check length
    if len(password) >= 8:
        score += 20
        details['length'] = True
    elif len(password) >= 6:
        score += 10
    
    # Check for uppercase
    if any(c.isupper() for c in password):
        score += 20
        details['uppercase'] = True
    
    # Check for lowercase
    if any(c.islower() for c in password):
        score += 20
        details['lowercase'] = True
    
    # Check for digits
    if any(c.isdigit() for c in password):
        score += 20
        details['digits'] = True
    
    # Check for special characters
    if any(c in "!@#$%^&*()-_+=<>?/;:[]{}|~`" for c in password):
        score += 20
        details['special'] = True
    
    # Determine level
    if score >= 80:
        level = "🔥 Very Strong"
        color = "#00ff00"
    elif score >= 60:
        level = "🔐 Strong"
        color = "#90ee90"
    elif score >= 40:
        level = "😐 Medium"
        color = "#ffa500"
    elif score >= 20:
        level = "⚠️ Weak"
        color = "#ff6347"
    else:
        level = "💀 Very Weak"
        color = "#ff0000"
    
    return {
        'score': score,
        'level': level,
        'color': color,
        'details': details
    }

def check_user_completed(user_id):
    """Check if user has already completed the password game"""
    conn = sqlite3.connect('game.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT is_completed, best_score 
        FROM game_progress 
        WHERE user_id = ? AND game_name = 'pswd'
    ''', (user_id,))
    
    result = cursor.fetchone()
    conn.close()
    
    if result and result[0]:  # is_completed = 1
        return True, result[1]  # Return completed status and score
    return False, 0

def save_game_progress(user_id, score):
    """Save or update game progress"""
    conn = sqlite3.connect('game.db')
    cursor = conn.cursor()
    
    try:
        # Check if record exists
        cursor.execute('''
            SELECT id, best_score, total_attempts 
            FROM game_progress 
            WHERE user_id = ? AND game_name = 'pswd'
        ''', (user_id,))
        
        existing = cursor.fetchone()
        
        if existing:
            # Update existing record
            new_best_score = max(existing[1], score)
            new_attempts = existing[2] + 1
            
            cursor.execute('''
                UPDATE game_progress 
                SET is_completed = 1, best_score = ?, total_attempts = ?
                WHERE user_id = ? AND game_name = 'pswd'
            ''', (new_best_score, new_attempts, user_id))
        else:
            # Insert new record
            cursor.execute('''
                INSERT INTO game_progress (user_id, game_name, is_completed, best_score, total_attempts)
                VALUES (?, 'pswd', 1, ?, 1)
            ''', (user_id, score))
        
        # Update user's total score and games completed
        cursor.execute('''
            UPDATE users 
            SET total_score = total_score + ?, 
                games_completed = games_completed + 1
            WHERE id = ? AND id NOT IN (
                SELECT user_id FROM game_progress 
                WHERE user_id = ? AND game_name = 'pswd' AND is_completed = 1
            )
        ''', (score, user_id, user_id))
        
        conn.commit()
        print(f"Game progress saved for user {user_id}: score {score}")
        
    except Exception as e:
        print(f"Error saving game progress: {e}")
        conn.rollback()
    finally:
        conn.close()

@pswd_app.route("/", methods=["GET", "POST"])
@login_required
def index():
    # Check if user has already completed the game
    completed, score = check_user_completed(current_user.id)
    
    if request.method == "POST" and not completed:
        # Get passwords
        password1 = request.form.get('password1', '')
        password2 = request.form.get('password2', '')
        password3 = request.form.get('password3', '')
        
        passwords = [password1, password2, password3]
        
        # Check for password similarity
        similarity_warnings, penalty = check_password_uniqueness(passwords)
        
        # Evaluate each password
        results = []
        base_score = 0
        
        for i, pwd in enumerate(passwords, 1):
            evaluation = evaluate_password_strength(pwd)
            # Give 1 point for each password that scores >= 60%
            if evaluation['score'] >= 60:
                base_score += 1
                
            results.append({
                'number': i,
                'score': evaluation['score'],
                'level': evaluation['level'],
                'color': evaluation['color'],
                'details': evaluation['details']
            })
        
        # Apply penalty for similar passwords
        final_score = max(0, base_score - penalty)
        final_score = int(final_score)  # Ensure it's an integer
        
        # Save progress to database
        save_game_progress(current_user.id, final_score)
        
        # Store in session for results page
        session['password_results'] = results
        session['final_score'] = final_score
        session['similarity_warnings'] = similarity_warnings
        session['penalty'] = penalty
        
        return redirect('/pswdChecker/results')
    
    return render_template_string(PASSWORD_INPUT_TEMPLATE, 
                                already_completed=completed, 
                                score=score)

@pswd_app.route("/results")
@login_required
def results():
    results = session.get('password_results')
    final_score = session.get('final_score')
    similarity_warnings = session.get('similarity_warnings', [])
    penalty = session.get('penalty', 0)
    
    if not results:
        return redirect('/pswdChecker/')
    
    # Clear session data
    session.pop('password_results', None)
    session.pop('final_score', None)
    session.pop('similarity_warnings', None)
    session.pop('penalty', None)
    
    return render_template_string(PASSWORD_RESULTS_TEMPLATE, 
                                results=results, 
                                final_score=final_score,
                                similarity_warnings=similarity_warnings,
                                penalty=penalty)