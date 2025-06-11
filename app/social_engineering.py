import hashlib
import sqlite3
from flask import Blueprint, render_template_string, request, session, redirect, flash
from flask_login import login_required, current_user

social_bp = Blueprint('social', __name__)

# Social Engineering Messages
SOCIAL_MESSAGES = [
    {
        "title": "📧 Email from IT Department",
        "content": """Dear Employee,

We've detected unusual activity on your account. As part of our security protocol, we need to verify your identity.

Please confirm your account details in the next window.

Remember: Always be cautious of phishing attempts!""",
        "sender": "it-support@company.com"
    },
    {
        "title": "💬 Instant Message",
        "content": """Hey! It's Mike from IT. 

I'm updating the security system and noticed your account needs verification. 

Can you help me out real quick? I'll need to verify your credentials.

PS: This is exactly how social engineering attacks start!""",
        "sender": "Mike_IT_Support"
    },
    {
        "title": "📱 SMS Alert",
        "content": """URGENT: Your account will be locked in 24 hours!

Click the link below to prevent this:
[SUSPICIOUS-LINK-REMOVED]

Warning: Never click on suspicious links in real life!""",
        "sender": "+1-555-SCAM"
    },
    {
        "title": "🎁 Prize Notification",
        "content": """CONGRATULATIONS! 

You've won our monthly security awareness lottery!

To claim your prize, we just need to verify your identity...

Remember: If it seems too good to be true, it probably is!""",
        "sender": "definitely-not-a-scam@lottery.com"
    },
    {
        "title": "🔐 Security Test",
        "content": """This has been a social engineering awareness test!

In real attacks, hackers use these tactics to steal your passwords.

Now, let's see if you remember YOUR passwords from the first challenge...

The best defense is a good memory!""",
        "sender": "CyberSec Academy"
    }
]

MAIN_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Social Engineering Challenge</title>
    <style>
        body {
            font-family: 'Segoe UI', Arial, sans-serif;
            background: linear-gradient(135deg, #0f0f23 0%, #1a1a3a 100%);
            color: #ffffff;
            min-height: 100vh;
            margin: 0;
            padding: 20px;
            display: flex;
            justify-content: center;
            align-items: center;
        }
        
        .container {
            background-color: rgba(42, 42, 42, 0.95);
            padding: 40px;
            border-radius: 15px;
            box-shadow: 0 0 30px rgba(0, 255, 136, 0.3);
            max-width: 600px;
            width: 100%;
            border: 2px solid rgba(0, 255, 136, 0.3);
        }
        
        h1 {
            text-align: center;
            color: #00ff88;
            text-shadow: 0 0 15px rgba(0, 255, 136, 0.5);
            margin-bottom: 30px;
            font-size: 2.5rem;
        }
        
        .locked-message {
            background: rgba(255, 69, 69, 0.2);
            border: 2px solid rgba(255, 69, 69, 0.5);
            border-radius: 10px;
            padding: 20px;
            text-align: center;
            margin: 20px 0;
        }
        
        .locked-message h2 {
            color: #ff4545;
            margin-bottom: 15px;
        }
        
        .locked-message p {
            color: #ffaaaa;
            line-height: 1.6;
        }
        
        .requirements {
            background: rgba(0, 0, 0, 0.3);
            border-radius: 10px;
            padding: 20px;
            margin: 20px 0;
        }
        
        .requirements h3 {
            color: #00ff88;
            margin-bottom: 15px;
        }
        
        .game-list {
            list-style: none;
            padding: 0;
        }
        
        .game-item {
            padding: 10px;
            margin: 5px 0;
            border-radius: 5px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .game-item.completed {
            background: rgba(0, 255, 136, 0.1);
            border: 1px solid rgba(0, 255, 136, 0.3);
        }
        
        .game-item.not-completed {
            background: rgba(255, 69, 69, 0.1);
            border: 1px solid rgba(255, 69, 69, 0.3);
        }
        
        .status-icon {
            font-size: 1.2rem;
        }
        
        .start-button {
            display: block;
            width: 100%;
            padding: 15px;
            background: linear-gradient(135deg, #00ff88, #00cc6a);
            color: #000000;
            border: none;
            border-radius: 10px;
            font-size: 1.2rem;
            font-weight: bold;
            cursor: pointer;
            text-align: center;
            text-decoration: none;
            margin-top: 30px;
            transition: all 0.3s ease;
        }
        
        .start-button:hover {
            background: linear-gradient(135deg, #00cc6a, #009955);
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0, 255, 136, 0.4);
        }
        
        .start-button:disabled {
            background: #666;
            cursor: not-allowed;
            transform: none;
        }
        
        .back-link {
            display: block;
            text-align: center;
            margin-top: 20px;
            color: #00ff88;
            text-decoration: none;
        }
        
        .back-link:hover {
            text-decoration: underline;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎭 Social Engineering Challenge</h1>
        
        {% if not can_access %}
        <div class="locked-message">
            <h2>🔒 Challenge Locked</h2>
            <p>This advanced challenge requires you to score at least 1 point in ALL other challenges first!</p>
            <p>Complete the challenges below to unlock this final test.</p>
        </div>
        
        <div class="requirements">
            <h3>Challenge Progress:</h3>
            <ul class="game-list">
                {% for game, status in game_status.items() %}
                <li class="game-item {% if status.completed %}completed{% else %}not-completed{% endif %}">
                    <span>{{ status.name }}</span>
                    <span class="status-icon">
                        {% if status.completed %}
                            ✅ Score: {{ status.score }}
                        {% else %}
                            ❌ Not completed
                        {% endif %}
                    </span>
                </li>
                {% endfor %}
            </ul>
        </div>
        
        <button class="start-button" disabled>Complete All Challenges First</button>
        
        {% else %}
        <div class="requirements" style="background: rgba(0, 255, 136, 0.1); border: 2px solid rgba(0, 255, 136, 0.3);">
            <h3 style="text-align: center;">🎯 Challenge Unlocked!</h3>
            <p style="text-align: center; margin: 20px 0;">
                Test your awareness against social engineering tactics and see if you remember your passwords!
            </p>
            <p style="text-align: center; color: #00ff88; font-weight: bold;">
                Warning: This challenge will test your memory of the passwords you created earlier.
            </p>
        </div>
        
        <form method="POST">
            <button type="submit" class="start-button">Start Social Engineering Test</button>
        </form>
        {% endif %}
        
        <a href="/map/" class="back-link">← Back to Challenge Map</a>
    </div>
</body>
</html>
"""

MESSAGE_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Social Engineering - Message {{ current }}/{{ total }}</title>
    <style>
        body {
            font-family: 'Segoe UI', Arial, sans-serif;
            background: linear-gradient(135deg, #0f0f23 0%, #1a1a3a 100%);
            color: #ffffff;
            min-height: 100vh;
            margin: 0;
            padding: 20px;
            display: flex;
            justify-content: center;
            align-items: center;
        }
        
        .message-container {
            background-color: rgba(42, 42, 42, 0.95);
            padding: 40px;
            border-radius: 15px;
            box-shadow: 0 0 30px rgba(0, 255, 136, 0.3);
            max-width: 700px;
            width: 100%;
            border: 2px solid rgba(0, 255, 136, 0.3);
        }
        
        .progress-bar {
            background: rgba(0, 0, 0, 0.3);
            height: 10px;
            border-radius: 5px;
            margin-bottom: 30px;
            overflow: hidden;
        }
        
        .progress-fill {
            background: linear-gradient(90deg, #00ff88, #00cc6a);
            height: 100%;
            transition: width 0.3s ease;
        }
        
        .message-header {
            background: rgba(0, 0, 0, 0.3);
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
        }
        
        .message-title {
            color: #00ff88;
            font-size: 1.5rem;
            margin-bottom: 10px;
        }
        
        .message-sender {
            color: #888;
            font-size: 0.9rem;
        }
        
        .message-content {
            background: rgba(255, 255, 255, 0.05);
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
            line-height: 1.8;
            font-size: 1.1rem;
            white-space: pre-line;
        }
        
        .next-button {
            display: block;
            width: 100%;
            padding: 15px;
            background: linear-gradient(135deg, #00ff88, #00cc6a);
            color: #000000;
            border: none;
            border-radius: 10px;
            font-size: 1.2rem;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .next-button:hover {
            background: linear-gradient(135deg, #00cc6a, #009955);
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0, 255, 136, 0.4);
        }
        
        .warning-note {
            background: rgba(255, 165, 0, 0.1);
            border: 1px solid rgba(255, 165, 0, 0.3);
            padding: 15px;
            border-radius: 5px;
            margin-top: 20px;
            text-align: center;
            color: #ffa500;
        }
    </style>
</head>
<body>
    <div class="message-container">
        <div class="progress-bar">
            <div class="progress-fill" style="width: {{ (current / total * 100)|int }}%"></div>
        </div>
        
        <div class="message-header">
            <h2 class="message-title">{{ message.title }}</h2>
            <div class="message-sender">From: {{ message.sender }}</div>
        </div>
        
        <div class="message-content">{{ message.content }}</div>
        
        <form method="POST">
            <button type="submit" class="next-button">
                {% if current < total %}
                    Next Message →
                {% else %}
                    Proceed to Password Test →
                {% endif %}
            </button>
        </form>
        
        <div class="warning-note">
            ⚠️ Educational Content: Learn to recognize social engineering tactics
        </div>
    </div>
</body>
</html>
"""

PASSWORD_TEST_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Social Engineering - Password Memory Test</title>
    <style>
        body {
            font-family: 'Segoe UI', Arial, sans-serif;
            background: linear-gradient(135deg, #0f0f23 0%, #1a1a3a 100%);
            color: #ffffff;
            min-height: 100vh;
            margin: 0;
            padding: 20px;
            display: flex;
            justify-content: center;
            align-items: center;
        }
        
        .test-container {
            background-color: rgba(42, 42, 42, 0.95);
            padding: 40px;
            border-radius: 15px;
            box-shadow: 0 0 30px rgba(0, 255, 136, 0.3);
            max-width: 600px;
            width: 100%;
            border: 2px solid rgba(0, 255, 136, 0.3);
        }
        
        h1 {
            text-align: center;
            color: #00ff88;
            text-shadow: 0 0 15px rgba(0, 255, 136, 0.5);
            margin-bottom: 30px;
        }
        
        .test-intro {
            background: rgba(0, 0, 0, 0.3);
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 30px;
            text-align: center;
            line-height: 1.6;
        }
        
        .password-group {
            margin-bottom: 25px;
        }
        
        label {
            display: block;
            margin-bottom: 8px;
            color: #00ff88;
            font-weight: bold;
        }
        
        input[type="password"] {
            width: 100%;
            padding: 12px;
            background-color: #1a1a1a;
            border: 2px solid #00ff88;
            color: #ffffff;
            border-radius: 5px;
            font-size: 16px;
            box-sizing: border-box;
        }
        
        input[type="password"]:focus {
            outline: none;
            border-color: #00ff88;
            box-shadow: 0 0 10px rgba(0, 255, 136, 0.5);
        }
        
        .submit-button {
            display: block;
            width: 100%;
            padding: 15px;
            background: linear-gradient(135deg, #00ff88, #00cc6a);
            color: #000000;
            border: none;
            border-radius: 10px;
            font-size: 1.2rem;
            font-weight: bold;
            cursor: pointer;
            margin-top: 30px;
            transition: all 0.3s ease;
        }
        
        .submit-button:hover {
            background: linear-gradient(135deg, #00cc6a, #009955);
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0, 255, 136, 0.4);
        }
        
        .hint {
            background: rgba(255, 165, 0, 0.1);
            border: 1px solid rgba(255, 165, 0, 0.3);
            padding: 15px;
            border-radius: 5px;
            margin-top: 20px;
            color: #ffa500;
            font-size: 0.9rem;
        }
    </style>
</head>
<body>
    <div class="test-container">
        <h1>🧠 Password Memory Test</h1>
        
        <div class="test-intro">
            <p><strong>The Ultimate Test!</strong></p>
            <p>Do you remember the three passwords you created in the Password Security challenge?</p>
            <p>Enter them below in the same order. Your memory is your best defense!</p>
        </div>
        
        <form method="POST">
            <div class="password-group">
                <label for="password1">First Password:</label>
                <input type="password" id="password1" name="password1" placeholder="Enter your first password" required>
            </div>
            
            <div class="password-group">
                <label for="password2">Second Password:</label>
                <input type="password" id="password2" name="password2" placeholder="Enter your second password" required>
            </div>
            
            <div class="password-group">
                <label for="password3">Third Password:</label>
                <input type="password" id="password3" name="password3" placeholder="Enter your third password" required>
            </div>
            
            <button type="submit" class="submit-button">Submit Passwords</button>
        </form>
        
        <div class="hint">
            💡 Hint: Strong passwords are memorable but hard to guess. Did you use a pattern?
        </div>
    </div>
</body>
</html>
"""

RESULTS_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Social Engineering - Results</title>
    <style>
        body {
            font-family: 'Segoe UI', Arial, sans-serif;
            background: linear-gradient(135deg, #0f0f23 0%, #1a1a3a 100%);
            color: #ffffff;
            min-height: 100vh;
            margin: 0;
            padding: 20px;
            display: flex;
            justify-content: center;
            align-items: center;
        }
        
        .results-container {
            background-color: rgba(42, 42, 42, 0.95);
            padding: 40px;
            border-radius: 15px;
            box-shadow: 0 0 30px rgba(0, 255, 136, 0.3);
            max-width: 600px;
            width: 100%;
            border: 2px solid rgba(0, 255, 136, 0.3);
        }
        
        h1 {
            text-align: center;
            color: #00ff88;
            text-shadow: 0 0 15px rgba(0, 255, 136, 0.5);
            margin-bottom: 30px;
        }
        
        .result-item {
            background: rgba(0, 0, 0, 0.3);
            padding: 15px;
            border-radius: 10px;
            margin: 10px 0;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .result-item.correct {
            border: 2px solid rgba(0, 255, 136, 0.5);
        }
        
        .result-item.incorrect {
            border: 2px solid rgba(255, 69, 69, 0.5);
        }
        
        .score-summary {
            background: rgba(0, 255, 136, 0.1);
            border: 2px solid rgba(0, 255, 136, 0.3);
            padding: 20px;
            border-radius: 10px;
            margin: 30px 0;
            text-align: center;
        }
        
        .score-value {
            font-size: 3rem;
            font-weight: bold;
            color: #00ff88;
            text-shadow: 0 0 20px rgba(0, 255, 136, 0.5);
        }
        
        .score-breakdown {
            margin-top: 15px;
            font-size: 0.9rem;
            color: #aaa;
        }
        
        .lesson-learned {
            background: rgba(255, 165, 0, 0.1);
            border: 1px solid rgba(255, 165, 0, 0.3);
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
            line-height: 1.6;
        }
        
        .back-button {
            display: block;
            width: 200px;
            margin: 30px auto 0;
            padding: 12px;
            background: #00ff88;
            color: #000000;
            text-align: center;
            text-decoration: none;
            border-radius: 10px;
            font-weight: bold;
            transition: all 0.3s ease;
        }
        
        .back-button:hover {
            background: #00cc6a;
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0, 255, 136, 0.4);
        }
    </style>
</head>
<body>
    <div class="results-container">
        <h1>🎭 Challenge Complete!</h1>
        
        <div class="result-item {% if results[0] %}correct{% else %}incorrect{% endif %}">
            <span>Password 1</span>
            <span>{% if results[0] %}✅ Correct{% else %}❌ Incorrect{% endif %}</span>
        </div>
        
        <div class="result-item {% if results[1] %}correct{% else %}incorrect{% endif %}">
            <span>Password 2</span>
            <span>{% if results[1] %}✅ Correct{% else %}❌ Incorrect{% endif %}</span>
        </div>
        
        <div class="result-item {% if results[2] %}correct{% else %}incorrect{% endif %}">
            <span>Password 3</span>
            <span>{% if results[2] %}✅ Correct{% else %}❌ Incorrect{% endif %}</span>
        </div>
        
        <div class="score-summary">
            <div class="score-value">{{ final_score }}</div>
            <div>Final Score</div>
            <div class="score-breakdown">
                Original score: {{ original_score }} | 
                Multiplier: {{ multiplier }}x | 
                Correct: {{ correct_count }}/3
            </div>
        </div>
        
        <div class="lesson-learned">
            <h3 style="color: #ffa500; margin-top: 0;">🎓 Lesson Learned</h3>
            {% if correct_count == 3 %}
                <p>Excellent memory! You remembered all your passwords. This is crucial for security - never share or write down passwords where others can find them.</p>
            {% elif correct_count >= 1 %}
                <p>Good effort! You remembered some passwords. In real life, using a password manager can help you maintain strong, unique passwords without relying on memory alone.</p>
            {% else %}
                <p>Password memory is challenging! This shows why many people fall for social engineering - they panic and share passwords they can't remember. Consider using a password manager.</p>
            {% endif %}
            <p style="margin-bottom: 0;"><strong>Remember:</strong> Social engineers exploit human psychology. Stay vigilant and never share passwords, even under pressure!</p>
        </div>
        
        <a href="/map/" class="back-button">Back to Map</a>
    </div>
</body>
</html>
"""

def check_all_games_completed(user_id):
    """Check if user has scored at least 1 point in all other games"""
    conn = sqlite3.connect('game.db')
    cursor = conn.cursor()
    
    required_games = ['pswd', 'quiz', 'vigenere', 'hashgame', 'sqlinjector']
    game_status = {}
    all_completed = True
    
    for game in required_games:
        cursor.execute('''
            SELECT is_completed, best_score 
            FROM game_progress 
            WHERE user_id = ? AND game_name = ?
        ''', (user_id, game))
        
        result = cursor.fetchone()
        
        game_names = {
            'pswd': 'Password Security',
            'quiz': 'Security Quiz',
            'vigenere': 'Vigenère Cipher',
            'hashgame': 'Hash Detective',
            'sqlinjector': 'SQL Injection'
        }
        
        if result and result[0] and result[1] > 0:  # completed and score > 0
            game_status[game] = {
                'completed': True,
                'score': result[1],
                'name': game_names[game]
            }
        else:
            game_status[game] = {
                'completed': False,
                'score': 0,
                'name': game_names[game]
            }
            all_completed = False
    
    conn.close()
    return all_completed, game_status

def get_user_password_hashes(user_id):
    """Get the password hashes from the user's password game"""
    conn = sqlite3.connect('game.db')
    cursor = conn.cursor()
    
    # Get the 3 most recent password hashes for this user
    cursor.execute('''
        SELECT password_hash 
        FROM user_passwords 
        WHERE user_id = ? 
        ORDER BY id DESC 
        LIMIT 3
    ''', (user_id,))
    
    results = cursor.fetchall()
    conn.close()
    
    # Reverse to get original order (1st, 2nd, 3rd)
    if results:
        return [r[0] for r in reversed(results)]
    return []

def update_user_score_with_multiplier(user_id, multiplier):
    """Update user's total score with multiplier"""
    conn = sqlite3.connect('game.db')
    cursor = conn.cursor()
    
    try:
        # Get current total score
        cursor.execute('SELECT total_score FROM users WHERE id = ?', (user_id,))
        current_score = cursor.fetchone()[0] or 0
        
        # Calculate new score
        new_score = int(current_score * multiplier)
        
        # Update score
        cursor.execute('UPDATE users SET total_score = ? WHERE id = ?', (new_score, user_id))
        
        # Mark social engineering as completed
        cursor.execute('''
            INSERT OR REPLACE INTO game_progress 
            (user_id, game_name, is_completed, best_score, total_attempts)
            VALUES (?, 'social', 1, ?, 1)
        ''', (user_id, new_score - current_score))
        
        conn.commit()
        return current_score, new_score
        
    except Exception as e:
        print(f"Error updating score: {e}")
        conn.rollback()
        return 0, 0
    finally:
        conn.close()

@social_bp.route('/', methods=['GET', 'POST'])
@login_required
def index():
    can_access, game_status = check_all_games_completed(current_user.id)
    
    if request.method == 'POST' and can_access:
        # Start the social engineering messages
        session['social_message_index'] = 0
        return redirect('/social/message')
    
    return render_template_string(MAIN_TEMPLATE, 
                                can_access=can_access, 
                                game_status=game_status)

@social_bp.route('/message', methods=['GET', 'POST'])
@login_required
def show_message():
    message_index = session.get('social_message_index', 0)
    
    if message_index >= len(SOCIAL_MESSAGES):
        return redirect('/social/test')
    
    if request.method == 'POST':
        # Move to next message
        session['social_message_index'] = message_index + 1
        return redirect('/social/message')
    
    return render_template_string(MESSAGE_TEMPLATE,
                                message=SOCIAL_MESSAGES[message_index],
                                current=message_index + 1,
                                total=len(SOCIAL_MESSAGES))

@social_bp.route('/test', methods=['GET', 'POST'])
@login_required
def password_test():
    if request.method == 'POST':
        # Get submitted passwords
        submitted_passwords = [
            request.form.get('password1', ''),
            request.form.get('password2', ''),
            request.form.get('password3', '')
        ]
        
        # Get original password hashes
        original_hashes = get_user_password_hashes(current_user.id)
        
        if not original_hashes:
            flash("Error: Could not retrieve your original passwords.", "error")
            return redirect('/social/')
        
        # Check each password
        results = []
        correct_count = 0
        
        for i, submitted_pwd in enumerate(submitted_passwords):
            submitted_hash = hashlib.sha256(submitted_pwd.encode()).hexdigest()
            if i < len(original_hashes) and submitted_hash == original_hashes[i]:
                results.append(True)
                correct_count += 1
            else:
                results.append(False)
        
        # Calculate multiplier based on correct passwords
        if correct_count == 3:
            multiplier = 1.5  # All correct: 50% bonus
        elif correct_count == 2:
            multiplier = 1.3  # Two correct: 30% bonus
        elif correct_count == 1:
            multiplier = 1.1  # One correct: 10% bonus
        else:
            multiplier = 0.7  # None correct: 30% penalty
        
        # Update user score
        original_score, new_score = update_user_score_with_multiplier(current_user.id, multiplier)
        
        # Store results in session
        session['social_results'] = {
            'results': results,
            'correct_count': correct_count,
            'multiplier': multiplier,
            'original_score': original_score,
            'final_score': new_score
        }
        
        # Clear message index
        session.pop('social_message_index', None)
        
        return redirect('/social/results')
    
    return render_template_string(PASSWORD_TEST_TEMPLATE)

@social_bp.route('/results')
@login_required
def results():
    results_data = session.get('social_results')
    
    if not results_data:
        return redirect('/social/')
    
    # Clear session data
    session.pop('social_results', None)
    
    return render_template_string(RESULTS_TEMPLATE,
                                results=results_data['results'],
                                correct_count=results_data['correct_count'],
                                multiplier=results_data['multiplier'],
                                original_score=results_data['original_score'],
                                final_score=results_data['final_score'])