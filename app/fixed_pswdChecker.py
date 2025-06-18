import hashlib
import sqlite3
import re
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
            max-width: 600px;
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
        
        .scoring-info {
            background-color: rgba(0, 255, 0, 0.1);
            border: 1px solid #00ff00;
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 25px;
            font-size: 14px;
        }
        
        .scoring-info h3 {
            color: #00ff00;
            margin-top: 0;
            margin-bottom: 10px;
        }
        
        .scoring-info ul {
            margin: 5px 0;
            padding-left: 20px;
        }
        
        .scoring-info li {
            margin: 3px 0;
            color: #bbbbbb;
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
            <p>Your score: {{ score }} points</p>
            <a href="/menu/" class="back-btn">Back to Menu</a>
        </div>
        {% else %}
        <div class="instruction">
            <p>Create 3 different passwords and test their strength.</p>
            <p>The stronger and more unique your passwords, the more points you'll earn!</p>
        </div>
        
        <div class="scoring-info">
            <h3>📊 Scoring System:</h3>
            <ul>
                <li><strong>Length:</strong> 8-9 chars (2pts), 10-11 (4pts), 12-14 (6pts), 15+ (8pts)</li>
                <li><strong>Character Types:</strong> 2pts each for uppercase, lowercase, numbers, specials</li>
                <li><strong>Special Characters:</strong> 1 special (1pt), 2-3 (3pts), 4+ (5pts)</li>
                <li><strong>Complexity Bonus:</strong> Using all 4 character types (+3pts)</li>
                <li><strong>Uniqueness Bonus:</strong> Very different passwords (+5pts)</li>
                <li><strong>Maximum possible:</strong> ~45 points</li>
            </ul>
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
            max-width: 700px;
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
        
        .score-breakdown {
            background-color: rgba(0, 255, 0, 0.05);
            border: 1px solid rgba(0, 255, 0, 0.3);
            border-radius: 5px;
            padding: 15px;
            margin: 15px 0;
        }
        
        .score-item {
            display: flex;
            justify-content: space-between;
            margin: 5px 0;
            font-size: 14px;
        }
        
        .score-item.bonus {
            color: #00ff00;
            font-weight: bold;
        }
        
        .score-item.penalty {
            color: #ff6347;
        }
        
        .total-password-score {
            margin-top: 10px;
            padding-top: 10px;
            border-top: 1px solid #00ff00;
            font-weight: bold;
            color: #00ff00;
            text-align: right;
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
        
        .bonus-section {
            background-color: rgba(0, 255, 0, 0.1);
            border: 2px solid #00ff00;
            border-radius: 8px;
            padding: 15px;
            margin: 20px 0;
            text-align: center;
        }
        
        .bonus-section h3 {
            color: #00ff00;
            margin-top: 0;
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
            font-size: 28px;
            font-weight: bold;
            padding: 25px;
            background-color: #1a1a1a;
            border: 3px solid #00ff00;
            border-radius: 10px;
            box-shadow: 0 0 20px rgba(0, 255, 0, 0.5);
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
                <div class="strength-fill" style="width: {{ result.display_percentage }}%; background-color: {{ result.color }};">
                    {{ result.level }}
                </div>
            </div>
            
            <div class="score-breakdown">
                <h4 style="margin-top: 0; color: #00ff00;">Score Breakdown:</h4>
                <div class="score-item">
                    <span>Length ({{ result.details.length_chars }} chars):</span>
                    <span>+{{ result.scoring.length_points }} pts</span>
                </div>
                {% if result.scoring.uppercase_points > 0 %}
                <div class="score-item">
                    <span>Uppercase letters:</span>
                    <span>+{{ result.scoring.uppercase_points }} pts</span>
                </div>
                {% endif %}
                {% if result.scoring.lowercase_points > 0 %}
                <div class="score-item">
                    <span>Lowercase letters:</span>
                    <span>+{{ result.scoring.lowercase_points }} pts</span>
                </div>
                {% endif %}
                {% if result.scoring.digit_points > 0 %}
                <div class="score-item">
                    <span>Numbers:</span>
                    <span>+{{ result.scoring.digit_points }} pts</span>
                </div>
                {% endif %}
                {% if result.scoring.special_char_points > 0 %}
                <div class="score-item">
                    <span>Special characters ({{ result.details.special_count }}):</span>
                    <span>+{{ result.scoring.special_char_points }} pts</span>
                </div>
                {% endif %}
                {% if result.scoring.special_bonus > 0 %}
                <div class="score-item bonus">
                    <span>Special char bonus:</span>
                    <span>+{{ result.scoring.special_bonus }} pts</span>
                </div>
                {% endif %}
                {% if result.scoring.complexity_bonus > 0 %}
                <div class="score-item bonus">
                    <span>All character types bonus:</span>
                    <span>+{{ result.scoring.complexity_bonus }} pts</span>
                </div>
                {% endif %}
                <div class="total-password-score">
                    Total: {{ result.score }} points
                </div>
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
        
        {% if uniqueness_bonus > 0 %}
        <div class="bonus-section">
            <h3>🌟 Uniqueness Bonus!</h3>
            <p>Your passwords are very different from each other!</p>
            <p style="font-size: 20px; font-weight: bold;">+{{ uniqueness_bonus }} points</p>
        </div>
        {% endif %}
        
        {% if similarity_warnings %}
        <div class="similarity-warning">
            <h3>⚠️ Password Similarity Warning</h3>
            {% for warning in similarity_warnings %}
            <p>{{ warning }}</p>
            {% endfor %}
            <p style="font-weight: bold; margin-top: 10px;">
                Penalty: -{{ penalty }} points
            </p>
        </div>
        {% endif %}
        
        <div class="final-score">
            🏆 Final Score: {{ final_score }} points
            <div style="font-size: 16px; margin-top: 10px; color: #cccccc;">
                (Maximum possible: ~45 points)
            </div>
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
    uniqueness_bonus = 0
    
    total_similarity = 0
    comparisons = 0
    
    # Compare each pair of passwords
    for i in range(len(passwords)):
        for j in range(i + 1, len(passwords)):
            similarity = calculate_similarity(passwords[i], passwords[j])
            total_similarity += similarity
            comparisons += 1
            
            if similarity > 80:
                similarity_warnings.append(f"Password {i+1} and {j+1} are very similar ({similarity:.0f}%)")
                penalty += 5
            elif similarity > 60:
                similarity_warnings.append(f"Password {i+1} and {j+1} are quite similar ({similarity:.0f}%)")
                penalty += 3
            elif similarity > 40:
                penalty += 1
    
    # Calculate average similarity
    avg_similarity = total_similarity / comparisons if comparisons > 0 else 0
    
    # Give bonus for very different passwords
    if avg_similarity < 20 and not similarity_warnings:
        uniqueness_bonus = 5
    elif avg_similarity < 30 and not similarity_warnings:
        uniqueness_bonus = 3
    
    return similarity_warnings, penalty, uniqueness_bonus

def evaluate_password_strength(password):
    """Enhanced password strength evaluation with detailed scoring"""
    score = 0
    scoring_breakdown = {
        'length_points': 0,
        'uppercase_points': 0,
        'lowercase_points': 0,
        'digit_points': 0,
        'special_char_points': 0,
        'special_bonus': 0,
        'complexity_bonus': 0
    }
    
    details = {
        'length': False,
        'length_chars': len(password),
        'uppercase': False,
        'lowercase': False,
        'digits': False,
        'special': False,
        'special_count': 0
    }
    
    # Length scoring (more generous)
    length = len(password)
    if length >= 15:
        scoring_breakdown['length_points'] = 8
        details['length'] = True
    elif length >= 12:
        scoring_breakdown['length_points'] = 6
        details['length'] = True
    elif length >= 10:
        scoring_breakdown['length_points'] = 4
        details['length'] = True
    elif length >= 8:
        scoring_breakdown['length_points'] = 2
        details['length'] = True
    else:
        scoring_breakdown['length_points'] = 0
    
    # Character type scoring
    if any(c.isupper() for c in password):
        scoring_breakdown['uppercase_points'] = 2
        details['uppercase'] = True
    
    if any(c.islower() for c in password):
        scoring_breakdown['lowercase_points'] = 2
        details['lowercase'] = True
    
    if any(c.isdigit() for c in password):
        scoring_breakdown['digit_points'] = 2
        details['digits'] = True
    
    # Special characters (enhanced scoring)
    special_chars = "!@#$%^&*()-_+=<>?/;:[]{}|~`"
    special_count = sum(1 for c in password if c in special_chars)
    details['special_count'] = special_count
    
    if special_count > 0:
        details['special'] = True
        scoring_breakdown['special_char_points'] = 2  # Base points for having specials
        
        # Bonus points for multiple special characters
        if special_count >= 4:
            scoring_breakdown['special_bonus'] = 5
        elif special_count >= 2:
            scoring_breakdown['special_bonus'] = 3
        else:
            scoring_breakdown['special_bonus'] = 1
    
    # Complexity bonus for using all character types
    if all([details['uppercase'], details['lowercase'], details['digits'], details['special']]):
        scoring_breakdown['complexity_bonus'] = 3
    
    # Calculate total score
    score = sum(scoring_breakdown.values())
    
    # Determine display percentage (for visual meter)
    max_possible_per_password = 21  # Maximum possible score per password
    display_percentage = min(100, (score / max_possible_per_password) * 100)
    
    # Determine level and color
    if score >= 15:
        level = "🔥 ULTRA STRONG"
        color = "#00ff00"
    elif score >= 12:
        level = "💪 Very Strong"
        color = "#00ff00"
    elif score >= 9:
        level = "🔐 Strong"
        color = "#90ee90"
    elif score >= 6:
        level = "😐 Medium"
        color = "#ffa500"
    elif score >= 3:
        level = "⚠️ Weak"
        color = "#ff6347"
    else:
        level = "💀 Very Weak"
        color = "#ff0000"
    
    return {
        'score': score,
        'level': level,
        'color': color,
        'details': details,
        'scoring': scoring_breakdown,
        'display_percentage': int(display_percentage)
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
    
    if result and result[0] == 1:  # is_completed = 1
        return True, result[1]  # Return completed status and score
    return False, 0

def save_game_progress(user_id, score, passwords=None):
    """Save or update game progress and store password hashes"""
    conn = sqlite3.connect('game.db')
    cursor = conn.cursor()
    
    try:
        print(f"[DEBUG] Saving progress for user {user_id}, score: {score}")
        
        # Create a new table for password hashes if needed
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pswd_hashes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                password_number INTEGER NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Store password hashes if provided
        if passwords:
            print(f"[DEBUG] Storing {len(passwords)} passwords")
            # Delete old passwords for this user
            cursor.execute('DELETE FROM pswd_hashes WHERE user_id = ?', (user_id,))
            
            # Insert new password hashes
            for i, pwd in enumerate(passwords, 1):
                pwd_hash = hashlib.sha256(pwd.encode()).hexdigest()
                cursor.execute('''
                    INSERT INTO pswd_hashes (user_id, password_number, password_hash)
                    VALUES (?, ?, ?)
                ''', (user_id, i, pwd_hash))
        
        # Check if record exists
        cursor.execute('''
            SELECT id, best_score, is_completed 
            FROM game_progress 
            WHERE user_id = ? AND game_name = 'pswd'
        ''', (user_id,))
        
        existing = cursor.fetchone()
        print(f"[DEBUG] Existing record: {existing}")
        
        if existing:
            record_id, old_score, was_completed = existing
            new_score = max(old_score, score)
            
            # Update existing record - ALWAYS set is_completed to 1
            cursor.execute('''
                UPDATE game_progress 
                SET is_completed = 1, 
                    best_score = ?, 
                    total_attempts = total_attempts + 1
                WHERE id = ?
            ''', (new_score, record_id))
            print(f"[DEBUG] Updated existing record with score {new_score}")
            
            # Update user total score (add the difference)
            if new_score > old_score:
                score_diff = new_score - old_score
                cursor.execute('''
                    UPDATE users 
                    SET total_score = total_score + ?
                    WHERE id = ?
                ''', (score_diff, user_id))
                print(f"[DEBUG] Updated user total score by +{score_diff}")
                
            # Update games completed if first time completing
            if was_completed == 0 or was_completed is None:  # Was not completed before
                cursor.execute('''
                    UPDATE users 
                    SET games_completed = games_completed + 1
                    WHERE id = ?
                ''', (user_id,))
                print(f"[DEBUG] Incremented games_completed")
        else:
            # Insert new record
            cursor.execute('''
                INSERT INTO game_progress (user_id, game_name, is_completed, best_score, total_attempts)
                VALUES (?, 'pswd', 1, ?, 1)
            ''', (user_id, score))
            print(f"[DEBUG] Inserted new record with score {score}")
            
            # Update user total score and games completed
            cursor.execute('''
                UPDATE users 
                SET total_score = total_score + ?, 
                    games_completed = games_completed + 1
                WHERE id = ?
            ''', (score, user_id))
            print(f"[DEBUG] Updated user stats: +{score} score, +1 game")
        
        conn.commit()
        print(f"[DEBUG] Save successful!")
        
    except Exception as e:
        print(f"[ERROR] Error saving game progress: {e}")
        import traceback
        traceback.print_exc()
        conn.rollback()
    finally:
        conn.close()

@pswd_app.route("/", methods=["GET", "POST"])
@login_required
def index():
    # Check if user has already completed the game
    completed, score = check_user_completed(current_user.id)
    print(f"[DEBUG] User {current_user.id} - Completed: {completed}, Score: {score}")
    
    if request.method == "POST" and not completed:
        # Get passwords
        password1 = request.form.get('password1', '')
        password2 = request.form.get('password2', '')
        password3 = request.form.get('password3', '')
        
        passwords = [password1, password2, password3]
        
        # Check for password similarity and uniqueness
        similarity_warnings, penalty, uniqueness_bonus = check_password_uniqueness(passwords)
        
        # Evaluate each password
        results = []
        total_password_score = 0
        
        for i, pwd in enumerate(passwords, 1):
            evaluation = evaluate_password_strength(pwd)
            total_password_score += evaluation['score']
                
            results.append({
                'number': i,
                'score': evaluation['score'],
                'level': evaluation['level'],
                'color': evaluation['color'],
                'details': evaluation['details'],
                'scoring': evaluation['scoring'],
                'display_percentage': evaluation['display_percentage']
            })
        
        # Calculate final score
        final_score = total_password_score + uniqueness_bonus - penalty
        final_score = max(0, int(final_score))  # Ensure non-negative integer
        
        # Save progress to database with passwords
        save_game_progress(current_user.id, final_score, passwords)
        
        # Store in session for results page
        session['password_results'] = results
        session['final_score'] = final_score
        session['similarity_warnings'] = similarity_warnings
        session['penalty'] = penalty
        session['uniqueness_bonus'] = uniqueness_bonus
        
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
    uniqueness_bonus = session.get('uniqueness_bonus', 0)
    
    if not results:
        return redirect('/pswdChecker/')
    
    # Clear session data
    session.pop('password_results', None)
    session.pop('final_score', None)
    session.pop('similarity_warnings', None)
    session.pop('penalty', None)
    session.pop('uniqueness_bonus', None)
    
    return render_template_string(PASSWORD_RESULTS_TEMPLATE, 
                                results=results, 
                                final_score=final_score,
                                similarity_warnings=similarity_warnings,
                                penalty=penalty,
                                uniqueness_bonus=uniqueness_bonus)