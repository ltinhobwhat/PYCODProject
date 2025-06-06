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

def get_user_dashboard_data(user_id):
    """Get user's detailed progress"""
    conn = sqlite3.connect('game.db')
    cursor = conn.cursor()
    
    # Get user info
    cursor.execute('SELECT username, total_score, games_completed FROM users WHERE id = ?', (user_id,))
    user_data = cursor.fetchone()
    
    if not user_data:
        conn.close()
        return None
    
    # Get user's rank
    cursor.execute('SELECT COUNT(*) FROM users WHERE total_score > ?', (user_data[1],))
    rank = cursor.fetchone()[0] + 1
    
    # Get game progress
    cursor.execute('''
        SELECT game_name, is_completed, best_score, total_attempts 
        FROM game_progress 
        WHERE user_id = ?
    ''', (user_id,))
    
    game_progress = {}
    for row in cursor.fetchall():
        game_progress[row[0]] = {
            'is_completed': bool(row[1]),
            'best_score': row[2],
            'total_attempts': row[3]
        }
    
    conn.close()
    
    return {
        'user': {
            'username': user_data[0],
            'total_score': user_data[1],
            'games_completed': user_data[2],
            'rank': rank
        },
        'games': game_progress,
        'progress_percentage': (user_data[2] / 6) * 100
    }

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
    
    # Build the table rows safely
    table_rows = ""
    for player in leaderboard_data:
        rank_class = "rank-1" if player['rank'] == 1 else "rank-2" if player['rank'] == 2 else "rank-3" if player['rank'] == 3 else "rank-other"
        rank_emoji = "🥇" if player['rank'] == 1 else "🥈" if player['rank'] == 2 else "🥉" if player['rank'] == 3 else ""
        
        table_rows += f'''
        <div class="table-row">
            <div class="rank {rank_class}">
                {rank_emoji} #{player['rank']}
            </div>
            <div class="username">{player['username']}</div>
            <div class="score">{player['total_score']} pts</div>
            <div>{player['games_completed']}/6</div>
            <div>{player['progress_percentage']:.1f}%</div>
        </div>
        '''
    
    # Calculate stats safely
    highest_score = leaderboard_data[0]['total_score'] if leaderboard_data else 0
    complete_players = len([p for p in leaderboard_data if p['progress_percentage'] == 100])
    
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
                <a href="/leaderboard/dashboard">📊 My Dashboard</a>
                <a href="/auth/logout">🚪 Logout</a>
            </div>
            
            <h1>🏆 Global Leaderboard</h1>
            
            <div class="stats">
                <div class="stat-card">
                    <div class="stat-number">{total_users}</div>
                    <div class="stat-label">Total Players</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{highest_score}</div>
                    <div class="stat-label">Highest Score</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">6</div>
                    <div class="stat-label">Security Challenges</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{complete_players}</div>
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
                
                {table_rows}
            </div>
        </div>
    </body>
    </html>
    '''

@leaderboard_bp.route('/dashboard')
@login_required
def dashboard():
    """User's personal progress dashboard"""
    dashboard_data = get_user_dashboard_data(current_user.id)
    
    if not dashboard_data:
        return "User not found", 404
    
    games_info = {
        'pswd': {'name': 'Password Security', 'max_score': 3},
        'quiz': {'name': 'Security Quiz', 'max_score': 10},
        'vigenere': {'name': 'Vigenère Cipher', 'max_score': 10},
        'hashgame': {'name': 'Hash Detective', 'max_score': 15},
        'sqlinjector': {'name': 'SQL Injection', 'max_score': 3},
        'sqldefender': {'name': 'SQL Defense', 'max_score': 1}
    }
    
    # Calculate progress safely OUTSIDE the f-string
    progress_percentage = dashboard_data['progress_percentage']
    progress_degrees = int(progress_percentage * 3.6)
    
    # Build the progress circle CSS safely
    progress_bg = f"background: conic-gradient(#00ff88 0deg, #00ff88 {progress_degrees}deg, rgba(255,255,255,0.2) {progress_degrees}deg);"
    
    # Build game cards safely
    game_cards = ""
    for game_id, info in games_info.items():
        game_data = dashboard_data['games'].get(game_id, {})
        is_completed = game_data.get('is_completed', False)
        best_score = game_data.get('best_score', 0)
        total_attempts = game_data.get('total_attempts', 0)
        
        status_icon = "✅" if is_completed else "⭕"
        card_class = "completed" if is_completed else ""
        
        if is_completed:
            status_text = "Completed"
        elif total_attempts > 0:
            status_text = "In Progress"
        else:
            status_text = "Not Started"
        
        game_cards += f'''
        <div class="game-card {card_class}">
            <div class="game-title">{status_icon} {info['name']}</div>
            <div class="game-stats">
                <span>Score: {best_score}/{info['max_score']}</span>
                <span>Attempts: {total_attempts}</span>
            </div>
            <p>Status: {status_text}</p>
        </div>
        '''
    
    return f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>My Progress Dashboard</title>
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
            .user-stats {{ 
                background: rgba(0,255,136,0.1); 
                padding: 2rem; 
                border-radius: 10px; 
                text-align: center;
                margin-bottom: 2rem;
                border: 1px solid rgba(0,255,136,0.3);
            }}
            .games-grid {{ 
                display: grid; 
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); 
                gap: 1.5rem; 
            }}
            .game-card {{ 
                background: rgba(255,255,255,0.1); 
                padding: 1.5rem; 
                border-radius: 10px;
                border: 1px solid rgba(0,255,136,0.3);
            }}
            .game-card.completed {{ 
                border-color: #00ff88;
                background: rgba(0,255,136,0.2);
            }}
            .game-title {{ color: #00ff88; font-size: 1.2rem; font-weight: bold; margin-bottom: 1rem; }}
            .game-stats {{ display: flex; justify-content: space-between; margin-bottom: 1rem; }}
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
            .progress-circle {{ 
                width: 100px; 
                height: 100px; 
                border-radius: 50%; 
                {progress_bg}
                display: flex; 
                align-items: center; 
                justify-content: center; 
                margin: 0 auto 1rem;
                position: relative;
            }}
            .progress-circle::before {{ 
                content: ''; 
                width: 80px; 
                height: 80px; 
                border-radius: 50%; 
                background: #1a1a3a; 
                position: absolute;
            }}
            .progress-text {{ 
                position: relative; 
                z-index: 1; 
                font-weight: bold; 
                color: #00ff88;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="nav-links">
                <a href="/menu">🏠 Main Menu</a>
                <a href="/leaderboard">🏆 Leaderboard</a>
                <a href="/auth/logout">🚪 Logout</a>
            </div>
            
            <h1>📊 My Progress Dashboard</h1>
            
            <div class="user-stats">
                <h2>Welcome back, {dashboard_data['user']['username']}! 👋</h2>
                <div class="progress-circle">
                    <div class="progress-text">{progress_percentage:.0f}%</div>
                </div>
                <p><strong>Total Score:</strong> {dashboard_data['user']['total_score']} points</p>
                <p><strong>Games Completed:</strong> {dashboard_data['user']['games_completed']}/6</p>
                <p><strong>Global Rank:</strong> #{dashboard_data['user']['rank']}</p>
            </div>
            
            <div class="games-grid">
                {game_cards}
            </div>
        </div>
    </body>
    </html>
    '''

@leaderboard_bp.route('/statistics')
@login_required  
def statistics():
    """Global platform statistics"""
    conn = sqlite3.connect('game.db')
    cursor = conn.cursor()
    
    # Get global stats
    cursor.execute('SELECT COUNT(*) FROM users')
    total_users = cursor.fetchone()[0]
    
    cursor.execute('SELECT AVG(total_score) FROM users WHERE total_score > 0')
    avg_score = cursor.fetchone()[0] or 0
    
    cursor.execute('SELECT COUNT(*) FROM game_progress WHERE is_completed = 1')
    total_completions = cursor.fetchone()[0]
    
    cursor.execute('SELECT MAX(total_score) FROM users')
    max_score = cursor.fetchone()[0] or 0
    
    cursor.execute('SELECT COUNT(DISTINCT user_id) FROM game_progress WHERE is_completed = 1')
    active_players = cursor.fetchone()[0]
    
    conn.close()
    
    return f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Platform Statistics</title>
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
            .stats-grid {{ 
                display: grid; 
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); 
                gap: 1.5rem; 
                margin-bottom: 2rem;
            }}
            .stat-card {{ 
                background: rgba(0,255,136,0.1); 
                padding: 2rem; 
                border-radius: 10px; 
                text-align: center;
                border: 1px solid rgba(0,255,136,0.3);
            }}
            .stat-number {{ font-size: 2.5rem; font-weight: bold; color: #00ff88; }}
            .stat-label {{ font-size: 1rem; opacity: 0.8; margin-top: 0.5rem; }}
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
                <a href="/leaderboard">🏆 Leaderboard</a>
                <a href="/leaderboard/dashboard">📊 My Dashboard</a>
                <a href="/auth/logout">🚪 Logout</a>
            </div>
            
            <h1>📈 Platform Statistics</h1>
            
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-number">{total_users}</div>
                    <div class="stat-label">Total Players</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{avg_score:.1f}</div>
                    <div class="stat-label">Average Score</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{total_completions}</div>
                    <div class="stat-label">Total Completions</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{max_score}</div>
                    <div class="stat-label">Highest Score</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{active_players}</div>
                    <div class="stat-label">Active Players</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">6</div>
                    <div class="stat-label">Total Challenges</div>
                </div>
            </div>
        </div>
    </body>
    </html>
    '''

@leaderboard_bp.route('/api/leaderboard')
def api_leaderboard():
    """API endpoint for leaderboard data"""
    leaderboard_data = get_leaderboard_data(50)
    return jsonify(leaderboard_data)

@leaderboard_bp.route('/api/dashboard')
@login_required
def api_dashboard():
    """API endpoint for user dashboard data"""
    dashboard_data = get_user_dashboard_data(current_user.id)
    return jsonify(dashboard_data)
