# app/menu.py (Einfache Version ohne komplexe Imports)
from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user

menu_bp = Blueprint('menu', __name__)

@menu_bp.route("/")
@login_required
def menu():
    # Einfache HTML-Version ohne externe Dependencies
    return f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>CyberSec Academy - Main Menu</title>
        <style>
            body {{ 
                font-family: 'Segoe UI', sans-serif; 
                background: linear-gradient(135deg, #0f0f23 0%, #1a1a3a 100%);
                color: white; 
                padding: 2rem; 
                margin: 0;
                min-height: 100vh;
            }}
            .container {{ max-width: 1000px; margin: 0 auto; }}
            h1 {{ color: #00ff88; text-align: center; font-size: 2.5rem; margin-bottom: 2rem; }}
            .stats {{ 
                background: rgba(0,255,136,0.1); 
                padding: 1.5rem; 
                border-radius: 10px; 
                margin-bottom: 2rem; 
                text-align: center;
                border: 1px solid rgba(0,255,136,0.3);
            }}
            .games-grid {{ 
                display: grid; 
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); 
                gap: 1.5rem; 
                margin-bottom: 2rem;
            }}
            .game-card {{ 
                background: rgba(255,255,255,0.1); 
                padding: 1.5rem; 
                border-radius: 10px; 
                text-align: center;
                border: 1px solid rgba(0,255,136,0.3);
                transition: transform 0.3s ease;
            }}
            .game-card:hover {{ transform: translateY(-5px); }}
            .game-card h3 {{ color: #00ff88; margin-bottom: 1rem; }}
            a {{ 
                color: #00ff88; 
                text-decoration: none; 
                font-weight: bold; 
                padding: 0.8rem 1.5rem; 
                background: rgba(0,255,136,0.2); 
                border-radius: 5px; 
                display: inline-block;
                margin: 0.5rem;
                transition: all 0.3s ease;
            }}
            a:hover {{ 
                background: rgba(0,255,136,0.3); 
                transform: translateY(-2px);
            }}
            .logout {{ background: rgba(255,0,0,0.2); color: #ff6b6b; }}
            .logout:hover {{ background: rgba(255,0,0,0.3); }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🛡️ CyberSec Academy</h1>
            
            <div class="stats">
                <h2>Welcome back, {current_user.username}! 👋</h2>
                <p><strong>Total Score:</strong> {current_user.total_score} points</p>
                <p><strong>Games Completed:</strong> {current_user.games_completed}/6</p>
                <p><strong>Rank:</strong> Rising Hacker 🚀</p>
            </div>
            
            <div class="games-grid">
                <div class="game-card">
                    <h3>🔑 Password Security</h3>
                    <p>Learn secure password practices and test your memory</p>
                    <a href="/pswdChecker">Start Challenge</a>
                </div>
                
                <div class="game-card">
                    <h3>🧠 Security Quiz</h3>
                    <p>Test your cybersecurity knowledge</p>
                    <a href="/quiz">Take Quiz</a>
                </div>
                
                <div class="game-card">
                    <h3>🔐 Vigenère Cipher</h3>
                    <p>Master classical cryptography</p>
                    <a href="/vigenere">Decrypt Now</a>
                </div>
                
                <div class="game-card">
                    <h3>🕵️ Hash Detective</h3>
                    <p>Identify hash algorithms</p>
                    <a href="/hashgame">Investigate</a>
                </div>
                
                <div class="game-card">
                    <h3>💀 SQL Injection</h3>
                    <p>Learn offensive security</p>
                    <a href="/sqlinjector">Exploit</a>
                </div>
                
                <div class="game-card">
                    <h3>🛡️ SQL Defense</h3>
                    <p>Protect against attacks</p>
                    <a href="/sqlinjector/defender">Defend</a>
                </div>
            </div>
            
            <div style="text-align: center;">
                <a href="/map">🗺️ Challenge Map</a>
                <a href="/leaderboard">🏆 Leaderboard</a>
                <a href="/auth/logout" class="logout">🚪 Logout</a>
            </div>
        </div>
    </body>
    </html>
    '''

@menu_bp.route('/end_game')
def end_game():
    return "Game ended!"