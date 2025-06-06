from .models import db, User, GameProgress, Achievement, UserAchievement
from flask_login import current_user
from datetime import datetime

class ProgressService:
    """Service for managing game progress and achievements"""
    
    GAME_CONFIGS = {
        'pswd': {
            'name': 'Password Security',
            'completion_threshold': 3,  # Perfect score on memory test
            'max_score': 3
        },
        'quiz': {
            'name': 'Security Quiz',
            'completion_threshold': 7,  # 70% correct
            'max_score': 10
        },
        'vigenere': {
            'name': 'Vigenère Cipher',
            'completion_threshold': 5,  # 5 correct decryptions
            'max_score': 10
        },
        'hashgame': {
            'name': 'Hash Detective',
            'completion_threshold': 10,  # 10 correct identifications
            'max_score': 15
        },
        'sqlinjector': {
            'name': 'SQL Injection',
            'completion_threshold': 3,  # Complete all 3 levels
            'max_score': 3
        },
        'sqldefender': {
            'name': 'SQL Defense',
            'completion_threshold': 1,  # Answer correctly
            'max_score': 1
        }
    }
    
    @staticmethod
    def get_or_create_progress(user_id, game_name):
        """Get or create game progress for user"""
        progress = GameProgress.query.filter_by(user_id=user_id, game_name=game_name).first()
        if not progress:
            progress = GameProgress(user_id=user_id, game_name=game_name)
            db.session.add(progress)
            db.session.commit()
        return progress
    
    @staticmethod
    def update_game_progress(user_id, game_name, score=None, completed=None, level=None, session_data=None):
        """Update progress for a specific game"""
        try:
            progress = ProgressService.get_or_create_progress(user_id, game_name)
            user = User.query.get(user_id)
            
            old_completed = progress.is_completed
            old_score = progress.best_score
            
            # Update progress
            progress.update_progress(score, completed, level, session_data)
            
            # Update user's overall stats
            if completed and not old_completed:
                user.games_completed += 1
                
            # Update total score (difference from old best score)
            if score is not None and score > old_score:
                user.total_score += (score - old_score)
            
            db.session.commit()
            
            # Check for new achievements
            ProgressService.check_achievements(user_id)
            
            return progress
            
        except Exception as e:
            db.session.rollback()
            print(f"Error updating progress: {e}")
            return None
    
    @staticmethod
    def check_achievements(user_id):
        """Check and award any new achievements"""
        user = User.query.get(user_id)
        if not user:
            return
            
        # Get all achievements user doesn't have yet
        existing_achievement_ids = [ua.achievement_id for ua in user.achievements]
        available_achievements = Achievement.query.filter(
            ~Achievement.id.in_(existing_achievement_ids)
        ).all()
        
        new_achievements = []
        for achievement in available_achievements:
            if achievement.check_condition(user):
                user_achievement = UserAchievement(
                    user_id=user_id,
                    achievement_id=achievement.id
                )
                db.session.add(user_achievement)
                user.total_score += achievement.points
                new_achievements.append(achievement)
        
        if new_achievements:
            db.session.commit()
            
        return new_achievements
    
    @staticmethod
    def get_user_dashboard(user_id):
        """Get comprehensive dashboard data for user"""
        user = User.query.get(user_id)
        if not user:
            return None
            
        # Get all game progress
        progress_data = {}
        for game_name, config in ProgressService.GAME_CONFIGS.items():
            progress = GameProgress.query.filter_by(user_id=user_id, game_name=game_name).first()
            if progress:
                progress_data[game_name] = {
                    **progress.to_dict(),
                    'game_display_name': config['name'],
                    'completion_threshold': config['completion_threshold'],
                    'max_score': config['max_score']
                }
            else:
                progress_data[game_name] = {
                    'game_name': game_name,
                    'game_display_name': config['name'],
                    'is_completed': False,
                    'best_score': 0,
                    'total_attempts': 0,
                    'completion_threshold': config['completion_threshold'],
                    'max_score': config['max_score']
                }
        
        # Get achievements
        user_achievements = []
        for ua in user.achievements:
            achievement_data = {
                'name': ua.achievement.name,
                'description': ua.achievement.description,
                'icon': ua.achievement.icon,
                'points': ua.achievement.points,
                'earned_at': ua.earned_at.isoformat()
            }
            user_achievements.append(achievement_data)
        
        return {
            'user': user.to_dict(),
            'games': progress_data,
            'achievements': user_achievements,
            'stats': {
                'total_games': len(ProgressService.GAME_CONFIGS),
                'completed_games': user.games_completed,
                'total_score': user.total_score,
                'progress_percentage': user.get_progress_percentage(),
                'rank': user.get_rank()
            }
        }
    
    @staticmethod
    def get_leaderboard(limit=50):
        """Get leaderboard data"""
        users = User.query.order_by(User.total_score.desc(), User.games_completed.desc()).limit(limit).all()
        
        leaderboard = []
        for i, user in enumerate(users, 1):
            user_data = user.to_dict()
            user_data['rank'] = i
            
            # Get completion stats
            completed_games = GameProgress.query.filter_by(
                user_id=user.id, 
                is_completed=True
            ).count()
            
            user_data['completed_games'] = completed_games
            user_data['achievement_count'] = len(user.achievements)
            
            leaderboard.append(user_data)
        
        return leaderboard
    
    @staticmethod
    def get_game_statistics():
        """Get overall game statistics"""
        total_users = User.query.count()
        
        stats = {
            'total_users': total_users,
            'games': {}
        }
        
        for game_name, config in ProgressService.GAME_CONFIGS.items():
            completed_count = GameProgress.query.filter_by(
                game_name=game_name, 
                is_completed=True
            ).count()
            
            attempted_count = GameProgress.query.filter_by(game_name=game_name).count()
            
            stats['games'][game_name] = {
                'name': config['name'],
                'attempted': attempted_count,
                'completed': completed_count,
                'completion_rate': (completed_count / attempted_count * 100) if attempted_count > 0 else 0
            }
        
        return stats

def initialize_achievements():
    """Initialize default achievements in database"""
    achievements = [
        {
            'name': 'First Steps',
            'description': 'Complete your first security challenge',
            'icon': '👶',
            'points': 10,
            'condition_type': 'complete_game',
            'condition_value': {'game_name': 'pswd'}
        },
        {
            'name': 'Quiz Master',
            'description': 'Complete the Security Quiz',
            'icon': '🧠',
            'points': 15,
            'condition_type': 'complete_game',
            'condition_value': {'game_name': 'quiz'}
        },
        {
            'name': 'Cipher Breaker',
            'description': 'Master the Vigenère cipher',
            'icon': '🔓',
            'points': 20,
            'condition_type': 'complete_game',
            'condition_value': {'game_name': 'vigenere'}
        },
        {
            'name': 'Hash Detective',
            'description': 'Identify hash algorithms like a pro',
            'icon': '🕵️',
            'points': 20,
            'condition_type': 'complete_game',
            'condition_value': {'game_name': 'hashgame'}
        },
        {
            'name': 'SQL Ninja',
            'description': 'Master SQL injection techniques',
            'icon': '🥷',
            'points': 25,
            'condition_type': 'complete_game',
            'condition_value': {'game_name': 'sqlinjector'}
        },
        {
            'name': 'Security Defender',
            'description': 'Learn to defend against SQL injection',
            'icon': '🛡️',
            'points': 15,
            'condition_type': 'complete_game',
            'condition_value': {'game_name': 'sqldefender'}
        },
        {
            'name': 'Century Club',
            'description': 'Score 100 points or more',
            'icon': '💯',
            'points': 50,
            'condition_type': 'total_score',
            'condition_value': {'min_score': 100}
        },
        {
            'name': 'Elite Hacker',
            'description': 'Complete all security challenges',
            'icon': '👑',
            'points': 100,
            'condition_type': 'complete_all',
            'condition_value': {}
        },
        {
            'name': 'Speed Demon',
            'description': 'Complete password game in under 2 minutes',
            'icon': '⚡',
            'points': 30,
            'condition_type': 'speed_completion',
            'condition_value': {'game_name': 'pswd', 'max_time': 120}
        }
    ]
    
    for ach_data in achievements:
        existing = Achievement.query.filter_by(name=ach_data['name']).first()
        if not existing:
            achievement = Achievement(**ach_data)
            db.session.add(achievement)
    
    db.session.commit()