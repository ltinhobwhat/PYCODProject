# simple_database.py
import sqlite3
import hashlib
from datetime import datetime

def create_database():
    """Erstelle die Datenbank mit allen nötigen Tabellen"""
    conn = sqlite3.connect('game.db')
    cursor = conn.cursor()
    
    # Users Tabelle
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            total_score INTEGER DEFAULT 0,
            games_completed INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Game Progress Tabelle
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS game_progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            game_name TEXT NOT NULL,
            is_completed BOOLEAN DEFAULT 0,
            best_score INTEGER DEFAULT 0,
            total_attempts INTEGER DEFAULT 0,
            completion_time INTEGER DEFAULT 0,
            session_data TEXT DEFAULT '{}',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Achievements Tabelle
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS achievements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            description TEXT NOT NULL,
            icon TEXT DEFAULT '🏆',
            points INTEGER DEFAULT 10
        )
    ''')
    
    # User Achievements Tabelle
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_achievements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            achievement_id INTEGER NOT NULL,
            earned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (achievement_id) REFERENCES achievements (id)
        )
    ''')
    
    # Standard Achievements hinzufügen
    achievements = [
        ('First Steps', 'Complete your first security challenge', '👶', 10),
        ('Quiz Master', 'Complete the Security Quiz', '🧠', 15),
        ('Cipher Breaker', 'Master the Vigenère cipher', '🔓', 20),
        ('Hash Detective', 'Identify hash algorithms like a pro', '🕵️', 20),
        ('SQL Ninja', 'Master SQL injection techniques', '🥷', 25),
        ('Security Defender', 'Learn to defend against SQL injection', '🛡️', 15),
        ('Century Club', 'Score 100 points or more', '💯', 50),
        ('Elite Hacker', 'Complete all security challenges', '👑', 100)
    ]
    
    for name, desc, icon, points in achievements:
        cursor.execute('''
            INSERT OR IGNORE INTO achievements (name, description, icon, points)
            VALUES (?, ?, ?, ?)
        ''', (name, desc, icon, points))
    
    # Test User erstellen
    test_users = [
        ('alice_cyber', 'alice@example.com', 'password123'),
        ('bob_hacker', 'bob@example.com', 'password123'),
        ('charlie_sec', 'charlie@example.com', 'password123')
    ]
    
    for username, email, password in test_users:
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        cursor.execute('''
            INSERT OR IGNORE INTO users (username, email, password_hash, total_score, games_completed)
            VALUES (?, ?, ?, ?, ?)
        ''', (username, email, password_hash, 50, 2))
    
    conn.commit()
    conn.close()
    print("✅ Database created successfully!")
    print("\nTest accounts:")
    print("Username: alice_cyber | Password: password123")
    print("Username: bob_hacker | Password: password123")
    print("Username: charlie_sec | Password: password123")

if __name__ == '__main__':
    create_database()