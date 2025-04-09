from flask import Flask, render_template, redirect, url_for
from pswdChecker import pswd_app  # Make sure pswdChecker.py has `pswd_app`
from menu import menu_bp  # Ensure menu.py is correct and includes the menu_bp blueprint

app = Flask(__name__)
app.secret_key = "supersecretkey"  # Keep this here on the app instance

# Register the blueprints
app.register_blueprint(menu_bp)
app.register_blueprint(pswd_app, url_prefix='/pswdChecker')  # Mount pswdChecker at `/pswdChecker`

if __name__ == "__main__":
    app.run(debug=True)
