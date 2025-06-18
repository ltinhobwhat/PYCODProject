import os
import glob

def clear_flask_sessions():
    """Clear all Flask session files"""
    # Flask stores sessions in different places depending on config
    session_paths = [
        'flask_session/*',  # Default flask-session location
        'sessions/*',       # Alternative location
        '/tmp/flask_session*',  # Temp directory
    ]
    
    cleared = 0
    for path_pattern in session_paths:
        for session_file in glob.glob(path_pattern):
            try:
                os.remove(session_file)
                cleared += 1
                print(f"Removed: {session_file}")
            except Exception as e:
                print(f"Could not remove {session_file}: {e}")
    
    print(f"\n✅ Cleared {cleared} session files")
    print("All users will need to log in again.")

if __name__ == "__main__":
    response = input("This will log out ALL users. Continue? (y/n): ")
    if response.lower() == 'y':
        clear_flask_sessions()
    else:
        print("Cancelled.")