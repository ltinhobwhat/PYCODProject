from flask import Flask, render_template, redirect, url_for
from pswdChecker import pswd_app  # Blueprint for password game
from menu import menu_bp         # Blueprint for menu
from map import map_bp           # NEW: Blueprint for the map
from quiz import quiz_bp
from vigenere import vigenere_bp
from hashgame import hashgame_bp
from sqlinjector import sqlinjector_bp


app = Flask(__name__)
app.secret_key = "supersecretkey"

# Register Blueprints
app.register_blueprint(menu_bp)
app.register_blueprint(pswd_app, url_prefix='/pswdChecker')
app.register_blueprint(map_bp, url_prefix='/map')  # Mount the map at `/map`
app.register_blueprint(quiz_bp, url_prefix='/quiz')
app.register_blueprint(vigenere_bp, url_prefix="/vigenere")
app.register_blueprint(hashgame_bp, url_prefix="/hashgame")
app.register_blueprint(sqlinjector_bp, url_prefix="/sqlinjector")


if __name__ == "__main__":
    app.run(debug=True)
