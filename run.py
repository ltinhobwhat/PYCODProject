import webbrowser
import os
import subprocess
import time
from main import app

if __name__ == "__main__":
    try:
        # Minimize the command prompt window
        if os.name == 'nt':  # Windows
            import ctypes
            ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 6)  # SW_MINIMIZE = 6
        
        # Start the Flask app in a separate thread
        import threading
        server = threading.Thread(target=app.run, kwargs={
            'debug': False,
            'host': '127.0.0.1',
            'port': 5000
        })
        server.daemon = True
        server.start()
        
        # Give the server a moment to start
        time.sleep(1.5)
        
        # Open the browser
        webbrowser.open('http://127.0.0.1:5000')
        
        # Keep the script running
        while True:
            time.sleep(1)
            
    except Exception as e:
        print(f"Error: {e}")
        print("\nPress Enter to exit...")
        input()
