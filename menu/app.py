# app.py - Main Flask application
from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
import os
import json
import datetime

app = Flask(__name__)
app.secret_key = 'cybersec_game_secret_key'  # For session and flash messages

# Database setup
DB_PATH = 'game_data.db'

def init_db():
    """Initialize the database with required tables."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Create game_saves table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS game_saves (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        save_name TEXT NOT NULL,
        level INTEGER NOT NULL,
        score INTEGER NOT NULL,
        game_data TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    ''')
    
    # Create settings table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS settings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        difficulty TEXT DEFAULT 'normal',
        sound_enabled BOOLEAN DEFAULT 1,
        display_mode TEXT DEFAULT 'light',
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    ''')
    
    conn.commit()
    conn.close()

# Initialize database when the app starts
init_db()

# Route for the home page / main menu
@app.route('/')
def main_menu():
    """Render the main menu page."""
    user_id = session.get('user_id')
    username = session.get('username')
    
    return render_template('main_menu.html', username=username)

# User authentication routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login."""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']  # In a real app, you'd use password hashing
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('SELECT id, username FROM users WHERE username = ? AND password = ?', 
                      (username, password))
        user = cursor.fetchone()
        conn.close()
        
        if user:
            session['user_id'] = user[0]
            session['username'] = user[1]
            flash('Login successful!', 'success')
            return redirect(url_for('main_menu'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Handle user registration."""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']  # In a real app, you'd use password hashing
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        try:
            cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', 
                          (username, password))
            conn.commit()
            
            user_id = cursor.lastrowid
            
            # Create default settings for the new user
            cursor.execute('INSERT INTO settings (user_id) VALUES (?)', (user_id,))
            conn.commit()
            
            conn.close()
            
            session['user_id'] = user_id
            session['username'] = username
            flash('Registration successful!', 'success')
            return redirect(url_for('main_menu'))
        except sqlite3.IntegrityError:
            flash('Username already exists', 'error')
            conn.close()
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    """Handle user logout."""
    session.pop('user_id', None)
    session.pop('username', None)
    flash('You have been logged out', 'info')
    return redirect(url_for('main_menu'))

# Game routes
@app.route('/new_game')
def new_game():
    """Start a new game."""
    if not session.get('user_id'):
        flash('Please login first', 'error')
        return redirect(url_for('login'))
    
    # Initialize a new game state
    new_game_data = {
        'level': 1,
        'score': 0,
        'map_position': [0, 0],
        'discovered_nodes': [],
        'inventory': {
            'encryption_key': 1, 
            'firewall': 0, 
            'exploit': 0
        },
        'created_at': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    # Store the initial game state in the session
    session['current_game'] = new_game_data
    
    return redirect(url_for('game_map'))

@app.route('/load_game')
def load_game_menu():
    """Show available saved games."""
    if not session.get('user_id'):
        flash('Please login first', 'error')
        return redirect(url_for('login'))
    
    user_id = session.get('user_id')
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, save_name, level, score, updated_at 
        FROM game_saves 
        WHERE user_id = ? 
        ORDER BY updated_at DESC
    ''', (user_id,))
    saves = cursor.fetchall()
    conn.close()
    
    return render_template('load_game.html', saves=saves)

@app.route('/load_game/<int:save_id>')
def load_game(save_id):
    """Load a specific saved game."""
    if not session.get('user_id'):
        flash('Please login first', 'error')
        return redirect(url_for('login'))
    
    user_id = session.get('user_id')
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT game_data 
        FROM game_saves 
        WHERE id = ? AND user_id = ?
    ''', (save_id, user_id))
    result = cursor.fetchone()
    conn.close()
    
    if result:
        game_data = json.loads(result[0])
        session['current_game'] = game_data
        flash('Game loaded successfully!', 'success')
        return redirect(url_for('game_map'))
    else:
        flash('Save file not found', 'error')
        return redirect(url_for('load_game_menu'))

@app.route('/save_game', methods=['GET', 'POST'])
def save_game():
    """Save the current game."""
    if not session.get('user_id'):
        flash('Please login first', 'error')
        return redirect(url_for('login'))
    
    if not session.get('current_game'):
        flash('No active game to save', 'error')
        return redirect(url_for('main_menu'))
    
    if request.method == 'POST':
        save_name = request.form['save_name']
        user_id = session.get('user_id')
        game_data = session.get('current_game')
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Check if save name already exists for this user
        cursor.execute('''
            SELECT id FROM game_saves 
            WHERE user_id = ? AND save_name = ?
        ''', (user_id, save_name))
        existing_save = cursor.fetchone()
        
        current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        game_data['updated_at'] = current_time
        
        if existing_save:
            # Update existing save
            cursor.execute('''
                UPDATE game_saves 
                SET level = ?, score = ?, game_data = ?, updated_at = ? 
                WHERE id = ?
            ''', (game_data['level'], game_data['score'], json.dumps(game_data), 
                  current_time, existing_save[0]))
            flash('Game updated successfully!', 'success')
        else:
            # Create new save
            cursor.execute('''
                INSERT INTO game_saves (user_id, save_name, level, score, game_data)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, save_name, game_data['level'], game_data['score'], 
                  json.dumps(game_data)))
            flash('Game saved successfully!', 'success')
        
        conn.commit()
        conn.close()
        return redirect(url_for('main_menu'))
    
    return render_template('save_game.html')

@app.route('/settings', methods=['GET', 'POST'])
def settings():
    """Manage game settings."""
    if not session.get('user_id'):
        flash('Please login first', 'error')
        return redirect(url_for('login'))
    
    user_id = session.get('user_id')
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    if request.method == 'POST':
        difficulty = request.form['difficulty']
        sound_enabled = 1 if request.form.get('sound_enabled') else 0
        display_mode = request.form['display_mode']
        
        cursor.execute('''
            UPDATE settings 
            SET difficulty = ?, sound_enabled = ?, display_mode = ? 
            WHERE user_id = ?
        ''', (difficulty, sound_enabled, display_mode, user_id))
        conn.commit()
        flash('Settings updated successfully!', 'success')
    
    # Get current settings
    cursor.execute('SELECT difficulty, sound_enabled, display_mode FROM settings WHERE user_id = ?', 
                  (user_id,))
    settings = cursor.fetchone()
    conn.close()
    
    if not settings:
        settings = ('normal', 1, 'light')  # Default settings
    
    return render_template('settings.html', settings=settings)

@app.route('/help')
def help_menu():
    """Display game help and instructions."""
    return render_template('help.html')

@app.route('/game_map')
def game_map():
    """Show the game map interface."""
    if not session.get('user_id'):
        flash('Please login first', 'error')
        return redirect(url_for('login'))
    
    if not session.get('current_game'):
        flash('No active game', 'error')
        return redirect(url_for('main_menu'))
    
    game_data = session.get('current_game')
    
    return render_template('game_map.html', game_data=game_data)

# Run the application
if __name__ == '__main__':
    app.run(debug=True)