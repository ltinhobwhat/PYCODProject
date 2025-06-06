import sqlite3
from flask import Blueprint, render_template, jsonify
from flask_login import login_required, current_user

leaderboard_bp = Blueprint('leaderboard', __name__)

def get_leaderboard_data(limit=50):
    """Get leaderboard data from SQLite"""
    conn = sqlite3.connect('game.db')
    cursor = conn.cursor()
    
    # Get users ordered by total score
    cursor.execute('''
        SELECT username, total_score, games_completed, created_at
        FROM users 
        ORDER BY total_score DESC, games_completed DESC 
        LIMIT ?
    ''', (limit,))
    
    users = cursor.fetchall()
    leaderboard = []
    
    for i, user in enumerate(users, 1):
        leaderboard.append({
            'rank': i,
            'username': user[0],
            'total_score': user[1],
            'games_completed': user[2],
            'progress_percentage': (user[2] / 6) * 100,  # 6 total games
            'created_at': user[3]
        })
    
    conn.close()
    return leaderboard

@leaderboard_bp.route('/')
def leaderboard():
    """Public leaderboard page"""
    leaderboard_data = get_leaderboard_data(100)
    
    # Get total stats
    conn = sqlite3.connect('game.db')
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM users')
    total_users = cursor.fetchone()[0]
    conn.close()
    
    return f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>CyberSec Academy - Leaderboard</title>
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
                display: grid; 
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); 
                gap: 1rem; 
                margin-bottom: 2rem;
            }}
            .stat-card {{ 
                background: rgba(0,255,136,0.1); 
                padding: 1.5rem; 
                border-radius: 10px; 
                text-align: center;
                border: 1px solid rgba(0,255,136,0.3);
            }}
            .stat-number {{ font-size: 2rem; font-weight: bold; color: #00ff88; }}
            .stat-label {{ font-size: 0.9rem; opacity: 0.8; }}
            .leaderboard-table {{ 
                background: rgba(255,255,255,0.1); 
                border-radius: 10px; 
                overflow: hidden;
                border: 1px solid rgba(0,255,136,0.3);
            }}
            .table-header {{ 
                background: rgba(0,255,136,0.2); 
                padding: 1rem; 
                display: grid; 
                grid-template-columns: 60px 1fr 100px 100px 120px;
                font-weight: bold;
                border-bottom: 1px solid rgba(0,255,136,0.3);
            }}
            .table-row {{ 
                padding: 1rem; 
                display: grid; 
                grid-template-columns: 60px 1fr 100px 100px 120px;
                border-bottom: 1px solid rgba(255,255,255,0.1);
                transition: background 0.3s ease;
            }}
            .table-row:hover {{ background: rgba(0,255,136,0.1); }}
            .rank {{ font-weight: bold; }}
            .rank-1 {{ color: #ffd700; }}
            .rank-2 {{ color: #c0c0c0; }}
            .rank-3 {{ color: #cd7f32; }}
            .username {{ font-weight: 600; }}
            .score {{ color: #00ff88; font-weight: bold; }}
            .nav-links {{ text-align: center; margin-bottom: 2rem; }}
            .nav-links a {{ 
                color: #00ff88; 
                text-decoration: none; 
                margin: 0 1rem; 
                padding: 0.5rem 1rem; 
                background: rgba(0,255,136,0.2); 
                border-radius: 5px;
                transition: all 0.3s ease;
            }}
            .nav-links a:hover {{ background: rgba(0,255,136,0.3); }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="nav-links">
                <a href="/menu">🏠 Main Menu</a>
                <a href="/auth/logout">🚪 Logout</a>
            </div>
            
            <h1>🏆 Global Leaderboard</h1>
            
            <div class="stats">
                <div class="stat-card">
                    <div class="stat-number">{total_users}</div>
                    <div class="stat-label">Total Players</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{leaderboard_data[0]['total_score'] if leaderboard_data else 0}</div>
                    <div class="stat-label">Highest Score</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">6</div>
                    <div class="stat-label">Security Challenges</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{len([p for p in leaderboard_data if p['progress_percentage'] == 100])}</div>
                    <div class="stat-label">Complete Players</div>
                </div>
            </div>
            
            <div class="leaderboard-table">
                <div class="table-header">
                    <div>Rank</div>
                    <div>Player</div>
                    <div>Score</div>
                    <div>Games</div>
                    <div>Progress</div>
                </div>
                
                {"".join([f'''
                <div class="table-row">
                    <div class="rank rank-{player['rank'] if player['rank'] <= 3 else 'other'}">
                        {'🥇' if player['rank'] == 1 else '🥈' if player['rank'] == 2 else '🥉' if player['rank'] == 3 else ''} #{player['rank']}
                    </div>
                    <div class="username">{player['username']}</div>
                    <div class="score">{player['total_score']} pts</div>
                    <div>{player['games_completed']}/6</div>
                    <div>{player['progress_percentage']:.1f}%</div>
                </div>
                ''' for player in leaderboard_data])}
            </div>
        </div>
    </body>
    </html>
    '''

@leaderboard_bp.route('/dashboard')
@login_required
def dashboard():
    """Temporary simple dashboard"""
    return '''
    <h1>Dashboard Coming Soon!</h1>
    <p>Dashboard temporarily disabled due to technical issues.</p>
    <a href="/leaderboard">← Back to Leaderboard</a>
    <a href="/menu">🏠 Main Menu</a>
    '''

@leaderboard_bp.route('/api/leaderboard')
def api_leaderboard():
    """API endpoint for leaderboard data"""
    leaderboard_data = get_leaderboard_data(50)
    return jsonify(leaderboard_data)
