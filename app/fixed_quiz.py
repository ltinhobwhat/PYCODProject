import random
import time
import sqlite3
from flask import Blueprint, render_template_string, request, redirect, session, url_for
from flask_login import login_required, current_user

quiz_bp = Blueprint("quiz", __name__)

# Expanded question pool with various cybersecurity topics
QUESTIONS = [
    # CIA Triad Questions
    {
        "text": "Which security principle ensures that data remains unaltered during transmission?",
        "options": ["Confidentiality", "Integrity", "Availability", "Authentication"],
        "answer": "Integrity"
    },
    {
        "text": "What does encryption primarily protect?",
        "options": ["Availability", "Integrity", "Confidentiality", "Non-repudiation"],
        "answer": "Confidentiality"
    },
    {
        "text": "A DDoS attack primarily targets which aspect of the CIA triad?",
        "options": ["Confidentiality", "Integrity", "Availability", "All three"],
        "answer": "Availability"
    },
    
    # Malware Questions
    {
        "text": "Which type of malware encrypts files and demands payment for decryption?",
        "options": ["Trojan", "Ransomware", "Spyware", "Adware"],
        "answer": "Ransomware"
    },
    {
        "text": "What type of malware disguises itself as legitimate software?",
        "options": ["Worm", "Virus", "Trojan", "Rootkit"],
        "answer": "Trojan"
    },
    {
        "text": "Which malware can replicate itself without human intervention?",
        "options": ["Trojan", "Spyware", "Worm", "Adware"],
        "answer": "Worm"
    },
    
    # Attack Vectors
    {
        "text": "What is the most common initial attack vector in cyber breaches?",
        "options": ["SQL Injection", "Phishing", "Zero-day exploits", "Physical access"],
        "answer": "Phishing"
    },
    {
        "text": "Which attack involves injecting malicious code into web forms?",
        "options": ["XSS", "DDoS", "Man-in-the-middle", "Buffer overflow"],
        "answer": "XSS"
    },
    {
        "text": "What type of attack exploits human psychology rather than technical vulnerabilities?",
        "options": ["Zero-day", "Social engineering", "SQL injection", "Buffer overflow"],
        "answer": "Social engineering"
    },
    
    # Cryptography & Certificates
    {
        "text": "What does SSL/TLS primarily provide?",
        "options": ["Antivirus protection", "Encrypted communication", "Firewall services", "Password management"],
        "answer": "Encrypted communication"
    },
    {
        "text": "Which hash algorithm is considered cryptographically broken?",
        "options": ["SHA-256", "SHA-512", "MD5", "SHA-3"],
        "answer": "MD5"
    },
    {
        "text": "What is the purpose of a digital certificate?",
        "options": ["Encrypt passwords", "Verify identity", "Block malware", "Compress data"],
        "answer": "Verify identity"
    },
    
    # Network Security
    {
        "text": "On which OSI layer does a firewall typically operate?",
        "options": ["Physical", "Network and Transport", "Application only", "All layers"],
        "answer": "Network and Transport"
    },
    {
        "text": "What port does HTTPS typically use?",
        "options": ["80", "443", "22", "3389"],
        "answer": "443"
    },
    {
        "text": "Which protocol is more secure for remote access?",
        "options": ["Telnet", "SSH", "FTP", "HTTP"],
        "answer": "SSH"
    },
    
    # Authentication & Access Control
    {
        "text": "What does two-factor authentication require?",
        "options": ["Two passwords", "Something you know and something you have", "Two usernames", "Two devices"],
        "answer": "Something you know and something you have"
    },
    {
        "text": "Which is the most secure password policy?",
        "options": ["8 characters minimum", "Complex passwords changed monthly", "Long passphrases", "Password + SMS code"],
        "answer": "Long passphrases"
    },
    {
        "text": "What is the principle of least privilege?",
        "options": ["Users get minimum required access", "Admins have all access", "Everyone has same access", "Access based on seniority"],
        "answer": "Users get minimum required access"
    },
    
    # Security Best Practices
    {
        "text": "How often should critical security patches be applied?",
        "options": ["Yearly", "Monthly", "As soon as possible", "Only if issues occur"],
        "answer": "As soon as possible"
    },
    {
        "text": "What is the best practice for handling suspicious emails?",
        "options": ["Open to investigate", "Forward to colleagues", "Delete and report", "Reply asking for details"],
        "answer": "Delete and report"
    },
    {
        "text": "Which is a key principle of secure coding?",
        "options": ["Speed over security", "Input validation", "Obscure code", "Minimal testing"],
        "answer": "Input validation"
    },
    
    # Incident Response
    {
        "text": "What is the first step in incident response?",
        "options": ["Eradication", "Identification", "Recovery", "Lessons learned"],
        "answer": "Identification"
    },
    {
        "text": "What should you do if you suspect your computer is infected?",
        "options": ["Keep working normally", "Disconnect from network", "Delete all files", "Install more antivirus"],
        "answer": "Disconnect from network"
    },
    
    # Advanced Topics
    {
        "text": "What is a zero-day vulnerability?",
        "options": ["Old vulnerability", "Unknown to vendor", "Patched vulnerability", "Low-risk bug"],
        "answer": "Unknown to vendor"
    },
    {
        "text": "What does OSINT stand for?",
        "options": ["Open Source Intelligence", "Operating System Interface", "Online Security International", "Organized Security Network"],
        "answer": "Open Source Intelligence"
    },
    {
        "text": "Which technique hides data within other data?",
        "options": ["Encryption", "Hashing", "Steganography", "Compression"],
        "answer": "Steganography"
    },
    {
        "text": "What is a honeypot in cybersecurity?",
        "options": ["Password manager", "Decoy system", "Firewall type", "Encryption method"],
        "answer": "Decoy system"
    },
    {
        "text": "What does APT stand for in cybersecurity?",
        "options": ["Advanced Persistent Threat", "Application Protocol Testing", "Automated Patch Tool", "Access Point Terminal"],
        "answer": "Advanced Persistent Threat"
    },
    {
        "text": "Which attack targets the domain name system?",
        "options": ["DNS poisoning", "IP spoofing", "MAC flooding", "Port scanning"],
        "answer": "DNS poisoning"
    },
    {
        "text": "What is the purpose of penetration testing?",
        "options": ["Install malware", "Find vulnerabilities", "Block users", "Encrypt data"],
        "answer": "Find vulnerabilities"
    }
]

NUM_QUESTIONS = 10

# HTML Template matching the style of other mini-games
QUIZ_QUESTION_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Security Knowledge Quiz</title>
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
            padding: 40px;
            border-radius: 10px;
            box-shadow: 0 0 20px rgba(0, 255, 0, 0.3);
            max-width: 700px;
            width: 100%;
            border: 2px solid rgba(0, 255, 0, 0.3);
        }
        
        h1 {
            text-align: center;
            color: #00ff00;
            text-shadow: 0 0 10px rgba(0, 255, 0, 0.5);
            margin-bottom: 30px;
        }
        
        .progress-section {
            background: rgba(0, 0, 0, 0.3);
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 30px;
            text-align: center;
        }
        
        .progress-bar-container {
            width: 100%;
            height: 20px;
            background-color: #333333;
            border-radius: 10px;
            overflow: hidden;
            margin: 10px 0;
        }
        
        .progress-bar {
            height: 100%;
            background: linear-gradient(90deg, #00ff88, #00cc6a);
            transition: width 0.3s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #000;
            font-weight: bold;
        }
        
        .question-block {
            background: rgba(0, 0, 0, 0.3);
            padding: 25px;
            border-radius: 8px;
            margin-bottom: 30px;
        }
        
        .question-text {
            font-size: 1.3rem;
            line-height: 1.6;
            color: #00ff88;
            margin-bottom: 25px;
        }
        
        .options-container {
            display: flex;
            flex-direction: column;
            gap: 15px;
        }
        
        .option {
            background: rgba(0, 255, 136, 0.05);
            border: 2px solid rgba(0, 255, 136, 0.3);
            border-radius: 5px;
            padding: 15px 20px;
            cursor: pointer;
            transition: all 0.3s ease;
            position: relative;
        }
        
        .option:hover {
            background: rgba(0, 255, 136, 0.1);
            border-color: #00ff88;
            transform: translateX(5px);
            box-shadow: 0 0 10px rgba(0, 255, 136, 0.5);
        }
        
        .option input[type="radio"] {
            position: absolute;
            opacity: 0;
        }
        
        .option label {
            display: block;
            cursor: pointer;
            font-size: 1.1rem;
            padding-left: 30px;
        }
        
        .option label:before {
            content: '';
            position: absolute;
            left: 10px;
            top: 50%;
            transform: translateY(-50%);
            width: 18px;
            height: 18px;
            border: 2px solid #00ff88;
            border-radius: 50%;
            background: transparent;
            transition: all 0.3s ease;
        }
        
        .option input[type="radio"]:checked + label:before {
            background: #00ff88;
            box-shadow: 0 0 10px rgba(0, 255, 136, 0.5);
        }
        
        .option input[type="radio"]:checked ~ label {
            color: #00ff88;
            text-shadow: 0 0 5px rgba(0, 255, 136, 0.5);
        }
        
        .submit-button {
            display: block;
            width: 100%;
            padding: 15px;
            background: linear-gradient(135deg, #00ff88, #00cc6a);
            color: #000000;
            border: none;
            border-radius: 5px;
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
        
        .submit-button:disabled {
            background: #666;
            cursor: not-allowed;
            transform: none;
        }
        
        .timer {
            text-align: center;
            color: #00ff88;
            font-size: 0.9rem;
            margin-top: 15px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🧠 Security Knowledge Quiz</h1>
        
        <div class="progress-section">
            <div>Question {{ current }} of {{ total }}</div>
            <div class="progress-bar-container">
                <div class="progress-bar" style="width: {{ (current / total * 100)|int }}%">
                    {{ (current / total * 100)|int }}%
                </div>
            </div>
        </div>
        
        <form method="POST" id="quizForm">
            <div class="question-block">
                <div class="question-text">{{ question.text }}</div>
                
                <div class="options-container">
                    {% for option in question.options %}
                    <div class="option">
                        <input type="radio" name="answer" id="option{{ loop.index }}" value="{{ option }}" required>
                        <label for="option{{ loop.index }}">{{ option }}</label>
                    </div>
                    {% endfor %}
                </div>
            </div>
            
            <button type="submit" class="submit-button" id="submitBtn">Submit Answer</button>
        </form>
        
        <div class="timer" id="timer">Time elapsed: <span id="timeDisplay">0:00</span></div>
    </div>
    
    <script>
        // Timer functionality
        let startTime = {{ start_time }};
        let timerInterval;
        
        function updateTimer() {
            let elapsed = Math.floor(Date.now() / 1000 - startTime);
            let minutes = Math.floor(elapsed / 60);
            let seconds = elapsed % 60;
            document.getElementById('timeDisplay').textContent = minutes + ':' + (seconds < 10 ? '0' : '') + seconds;
        }
        
        updateTimer();
        timerInterval = setInterval(updateTimer, 1000);
        
        // Auto-select visual feedback
        document.querySelectorAll('.option').forEach(option => {
            option.addEventListener('click', function() {
                const radio = this.querySelector('input[type="radio"]');
                radio.checked = true;
                
                // Remove selected state from all options
                document.querySelectorAll('.option').forEach(opt => {
                    opt.style.background = 'rgba(0, 255, 136, 0.05)';
                    opt.style.borderColor = 'rgba(0, 255, 136, 0.3)';
                });
                
                // Add selected state to clicked option
                this.style.background = 'rgba(0, 255, 136, 0.2)';
                this.style.borderColor = '#00ff88';
            });
        });
        
        // Prevent multiple submissions
        document.getElementById('quizForm').addEventListener('submit', function() {
            document.getElementById('submitBtn').disabled = true;
            document.getElementById('submitBtn').textContent = 'Processing...';
        });
    </script>
</body>
</html>
"""

QUIZ_RESULT_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Quiz Results - Security Knowledge</title>
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
            padding: 40px;
            border-radius: 10px;
            box-shadow: 0 0 20px rgba(0, 255, 0, 0.3);
            max-width: 600px;
            width: 100%;
            border: 2px solid rgba(0, 255, 0, 0.3);
            text-align: center;
        }
        
        h1 {
            color: #00ff00;
            text-shadow: 0 0 10px rgba(0, 255, 0, 0.5);
            margin-bottom: 30px;
        }
        
        .score-display {
            font-size: 4rem;
            font-weight: bold;
            color: #00ff00;
            text-shadow: 0 0 20px rgba(0, 255, 0, 0.8);
            margin: 30px 0;
        }
        
        .score-details {
            background: rgba(0, 0, 0, 0.3);
            padding: 20px;
            border-radius: 8px;
            margin: 20px 0;
        }
        
        .detail-row {
            display: flex;
            justify-content: space-between;
            margin: 10px 0;
            font-size: 1.1rem;
        }
        
        .detail-label {
            color: #aaa;
        }
        
        .detail-value {
            color: #00ff88;
            font-weight: bold;
        }
        
        .status-message {
            padding: 20px;
            margin: 30px 0;
            border-radius: 8px;
            font-size: 1.2rem;
        }
        
        .status-message.success {
            background: rgba(0, 255, 136, 0.1);
            border: 2px solid rgba(0, 255, 136, 0.3);
            color: #00ff88;
        }
        
        .status-message.failure {
            background: rgba(255, 165, 0, 0.1);
            border: 2px solid rgba(255, 165, 0, 0.3);
            color: #ffa500;
        }
        
        .progress-visual {
            width: 100%;
            height: 40px;
            background-color: #333333;
            border-radius: 20px;
            overflow: hidden;
            margin: 20px 0;
            position: relative;
        }
        
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #00ff88, #00cc6a);
            transition: width 1s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            color: #000;
        }
        
        .actions {
            display: flex;
            gap: 15px;
            justify-content: center;
            margin-top: 30px;
        }
        
        .action-button {
            padding: 12px 24px;
            background: #00ff88;
            color: #000000;
            text-decoration: none;
            border-radius: 5px;
            font-weight: bold;
            transition: all 0.3s ease;
            display: inline-block;
        }
        
        .action-button:hover {
            background: #00cc6a;
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0, 255, 136, 0.4);
        }
        
        .action-button.secondary {
            background: transparent;
            border: 2px solid #00ff88;
            color: #00ff88;
        }
        
        .action-button.secondary:hover {
            background: rgba(0, 255, 136, 0.1);
        }
        
        .achievement {
            background: rgba(255, 215, 0, 0.1);
            border: 2px solid rgba(255, 215, 0, 0.3);
            color: #ffd700;
            padding: 15px;
            border-radius: 8px;
            margin: 20px 0;
            font-size: 1.1rem;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 Quiz Complete!</h1>
        
        <div class="score-display">{{ score }}/{{ total }}</div>
        
        <div class="progress-visual">
            <div class="progress-fill" style="width: {{ percentage }}%">
                {{ percentage }}%
            </div>
        </div>
        
        <div class="score-details">
            <div class="detail-row">
                <span class="detail-label">Correct Answers:</span>
                <span class="detail-value">{{ score }}</span>
            </div>
            <div class="detail-row">
                <span class="detail-label">Total Questions:</span>
                <span class="detail-value">{{ total }}</span>
            </div>
            <div class="detail-row">
                <span class="detail-label">Time Taken:</span>
                <span class="detail-value">{{ time_taken }}</span>
            </div>
            <div class="detail-row">
                <span class="detail-label">Accuracy:</span>
                <span class="detail-value">{{ percentage }}%</span>
            </div>
        </div>
        
        {% if completed %}
        <div class="status-message success">
            ✅ Excellent work! You've demonstrated strong security knowledge.
        </div>
        {% if percentage == 100 %}
        <div class="achievement">
            🏆 Perfect Score! You're a cybersecurity expert!
        </div>
        {% endif %}
        {% else %}
        <div class="status-message failure">
            ❌ Keep studying! You need 70% or higher to pass. 
        </div>
        {% endif %}
        
        <div class="actions">
            <a href="/quiz/" class="action-button secondary">Try Again</a>
            <a href="/menu/" class="action-button">Back to Menu</a>
        </div>
    </div>
    
    <script>
        // Animate score display
        const scoreDisplay = document.querySelector('.score-display');
        const finalScore = {{ score }};
        let currentScore = 0;
        
        const animateScore = setInterval(() => {
            if (currentScore < finalScore) {
                currentScore++;
                scoreDisplay.textContent = currentScore + '/{{ total }}';
            } else {
                clearInterval(animateScore);
            }
        }, 50);
        
        // Animate progress bar
        const progressFill = document.querySelector('.progress-fill');
        setTimeout(() => {
            progressFill.style.width = '{{ percentage }}%';
        }, 100);
    </script>
</body>
</html>
"""

def save_progress(user_id, score, completed):
    """Save quiz progress to SQLite"""
    conn = sqlite3.connect('game.db')
    cursor = conn.cursor()
    
    # Check existing progress
    cursor.execute('''
        SELECT best_score, total_attempts 
        FROM game_progress 
        WHERE user_id = ? AND game_name = ?
    ''', (user_id, 'quiz'))
    
    current = cursor.fetchone()
    
    if current:
        best_score = max(current[0], score)
        total_attempts = current[1] + 1
        cursor.execute('''
            UPDATE game_progress 
            SET is_completed = ?, best_score = ?, total_attempts = ?
            WHERE user_id = ? AND game_name = ?
        ''', (completed or current[0], best_score, total_attempts, user_id, 'quiz'))
    else:
        cursor.execute('''
            INSERT INTO game_progress (user_id, game_name, is_completed, best_score, total_attempts)
            VALUES (?, ?, ?, ?, 1)
        ''', (user_id, 'quiz', completed, score))
    
    # Update user total score if completed for first time
    if completed and (not current or not current[0]):
        cursor.execute('''
            UPDATE users 
            SET total_score = total_score + ?, games_completed = games_completed + 1
            WHERE id = ?
        ''', (score, user_id))
    
    conn.commit()
    conn.close()

@quiz_bp.route("/", methods=["GET", "POST"])
@login_required
def index():
    # Force reset if something seems wrong
    if request.args.get('reset'):
        session.pop('quiz_questions', None)
        session.pop('quiz_index', None)
        session.pop('quiz_score', None)
        session.pop('quiz_start_time', None)
        return redirect(url_for('quiz.index'))
    
    # Initialize new quiz session if needed
    if ("quiz_questions" not in session or 
        "quiz_index" not in session or
        session.get("quiz_index", 0) >= NUM_QUESTIONS):
        
        # Clear any old data
        session.pop('quiz_questions', None)
        session.pop('quiz_index', None)
        session.pop('quiz_score', None)
        session.pop('quiz_start_time', None)
        
        # Start fresh
        selected_questions = random.sample(QUESTIONS, NUM_QUESTIONS)
        session["quiz_questions"] = selected_questions
        session["quiz_index"] = 0
        session["quiz_score"] = 0
        session["quiz_start_time"] = int(time.time())

    current_index = session.get("quiz_index", 0)
    questions = session.get("quiz_questions", [])
    
    # Safety check
    if not questions or current_index >= len(questions):
        # Something went wrong, restart
        session.pop('quiz_questions', None)
        session.pop('quiz_index', None)
        session.pop('quiz_score', None)
        session.pop('quiz_start_time', None)
        return redirect(url_for("quiz.index"))
    
    if request.method == "POST":
        # Process answer
        user_answer = request.form.get("answer")
        if user_answer:  # Only process if an answer was provided
            correct_answer = questions[current_index]["answer"]
            
            if user_answer == correct_answer:
                session["quiz_score"] = session.get("quiz_score", 0) + 1
            
            # Move to next question
            session["quiz_index"] = current_index + 1
            
            # Check if quiz is complete after answering
            if session["quiz_index"] >= len(questions):
                return redirect(url_for("quiz.result"))
            
            return redirect(url_for("quiz.index"))
    
    # Display current question
    try:
        current_question = questions[current_index]
    except (IndexError, TypeError):
        # Something is wrong with the data, restart
        session.pop('quiz_questions', None)
        session.pop('quiz_index', None)
        session.pop('quiz_score', None)
        session.pop('quiz_start_time', None)
        return redirect(url_for("quiz.index"))
    
    return render_template_string(
        QUIZ_QUESTION_TEMPLATE,
        question=current_question,
        current=current_index + 1,
        total=len(questions),
        start_time=session.get("quiz_start_time", int(time.time()))
    )

@quiz_bp.route("/result")
@login_required
def result():
    # Safety checks
    if ("quiz_questions" not in session or 
        "quiz_score" not in session):
        # No quiz data, redirect to start
        return redirect(url_for("quiz.index"))
    
    score = session.get("quiz_score", 0)
    total = len(session.get("quiz_questions", []))
    
    # Safety check for total
    if total == 0:
        return redirect(url_for("quiz.index"))
    
    # Calculate statistics
    percentage = int((score / total * 100)) if total > 0 else 0
    completed = percentage >= 70
    
    # Calculate time taken (with safety check)
    start_time = session.get("quiz_start_time", int(time.time()))
    current_time = int(time.time())
    
    # Sanity check: if time difference is more than 1 hour, something's wrong
    if current_time - start_time > 3600:
        time_taken = "N/A"
    else:
        time_taken_seconds = current_time - start_time
        minutes = time_taken_seconds // 60
        seconds = time_taken_seconds % 60
        time_taken = f"{minutes}:{seconds:02d}"
    
    # Save progress
    save_progress(current_user.id, score, completed)
    
    # Clear session
    session.pop('quiz_questions', None)
    session.pop('quiz_index', None)
    session.pop('quiz_score', None)
    session.pop('quiz_start_time', None)
    
    return render_template_string(
        QUIZ_RESULT_TEMPLATE,
        score=score,
        total=total,
        percentage=percentage,
        completed=completed,
        time_taken=time_taken
    )
@quiz_bp.route("/clear")
@login_required
def clear_session():
    session.pop('quiz_questions', None)
    session.pop('quiz_index', None)
    session.pop('quiz_score', None)
    session.pop('quiz_start_time', None)
    return redirect(url_for('quiz.index'))