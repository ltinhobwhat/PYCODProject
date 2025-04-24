import random
from flask import Blueprint, render_template, request, session, redirect, url_for

# Définition du blueprint
vigenere_bp = Blueprint('vigenere', __name__, template_folder='templates')

# Dictionnaires de mots et de clés
WORDS = ["network", "security", "password", "cipher", "encryption", "attack", "firewall"]
KEYS = ["key", "cipher", "alpha", "secure"]

# Fonction de chiffrement Vigenère
def vigenere_encrypt(text, key):
    encrypted = ""
    key = key.lower()
    for i, c in enumerate(text.lower()):
        if c.isalpha():
            shift = ord(key[i % len(key)]) - ord('a')
            encrypted += chr((ord(c) - ord('a') + shift) % 26 + ord('a'))
        else:
            encrypted += c
    return encrypted

# Route principale du mini-jeu
@vigenere_bp.route("/", methods=["GET", "POST"])
def index():
    if "score" not in session:
        session["score"] = 0
        session["total"] = 0

    result = None  # Message affiché après soumission

    if request.method == "POST":
        user_guess = request.form.get("guess", "").lower()
        original = request.form.get("original")
        key = request.form.get("key")
        encrypted = request.form.get("encrypted")
        session["total"] += 1

        if user_guess == original:
            session["score"] += 1
            result = "✅ Correct!"
        else:
            result = f"❌ Wrong. The correct word was: <strong>{original}</strong>"

    # Nouveau mot/chiffrement à chaque chargement
    word = random.choice(WORDS)
    key = random.choice(KEYS)
    encrypted = vigenere_encrypt(word, key)

    return render_template("vigenere.html",
                           encrypted=encrypted,
                           original=word,
                           key=key,
                           result=result,
                           score=session["score"],
                           total=session["total"])

# Route pour réinitialiser le score
@vigenere_bp.route("/reset")
def reset_score():
    session["score"] = 0
    session["total"] = 0
    return redirect(url_for('vigenere.index'))
