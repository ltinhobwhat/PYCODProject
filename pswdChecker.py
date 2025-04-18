from flask import Blueprint, render_template, request, session
import hashlib
import time

pswd_app = Blueprint('pswd_app', __name__)  

sites = ["Banque SecurePlus", "Réseau Social ChatterBox", "Forum GeekZone"]

def evaluate_password_strength(password):
    score = 0
    if len(password) >= 8: score += 1
    if any(c.isupper() for c in password): score += 1
    if any(c.isdigit() for c in password): score += 1
    if any(c in "!@#$%^&*()-_+=<>?/;:" for c in password): score += 1
    levels = ["💀 Très faible", "⚠️ Faible", "😐 Moyen", "🔐 Fort", "🔥 Très Fort"]
    return levels[score]

def simulate_crack(password):
    common_passwords = ["123456", "password", "qwerty", "azerty", "admin"]
    time.sleep(1)
    if password in common_passwords:
        return "💀 Mot de passe CRACKÉ en 0.01s !"
    elif len(password) < 6:
        return "😬 Mot de passe trop court, cracké en 1 seconde."
    else:
        return "✅ Mot de passe sécurisé, crackage estimé : plusieurs années."

@pswd_app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        passwords = {}
        evaluations = {}
        crack_results = {}
        for site in sites:
            password = request.form.get(site)
            passwords[site] = hashlib.sha256(password.encode()).hexdigest()
            evaluations[site] = evaluate_password_strength(password)
            crack_results[site] = simulate_crack(password)
        session['passwords'] = passwords
        session['memory_test'] = False
        return render_template("memory_test.html", sites=sites)
    return render_template("index.html", sites=sites)

@pswd_app.route("/memory_test", methods=["POST"])
def memory_test():
    passwords = session.get('passwords', {})
    score = 0
    results = {}
    for site in sites:
        attempt = request.form.get(site)
        if hashlib.sha256(attempt.encode()).hexdigest() == passwords.get(site):
            results[site] = "✅ Mot de passe correct !"
            score += 1
        else:
            results[site] = "❌ Mot de passe incorrect."
    session.pop('passwords', None)
    return render_template("result.html", results=results, score=score, total=len(sites))

    return render_template("result.html", results=results, score=score, total=len(sites))
