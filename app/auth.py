# auth.py
from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from .models import db, User  # This imports the db instance from models.py

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Proper query using the db session
        user = db.session.query(User).filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('menu.menu'))
        flash('Invalid username or password')
    return render_template('login.html')

@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')
        
        # Check for existing user
        if db.session.query(User).filter_by(username=username).first():
            flash('Username already exists')
            return redirect(url_for('auth.signup'))
            
        try:
            new_user = User(username=username, email=email)
            new_user.set_password(password)
            
            db.session.add(new_user)
            db.session.commit()
            
            login_user(new_user)
            return redirect(url_for('menu.menu'))
            
        except Exception as e:
            db.session.rollback()
            flash('Error creating account. Please try again.')
            return redirect(url_for('auth.signup'))
        
    return render_template('signup.html')

# In auth.py, update the logout route:
@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))  # Make sure this matches your blueprint name