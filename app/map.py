from flask import Blueprint, render_template, redirect, url_for

map_bp = Blueprint('map', __name__)

@map_bp.route('/')
def map_page():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>CyberSec Academy - Challenge Map</title>
        <style>
            body { 
                font-family: 'Segoe UI', sans-serif; 
                background: linear-gradient(135deg, #0f0f23 0%, #1a1a3a 100%);
                color: white; 
                padding: 2rem; 
                margin: 0;
                min-height: 100vh;
            }
            .container { max-width: 1200px; margin: 0 auto; }
            h1 { color: #00ff88; text-align: center; font-size: 2.5rem; margin-bottom: 2rem; }
            .nav-links { text-align: center; margin-bottom: 2rem; }
            .nav-links a { 
                color: #00ff88; 
                text-decoration: none; 
                margin: 0 1rem; 
                padding: 0.5rem 1rem; 
                background: rgba(0,255,136,0.2); 
                border-radius: 5px;
            }
            .challenges-grid { 
                display: grid; 
                grid-template-columns: repeat(auto-fit, minmax(350px, 1fr)); 
                gap: 2rem; 
            }
            .challenge-card { 
                background: rgba(255,255,255,0.1); 
                padding: 2rem; 
                border-radius: 15px; 
                border: 2px solid rgba(0,255,136,0.3);
                text-align: center;
                transition: all 0.3s ease;
            }
            .challenge-card:hover { 
                transform: translateY(-10px); 
                border-color: #00ff88;
                box-shadow: 0 20px 40px rgba(0,255,136,0.3);
            }
            .challenge-icon { font-size: 3rem; margin-bottom: 1rem; }
            .challenge-title { color: #00ff88; font-size: 1.5rem; font-weight: bold; margin-bottom: 1rem; }
            .challenge-description { margin-bottom: 1.5rem; line-height: 1.6; opacity: 0.9; }
            .difficulty { 
                padding: 0.3rem 0.8rem; 
                border-radius: 15px; 
                font-size: 0.8rem; 
                font-weight: bold; 
                margin-bottom: 1rem;
                display: inline-block;
            }
            .difficulty-beginner { background: rgba(0,255,136,0.3); color: #00ff88; }
            .difficulty-intermediate { background: rgba(255,165,0,0.3); color: #ffa500; }
            .difficulty-advanced { background: rgba(255,69,69,0.3); color: #ff4545; }
            .challenge-button { 
                width: 100%; 
                padding: 1rem; 
                background: linear-gradient(135deg, #00ff88, #00cc6a);
                color: #000000; 
                border: none; 
                border-radius: 10px; 
                font-weight: bold; 
                font-size: 1.1rem; 
                cursor: pointer; 
                text-decoration: none; 
                display: block;
                transition: all 0.3s ease;
            }
            .challenge-button:hover { 
                background: linear-gradient(135deg, #00cc6a, #009955);
                transform: translateY(-2px);
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="nav-links">
                <a href="/menu">🏠 Main Menu</a>
                <a href="/leaderboard">🏆 Leaderboard</a>
                <a href="/leaderboard/dashboard">📊 Dashboard</a>
                <a href="/auth/logout">🚪 Logout</a>
            </div>
            
            <h1>🗺️ Security Challenge Map</h1>
            <p style="text-align: center; margin-bottom: 2rem; opacity: 0.9;">Choose your path and master cybersecurity skills</p>
            
            <div class="challenges-grid">
                <!-- Password Security Challenge -->
                <div class="challenge-card">
                    <div class="challenge-icon">🔑</div>
                    <div class="challenge-title">Password Security</div>
                    <div class="difficulty difficulty-beginner">Beginner</div>
                    <div class="challenge-description">
                        Learn the fundamentals of password security. Create strong passwords and test your memory skills.
                    </div>
                    <a href="/pswdChecker" class="challenge-button">
                        🚀 Start Challenge
                    </a>
                </div>
                
                <!-- Security Quiz Challenge -->
                <div class="challenge-card">
                    <div class="challenge-icon">🧠</div>
                    <div class="challenge-title">Security Knowledge Quiz</div>
                    <div class="difficulty difficulty-beginner">Beginner</div>
                    <div class="challenge-description">
                        Test your cybersecurity knowledge covering the CIA triad, common attacks, and security best practices.
                    </div>
                    <a href="/quiz" class="challenge-button">
                        🚀 Take Quiz
                    </a>
                </div>
                
                <!-- Vigenère Cipher Challenge -->
                <div class="challenge-card">
                    <div class="challenge-icon">🔐</div>
                    <div class="challenge-title">Vigenère Cipher</div>
                    <div class="difficulty difficulty-intermediate">Intermediate</div>
                    <div class="challenge-description">
                        Master the classic Vigenère cipher by decrypting encrypted words. Learn about polyalphabetic substitution.
                    </div>
                    <a href="/vigenere" class="challenge-button">
                        🚀 Decrypt Now
                    </a>
                </div>
                
                <!-- Hash Detective Challenge -->
                <div class="challenge-card">
                    <div class="challenge-icon">🕵️</div>
                    <div class="challenge-title">Hash Detective</div>
                    <div class="difficulty difficulty-intermediate">Intermediate</div>
                    <div class="challenge-description">
                        Become a hash algorithm detective! Identify different hash functions by analyzing their output patterns.
                    </div>
                    <a href="/hashgame" class="challenge-button">
                        🚀 Investigate
                    </a>
                </div>

                <!-- SQL Injection Challenge -->
                <div class="challenge-card">
                    <div class="challenge-icon">💀</div>
                    <div class="challenge-title">SQL Injection Mastery</div>
                    <div class="difficulty difficulty-advanced">Advanced</div>
                    <div class="challenge-description">
                        Learn offensive security techniques by exploiting SQL injection vulnerabilities across multiple levels.
                    </div>
                    <a href="/sqlinjector" class="challenge-button">
                        🚀 Exploit
                    </a>
                </div>
                
                <!-- SQL Defense Challenge -->
                <div class="challenge-card">
                    <div class="challenge-icon">🛡️</div>
                    <div class="challenge-title">SQL Defense Training</div>
                    <div class="difficulty difficulty-intermediate">Intermediate</div>
                    <div class="challenge-description">
                        Learn how to defend against SQL injection attacks using secure coding practices and parameterized queries.
                    </div>
                    <a href="/sqldefender" class="challenge-button">
                        🚀 Defend
                    </a>
                </div>
                
                <!-- Social Engineering Challenge -->
                <div class="challenge-card">
                    <div class="challenge-icon">🎭</div>
                    <div class="challenge-title">Social Engineering</div>
                    <div class="difficulty difficulty-advanced">Advanced</div>
                    <div class="challenge-description">
                        Test your awareness against social engineering tactics and see if you remember your passwords!
                        <br><br>
                        <strong style="color: #ff4545;">⚠️ Requires completion of all other challenges!</strong>
                    </div>
                    <a href="/social" class="challenge-button">
                        🚀 Test Awareness
                    </a>
                </div>
            </div>
        </div>
        
        <script>
            // Add floating security icons
            function createFloatingIcon() {
                const icons = ['🔒', '🛡️', '🔑', '💻', '⚡', '🎯', '🔍', '⚙️'];
                const icon = document.createElement('div');
                icon.textContent = icons[Math.floor(Math.random() * icons.length)];
                icon.style.position = 'fixed';
                icon.style.left = Math.random() * 100 + '%';
                icon.style.top = '-50px';
                icon.style.fontSize = '20px';
                icon.style.pointerEvents = 'none';
                icon.style.opacity = '0.3';
                icon.style.zIndex = '-1';
                document.body.appendChild(icon);
                
                const animation = icon.animate([
                    { transform: 'translateY(-50px) rotate(0deg)', opacity: 0 },
                    { transform: 'translateY(50px) rotate(180deg)', opacity: 0.3 },
                    { transform: `translateY(${window.innerHeight + 50}px) rotate(360deg)`, opacity: 0 }
                ], {
                    duration: 8000,
                    easing: 'linear'
                });
                
                animation.onfinish = () => icon.remove();
            }
            
            // Create floating icons periodically
            setInterval(createFloatingIcon, 2000);
        </script>
    </body>
    </html>
    '''

# Route handlers for launching minigames
@map_bp.route('/minigame/password')
def launch_password_game():
    return redirect(url_for('pswd_app.index')) 

@map_bp.route('/minigame/quiz')
def launch_quiz():
    return redirect(url_for('quiz.index'))

@map_bp.route('/minigame/vigenere')
def launch_vigenere():
    return redirect(url_for('vigenere.index'))

@map_bp.route('/minigame/hashgame')
def launch_hashgame():
    return redirect(url_for('hashgame.index'))

@map_bp.route('/minigame/sqlinjector')
def launch_sqlinjector():
    return redirect(url_for('sqlinjector.index'))

@map_bp.route('/minigame/sqldefender')
def launch_sqldefender():
    return redirect(url_for('sqlinjector.defender'))