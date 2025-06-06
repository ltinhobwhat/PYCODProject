# app/auth.py (Emergency Fix)
from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from flask_login import login_user, logout_user, login_required
import sqlite3
import hashlib

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        conn = sqlite3.connect('game.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ? AND password_hash = ?', 
                      (username, password_hash))
        user_data = cursor.fetchone()
        conn.close()
        
        if user_data:
            from .simple_user import SimpleUser
            user = SimpleUser(user_data)
            login_user(user)
            # DIREKT zum Success-Page ohne Menu
            return redirect(url_for('auth.success'))
        else:
            flash('Invalid username or password')
    
    return render_template('login.html')

@auth_bp.route('/success')
@login_required
def success():
    from flask_login import current_user
    return f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Login Success</title>
        <style>
            body {{ font-family: Arial; background: #0f0f23; color: white; padding: 2rem; text-align: center; }}
            h1 {{ color: #00ff88; }}
            .success-box {{ background: rgba(0,255,136,0.1); padding: 2rem; border-radius: 10px; margin: 2rem auto; max-width: 600px; }}
            a {{ color: #00ff88; text-decoration: none; font-weight: bold; padding: 0.5rem 1rem; background: rgba(0,255,136,0.2); border-radius: 5px; margin: 0.5rem; display: inline-block; }}
            a:hover {{ background: rgba(0,255,136,0.3); }}
        </style>
    </head>
    <body>
        <div class="success-box">
            <h1>🎉 Welcome {current_user.username}!</h1>
            <p>Your CyberSec Academy account is now active.</p>
            <p>Score: {current_user.total_score} points | Games: {current_user.games_completed}/6</p>
            
            <div style="margin: 2rem 0;">
                <a href="/menu">🏠 Main Menu</a>
                <a href="/map">🗺️ Challenge Map</a>
                <a href="/auth/logout">🚪 Logout</a>
            </div>
        </div>
    </body>
    </html>
    '''

@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')
        
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        conn = sqlite3.connect('game.db')
        cursor = conn.cursor()
        
        cursor.execute('SELECT id FROM users WHERE username = ?', (username,))
        if cursor.fetchone():
            flash('Username already exists')
            conn.close()
            return redirect(url_for('auth.signup'))
        
        try:
            cursor.execute('''
                INSERT INTO users (username, email, password_hash, total_score, games_completed)
                VALUES (?, ?, ?, 0, 0)
            ''', (username, email, password_hash))
            conn.commit()
            
            user_id = cursor.lastrowid
            cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
            user_data = cursor.fetchone()
            conn.close()
            
            from .simple_user import SimpleUser
            user = SimpleUser(user_data)
            login_user(user)
            
            # DIREKT zum Success-Page
            return redirect(url_for('auth.success'))
            
        except Exception as e:
            conn.rollback()
            conn.close()
            flash('Error creating account. Please try again.')
            return redirect(url_for('auth.signup'))
        
    return render_template('signup.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))