from flask import Blueprint, render_template, redirect, url_for

menu_bp = Blueprint('menu', __name__)

@menu_bp.route("/")
def menu():
    return render_template("menu.html")

@menu_bp.route("/game1")
def game1():
    return redirect(url_for("pswd_app.index"))

@menu_bp.route('/save_game')
def save_game():
    return "Game saved!"

@menu_bp.route('/end_game')
def end_game():
    return "Game ended!"
