import sqlite3

def repair_database():
    """Repair and clean up the database"""
    conn = sqlite3.connect('game.db')
    cursor = conn.cursor()
    
    print("=== DATABASE REPAIR SCRIPT ===\n")
    
    # First, let's see what we have
    print("1. Checking current state...")
    cursor.execute("SELECT id, username, total_score, games_completed FROM users")
    users = cursor.fetchall()
    
    for user_id, username, total_score, games_completed in users:
        print(f"\nUser {user_id} ({username}):")
        print(f"  Current total_score: {total_score}, games_completed: {games_completed}")
        
        # Calculate what the values should be
        cursor.execute('''
            SELECT 
                COUNT(DISTINCT game_name) as games_count,
                SUM(best_score) as total_points
            FROM game_progress 
            WHERE user_id = ? AND is_completed = 1 AND best_score > 0
        ''', (user_id,))
        
        result = cursor.fetchone()
        correct_games = result[0] if result[0] else 0
        correct_score = result[1] if result[1] else 0
        
        print(f"  Should be: total_score: {correct_score}, games_completed: {correct_games}")
        
        # Update if different
        if total_score != correct_score or games_completed != correct_games:
            cursor.execute('''
                UPDATE users 
                SET total_score = ?, games_completed = ?
                WHERE id = ?
            ''', (correct_score, correct_games, user_id))
            print(f"  ✅ Fixed!")
    
    print("\n2. Checking for anomalies...")
    
    # Fix any game_progress records with score but not marked as completed
    cursor.execute('''
        UPDATE game_progress 
        SET is_completed = 1 
        WHERE best_score > 0 AND is_completed = 0
    ''')
    print(f"  Fixed {cursor.rowcount} incomplete records with scores")
    
    # Add missing sqldefender entries for users who have other games
    cursor.execute('''
        SELECT DISTINCT user_id FROM game_progress 
        WHERE user_id NOT IN (
            SELECT user_id FROM game_progress WHERE game_name = 'sqldefender'
        )
    ''')
    users_without_defender = cursor.fetchall()
    
    for (user_id,) in users_without_defender:
        cursor.execute('''
            INSERT INTO game_progress (user_id, game_name, is_completed, best_score, total_attempts)
            VALUES (?, 'sqldefender', 0, 0, 0)
        ''', (user_id,))
    print(f"  Added sqldefender entries for {len(users_without_defender)} users")
    
    conn.commit()
    print("\n✅ Database repair complete!")
    
    # Show final state
    print("\n3. Final state:")
    cursor.execute('''
        SELECT u.username, u.total_score, u.games_completed,
               (SELECT COUNT(*) FROM game_progress gp 
                WHERE gp.user_id = u.id AND gp.is_completed = 1) as actual_completed
        FROM users u
        ORDER BY u.total_score DESC
    ''')
    
    print("\n  Username         | Score | Games | Verified")
    print("  ----------------|-------|-------|----------")
    for row in cursor.fetchall():
        print(f"  {row[0]:<15} | {row[1]:<5} | {row[2]:<5} | {row[3]}")
    
    conn.close()

def purge_test_users():
    """Optional: Remove test users with 0 score and no real progress"""
    conn = sqlite3.connect('game.db')
    cursor = conn.cursor()
    
    print("\n=== PURGE TEST USERS ===")
    
    # Find users with 0 score and 0 games completed
    cursor.execute('''
        SELECT id, username 
        FROM users 
        WHERE total_score = 0 AND games_completed = 0
        AND id NOT IN (1, 2, 3)  -- Keep alice, bob, charlie
    ''')
    
    users_to_remove = cursor.fetchall()
    
    if users_to_remove:
        print(f"\nFound {len(users_to_remove)} users to remove:")
        for user_id, username in users_to_remove:
            print(f"  - {username} (ID: {user_id})")
        
        confirm = input("\nRemove these users? (y/n): ")
        if confirm.lower() == 'y':
            for user_id, _ in users_to_remove:
                # Delete game progress
                cursor.execute('DELETE FROM game_progress WHERE user_id = ?', (user_id,))
                # Delete user
                cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
            conn.commit()
            print("✅ Users removed!")
    else:
        print("No users to remove.")
    
    conn.close()

if __name__ == "__main__":
    repair_database()
    
    print("\n" + "="*50)
    purge = input("\nDo you want to purge test users with 0 progress? (y/n): ")
    if purge.lower() == 'y':
        purge_test_users()