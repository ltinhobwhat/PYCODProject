import random
import time
import sqlite3
from flask import Blueprint, render_template_string, request, redirect, session, url_for
from flask_login import login_required, current_user

quiz_bp = Blueprint("quiz", __name__)

# Import questions from your existing pool
QUESTIONS = [
    {
        "text": "HTTPS uses encryption to protect data in transit.",
        "answers": ["confidentiality"]
    },
    {
        "text": "Digital signatures help ensure a message hasn't been altered.",
        "answers": ["integrity"]
    },
    {
        "text": "A redundant server ensures service stays available even during failure.",
        "answers": ["availability"]
    },
    {
        "text": "Multi-factor authentication protects access to accounts.",
        "answers": ["confidentiality", "integrity"]
    },
    {
        "text": "Firewalls help filter traffic based on rules.",
        "answers": ["confidentiality"]
    },
    {
        "text": "Phishing attacks aim to steal user credentials.",
        "answers": ["confidentiality"]
    },
    {
        "text": "Hash functions create fixed-size outputs from variable input data.",
        "answers": ["integrity"]
    },
    {
        "text": "Social engineering exploits human psychology for attacks.",
        "answers": ["confidentiality"]
    },
    {
        "text": "Regular software updates help fix security vulnerabilities.",
        "answers": ["availability", "integrity"]
    },
    {
        "text": "Strong passwords reduce the risk of unauthorized access.",
        "answers": ["confidentiality"]
    }
]

NUM_QUESTIONS = 10

# HTML Template for quiz question - Neon City style with green theme
QUIZ_QUESTION_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CIA Triad Challenge - Cyber City</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            margin: 0;
            font-family: 'Orbitron', 'Rajdhani', 'Segoe UI', sans-serif;
            background: #080818;
            color: #00ff88;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            min-height: 100vh;
            overflow: hidden;
            position: relative;
        }
        
        /* Grid background */
        body::before {
            content: "";
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: 
                linear-gradient(90deg, transparent 95%, rgba(0, 255, 136, 0.1) 5%), 
                linear-gradient(transparent 95%, rgba(0, 255, 136, 0.1) 5%);
            background-size: 30px 30px;
            z-index: -1;
        }
        
        /* Radial glow */
        body::after {
            content: "";
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            width: 100%;
            height: 100%;
            background: radial-gradient(circle, rgba(0, 255, 136, 0.1) 0%, transparent 70%);
            z-index: -1;
        }
        
        .title-section {
            margin-bottom: 20px;
            text-align: center;
        }
        
        h1 {
            font-size: 2.5rem;
            margin-bottom: 1rem;
            text-shadow: 0 0 10px #00ff88;
            letter-spacing: 3px;
            text-transform: uppercase;
        }
        
        .subtitle {
            color: rgba(0, 255, 136, 0.7);
            font-size: 1rem;
            margin-bottom: 20px;
            letter-spacing: 2px;
        }
        
        .quiz-container {
            width: 90%;
            max-width: 900px;
            min-height: 600px;
            position: relative;
            border: 2px solid rgba(0, 255, 136, 0.5);
            border-radius: 8px;
            box-shadow: 0 0 15px rgba(0, 255, 136, 0.3), inset 0 0 15px rgba(0, 255, 136, 0.1);
            background: rgba(8, 8, 24, 0.8);
            overflow: hidden;
            padding: 40px;
        }
        
        /* Scanner effect */
        .scanner {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 5px;
            background: linear-gradient(90deg, transparent, rgba(0, 255, 136, 0.5), transparent);
            z-index: 4;
            animation: scan 4s linear infinite;
            opacity: 0.7;
        }
        
        @keyframes scan {
            0% { top: 0; }
            100% { top: 100%; }
        }
        
        /* HUD corners */
        .hud-corner {
            position: absolute;
            width: 30px;
            height: 30px;
            border: 2px solid rgba(0, 255, 136, 0.7);
            z-index: 5;
        }
        
        .hud-corner-tl {
            top: 10px;
            left: 10px;
            border-right: none;
            border-bottom: none;
        }
        
        .hud-corner-tr {
            top: 10px;
            right: 10px;
            border-left: none;
            border-bottom: none;
        }
        
        .hud-corner-bl {
            bottom: 10px;
            left: 10px;
            border-right: none;
            border-top: none;
        }
        
        .hud-corner-br {
            bottom: 10px;
            right: 10px;
            border-left: none;
            border-top: none;
        }
        
        /* HUD top display */
        .hud-top {
            position: absolute;
            top: 10px;
            left: 50%;
            transform: translateX(-50%);
            display: flex;
            align-items: center;
            font-size: 0.8rem;
            color: rgba(0, 255, 136, 0.8);
            z-index: 5;
        }
        
        .hud-dot {
            width: 8px;
            height: 8px;
            background: #00ff88;
            border-radius: 50%;
            margin-right: 8px;
            animation: hudBlink 1.5s infinite;
        }
        
        @keyframes hudBlink {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.3; }
        }
        
        .progress-section {
            text-align: center;
            margin-bottom: 30px;
        }
        
        .progress-label {
            color: rgba(0, 255, 136, 0.7);
            font-size: 0.9rem;
            text-transform: uppercase;
            letter-spacing: 2px;
            margin-bottom: 10px;
        }
        
        .progress-bar-container {
            width: 100%;
            height: 25px;
            background: rgba(0, 255, 136, 0.1);
            border: 1px solid rgba(0, 255, 136, 0.3);
            border-radius: 3px;
            position: relative;
            overflow: hidden;
        }
        
        .progress-bar {
            height: 100%;
            background: linear-gradient(90deg, #00ff88, rgba(0, 255, 136, 0.5));
            transition: width 0.5s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            color: #080818;
        }
        
        .question-block {
            background: rgba(0, 255, 136, 0.05);
            border: 1px solid rgba(0, 255, 136, 0.3);
            border-radius: 8px;
            padding: 30px;
            margin-bottom: 30px;
            position: relative;
        }
        
        .question-text {
            font-size: 1.3rem;
            line-height: 1.6;
            color: #00ff88;
            text-shadow: 0 0 5px rgba(0, 255, 136, 0.5);
            margin-bottom: 30px;
        }
        
        .answer-option {
            background: rgba(8, 8, 24, 0.6);
            border: 1px solid rgba(0, 255, 136, 0.3);
            border-radius: 5px;
            padding: 15px 20px;
            margin-bottom: 15px;
            cursor: pointer;
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }
        
        .answer-option::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(0, 255, 136, 0.2), transparent);
            transition: left 0.5s ease;
        }
        
        .answer-option:hover::before {
            left: 100%;
        }
        
        .answer-option:hover {
            background: rgba(0, 255, 136, 0.1);
            border-color: #00ff88;
            box-shadow: 0 0 10px rgba(0, 255, 136, 0.5);
        }
        
        .answer-option label {
            display: flex;
            align-items: center;
            cursor: pointer;
            color: #00ff88;
            font-size: 1.1rem;
        }
        
        .answer-option input[type="checkbox"] {
            margin-right: 15px;
            width: 20px;
            height: 20px;
            cursor: pointer;
            accent-color: #00ff88;
        }
        
        .control-panel {
            display: flex;
            justify-content: center;
            gap: 20px;
            margin-top: 30px;
        }
        
        .control-button {
            background: rgba(0, 255, 136, 0.1);
            border: 1px solid rgba(0, 255, 136, 0.5);
            color: #00ff88;
            padding: 12px 24px;
            font-size: 0.9rem;
            cursor: pointer;
            transition: all 0.3s ease;
            text-transform: uppercase;
            font-family: 'Orbitron', sans-serif;
            letter-spacing: 1px;
            border-radius: 3px;
        }
        
        .control-button:hover {
            background: rgba(0, 255, 136, 0.2);
            box-shadow: 0 0 10px rgba(0, 255, 136, 0.5);
        }
        
        .back-link {
            display: inline-block;
            margin-top: 20px;
            color: #00ff88;
            text-decoration: none;
            text-transform: uppercase;
            letter-spacing: 1px;
            font-size: 0.9rem;
            transition: all 0.3s ease;
        }
        
        .back-link:hover {
            text-shadow: 0 0 10px rgba(0, 255, 136, 0.8);
        }
    </style>
</head>
<body>
    <div class="title-section">
        <h1>CIA TRIAD CHALLENGE</h1>
        <div class="subtitle">SECURITY ASSESSMENT PROTOCOL</div>
    </div>
    
    <div class="quiz-container">
        <!-- Scanner effect -->
        <div class="scanner"></div>
        
        <!-- HUD corners -->
        <div class="hud-corner hud-corner-tl"></div>
        <div class="hud-corner hud-corner-tr"></div>
        <div class="hud-corner hud-corner-bl"></div>
        <div class="hud-corner hud-corner-br"></div>
        
        <!-- HUD top display -->
        <div class="hud-top">
            <div class="hud-dot"></div>
            <span>SECURE CONNECTION ACTIVE • ASSESSMENT IN PROGRESS</span>
        </div>
        
        <form method="post">
            <!-- Progress section -->
            <div class="progress-section">
                <div class="progress-label">QUESTION {{ index }} OF {{ total }}</div>
                <div class="progress-bar-container">
                    <div class="progress-bar" style="width: {{ (index / total * 100)|round(0, 'floor') }}%">
                        {{ (index / total * 100)|round(0, 'floor') }}%
                    </div>
                </div>
            </div>
            
            <!-- Question block -->
            <div class="question-block">
                <div class="question-text">
                    {{ question.text }}
                </div>
                
                <div class="answer-option">
                    <label>
                        <input type="checkbox" name="answer" value="confidentiality">
                        CONFIDENTIALITY
                    </label>
                </div>
                <div class="answer-option">
                    <label>
                        <input type="checkbox" name="answer" value="integrity">
                        INTEGRITY
                    </label>
                </div>
                <div class="answer-option">
                    <label>
                        <input type="checkbox" name="answer" value="availability">
                        AVAILABILITY
                    </label>
                </div>
            </div>
            
            <!-- Control panel -->
            <div class="control-panel">
                <button type="submit" class="control-button">SUBMIT ANSWER</button>
            </div>
        </form>
        
        <center>
            <a href="{{ url_for('menu.menu') }}" class="back-link">⬅️ RETURN TO MAIN MENU</a>
        </center>
    </div>
    
    <script>
        // Create random decorative dots
        document.addEventListener('DOMContentLoaded', function() {
            const container = document.querySelector('.quiz-container');
            for (let i = 0; i < 20; i++) {
                const dot = document.createElement('div');
                dot.style.position = 'absolute';
                dot.style.width = '2px';
                dot.style.height = '2px';
                dot.style.backgroundColor = 'rgba(0, 255, 136, 0.3)';
                dot.style.borderRadius = '50%';
                dot.style.top = Math.random() * 100 + '%';
                dot.style.left = Math.random() * 100 + '%';
                dot.style.zIndex = '0';
                container.appendChild(dot);
            }
            
            // Add visual feedback for checkbox selection
            const checkboxes = document.querySelectorAll('input[type="checkbox"]');
            checkboxes.forEach(checkbox => {
                checkbox.addEventListener('change', function() {
                    const option = this.closest('.answer-option');
                    if (this.checked) {
                        option.style.background = 'rgba(0, 255, 136, 0.2)';
                        option.style.borderColor = '#00ff88';
                    } else {
                        option.style.background = 'rgba(8, 8, 24, 0.6)';
                        option.style.borderColor = 'rgba(0, 255, 136, 0.3)';
                    }
                });
            });
        });
    </script>
</body>
</html>
"""

# HTML Template for quiz results - Neon City style with green theme
QUIZ_RESULT_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mission Complete - CIA Triad Challenge</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            margin: 0;
            font-family: 'Orbitron', 'Rajdhani', 'Segoe UI', sans-serif;
            background: #080818;
            color: #00ff88;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            min-height: 100vh;
            overflow: hidden;
            position: relative;
        }
        
        /* Grid background */
        body::before {
            content: "";
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: 
                linear-gradient(90deg, transparent 95%, rgba(0, 255, 136, 0.1) 5%), 
                linear-gradient(transparent 95%, rgba(0, 255, 136, 0.1) 5%);
            background-size: 30px 30px;
            z-index: -1;
        }
        
        /* Radial glow */
        body::after {
            content: "";
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            width: 100%;
            height: 100%;
            background: radial-gradient(circle, rgba(0, 255, 136, 0.1) 0%, transparent 70%);
            z-index: -1;
        }
        
        .title-section {
            margin-bottom: 20px;
            text-align: center;
        }
        
        h1 {
            font-size: 2.5rem;
            margin-bottom: 1rem;
            text-shadow: 0 0 10px #00ff88;
            letter-spacing: 3px;
            text-transform: uppercase;
        }
        
        .subtitle {
            color: rgba(0, 255, 136, 0.7);
            font-size: 1rem;
            margin-bottom: 20px;
            letter-spacing: 2px;
        }
        
        .results-container {
            width: 90%;
            max-width: 900px;
            min-height: 500px;
            position: relative;
            border: 2px solid rgba(0, 255, 136, 0.5);
            border-radius: 8px;
            box-shadow: 0 0 15px rgba(0, 255, 136, 0.3), inset 0 0 15px rgba(0, 255, 136, 0.1);
            background: rgba(8, 8, 24, 0.8);
            overflow: hidden;
            padding: 40px;
        }
        
        /* Scanner effect */
        .scanner {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 5px;
            background: linear-gradient(90deg, transparent, rgba(0, 255, 136, 0.5), transparent);
            z-index: 4;
            animation: scan 4s linear infinite;
            opacity: 0.7;
        }
        
        @keyframes scan {
            0% { top: 0; }
            100% { top: 100%; }
        }
        
        /* HUD corners */
        .hud-corner {
            position: absolute;
            width: 30px;
            height: 30px;
            border: 2px solid rgba(0, 255, 136, 0.7);
            z-index: 5;
        }
        
        .hud-corner-tl {
            top: 10px;
            left: 10px;
            border-right: none;
            border-bottom: none;
        }
        
        .hud-corner-tr {
            top: 10px;
            right: 10px;
            border-left: none;
            border-bottom: none;
        }
        
        .hud-corner-bl {
            bottom: 10px;
            left: 10px;
            border-right: none;
            border-top: none;
        }
        
        .hud-corner-br {
            bottom: 10px;
            right: 10px;
            border-left: none;
            border-top: none;
        }
        
        /* HUD top display */
        .hud-top {
            position: absolute;
            top: 10px;
            left: 50%;
            transform: translateX(-50%);
            display: flex;
            align-items: center;
            font-size: 0.8rem;
            color: rgba(0, 255, 136, 0.8);
            z-index: 5;
        }
        
        .hud-dot {
            width: 8px;
            height: 8px;
            background: #00ff88;
            border-radius: 50%;
            margin-right: 8px;
            animation: hudBlink 1.5s infinite;
        }
        
        @keyframes hudBlink {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.3; }
        }
        
        .score-section {
            text-align: center;
            margin: 40px 0;
        }
        
        .score-value {
            font-size: 5rem;
            font-weight: bold;
            color: #00ff88;
            text-shadow: 0 0 30px rgba(0, 255, 136, 0.8);
            margin-bottom: 10px;
            font-family: 'Orbitron', monospace;
        }
        
        .score-details {
            font-size: 1.2rem;
            color: rgba(0, 255, 136, 0.8);
            margin-bottom: 30px;
        }
        
        .progress-visual {
            width: 100%;
            max-width: 600px;
            margin: 0 auto 40px;
        }
        
        .progress-bar-container {
            width: 100%;
            height: 40px;
            background: rgba(0, 255, 136, 0.1);
            border: 1px solid rgba(0, 255, 136, 0.3);
            border-radius: 3px;
            overflow: hidden;
            position: relative;
        }
        
        .progress-bar {
            height: 100%;
            background: linear-gradient(90deg, #00ff88, rgba(0, 255, 136, 0.7));
            transition: width 1.5s ease;
            position: relative;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            font-size: 1.1rem;
            color: #080818;
            text-shadow: 0 0 5px rgba(255, 255, 255, 0.5);
        }
        
        .status-message {
            text-align: center;
            padding: 20px;
            margin: 30px 0;
            background: rgba(0, 255, 136, 0.1);
            border: 1px solid rgba(0, 255, 136, 0.3);
            border-radius: 5px;
        }
        
        .status-message.success {
            background: rgba(0, 255, 136, 0.1);
            border-color: rgba(0, 255, 136, 0.3);
            color: #00ff88;
        }
        
        .status-message.failure {
            background: rgba(255, 165, 0, 0.1);
            border-color: rgba(255, 165, 0, 0.3);
            color: #ffa500;
        }
        
        .status-title {
            font-size: 1.5rem;
            font-weight: bold;
            margin-bottom: 10px;
            text-transform: uppercase;
            letter-spacing: 2px;
        }
        
        .control-panel {
            display: flex;
            justify-content: center;
            gap: 20px;
            margin-top: 40px;
        }
        
        .control-button {
            background: rgba(0, 255, 136, 0.1);
            border: 1px solid rgba(0, 255, 136, 0.5);
            color: #00ff88;
            padding: 12px 24px;
            font-size: 0.9rem;
            cursor: pointer;
            transition: all 0.3s ease;
            text-transform: uppercase;
            font-family: 'Orbitron', sans-serif;
            letter-spacing: 1px;
            border-radius: 3px;
            text-decoration: none;
            display: inline-block;
        }
        
        .control-button:hover {
            background: rgba(0, 255, 136, 0.2);
            box-shadow: 0 0 10px rgba(0, 255, 136, 0.5);
        }
    </style>
</head>
<body>
    <div class="title-section">
        <h1>MISSION COMPLETE</h1>
        <div class="subtitle">CIA TRIAD ASSESSMENT RESULTS</div>
    </div>
    
    <div class="results-container">
        <!-- Scanner effect -->
        <div class="scanner"></div>
        
        <!-- HUD corners -->
        <div class="hud-corner hud-corner-tl"></div>
        <div class="hud-corner hud-corner-tr"></div>
        <div class="hud-corner hud-corner-bl"></div>
        <div class="hud-corner hud-corner-br"></div>
        
        <!-- HUD top display -->
        <div class="hud-top">
            <div class="hud-dot"></div>
            <span>ASSESSMENT COMPLETE • RESULTS COMPILED</span>
        </div>
        
        <!-- Score display -->
        <div class="score-section">
            <div class="score-value">{{ score }}/{{ total }}</div>
            <div class="score-details">
                You correctly identified {{ score }} out of {{ total }} security principles
            </div>
        </div>
        
        <!-- Progress bar -->
        <div class="progress-visual">
            <div class="progress-bar-container">
                <div class="progress-bar" style="width: {{ percentage }}%">
                    {{ "%.0f"|format(percentage) }}% COMPLETE
                </div>
            </div>
        </div>
        
        <!-- Status message -->
        <div class="status-message {{ 'success' if completed else 'failure' }}">
            <div class="status-title">
                {% if completed %}
                    CHALLENGE PASSED
                {% else %}
                    CHALLENGE FAILED
                {% endif %}
            </div>
            <div class="status-description">
                {% if completed %}
                    Excellent work, Agent! You have demonstrated strong understanding of the CIA Triad.
                {% else %}
                    Keep training, Agent. You need 70% or higher to pass this challenge.
                {% endif %}
            </div>
        </div>
        
        <!-- Control panel -->
        <div class="control-panel">
            <a href="{{ url_for('quiz.index') }}" class="control-button">RETRY MISSION</a>
            <a href="{{ url_for('map.map_view') }}" class="control-button">RETURN TO MAP</a>
            <a href="{{ url_for('menu.menu') }}" class="control-button">MAIN MENU</a>
        </div>
    </div>
    
    <script>
        // Animate progress bar on load
        document.addEventListener('DOMContentLoaded', function() {
            const progressBar = document.querySelector('.progress-bar');
            const finalWidth = progressBar.style.width;
            progressBar.style.width = '0%';
            setTimeout(() => {
                progressBar.style.width = finalWidth;
            }, 500);
            
            // Create random decorative dots
            const container = document.querySelector('.results-container');
            for (let i = 0; i < 20; i++) {
                const dot = document.createElement('div');
                dot.style.position = 'absolute';
                dot.style.width = '2px';
                dot.style.height = '2px';
                dot.style.backgroundColor = 'rgba(0, 255, 136, 0.3)';
                dot.style.borderRadius = '50%';
                dot.style.top = Math.random() * 100 + '%';
                dot.style.left = Math.random() * 100 + '%';
                dot.style.zIndex = '0';
                container.appendChild(dot);
            }
        });
    </script>
</body>
</html>
"""

def save_progress(user_id, score, completed, percentage):
    """Save quiz progress to SQLite"""
    conn = sqlite3.connect('game.db')
    cursor = conn.cursor()
    
    # Get current progress
    cursor.execute('SELECT best_score, total_attempts FROM game_progress WHERE user_id = ? AND game_name = ?', 
                   (user_id, 'quiz'))
    current = cursor.fetchone()
    
    if current:
        best_score = max(current[0], score)
        total_attempts = current[1] + 1
        cursor.execute('''
            UPDATE game_progress 
            SET is_completed = ?, best_score = ?, total_attempts = ?
            WHERE user_id = ? AND game_name = ?
        ''', (completed, best_score, total_attempts, user_id, 'quiz'))
    else:
        cursor.execute('''
            INSERT INTO game_progress (user_id, game_name, is_completed, best_score, total_attempts)
            VALUES (?, ?, ?, ?, 1)
        ''', (user_id, 'quiz', completed, score))
    
    # Update user total score if completed for first time
    if completed:
        cursor.execute('''
            UPDATE users 
            SET total_score = total_score + ?, games_completed = games_completed + 1
            WHERE id = ? AND id NOT IN (
                SELECT user_id FROM game_progress 
                WHERE user_id = ? AND game_name = ? AND is_completed = 1
            )
        ''', (score, user_id, user_id, 'quiz'))
    
    conn.commit()
    conn.close()

@quiz_bp.route("/", methods=["GET", "POST"])
@login_required
def index():
    if "quiz_questions" not in session or "quiz_index" not in session:
        num_to_pick = min(NUM_QUESTIONS, len(QUESTIONS))
        session["quiz_questions"] = random.sample(QUESTIONS, num_to_pick)
        session["quiz_index"] = 0
        session["quiz_score"] = 0
        session["quiz_answers"] = []
        session["quiz_start_time"] = time.time()

    quiz_questions = session["quiz_questions"]
    index = session.get("quiz_index", 0)
    total = len(quiz_questions)

    if request.method == "POST":
        user_answers = request.form.getlist("answer")
        correct_answers = quiz_questions[index]["answers"]
        if set(user_answers) == set(correct_answers):
            session["quiz_score"] += 1
        session["quiz_answers"].append(user_answers)
        session["quiz_index"] += 1
        index += 1

        if index >= total:
            return redirect(url_for("quiz.result"))

    question = quiz_questions[index]
    return render_template_string(QUIZ_QUESTION_TEMPLATE, 
                         question=question, 
                         index=index + 1, 
                         total=total)

@quiz_bp.route("/result")
@login_required
def result():
    score = session.get("quiz_score", 0)
    total = len(session.get("quiz_questions", []))
    
    # Calculate percentage and completion time
    percentage = (score / total) * 100 if total > 0 else 0
    completed = percentage >= 70  # Consider 70% as completion threshold
    
    start_time = session.get("quiz_start_time", time.time())
    completion_time = time.time() - start_time
    
    # Save progress
    save_progress(current_user.id, score, completed, percentage)
    
    # Clean up session
    session.pop('quiz_questions', None)
    session.pop('quiz_index', None)
    session.pop('quiz_score', None)
    session.pop('quiz_answers', None)
    session.pop('quiz_start_time', None)
    
    return render_template_string(QUIZ_RESULT_TEMPLATE, 
                         score=score, 
                         total=total,
                         percentage=percentage,
                         completed=completed)