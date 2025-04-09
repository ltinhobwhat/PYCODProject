from flask import Flask, render_template, redirect, url_for
from pswdChecker import app as pswd_app
from menu import menu_bp 

app = Flask(__name__)
app.secret_key = "supersecretkey"

# Register the blueprints
app.register_blueprint(menu_bp)
app.register_blueprint(pswd_app, url_prefix='/pswdChecker')

if __name__ == "__main__":
    app.run(debug=True)
