#!/usr/bin/env python3
"""
Database initialization script for CyberSec Academy
Run this script to set up the database with achievements and sample data
"""

from app import create_app
from app.models import db, User, Achievement, GameProgress, UserAchievement
from app.progress_service import initialize_achievements
from werkzeug.security import generate_password_hash
import random

def create_sample_users():
    """Create sample users for testing"""
    sample_users = [
        {'username': 'alice_cyber', 'email': 'alice@example.com', 'password': 'password123'},
        {'username': 'bob_hacker', 'email': 'bob@example.com', 'password': 'password123'},
        {'username': 'charlie_sec', 'email': 'charlie@example.com', 'password': 'password123'},
        {'username': 'diana_expert', 'email': 'diana@example.com', 'password': 'password123'},
        {'username': 'eve_newbie', 'email': 'eve@example.com', 'password': 'password123'},
    ]
    
    created_users = []
    for user_data in sample_users:
        # Check if user already exists
        existing_user = User.query.filter_by(username=user_data['username']).first()
        if not existing_user:
            user = User(
                username=user_data['username'],
                email=user_data['email']
            )
            user.set_password(user_data['password'])
            
            # Add some random progress
            user.total_score = random.randint(0, 150)
            user.games_completed = random.randint(0, 6)
            user.current_level = random.randint(1, 5)
            
            db.session.add(user)
            created_users.append(user)
            print(f"Created user: {user.username}")
    
    db.session.commit()
    return created_users

def create_sample_progress(users):
    """Create sample game progress for users"""
    games = ['pswd', 'quiz', 'vigenere', 'hashgame', 'sqlinjector', 'sqldefender']
    
    for user in users:
        # Randomly complete some games for each user
        completed_games = random.sample(games, random.randint(0, len(games)))
        
        for game in games:
            progress = GameProgress(
                user_id=user.id,
                game_name=game,
                is_completed=(game in completed_games),
                best_score=random.randint(0, 15) if game in completed_games else random.randint(0, 8),
                total_attempts=random.randint(1, 10),
                completion_time=random.randint(30, 600) if game in completed_games else 0,
                current_level=random.randint(1, 3),
                session_data={
                    'accuracy': random.randint(50, 100),
                    'completion_time': random.randint(30, 600)
                }
            )
            
            if game in completed_games:
                progress.completed_at = db.func.current_timestamp()
            
            db.session.add(progress)
        
        print(f"Created progress for user: {user.username}")
    
    db.session.commit()

def award_sample_achievements(users):
    """Award some achievements to sample users"""
    achievements = Achievement.query.all()
    
    for user in users:
        # Randomly award some achievements
        num_achievements = random.randint(0, min(len(achievements), 5))
        awarded_achievements = random.sample(achievements, num_achievements)
        
        for achievement in awarded_achievements:
            user_achievement = UserAchievement(
                user_id=user.id,
                achievement_id=achievement.id
            )
            db.session.add(user_achievement)
            user.total_score += achievement.points
        
        print(f"Awarded {len(awarded_achievements)} achievements to {user.username}")
    
    db.session.commit()

def main():
    """Main initialization function"""
    app = create_app()
    
    with app.app_context():
        print("Initializing CyberSec Academy Database...")
        
        # Create all tables
        print("Creating database tables...")
        db.create_all()
        
        # Initialize achievements
        print("Setting up achievements...")
        initialize_achievements()
        
        # Create sample users (optional, for testing)
        print("Creating sample users...")
        sample_users = create_sample_users()
        
        if sample_users:
            print("Creating sample progress...")
            create_sample_progress(sample_users)
            
            print("Awarding sample achievements...")
            award_sample_achievements(sample_users)
        
        print("Database initialization complete!")
        print("\nSample login credentials:")
        print("Username: alice_cyber | Password: password123")
        print("Username: bob_hacker | Password: password123")
        print("Username: charlie_sec | Password: password123")
        print("Username: diana_expert | Password: password123")
        print("Username: eve_newbie | Password: password123")
        print("\nYou can also create your own account through the signup page.")

if __name__ == '__main__':
    main()