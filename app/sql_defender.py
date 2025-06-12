import time
import sqlite3
from flask import Blueprint, render_template_string, request, session, redirect, url_for
from flask_login import login_required, current_user

sqldefender_bp = Blueprint('sqldefender', __name__)

# Defense challenges
DEFENSE_CHALLENGES = [
    {
        "id": 1,
        "title": "Basic Input Sanitization",
        "vulnerable_code": """
def login(username, password):
    query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
    return execute_query(query)
""",
        "description": "This code is vulnerable to SQL injection. Fix it using parameterized queries.",
        "hint": "Use placeholders (?) and pass parameters separately",
        "correct_answers": [
            "query = \"SELECT * FROM users WHERE username=? AND password=?\"",
            "execute_query(query, (username, password))",
            "cursor.execute(\"SELECT * FROM users WHERE username=? AND password=?\", (username, password))"
        ],
        "points": 5
    },
    {
        "id": 2,
        "title": "Prepared Statements",
        "vulnerable_code": """
user_id = request.form['id']
query = "SELECT * FROM users WHERE id = " + user_id
cursor.execute(query)
""",
        "description": "Fix this concatenation vulnerability using prepared statements.",
        "hint": "Never concatenate user input directly into SQL queries",
        "correct_answers": [
            "cursor.execute(\"SELECT * FROM users WHERE id = ?\", (user_id,))",
            "query = \"SELECT * FROM users WHERE id = ?\"",
            "cursor.execute(\"SELECT * FROM users WHERE id = %s\", (user_id,))"
        ],
        "points": 7
    },
    {
        "id": 3,
        "title": "Input Validation",
        "vulnerable_code": """
search_term = request.args.get('search')
query = f"SELECT * FROM products WHERE name LIKE '%{search_term}%'"
""",
        "description": "Add input validation and use safe query methods.",
        "hint": "Validate input and use parameterized LIKE queries",
        "correct_answers": [
            "cursor.execute(\"SELECT * FROM products WHERE name LIKE ?\", (f'%{search_term}%',))",
            "cursor.execute(\"SELECT * FROM products WHERE name LIKE ?\", ('%' + search_term + '%',))",
            "if search_term and search_term.isalnum():"
        ],
        "points": 10
    },
    {
        "id": 4,
        "title": "Stored Procedures",
        "vulnerable_code": """
order_by = request.args.get('sort', 'name')
query = f"SELECT * FROM products ORDER BY {order_by}"
""",
        "description": "Dynamic ORDER BY is tricky. Implement a whitelist approach.",
        "hint": "Create a whitelist of allowed columns",
        "correct_answers": [
            "allowed_columns = ['name', 'price', 'date']",
            "if order_by in allowed_columns:",
            "order_by = 'name' if order_by not in allowed_columns else order_by"
        ],
        "points": 12
    },
    {
        "id": 5,
        "title": "Escape Special Characters",
        "vulnerable_code": """
comment = request.form['comment']
query = f"INSERT INTO comments (text) VALUES ('{comment}')"
""",
        "description": "Properly escape or parameterize this INSERT statement.",
        "hint": "Use parameterized queries for all user input",
        "correct_answers": [
            "cursor.execute(\"INSERT INTO comments (text) VALUES (?)\", (comment,))",
            "query = \"INSERT INTO comments (text) VALUES (?)\"",
            "cursor.execute(\"INSERT INTO comments (text) VALUES (%s)\", (comment,))"
        ],
        "points": 15
    }
]

SQL_DEFENDER_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SQL Defense Training</title>
    <style>
        body {
            font-family: 'Monaco', 'Courier New', monospace;
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
            max-width: 1000px;
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
        
        .shield-icon {
            font-size: 3em;
            margin-bottom: 10px;
        }
        
        .challenge-info {
            background: rgba(0, 0, 0, 0.7);
            border: 1px solid #00ff00;
            padding: 20px;
            margin: 20px 0;
            border-radius: 5px;
        }
        
        .challenge-title {
            font-size: 1.5em;
            color: #00ff00;
            margin-bottom: 15px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .points-badge {
            background: #00ff00;
            color: #000;
            padding: 5px 15px;
            border-radius: 15px;
            font-size: 0.8em;
        }
        
        .code-block {
            background: #1a1a1a;
            border: 1px solid #333;
            padding: 20px;
            margin: 15px 0;
            font-family: 'Monaco', monospace;
            white-space: pre-wrap;
            overflow-x: auto;
            position: relative;
        }
        
        .code-block.vulnerable {
            border-color: #ff4444;
            box-shadow: 0 0 10px rgba(255, 68, 68, 0.3);
        }
        
        .code-block.secure {
            border-color: #00ff00;
            box-shadow: 0 0 10px rgba(0, 255, 0, 0.3);
        }
        
        .code-label {
            position: absolute;
            top: -10px;
            left: 10px;
            background: #1a1a1a;
            padding: 0 10px;
            font-size: 0.8em;
            color: #ff4444;
        }
        
        .code-label.secure {
            color: #00ff00;
        }
        
        textarea {
            width: 100%;
            min-height: 150px;
            background: #000;
            border: 2px solid #00ff00;
            color: #00ff00;
            padding: 15px;
            font-family: 'Monaco', monospace;
            font-size: 14px;
            resize: vertical;
            box-sizing: border-box;
        }
        
        textarea:focus {
            outline: none;
            box-shadow: 0 0 15px rgba(0, 255, 0, 0.5);
        }
        
        .button-group {
            display: flex;
            gap: 10px;
            margin: 20px 0;
        }
        
        .button {
            background: transparent;
            border: 2px solid #00ff00;
            color: #00ff00;
            padding: 10px 20px;
            cursor: pointer;
            text-transform: uppercase;
            letter-spacing: 1px;
            font-family: inherit;
            transition: all 0.3s;
            text-decoration: none;
            display: inline-block;
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
        
        .progress-bar {
            background: #111;
            height: 30px;
            border: 1px solid #00ff00;
            margin: 20px 0;
            position: relative;
            overflow: hidden;
        }
        
        .progress-fill {
            background: linear-gradient(90deg, #00ff00, #00cc00);
            height: 100%;
            transition: width 0.5s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #000;
            font-weight: bold;
        }
        
        .stats {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 20px;
            margin: 20px 0;
        }
        
        .stat-card {
            background: rgba(0, 0, 0, 0.5);
            border: 1px solid #00ff00;
            padding: 15px;
            text-align: center;
        }
        
        .stat-value {
            font-size: 2em;
            color: #00ff00;
            text-shadow: 0 0 10px #00ff00;
        }
        
        .stat-label {
            color: #888;
            font-size: 0.9em;
            margin-top: 5px;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(-10px); }
            to { opacity: 1; transform: translateY(0); }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="shield-icon">🛡️</div>
            <h1>SQL Defense Training</h1>
            <p>Learn to protect against SQL injection attacks</p>
        </div>
        
        <div class="progress-bar">
            <div class="progress-fill" style="width: {{ progress }}%">
                {{ current_challenge }}/{{ total_challenges }} Challenges
            </div>
        </div>
        
        <div class="challenge-info">
            <div class="challenge-title">
                <span>Challenge {{ current_challenge }}: {{ challenge.title }}</span>
                <span class="points-badge">{{ challenge.points }} points</span>
            </div>
            <p>{{ challenge.description }}</p>
        </div>
        
        <div class="code-block vulnerable">
            <span class="code-label">⚠️ VULNERABLE CODE</span>
{{ challenge.vulnerable_code }}
        </div>
        
        <form method="POST">
            <label style="display: block; margin: 20px 0 10px; font-size: 1.1em;">
                📝 Write the secure version:
            </label>
            <textarea name="solution" placeholder="Write your secure code here..." required>{{ previous_answer }}</textarea>
            
            <div class="button-group">
                <button type="submit" class="button">Submit Solution</button>
                <button type="button" class="button" onclick="toggleHint()">Show Hint</button>
            </div>
        </form>
        
        <div class="hint-box" id="hintBox">
            <strong>💡 Hint:</strong> {{ challenge.hint }}
        </div>
        
        {% if result %}
        <div class="result {{ 'success' if success else 'failure' }}">
            {{ result }}
            {% if success and current_challenge < total_challenges %}
            <form method="POST" action="{{ url_for('sqldefender.next_challenge') }}" style="margin-top: 15px;">
                <button type="submit" class="button">Next Challenge →</button>
            </form>
            {% elif current_challenge >= total_challenges and success %}
            <div style="margin-top: 20px;">
                <p>🏆 Congratulations! You've completed all defense challenges!</p>
                <p>Total Score: {{ total_score }} points</p>
                <a href="/menu/" class="button">Back to Menu</a>
            </div>
            {% endif %}
        </div>
        {% endif %}
        
        <div class="stats">
            <div class="stat-card">
                <div class="stat-value">{{ score }}</div>
                <div class="stat-label">Current Score</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{{ attempts }}</div>
                <div class="stat-label">Attempts</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{{ time_elapsed }}</div>
                <div class="stat-label">Time Elapsed</div>
            </div>
        </div>
        
        <div style="text-align: center; margin-top: 30px;">
            <a href="/sqlinjector" class="button" style="margin-right: 10px;">⚔️ Try Injection Mode</a>
            <a href="/menu/" class="button">← Back to Menu</a>
        </div>
    </div>
    
    <script>
        function toggleHint() {
            const hintBox = document.getElementById('hintBox');
            hintBox.classList.toggle('show');
        }
        
        // Auto-resize textarea
        const textarea = document.querySelector('textarea');
        textarea.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = this.scrollHeight + 'px';
        });
    </script>
</body>
</html>
"""

def check_solution(solution, correct_answers):
    """Check if the solution contains correct secure coding practices"""
    solution_lower = solution.lower().strip()
    
    # Remove extra spaces and normalize
    solution_normalized = ' '.join(solution_lower.split())
    
    for correct in correct_answers:
        correct_normalized = ' '.join(correct.lower().split())
        if correct_normalized in solution_normalized:
            return True
    
    # Check for common secure patterns
    secure_patterns = [
        "cursor.execute(",
        "?,",
        "%s,",
        "parameterized",
        "prepared statement",
        "whitelist",
        "allowed_"
    ]
    
    matches = sum(1 for pattern in secure_patterns if pattern in solution_lower)
    return matches >= 2

def save_defender_progress(user_id, score):
    """Save SQL Defender progress"""
    conn = sqlite3.connect('game.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT best_score, total_attempts 
        FROM game_progress 
        WHERE user_id = ? AND game_name = ?
    ''', (user_id, 'sqldefender'))
    
    current = cursor.fetchone()
    
    if current:
        best_score = max(current[0], score)
        total_attempts = current[1] + 1
        cursor.execute('''
            UPDATE game_progress 
            SET is_completed = ?, best_score = ?, total_attempts = ?
            WHERE user_id = ? AND game_name = ?
        ''', (score > 0, best_score, total_attempts, user_id, 'sqldefender'))
    else:
        cursor.execute('''
            INSERT INTO game_progress (user_id, game_name, is_completed, best_score, total_attempts)
            VALUES (?, ?, ?, ?, 1)
        ''', (user_id, 'sqldefender', score > 0, score))
    
    # Update user total score only for new high scores
    if not current or score > current[0]:
        score_diff = score - (current[0] if current else 0)
        cursor.execute('''
            UPDATE users 
            SET total_score = total_score + ?
            WHERE id = ?
        ''', (score_diff, user_id))
        
        # Update games completed if first time completing
        if not current and score > 0:
            cursor.execute('''
                UPDATE users 
                SET games_completed = games_completed + 1
                WHERE id = ?
            ''', (user_id,))
    
    conn.commit()
    conn.close()

@sqldefender_bp.route("/", methods=["GET", "POST"])
@login_required
def index():
    # Initialize session
    if "defender_challenge" not in session:
        session["defender_challenge"] = 1
        session["defender_score"] = 0
        session["defender_attempts"] = 0
        session["defender_start_time"] = time.time()
    
    current = session.get("defender_challenge", 1)
    
    if current > len(DEFENSE_CHALLENGES):
        current = len(DEFENSE_CHALLENGES)
        session["defender_challenge"] = current
    
    challenge = DEFENSE_CHALLENGES[current - 1]
    result = None
    success = False
    previous_answer = ""
    
    if request.method == "POST":
        solution = request.form.get("solution", "")
        previous_answer = solution
        session["defender_attempts"] += 1
        
        if check_solution(solution, challenge["correct_answers"]):
            session["defender_score"] += challenge["points"]
            result = f"✅ Excellent! Your solution is secure. +{challenge['points']} points!"
            success = True
            
            if current >= len(DEFENSE_CHALLENGES):
                save_defender_progress(current_user.id, session["defender_score"])
        else:
            result = "❌ Not quite right. Make sure you're using parameterized queries or proper validation."
    
    # Calculate stats
    elapsed = int(time.time() - session.get("defender_start_time", time.time()))
    time_elapsed = f"{elapsed // 60}:{elapsed % 60:02d}"
    progress = int((current - 1) / len(DEFENSE_CHALLENGES) * 100)
    
    return render_template_string(
        SQL_DEFENDER_TEMPLATE,
        challenge=challenge,
        current_challenge=current,
        total_challenges=len(DEFENSE_CHALLENGES),
        progress=progress,
        score=session.get("defender_score", 0),
        total_score=session.get("defender_score", 0),
        attempts=session.get("defender_attempts", 0),
        time_elapsed=time_elapsed,
        result=result,
        success=success,
        previous_answer=previous_answer
    )

@sqldefender_bp.route("/next", methods=["POST"])
@login_required
def next_challenge():
    current = session.get("defender_challenge", 1)
    if current < len(DEFENSE_CHALLENGES):
        session["defender_challenge"] = current + 1
    return redirect(url_for('sqldefender.index'))

@sqldefender_bp.route("/reset")
@login_required
def reset():
    session.pop("defender_challenge", None)
    session.pop("defender_score", None)
    session.pop("defender_attempts", None)
    session.pop("defender_start_time", None)
    return redirect(url_for('sqldefender.index'))