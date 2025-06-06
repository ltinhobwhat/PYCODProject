# main.py - Updated for Render deployment
import os
import subprocess
from app import create_app

app = create_app()

def init_db_if_needed():
    """Initialize database if it doesn't exist"""
    if not os.path.exists('game.db'):
        print("Database not found, initializing...")
        try:
            subprocess.run(['python', 'simple_database.py'], check=True)
            print("Database initialized successfully!")
        except subprocess.CalledProcessError as e:
            print(f"Error initializing database: {e}")
        except FileNotFoundError:
            print("simple_database.py not found - make sure it exists in your project")

if __name__ == "__main__":
    # Initialize database for production
    init_db_if_needed()
    
    # Get port from environment variable (Render sets this)
    port = int(os.environ.get('PORT', 5000))
    
    # Check if running in production
    debug_mode = os.environ.get('FLASK_ENV') != 'production'
    
    # Start the app
    app.run(host='0.0.0.0', port=port, debug=debug_mode)