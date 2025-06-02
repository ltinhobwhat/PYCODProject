from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from .models import User


menu_bp = Blueprint('menu', __name__)

@menu_bp.route("/")
@login_required
def menu():
    return render_template("menu.html", user=current_user)

@menu_bp.route('/end_game')
def end_game():
    return "Game ended!"