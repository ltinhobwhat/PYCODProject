import random
from flask import Blueprint, render_template, request

vigenere_bp = Blueprint('vigenere', __name__, template_folder='templates')

WORDS = ["network", "security", "password", "cipher", "encryption", "attack", "firewall"]
KEYS = ["key", "cipher", "alpha", "secure"]

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

@vigenere_bp.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        user_guess = request.form.get("guess", "").lower()
        original = request.form.get("original")
        key = request.form.get("key")
        encrypted = request.form.get("encrypted")
        if user_guess == original:
            result = "✅ Correct!"
        else:
            result = f"❌ Wrong. The correct word was: <strong>{original}</strong>"

        # Nouvel essai à chaque fois
        new_word = random.choice(WORDS)
        new_key = random.choice(KEYS)
        new_encrypted = vigenere_encrypt(new_word, new_key)

        return render_template("vigenere.html",
                               encrypted=new_encrypted,
                               original=new_word,
                               key=new_key,
                               result=result)

    word = random.choice(WORDS)
    key = random.choice(KEYS)
    encrypted = vigenere_encrypt(word, key)
    return render_template("vigenere.html", encrypted=encrypted, original=word, key=key)
