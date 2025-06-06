# CyberSec Academy - Comprehensive Progress Tracking System

A cybersecurity learning platform with comprehensive progress tracking, achievements, and leaderboards similar to CTF platforms like TryHackMe.

## 🚀 Features

### Progress Tracking System
- **Individual Game Progress**: Track scores, completion status, attempts, and time
- **Global Leaderboard**: Real-time ranking system based on total scores
- **Achievement System**: Unlock badges for various accomplishments
- **Personal Dashboard**: Comprehensive view of your learning journey
- **Statistics Page**: Platform-wide analytics and difficulty analysis

### Games Included
1. **Password Security** - Learn secure password practices
2. **Security Quiz** - Test your cybersecurity knowledge  
3. **Vigenère Cipher** - Master classical cryptography
4. **Hash Detective** - Identify different hash algorithms
5. **SQL Injection** - Learn offensive security techniques
6. **SQL Defense** - Understand defensive strategies

### CTF-Style Features
- **Real-time Leaderboards** with ranking system
- **Achievement Badges** for milestones and skills
- **Progress Percentages** and completion tracking
- **Time-based Challenges** with speed bonuses
- **Global Statistics** showing platform usage
- **User Profiles** with comprehensive progress data

## 📁 Project Structure

```
cybersec_academy/
├── app/
│   ├── __init__.py              # Flask app factory
│   ├── models.py                # Database models (User, GameProgress, Achievement)
│   ├── progress_service.py      # Progress tracking service
│   ├── leaderboard.py          # Leaderboard and statistics routes
│   ├── auth.py                 # Authentication (login/signup)
│   ├── menu.py                 # Main menu with progress integration
│   ├── map.py                  # Game navigation
│   ├── pswdChecker.py          # Password security game
│   ├── quiz.py                 # Security knowledge quiz
│   ├── vigenere.py             # Cipher decryption game
│   ├── hashgame.py             # Hash identification game
│   ├── sqlinjector.py          # SQL injection challenges
│   ├── questions_pool.py       # Quiz questions database
│   └── templates/
│       ├── menu.html           # Enhanced main menu
│       ├── leaderboard.html    # Global leaderboard
│       ├── dashboard.html      # Personal progress dashboard
│       ├── statistics.html     # Platform statistics
│       └── [game templates]    # Individual game templates
├── init_database.py            # Database initialization script
├── main.py                     # Application entry point
└── requirements.txt            # Python dependencies
```

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.8+
- pip (Python package installer)

### 1. Clone and Setup
```bash
# Clone the repository
git clone <your-repo-url>
cd cybersec_academy

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Database Setup
```bash
# Initialize database with sample data
python init_database.py
```

This script will:
- Create all necessary database tables
- Set up the achievement system
- Create sample users for testing
- Generate sample progress data
- Award sample achievements

### 3. Run the Application
```bash
python main.py
```

The application will be available at `http://localhost:5000`

### 4. Login Credentials
**Sample Accounts:**
- Username: `alice_cyber` | Password: `password123`
- Username: `bob_hacker` | Password: `password123`
- Username: `charlie_sec` | Password: `password123`
- Username: `diana_expert` | Password: `password123`
- Username: `eve_newbie` | Password: `password123`

Or create your own account through the signup page.

## 📊 Progress Tracking Features

### Achievement System
The platform includes 9 built-in achievements:

1. **First Steps** 👶 - Complete your first security challenge (10 pts)
2. **Quiz Master** 🧠 - Complete the Security Quiz (15 pts)
3. **Cipher Breaker** 🔓 - Master the Vigenère cipher (20 pts)
4. **Hash Detective** 🕵️ - Identify hash algorithms like a pro (20 pts)
5. **SQL Ninja** 🥷 - Master SQL injection techniques (25 pts)
6. **Security Defender** 🛡️ - Learn to defend against SQL injection (15 pts)
7. **Century Club** 💯 - Score 100 points or more (50 pts)
8. **Elite Hacker** 👑 - Complete all security challenges (100 pts)
9. **Speed Demon** ⚡ - Complete password game in under 2 minutes (30 pts)

### Game Completion Criteria
- **Password Security**: Perfect score (3/3) on memory test
- **Security Quiz**: 70% or higher (7/10 questions)
- **Vigenère Cipher**: 5 correct decryptions
- **Hash Detective**: 10 correct hash identifications
- **SQL Injection**: Complete all 3 levels
- **SQL Defense**: Answer correctly

### Leaderboard System
- **Real-time Rankings**: Based on total score and games completed
- **Global Statistics**: Platform-wide completion rates and difficulty analysis
- **Personal Dashboard**: Individual progress tracking with detailed metrics
- **Podium Display**: Top 3 players prominently featured

## 🎮 Game Integration

Each game now automatically:
- ✅ Tracks progress and scores
- ✅ Awards achievements when earned
- ✅ Updates global leaderboard
- ✅ Records completion times
- ✅ Maintains session data
- ✅ Calculates accuracy percentages

## 🔧 Configuration

### Database Configuration
The application uses SQLite by default. To change the database:

```python
# In __init__.py, modify:
app.config['SQLALCHEMY_DATABASE_URI'] = 'your_database_url_here'
```

### Adding New Achievements
Add achievements in `progress_service.py`:

```python
def initialize_achievements():
    achievements = [
        {
            'name': 'Your Achievement',
            'description': 'Achievement description',
            'icon': '🏆',
            'points': 25,
            'condition_type': 'complete_game',  # or 'total_score', 'speed_completion'
            'condition_value': {'game_name': 'your_game'}
        }
        # ... add more achievements
    ]
```

### Adding New Games
1. Create game blueprint in separate file
2. Add to `GAME_CONFIGS` in `progress_service.py`
3. Integrate progress tracking with `ProgressService.update_game_progress()`
4. Register blueprint in `__init__.py`

## 📱 API Endpoints

### Progress API
- `GET /leaderboard/api/leaderboard` - Get leaderboard data
- `GET /leaderboard/api/dashboard` - Get user dashboard data

### Navigation
- `/` - Main menu with progress overview
- `/leaderboard` - Global leaderboard
- `/leaderboard/dashboard` - Personal dashboard
- `/leaderboard/statistics` - Platform statistics
- `/map` - Challenge navigation map

## 🎨 Customization

### Styling
The interface uses a cybersecurity theme with:
- Dark background gradients
- Neon green (#00ff88) accent colors
- Glassmorphism effects
- Smooth animations and transitions
- Responsive design for mobile devices

### Adding Custom Themes
Modify the CSS variables in the template files to change colors:

```css
:root {
    --primary-color: #00ff88;
    --background-gradient: linear-gradient(135deg, #0f0f23 0%, #1a1a3a 100%);
    --card-background: rgba(255, 255, 255, 0.1);
}
```

## 🚀 Production Deployment

### Environment Variables
Create a `.env` file:

```bash
SECRET_KEY=your_super_secret_key_here
DATABASE_URL=your_production_database_url
FLASK_ENV=production
```

### Using Docker
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 5000

CMD ["python", "main.py"]
```

### Using Gunicorn
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 main:app
```

## 🔐 Security Considerations

1. **Change Default Secret Key**: Use a strong, random secret key in production
2. **Database Security**: Use proper database credentials and SSL
3. **Input Validation**: All user inputs are validated and sanitized
4. **Session Management**: Secure session handling with Flask-Login
5. **SQL Injection Prevention**: Uses SQLAlchemy ORM with parameterized queries

## 📈 Monitoring & Analytics

### Built-in Statistics
- Total platform users
- Game completion rates
- User engagement metrics
- Difficulty analysis by completion rates
- Real-time leaderboard updates

### Adding Custom Metrics
Extend `ProgressService.get_game_statistics()` to add more analytics.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add your improvements
4. Test thoroughly
5. Submit a pull request

### Development Guidelines
- Follow PEP 8 style guidelines
- Add docstrings to all functions
- Test new features with sample data
- Update this README for new features

## 📄 License

This project is open source. Feel free to use, modify, and distribute.

## 🆘 Support

If you encounter issues:

1. Check the console for error messages
2. Ensure all dependencies are installed
3. Verify database initialization completed successfully
4. Check file permissions and paths

### Common Issues
- **Database errors**: Run `python init_database.py` again
- **Import errors**: Ensure virtual environment is activated
- **Template not found**: Check file paths and template folder structure
- **Static files not loading**: Verify static folder configuration

## 🎯 Future Enhancements

Potential additions:
- **Team Competitions**: Group challenges and team leaderboards
- **Learning Paths**: Structured progression through topics
- **Badges System**: More detailed achievement categories
- **Social Features**: User profiles and challenge sharing
- **Mobile App**: Native mobile application
- **Integration**: Connect with other cybersecurity platforms
- **Advanced Analytics**: Detailed learning analytics dashboard
- **Certification**: Digital certificates for course completion

---

**Happy Learning! 🚀 Master cybersecurity through gamification!**