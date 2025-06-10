import hashlib
from flask import Blueprint, render_template_string, request, session, redirect, url_for
from flask_login import login_required, current_user

pswd_app = Blueprint('pswd_app', __name__)  

# HTML Templates
PASSWORD_INPUT_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Password Strength Test</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #1a1a1a;
            color: #00ff00;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            margin: 0;
            padding: 20px;
        }
        
        .container {
            background-color: #2a2a2a;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 0 20px rgba(0, 255, 0, 0.3);
            max-width: 500px;
            width: 100%;
        }
        
        h1 {
            text-align: center;
            color: #00ff00;
            text-shadow: 0 0 10px rgba(0, 255, 0, 0.5);
            margin-bottom: 30px;
        }
        
        .instruction {
            text-align: center;
            margin-bottom: 30px;
            color: #cccccc;
            line-height: 1.6;
        }
        
        .password-group {
            margin-bottom: 25px;
        }
        
        label {
            display: block;
            margin-bottom: 8px;
            color: #00ff00;
            font-weight: bold;
        }
        
        input[type="password"] {
            width: 100%;
            padding: 12px;
            background-color: #1a1a1a;
            border: 2px solid #00ff00;
            color: #ffffff;
            border-radius: 5px;
            font-size: 16px;
            box-sizing: border-box;
        }
        
        input[type="password"]:focus {
            outline: none;
            border-color: #00ff00;
            box-shadow: 0 0 10px rgba(0, 255, 0, 0.5);
        }
        
        .submit-btn {
            width: 100%;
            padding: 15px;
            background-color: #00ff00;
            color: #000000;
            border: none;
            border-radius: 5px;
            font-size: 18px;
            font-weight: bold;
            cursor: pointer;
            margin-top: 20px;
        }
        
        .submit-btn:hover {
            background-color: #00cc00;
            box-shadow: 0 0 15px rgba(0, 255, 0, 0.7);
        }
        
        .warning {
            color: #ff6347;
            text-align: center;
            margin-top: 15px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔐 Password Strength Test</h1>
        
        <div class="instruction">
            <p>Create 3 different passwords and test their strength.</p>
            <p>A strong password contains: uppercase, lowercase, numbers and special characters.</p>
        </div>
        
        <form method="POST">
            <div class="password-group">
                <label for="password1">Password 1:</label>
                <input type="password" id="password1" name="password1" placeholder="Enter your first password" required>
            </div>
            
            <div class="password-group">
                <label for="password2">Password 2:</label>
                <input type="password" id="password2" name="password2" placeholder="Enter your second password" required>
            </div>
            
            <div class="password-group">
                <label for="password3">Password 3:</label>
                <input type="password" id="password3" name="password3" placeholder="Enter your third password" required>
            </div>
            
            <button type="submit" class="submit-btn">Analyze Passwords</button>
        </form>
    </div>
</body>
</html>
"""

PASSWORD_RESULTS_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Results - Password Strength Test</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #1a1a1a;
            color: #00ff00;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            margin: 0;
            padding: 20px;
        }
        
        .container {
            background-color: #2a2a2a;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 0 20px rgba(0, 255, 0, 0.3);
            max-width: 600px;
            width: 100%;
        }
        
        h1 {
            text-align: center;
            color: #00ff00;
            text-shadow: 0 0 10px rgba(0, 255, 0, 0.5);
            margin-bottom: 30px;
        }
        
        .result-card {
            background-color: #1a1a1a;
            border: 2px solid #00ff00;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 20px;
        }
        
        .password-number {
            font-size: 18px;
            font-weight: bold;
            margin-bottom: 15px;
            color: #00ff00;
        }
        
        .strength-meter {
            height: 30px;
            background-color: #333333;
            border-radius: 15px;
            overflow: hidden;
            margin: 10px 0;
        }
        
        .strength-fill {
            height: 100%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            color: #000000;
        }
        
        .criteria {
            margin-top: 15px;
        }
        
        .criteria-item {
            margin: 5px 0;
            font-size: 14px;
        }
        
        .criteria-item.met {
            color: #00ff00;
        }
        
        .criteria-item.not-met {
            color: #ff6347;
        }
        
        .average-score {
            text-align: center;
            margin-top: 30px;
            font-size: 24px;
            font-weight: bold;
            padding: 20px;
            background-color: #1a1a1a;
            border: 3px solid #00ff00;
            border-radius: 10px;
        }
        
        .back-btn {
            display: block;
            width: 200px;
            margin: 30px auto 0;
            padding: 12px;
            background-color: #00ff00;
            color: #000000;
            text-align: center;
            text-decoration: none;
            border-radius: 5px;
            font-weight: bold;
        }
        
        .back-btn:hover {
            background-color: #00cc00;
            box-shadow: 0 0 15px rgba(0, 255, 0, 0.7);
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 Analysis Results</h1>
        
        {% for result in results %}
        <div class="result-card">
            <div class="password-number">Password {{ result.number }}</div>
            
            <div class="strength-meter">
                <div class="strength-fill" style="width: {{ result.score }}%; background-color: {{ result.color }};">
                    {{ result.score }}%
                </div>
            </div>
            
            <div style="text-align: center; margin: 10px 0; font-size: 20px;">
                {{ result.level }}
            </div>
            
            <div class="criteria">
                <div class="criteria-item {% if result.details.length %}met{% else %}not-met{% endif %}">
                    {% if result.details.length %}✅{% else %}❌{% endif %} Minimum length (8 characters)
                </div>
                <div class="criteria-item {% if result.details.uppercase %}met{% else %}not-met{% endif %}">
                    {% if result.details.uppercase %}✅{% else %}❌{% endif %} Uppercase letters
                </div>
                <div class="criteria-item {% if result.details.lowercase %}met{% else %}not-met{% endif %}">
                    {% if result.details.lowercase %}✅{% else %}❌{% endif %} Lowercase letters
                </div>
                <div class="criteria-item {% if result.details.digits %}met{% else %}not-met{% endif %}">
                    {% if result.details.digits %}✅{% else %}❌{% endif %} Numbers
                </div>
                <div class="criteria-item {% if result.details.special %}met{% else %}not-met{% endif %}">
                    {% if result.details.special %}✅{% else %}❌{% endif %} Special characters
                </div>
            </div>
        </div>
        {% endfor %}
        
        <div class="average-score">
            Average Score: {{ "%.0f"|format(average_score) }}%
        </div>
        
        <a href="/menu/" class="back-btn">Back to Menu</a>
    </div>
</body>
</html>
"""

def evaluate_password_strength(password):
    """Simple password strength evaluation"""
    score = 0
    details = {
        'length': False,
        'uppercase': False,
        'lowercase': False,
        'digits': False,
        'special': False
    }
    
    # Check length
    if len(password) >= 8:
        score += 20
        details['length'] = True
    elif len(password) >= 6:
        score += 10
    
    # Check for uppercase
    if any(c.isupper() for c in password):
        score += 20
        details['uppercase'] = True
    
    # Check for lowercase
    if any(c.islower() for c in password):
        score += 20
        details['lowercase'] = True
    
    # Check for digits
    if any(c.isdigit() for c in password):
        score += 20
        details['digits'] = True
    
    # Check for special characters
    if any(c in "!@#$%^&*()-_+=<>?/;:[]{}|~`" for c in password):
        score += 20
        details['special'] = True
    
    # Determine level
    if score >= 80:
        level = "🔥 Very Strong"
        color = "#00ff00"
    elif score >= 60:
        level = "🔐 Strong"
        color = "#90ee90"
    elif score >= 40:
        level = "😐 Medium"
        color = "#ffa500"
    elif score >= 20:
        level = "⚠️ Weak"
        color = "#ff6347"
    else:
        level = "💀 Very Weak"
        color = "#ff0000"
    
    return {
        'score': score,
        'level': level,
        'color': color,
        'details': details
    }

@pswd_app.route("/", methods=["GET", "POST"])
@login_required
def index():
    if request.method == "POST":
        # Get passwords
        password1 = request.form.get('password1', '')
        password2 = request.form.get('password2', '')
        password3 = request.form.get('password3', '')
        
        # Evaluate each password
        results = []
        for i, pwd in enumerate([password1, password2, password3], 1):
            evaluation = evaluate_password_strength(pwd)
            results.append({
                'number': i,
                'score': evaluation['score'],
                'level': evaluation['level'],
                'color': evaluation['color'],
                'details': evaluation['details']
            })
        
        # Calculate average
        avg_score = sum(r['score'] for r in results) / len(results)
        
        # Store in session
        session['password_results'] = results
        session['average_score'] = avg_score
        
        return redirect('/pswdChecker/results')
    
    return render_template_string(PASSWORD_INPUT_TEMPLATE)

@pswd_app.route("/results")
@login_required
def results():
    results = session.get('password_results')
    avg_score = session.get('average_score')
    
    if not results:
        return redirect('/pswdChecker/')
    
    return render_template_string(PASSWORD_RESULTS_TEMPLATE, 
                                results=results, 
                                average_score=avg_score)