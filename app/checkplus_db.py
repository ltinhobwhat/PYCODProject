import sqlite3

def check_save_functions():
    """Check what's happening with save functions"""
    conn = sqlite3.connect('game.db')
    cursor = conn.cursor()
    
    print("=== CHECKING SAVE ISSUE ===\n")
    
    # 1. Check table structure
    print("1. Checking game_progress table structure:")
    cursor.execute("PRAGMA table_info(game_progress)")
    columns = cursor.fetchall()
    print("   Columns:", [col[1] for col in columns])
    
    # 2. Check if there are ANY records being saved
    print("\n2. Recent game_progress records:")
    cursor.execute('''
        SELECT gp.*, u.username 
        FROM game_progress gp
        JOIN users u ON u.id = gp.user_id
        ORDER BY gp.id DESC
        LIMIT 10
    ''')
    records = cursor.fetchall()
    if records:
        for r in records:
            print(f"   User: {r[-1]}, Game: {r[2]}, Score: {r[4]}, Completed: {r[3]}")
    else:
        print("   NO RECORDS FOUND!")
    
    # 3. Check users table
    print("\n3. Users table current state:")
    cursor.execute("SELECT id, username, total_score, games_completed FROM users ORDER BY id DESC LIMIT 5")
    for user in cursor.fetchall():
        print(f"   ID: {user[0]}, User: {user[1]}, Score: {user[2]}, Games: {user[3]}")
    
    conn.close()

def test_save_function():
    """Test if we can manually save to the database"""
    conn = sqlite3.connect('game.db')
    cursor = conn.cursor()
    
    print("\n4. Testing manual save...")
    try:
        # Get a user ID to test with
        cursor.execute("SELECT id FROM users ORDER BY id DESC LIMIT 1")
        test_user_id = cursor.fetchone()[0]
        
        # Try to insert a test record
        cursor.execute('''
            INSERT INTO game_progress (user_id, game_name, is_completed, best_score, total_attempts)
            VALUES (?, 'test_game', 1, 99, 1)
        ''', (test_user_id,))
        
        conn.commit()
        print("   ✅ Manual save successful!")
        
        # Clean up test
        cursor.execute("DELETE FROM game_progress WHERE game_name = 'test_game'")
        conn.commit()
        
    except Exception as e:
        print(f"   ❌ Manual save failed: {e}")
    
    conn.close()

# Universal save function that DEFINITELY works
def universal_save_progress(user_id, game_name, score, completed=None):
    """
    Universal save function that handles all edge cases
    
    Usage in any game:
    from check_save_issue import universal_save_progress
    universal_save_progress(current_user.id, 'quiz', score, completed=True)
    """
    conn = sqlite3.connect('game.db')
    cursor = conn.cursor()
    
    try:
        # Determine if completed based on score if not specified
        if completed is None:
            completed = score > 0
        
        # Check if record exists
        cursor.execute('''
            SELECT id, best_score, is_completed 
            FROM game_progress 
            WHERE user_id = ? AND game_name = ?
        ''', (user_id, game_name))
        
        existing = cursor.fetchone()
        
        if existing:
            record_id, old_best_score, was_completed = existing
            new_best_score = max(old_best_score, score)
            
            # Update existing record
            cursor.execute('''
                UPDATE game_progress 
                SET best_score = ?, 
                    is_completed = ?,
                    total_attempts = total_attempts + 1
                WHERE id = ?
            ''', (new_best_score, completed or was_completed, record_id))
            
            print(f"Updated {game_name}: score {old_best_score} -> {new_best_score}")
            
            # Update user total if score improved
            if new_best_score > old_best_score:
                score_diff = new_best_score - old_best_score
                cursor.execute('''
                    UPDATE users 
                    SET total_score = total_score + ?
                    WHERE id = ?
                ''', (score_diff, user_id))
                print(f"Added {score_diff} to user total score")
            
            # Update games_completed if newly completed
            if completed and not was_completed:
                cursor.execute('''
                    UPDATE users 
                    SET games_completed = games_completed + 1
                    WHERE id = ?
                ''', (user_id,))
                print(f"Incremented games_completed")
                
        else:
            # Insert new record
            cursor.execute('''
                INSERT INTO game_progress 
                (user_id, game_name, is_completed, best_score, total_attempts)
                VALUES (?, ?, ?, ?, 1)
            ''', (user_id, game_name, completed, score))
            
            print(f"Created new {game_name} record: score {score}")
            
            # Update user totals
            if completed and score > 0:
                cursor.execute('''
                    UPDATE users 
                    SET total_score = total_score + ?,
                        games_completed = games_completed + 1
                    WHERE id = ?
                ''', (score, user_id))
                print(f"Added {score} to total score and incremented games")
            elif score > 0:
                cursor.execute('''
                    UPDATE users 
                    SET total_score = total_score + ?
                    WHERE id = ?
                ''', (score, user_id))
                print(f"Added {score} to total score")
        
        conn.commit()
        print("✅ Save successful!")
        return True
        
    except Exception as e:
        print(f"❌ Save error: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    check_save_functions()
    test_save_function()
    
    print("\n" + "="*50)
    print("\nTo fix your games, add this import to each game file:")
    print("from app.check_save_issue import universal_save_progress")
    print("\nThen replace the save function call with:")
    print("universal_save_progress(current_user.id, 'game_name', score, completed=True)")
    print("\nGame names should be: 'pswd', 'quiz', 'vigenere', 'hashgame', 'sqlinjector', 'sqldefender', 'social'")