import random
import hashlib
from flask import Blueprint, render_template, request

hashgame_bp = Blueprint('hashgame', __name__, template_folder='templates')

WORDS = ["password", "admin", "network", "cyber", "python"]

HASH_ALGOS = {
    "md5": lambda x: hashlib.md5(x.encode()).hexdigest(),
    "sha1": lambda x: hashlib.sha1(x.encode()).hexdigest(),
    "sha256": lambda x: hashlib.sha256(x.encode()).hexdigest(),
}

@hashgame_bp.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        correct_algo = request.form.get("correct_algo")
        user_choice = request.form.get("algo_choice")
        if user_choice == correct_algo:
            result = "✅ Correct!"
        else:
            result = f"❌ Wrong. It was {correct_algo.upper()}."
        
        # Générer un nouveau challenge après réponse
        word, algo, hashed_word = generate_hash_challenge()
        return render_template("hashgame.html", hashed_word=hashed_word,
                               correct_algo=algo, result=result)
    
    # Premier chargement
    word, algo, hashed_word = generate_hash_challenge()
    return render_template("hashgame.html", hashed_word=hashed_word,
                           correct_algo=algo)

def generate_hash_challenge():
    word = random.choice(WORDS)
    algo = random.choice(list(HASH_ALGOS.keys()))
    hashed_word = HASH_ALGOS[algo](word)
    return word, algo, hashed_word
