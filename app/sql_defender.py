import time
import sqlite3
from flask import Blueprint, render_template_string, request, session, redirect, url_for
from flask_login import login_required, current_user

sqldefender_bp = Blueprint('sqldefender', __name__)

# Defense challenges with clearer examples
DEFENSE_CHALLENGES = [
    {
        "id": 1,
        "title": "Basic Input Sanitization",
        "vulnerable_code": """def login(username, password):
    query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
    return execute_query(query)""",
        "description": "This code is vulnerable to SQL injection. Fix it using parameterized queries.",
        "hint": """Use placeholders (?) and pass parameters separately. Example:
cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))

The key is to NEVER put user input directly in the SQL string!""",
        "example_solution": """def login(username, password):
    query = "SELECT * FROM users WHERE username=? AND password=?"
    return execute_query(query, (username, password))""",
        "correct_patterns": [
            "username=?",
            "password=?",
            "(username, password)",
            "execute_query(query, (",
            "cursor.execute(",
            "WHERE username = ? AND password = ?"
        ],
        "points": 5
    },
    {
        "id": 2,
        "title": "Prepared Statements",
        "vulnerable_code": """user_id = request.form['id']
query = "SELECT * FROM users WHERE id = " + user_id
cursor.execute(query)""",
        "description": "Fix this concatenation vulnerability using prepared statements.",
        "hint": """Never concatenate user input! Use placeholders instead:
cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))

Note the comma after user_id - it makes it a tuple!""",
        "example_solution": """user_id = request.form['id']
cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))""",
        "correct_patterns": [
            "id = ?",
            "(user_id,)",
            "cursor.execute(",
            "WHERE id = ?",
            "id=?"
        ],
        "points": 7
    },
    {
        "id": 3,
        "title": "Input Validation",
        "vulnerable_code": """search_term = request.args.get('search')
query = f"SELECT * FROM products WHERE name LIKE '%{search_term}%'"
cursor.execute(query)""",
        "description": "Add input validation and use safe query methods for LIKE queries.",
        "hint": """For LIKE queries, put the % symbols in the parameter, not the query:
cursor.execute("SELECT * FROM products WHERE name LIKE ?", (f'%{search_term}%',))

The key is to pass the % symbols as part of the parameter value!
You can also use string concatenation: ('%' + search_term + '%',)""",
        "example_solution": """search_term = request.args.get('search')
cursor.execute("SELECT * FROM products WHERE name LIKE ?", (f'%{search_term}%',))""",
        "correct_patterns": [
            "LIKE ?",
            "like ?",
            "cursor.execute(",
            "(f'%{search_term}%',)",
            "('%' + search_term + '%',)",
            ", (f'%",
            ", ('%"
        ],
        "points": 10
    },
    {
        "id": 4,
        "title": "Dynamic Column Names",
        "vulnerable_code": """order_by = request.args.get('sort', 'name')
query = f"SELECT * FROM products ORDER BY {order_by}"
cursor.execute(query)""",
        "description": "Dynamic ORDER BY is tricky. Implement a whitelist approach.",
        "hint": """You can't use placeholders for column names. Use a whitelist instead:
allowed_columns = ['name', 'price', 'date']
if order_by not in allowed_columns:
    order_by = 'name'  # default
query = f"SELECT * FROM products ORDER BY {order_by}"

This ensures only safe column names are used!""",
        "example_solution": """order_by = request.args.get('sort', 'name')
allowed_columns = ['name', 'price', 'date']
if order_by not in allowed_columns:
    order_by = 'name'
query = f"SELECT * FROM products ORDER BY {order_by}"
cursor.execute(query)""",
        "correct_patterns": [
            "allowed_columns",
            "['name', 'price'",
            "if order_by not in",
            "if order_by in",
            "whitelist",
            "order_by = 'name'"
        ],
        "points": 12
    },
    {
        "id": 5,
        "title": "Safe INSERT Statements",
        "vulnerable_code": """comment = request.form['comment']
user_id = session['user_id']
query = f"INSERT INTO comments (user_id, text) VALUES ({user_id}, '{comment}')"
cursor.execute(query)""",
        "description": "Properly parameterize this INSERT statement for ALL values.",
        "hint": """Even if user_id comes from session, parameterize everything:
cursor.execute("INSERT INTO comments (user_id, text) VALUES (?, ?)", (user_id, comment))

This protects against all injection, even from compromised sessions!""",
        "example_solution": """comment = request.form['comment']
user_id = session['user_id']
cursor.execute("INSERT INTO comments (user_id, text) VALUES (?, ?)", (user_id, comment))""",
        "correct_patterns": [
            "VALUES (?, ?)",
            "(user_id, comment)",
            "INSERT INTO comments",
            "cursor.execute(",
            "VALUES (?,?)",
            "VALUES ( ?, ? )"
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
        
        .instructions {
            background: rgba(0, 255, 136, 0.1);
            border: 2px solid #00ff88;
            padding: 20px;
            margin: 20px 0;
            border-radius: 10px;
        }
        
        .instructions h2 {
            color: #00ff88;
            margin-top: 0;
        }
        
        .instructions ul {
            margin: 10px 0;
            padding-left: 25px;
        }
        
        .instructions li {
            margin: 8px 0;
            line-height: 1.6;
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
            font-size: 14px;
            line-height: 1.5;
            overflow-x: auto;
            position: relative;
            white-space: pre;
        }
        
        .code-block.vulnerable {
            border-color: #ff4444;
            box-shadow: 0 0 10px rgba(255, 68, 68, 0.3);
        }
        
        .code-block.example {
            border-color: #00ff00;
            box-shadow: 0 0 10px rgba(0, 255, 0, 0.3);
            display: none;
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
            line-height: 1.5;
        }
        
        textarea:focus {
            outline: none;
            box-shadow: 0 0 15px rgba(0, 255, 0, 0.5);
        }
        
        textarea:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }
        
        .form-disabled {
            opacity: 0.5;
            pointer-events: none;
        }
        
        .button-group {
            display: flex;
            gap: 10px;
            margin: 20px 0;
            flex-wrap: wrap;
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
            padding: 20px;
            margin: 20px 0;
            color: #ffa500;
            display: none;
            white-space: pre-line;
            line-height: 1.6;
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
        
        @media (max-width: 768px) {
            .stats {
                grid-template-columns: 1fr;
            }
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
        
        {% if current_challenge == 1 and attempts == 0 %}
        <div class="instructions">
            <h2>📚 How to Play</h2>
            <p>Welcome to SQL Defense Training! Your mission is to fix vulnerable code.</p>
            <ul>
                <li><strong>Look at the vulnerable code</strong> - It has SQL injection flaws</li>
                <li><strong>Write the secure version</strong> - Use parameterized queries</li>
                <li><strong>Key principle:</strong> NEVER put user input directly in SQL strings!</li>
                <li><strong>Use placeholders:</strong> ? for SQLite/MySQL, %s for PostgreSQL</li>
                <li><strong>Example:</strong> Instead of f"WHERE id={user_id}", use "WHERE id=?" with parameters</li>
            </ul>
            <p style="margin-top: 15px; color: #ffa500;">💡 Click "Show Hint" if you need help with the specific solution!</p>
        </div>
        {% endif %}
        
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
            <span class="code-label">⚠️ VULNERABLE CODE</span>{{ challenge.vulnerable_code }}</div>
        
        <form method="POST" {% if success %}class="form-disabled"{% endif %}>
            <label style="display: block; margin: 20px 0 10px; font-size: 1.1em;">
                📝 Write the secure version:
            </label>
            <textarea name="solution" placeholder="Write your secure code here..." required {% if success %}disabled{% endif %}>{{ previous_answer }}</textarea>
            
            <div class="button-group">
                <button type="submit" class="button" {% if success %}disabled{% endif %}>Submit Solution</button>
                <button type="button" class="button" onclick="toggleHint()">Show Hint</button>
                <button type="button" class="button" onclick="toggleExample()">Show Example</button>
            </div>
        </form>
        
        <div class="hint-box" id="hintBox">
            <strong>💡 Hint:</strong>
{{ challenge.hint }}</div>
        
        <div class="code-block example" id="exampleBox">
            <span class="code-label secure">✅ EXAMPLE SOLUTION</span>{{ challenge.example_solution }}</div>
        
        {% if result %}
        <div class="result {{ 'success' if success else 'failure' }}">
            {{ result }}
            {% if success and current_challenge < total_challenges %}
            <p style="margin-top: 15px;">⏳ Moving to next challenge in 3 seconds...</p>
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
        
        function toggleExample() {
            const exampleBox = document.getElementById('exampleBox');
            exampleBox.classList.toggle('show');
            if (exampleBox.style.display === 'none' || exampleBox.style.display === '') {
                exampleBox.style.display = 'block';
            } else {
                exampleBox.style.display = 'none';
            }
        }
        
        // Auto-resize textarea
        const textarea = document.querySelector('textarea');
        if (textarea && !textarea.disabled) {
            textarea.addEventListener('input', function() {
                this.style.height = 'auto';
                this.style.height = this.scrollHeight + 'px';
            });
        }
        
        // Auto-redirect after success
        {% if success and current_challenge < total_challenges %}
        setTimeout(function() {
            window.location.href = "{{ url_for('sqldefender.next_challenge') }}";
        }, 3000);
        {% endif %}
    </script>
</body>
</html>
"""

def check_solution(solution, correct_patterns):
    """Check if the solution contains correct secure coding patterns - more flexible"""
    if not solution:
        return False
        
    solution_lower = solution.lower().strip()
    
    # Remove extra spaces and normalize
    solution_normalized = ' '.join(solution_lower.split())
    
    # Special check for LIKE queries (level 3)
    if "like ?" in solution_normalized:
        # Check if they're passing the % in the parameter
        if any(pattern in solution_normalized for pattern in ["(f'%", "('%", '(f"%', '("%', "('"]):
            return True
    
    # Count how many patterns match
    matches = 0
    for pattern in correct_patterns:
        pattern_normalized = pattern.lower().strip()
        if pattern_normalized in solution_normalized:
            matches += 1
    
    # Need at least 2 patterns to match for a correct answer
    required_matches = 2
    return matches >= required_matches

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
        
        if check_solution(solution, challenge["correct_patterns"]):
            session["defender_score"] += challenge["points"]
            result = f"✅ Excellent! Your solution is secure. +{challenge['points']} points!"
            success = True
            
            if current >= len(DEFENSE_CHALLENGES):
                save_defender_progress(current_user.id, session["defender_score"])
        else:
            result = "❌ Not quite right. Remember: use placeholders (?) and pass parameters separately. Check the hint for the exact syntax!"
    
    # Calculate stats
    elapsed = int(time.time() - session.get("defender_start_time", time.time()))
    time_elapsed = f"{elapsed // 60}:{elapsed % 60:02d}"
    progress = int((current - 1) / len(DEFENSE_CHALLENGES) * 100)
    if success and current == len(DEFENSE_CHALLENGES):
        progress = 100
    
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

@sqldefender_bp.route("/next", methods=["GET", "POST"])
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