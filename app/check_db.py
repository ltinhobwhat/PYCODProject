import sqlite3

def deep_clean_database():
    """Deep clean and repair the database"""
    conn = sqlite3.connect('game.db')
    cursor = conn.cursor()
    
    print("=== DEEP DATABASE CLEANING ===\n")
    
    # 1. First, recalculate all scores properly
    print("1. Recalculating all user scores...")
    cursor.execute("SELECT id, username FROM users")
    all_users = cursor.fetchall()
    
    for user_id, username in all_users:
        # Get the sum of best scores for completed games
        cursor.execute('''
            SELECT COALESCE(SUM(best_score), 0)
            FROM game_progress 
            WHERE user_id = ? AND is_completed = 1
        ''', (user_id,))
        correct_score = cursor.fetchone()[0]
        
        # Get count of completed games
        cursor.execute('''
            SELECT COUNT(DISTINCT game_name)
            FROM game_progress 
            WHERE user_id = ? AND is_completed = 1 AND best_score > 0
        ''', (user_id,))
        correct_games = cursor.fetchone()[0]
        
        # Update user
        cursor.execute('''
            UPDATE users 
            SET total_score = ?, games_completed = ?
            WHERE id = ?
        ''', (correct_score, correct_games, user_id))
        
        print(f"  {username}: Score={correct_score}, Games={correct_games}")
    
    # 2. Remove users with absolutely no activity
    print("\n2. Removing inactive users...")
    cursor.execute('''
        SELECT u.id, u.username 
        FROM users u
        WHERE u.id NOT IN (1, 2, 3)  -- Keep test users
        AND NOT EXISTS (
            SELECT 1 FROM game_progress gp 
            WHERE gp.user_id = u.id AND (gp.best_score > 0 OR gp.total_attempts > 0)
        )
    ''')
    
    inactive_users = cursor.fetchall()
    if inactive_users:
        print(f"  Found {len(inactive_users)} inactive users:")
        for user_id, username in inactive_users:
            print(f"    - {username} (ID: {user_id})")
            # Delete their empty game_progress records
            cursor.execute('DELETE FROM game_progress WHERE user_id = ?', (user_id,))
            # Delete the user
            cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
    else:
        print("  No inactive users found")
    
    # 3. Fix alice, bob, charlie if they exist
    print("\n3. Resetting test users (alice, bob, charlie)...")
    test_users = [
        (1, 'alice_cyber', 0, 0),
        (2, 'bob_hacker', 0, 0),
        (3, 'charlie_sec', 0, 0)
    ]
    
    for user_id, username, score, games in test_users:
        cursor.execute('''
            UPDATE users 
            SET total_score = ?, games_completed = ?
            WHERE id = ? AND username = ?
        ''', (score, games, user_id, username))
        
        # Remove any game progress for test users
        cursor.execute('DELETE FROM game_progress WHERE user_id = ?', (user_id,))
    
    # 4. Clean up orphaned game_progress records
    print("\n4. Cleaning orphaned records...")
    cursor.execute('''
        DELETE FROM game_progress 
        WHERE user_id NOT IN (SELECT id FROM users)
    ''')
    orphaned = cursor.rowcount
    print(f"  Removed {orphaned} orphaned game_progress records")
    
    # 5. Final verification
    print("\n5. Final state of the database:")
    cursor.execute('''
        SELECT u.id, u.username, u.total_score, u.games_completed,
               (SELECT COUNT(*) FROM game_progress gp 
                WHERE gp.user_id = u.id AND gp.is_completed = 1) as verified_games,
               (SELECT COALESCE(SUM(best_score), 0) FROM game_progress gp 
                WHERE gp.user_id = u.id AND gp.is_completed = 1) as verified_score
        FROM users u
        ORDER BY u.total_score DESC, u.id ASC
    ''')
    
    print("\n  ID | Username       | Score | Games | V.Score | V.Games")
    print("  ---|----------------|-------|-------|---------|--------")
    for row in cursor.fetchall():
        user_id, username, score, games, v_games, v_score = row
        match = "✓" if score == v_score and games == v_games else "✗"
        print(f"  {user_id:<2} | {username:<14} | {score:<5} | {games:<5} | {v_score:<7} | {v_games:<6} {match}")
    
    conn.commit()
    conn.close()
    print("\n✅ Deep cleaning complete!")

def show_game_progress_details():
    """Show detailed game progress for verification"""
    conn = sqlite3.connect('game.db')
    cursor = conn.cursor()
    
    print("\n=== GAME PROGRESS DETAILS ===")
    cursor.execute('''
        SELECT u.username, gp.game_name, gp.is_completed, gp.best_score, gp.total_attempts
        FROM game_progress gp
        JOIN users u ON u.id = gp.user_id
        WHERE gp.best_score > 0 OR gp.total_attempts > 0
        ORDER BY u.username, gp.game_name
    ''')
    
    current_user = None
    for row in cursor.fetchall():
        username, game, completed, score, attempts = row
        if username != current_user:
            current_user = username
            print(f"\n{username}:")
        print(f"  - {game}: Score={score}, Completed={bool(completed)}, Attempts={attempts}")
    
    conn.close()

if __name__ == "__main__":
    deep_clean_database()
    
    print("\n" + "="*60)
    show_details = input("\nShow detailed game progress? (y/n): ")
    if show_details.lower() == 'y':
        show_game_progress_details()