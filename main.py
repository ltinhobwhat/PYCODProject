from flask import Flask, render_template, redirect, url_for
from pswdChecker import pswd_app  # Blueprint for password game
from menu import menu_bp         # Blueprint for menu
from map import map_bp           # NEW: Blueprint for the map
from quiz import quiz_bp
from vigenere import vigenere_bp




app = Flask(__name__)
app.secret_key = "supersecretkey"

# Register Blueprints
app.register_blueprint(menu_bp)
app.register_blueprint(pswd_app, url_prefix='/pswdChecker')
app.register_blueprint(map_bp, url_prefix='/map')  # Mount the map at `/map`
app.register_blueprint(quiz_bp, url_prefix='/quiz')
app.register_blueprint(vigenere_bp, url_prefix="/vigenere")

if __name__ == "__main__":
    app.run(debug=True)
