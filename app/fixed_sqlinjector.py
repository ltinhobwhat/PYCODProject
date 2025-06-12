import time
import sqlite3
import html
from flask import Blueprint, render_template_string, request, session, redirect, url_for, flash
from flask_login import login_required, current_user

sqlinjector_bp = Blueprint('sqlinjector', __name__)

# Enhanced levels with better progression
LEVELS = [
    {
        "id": 1,
        "title": "Basic Authentication Bypass",
        "description": "The login form has no protection. Try a classic SQL injection.",
        "hint": "What if you could make the WHERE clause always true? Think about OR conditions...",
        "solution_hints": ["' OR '1'='1", "' OR 1=1--", "admin' --"],
        "points": 5,
        "difficulty": "Beginner"
    },
    {
        "id": 2,
        "title": "Comment Attack",
        "description": "The system filters some characters but forgot about SQL comments.",
        "hint": "SQL comments can terminate the rest of a query. Try -- or #",
        "solution_hints": ["admin'--", "admin' --", "' OR 1=1--"],
        "points": 7,
        "difficulty": "Intermediate"
    },
    {
        "id": 3,
        "title": "Password Field Injection",
        "description": "The username field is protected, but what about the password?",
        "hint": "Sometimes developers only protect one field. Try injecting in the password field.",
        "solution_hints": ["' OR '1'='1", "' OR 1=1--", "anything' OR 'x'='x"],
        "points": 10,
        "difficulty": "Intermediate"
    },
    {
        "id": 4,
        "title": "Union-Based Attack",
        "description": "Can you extract data from other tables?",
        "hint": "UNION SELECT allows you to combine results. Try to match the column count.",
        "solution_hints": ["' UNION SELECT", "' UNION SELECT null", "' UNION SELECT 1,2,3--"],
        "points": 15,
        "difficulty": "Advanced"
    },
    {
        "id": 5,
        "title": "Blind Injection",
        "description": "No error messages shown. Use time-based or boolean-based injection.",
        "hint": "Try conditions that cause delays or different responses: ' AND SLEEP(5)--",
        "solution_hints": ["' AND 1=1--", "' AND SLEEP", "' OR IF("],
        "points": 20,
        "difficulty": "Expert"
    }
]

SQL_INJECTION_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SQL Injection Lab</title>
    <style>
        body {
            font-family: 'Courier New', monospace;
            background-color: #0a0a0a;
            color: #00ff00;
            margin: 0;
            padding: 20px;
            min-height: 100vh;
            background-image: 
                repeating-linear-gradient(
                    0deg,
                    rgba(0, 255, 0, 0.03),
                    rgba(0, 255, 0, 0.03) 1px,
                    transparent 1px,
                    transparent 2px
                );
        }
        
        .container {
            max-width: 900px;
            margin: 0 auto;
        }
        
        .header {
            text-align: center;
            margin-bottom: 30px;
            padding: 20px;
            border: 2px solid #00ff00;
            background: rgba(0, 0, 0, 0.8);
            box-shadow: 0 0 20px rgba(0, 255, 0, 0.5);
        }
        
        h1 {
            color: #00ff00;
            text-shadow: 0 0 10px #00ff00;
            margin: 0 0 10px 0;
            font-size: 2.5em;
        }
        
        .level-info {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin: 20px 0;
            padding: 15px;
            background: rgba(0, 255, 0, 0.1);
            border: 1px solid #00ff00;
        }
        
        .level-progress {
            display: flex;
            gap: 10px;
            margin: 20px 0;
        }
        
        .level-dot {
            width: 30px;
            height: 30px;
            border: 2px solid #00ff00;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            transition: all 0.3s;
        }
        
        .level-dot.completed {
            background: #00ff00;
            color: #000;
            box-shadow: 0 0 10px #00ff00;
        }
        
        .level-dot.current {
            animation: pulse 1.5s infinite;
        }
        
        @keyframes pulse {
            0% { box-shadow: 0 0 0 0 rgba(0, 255, 0, 0.7); }
            70% { box-shadow: 0 0 0 10px rgba(0, 255, 0, 0); }
            100% { box-shadow: 0 0 0 0 rgba(0, 255, 0, 0); }
        }
        
        .terminal {
            background: #000;
            border: 2px solid #00ff00;
            padding: 20px;
            margin: 20px 0;
            font-family: 'Courier New', monospace;
            box-shadow: 0 0 20px rgba(0, 255, 0, 0.3);
        }
        
        .terminal-header {
            color: #00ff00;
            margin-bottom: 15px;
            font-size: 1.2em;
        }
        
        .login-form {
            background: rgba(0, 0, 0, 0.7);
            border: 1px solid #00ff00;
            padding: 30px;
            margin: 20px 0;
        }
        
        .form-group {
            margin-bottom: 20px;
        }
        
        label {
            display: block;
            color: #00ff00;
            margin-bottom: 5px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        input[type="text"], input[type="password"] {
            width: 100%;
            padding: 10px;
            background: #000;
            border: 1px solid #00ff00;
            color: #00ff00;
            font-family: 'Courier New', monospace;
            font-size: 16px;
            box-sizing: border-box;
        }
        
        input[type="text"]:focus, input[type="password"]:focus {
            outline: none;
            box-shadow: 0 0 10px rgba(0, 255, 0, 0.5);
        }
        
        .sql-display {
            background: #111;
            border: 1px solid #00ff00;
            padding: 15px;
            margin: 20px 0;
            white-space: pre-wrap;
            word-break: break-all;
            font-size: 14px;
            color: #00ff00;
            position: relative;
            overflow-x: auto;
        }
        
        .sql-display::before {
            content: "GENERATED SQL:";
            position: absolute;
            top: -10px;
            left: 10px;
            background: #111;
            padding: 0 5px;
            font-size: 12px;
            color: #00ff00;
        }
        
        .button {
            background: transparent;
            border: 2px solid #00ff00;
            color: #00ff00;
            padding: 10px 20px;
            cursor: pointer;
            text-transform: uppercase;
            letter-spacing: 1px;
            font-family: 'Courier New', monospace;
            transition: all 0.3s;
            margin-right: 10px;
        }
        
        .button:hover {
            background: #00ff00;
            color: #000;
            box-shadow: 0 0 20px rgba(0, 255, 0, 0.5);
        }
        
        .hint-box {
            background: rgba(255, 165, 0, 0.1);
            border: 1px solid #ffa500;
            padding: 15px;
            margin: 20px 0;
            color: #ffa500;
            display: none;
        }
        
        .hint-box.show {
            display: block;
        }
        
        .result {
            padding: 20px;
            margin: 20px 0;
            border-radius: 5px;
            text-align: center;
            font-weight: bold;
            animation: fadeIn 0.5s;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(-10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .result.success {
            background: rgba(0, 255, 0, 0.2);
            border: 2px solid #00ff00;
            color: #00ff00;
        }
        
        .result.failure {
            background: rgba(255, 0, 0, 0.2);
            border: 2px solid #ff0000;
            color: #ff0000;
        }
        
        .stats {
            display: flex;
            justify-content: space-around;
            margin: 20px 0;
            padding: 20px;
            background: rgba(0, 0, 0, 0.5);
            border: 1px solid #00ff00;
        }
        
        .stat-item {
            text-align: center;
        }
        
        .stat-value {
            font-size: 2em;
            color: #00ff00;
            text-shadow: 0 0 10px #00ff00;
        }
        
        .stat-label {
            color: #888;
            text-transform: uppercase;
            font-size: 0.8em;
            margin-top: 5px;
        }
        
        .difficulty {
            padding: 5px 10px;
            border-radius: 3px;
            font-size: 0.8em;
            text-transform: uppercase;
        }
        
        .difficulty.Beginner { background: #00ff00; color: #000; }
        .difficulty.Intermediate { background: #ffa500; color: #000; }
        .difficulty.Advanced { background: #ff6347; color: #fff; }
        .difficulty.Expert { background: #ff0000; color: #fff; }
        
        .back-link {
            display: inline-block;
            margin: 20px 0;
            color: #00ff00;
            text-decoration: none;
            transition: all 0.3s;
        }
        
        .back-link:hover {
            text-shadow: 0 0 10px #00ff00;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔓 SQL Injection Laboratory</h1>
            <p>Master the art of SQL injection attacks</p>
        </div>
        
        <div class="level-progress">
            {% for i in range(1, total_levels + 1) %}
            <div class="level-dot {% if i < current_level %}completed{% elif i == current_level %}current{% endif %}">
                {{ i }}
            </div>
            {% endfor %}
        </div>
        
        <div class="level-info">
            <div>
                <h2>Level {{ current_level }}: {{ level_data.title }}</h2>
                <span class="difficulty {{ level_data.difficulty }}">{{ level_data.difficulty }}</span>
            </div>
            <div>
                <strong>Points: {{ level_data.points }}</strong>
            </div>
        </div>
        
        <div class="terminal">
            <div class="terminal-header">&gt; CHALLENGE DESCRIPTION</div>
            <p>{{ level_data.description }}</p>
        </div>
        
        <div class="login-form">
            <h3>Vulnerable Login Form</h3>
            <form method="POST" id="loginForm">
                <div class="form-group">
                    <label for="username">Username:</label>
                    <input type="text" id="username" name="username" autocomplete="off" 
                           placeholder="Enter username or injection">
                </div>
                <div class="form-group">
                    <label for="password">Password:</label>
                    <input type="password" id="password" name="password" autocomplete="off"
                           placeholder="Enter password or injection">
                </div>
                <button type="submit" class="button">Execute Query</button>
                <button type="button" class="button" onclick="toggleHint()">Show Hint</button>
            </form>
        </div>
        
        <div class="hint-box" id="hintBox">
            <strong>💡 Hint:</strong> {{ level_data.hint }}
        </div>
        
        {% if query %}
        <div class="sql-display">{{ query }}</div>
        {% endif %}
        
        {% if result %}
        <div class="result {{ 'success' if success else 'failure' }}">
            {{ result }}
            {% if success and not completed %}
            <form method="POST" action="{{ url_for('sqlinjector.next_level') }}" style="margin-top: 15px;">
                <button type="submit" class="button">Continue to Next Level →</button>
            </form>
            {% elif completed %}
            <div style="margin-top: 20px;">
                <p>🏆 Congratulations! You've mastered all SQL injection levels!</p>
                <p>Total Score: {{ total_score }} points</p>
                <a href="/menu/" class="button" style="text-decoration: none; display: inline-block; margin-top: 10px;">Back to Menu</a>
            </div>
            {% endif %}
        </div>
        {% endif %}
        
        <div class="stats">
            <div class="stat-item">
                <div class="stat-value">{{ attempts }}</div>
                <div class="stat-label">Attempts</div>
            </div>
            <div class="stat-item">
                <div class="stat-value">{{ score }}</div>
                <div class="stat-label">Score</div>
            </div>
            <div class="stat-item">
                <div class="stat-value">{{ time_elapsed }}</div>
                <div class="stat-label">Time</div>
            </div>
        </div>
        
        <a href="{{ url_for('sqlinjector.reset_levels') }}" class="back-link">↻ Reset Progress</a>
        <a href="/menu/" class="back-link">← Back to Menu</a>
    </div>
    
    <script>
        function toggleHint() {
            const hintBox = document.getElementById('hintBox');
            hintBox.classList.toggle('show');
        }
        
        // Auto-focus on username field
        document.getElementById('username').focus();
        
        // Add typing effect to SQL display
        {% if query %}
        const sqlDisplay = document.querySelector('.sql-display');
        const text = sqlDisplay.textContent;
        sqlDisplay.textContent = '';
        let i = 0;
        function typeWriter() {
            if (i < text.length) {
                sqlDisplay.textContent += text.charAt(i);
                i++;
                setTimeout(typeWriter, 20);
            }
        }
        typeWriter();
        {% endif %}
    </script>
</body>
</html>
"""

def check_injection(username, password, level):
    """Check if the injection is successful for the current level"""
    username_lower = username.lower()
    password_lower = password.lower()
    
    if level == 1:
        # Basic OR injection
        if ("' or '1'='1" in username_lower or "' or '1'='1" in password_lower or
            "' or 1=1" in username_lower or "' or 1=1" in password_lower or
            "admin' or" in username_lower):
            return True
            
    elif level == 2:
        # Comment-based injection
        if ("--" in username or "--" in password or
            "#" in username or "#" in password):
            # Must have proper injection before comment
            if ("admin'" in username_lower or "' or" in username_lower or 
                "' or" in password_lower):
                return True
                
    elif level == 3:
        # Password field only
        if username.lower() in ['admin', 'user', 'test']:  # Normal username
            if ("' or '1'='1" in password_lower or "' or 1=1" in password_lower or
                "' or 'x'='x" in password_lower):
                return True
                
    elif level == 4:
        # Union-based
        if ("union select" in username_lower or "union select" in password_lower):
            return True
            
    elif level == 5:
        # Blind injection simulation
        if ("and 1=1" in username_lower or "and 1=1" in password_lower or
            "and sleep" in username_lower or "and sleep" in password_lower or
            "or if(" in username_lower or "or if(" in password_lower):
            return True
            
    return False

def save_progress(user_id, score, completed):
    """Save progress to SQLite"""
    conn = sqlite3.connect('game.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT best_score, total_attempts 
        FROM game_progress 
        WHERE user_id = ? AND game_name = ?
    ''', (user_id, 'sqlinjector'))
    
    current = cursor.fetchone()
    
    if current:
        best_score = max(current[0], score)
        total_attempts = current[1] + 1
        cursor.execute('''
            UPDATE game_progress 
            SET is_completed = ?, best_score = ?, total_attempts = ?
            WHERE user_id = ? AND game_name = ?
        ''', (completed or current[0], best_score, total_attempts, user_id, 'sqlinjector'))
    else:
        cursor.execute('''
            INSERT INTO game_progress (user_id, game_name, is_completed, best_score, total_attempts)
            VALUES (?, ?, ?, ?, 1)
        ''', (user_id, 'sqlinjector', completed, score))
    
    if completed and (not current or not current[0]):
        cursor.execute('''
            UPDATE users 
            SET total_score = total_score + ?, games_completed = games_completed + 1
            WHERE id = ?
        ''', (score, user_id))
    
    conn.commit()
    conn.close()

@sqlinjector_bp.route("/", methods=["GET", "POST"])
@login_required
def index():
    # Initialize session
    if "sql_level" not in session:
        session["sql_level"] = 1
        session["sql_attempts"] = 0
        session["sql_score"] = 0
        session["sql_start_time"] = time.time()
    
    current_level = session.get("sql_level", 1)
    
    # Prevent going beyond available levels
    if current_level > len(LEVELS):
        current_level = len(LEVELS)
        session["sql_level"] = current_level
    
    level_data = LEVELS[current_level - 1]
    query = None
    result = None
    success = False
    completed = False
    
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        
        # Escape HTML to prevent display issues
        safe_username = html.escape(username)
        safe_password = html.escape(password)
        
        # Build the "vulnerable" query for display
        query = f"SELECT * FROM users WHERE username = '{safe_username}' AND password = '{safe_password}';"
        
        session["sql_attempts"] += 1
        
        # Check if injection is successful
        success = check_injection(username, password, current_level)
        
        if success:
            session["sql_score"] += level_data["points"]
            result = f"✅ Injection successful! You earned {level_data['points']} points!"
            
            # Check if all levels completed
            if current_level >= len(LEVELS):
                completed = True
                result = "🎉 All levels completed! You're now an SQL Injection expert!"
                save_progress(current_user.id, session["sql_score"], True)
        else:
            result = "❌ Injection failed. Try a different approach!"
    
    # Calculate time elapsed
    elapsed = int(time.time() - session.get("sql_start_time", time.time()))
    time_elapsed = f"{elapsed // 60}:{elapsed % 60:02d}"
    
    return render_template_string(
        SQL_INJECTION_TEMPLATE,
        current_level=current_level,
        total_levels=len(LEVELS),
        level_data=level_data,
        query=query,
        result=result,
        success=success,
        completed=completed,
        attempts=session.get("sql_attempts", 0),
        score=session.get("sql_score", 0),
        total_score=session.get("sql_score", 0),
        time_elapsed=time_elapsed
    )

@sqlinjector_bp.route("/next_level", methods=["POST"])
@login_required
def next_level():
    current_level = session.get("sql_level", 1)
    if current_level < len(LEVELS):
        session["sql_level"] = current_level + 1
    return redirect(url_for('sqlinjector.index'))

@sqlinjector_bp.route("/reset")
@login_required
def reset_levels():
    session.pop("sql_level", None)
    session.pop("sql_attempts", None)
    session.pop("sql_score", None)
    session.pop("sql_start_time", None)
    return redirect(url_for('sqlinjector.index'))
@sqlinjector_bp.route("/defender")
@login_required
def defender_redirect():
    return redirect(url_for('sqldefender.index'))