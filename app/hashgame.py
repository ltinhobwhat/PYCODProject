
# ==========================================
# Updated hashgame.py
import random
import hashlib
from flask import Blueprint, render_template, request, session

hashgame_bp = Blueprint('hashgame', __name__, template_folder='templates')

WORDS = ["password", "admin", "network", "cyber", "python"]
HASH_ALGOS = {
    "md5": lambda x: hashlib.md5(x.encode()).hexdigest(),
    "sha1": lambda x: hashlib.sha1(x.encode()).hexdigest(),
    "sha256": lambda x: hashlib.sha256(x.encode()).hexdigest(),
}

@hashgame_bp.route("/", methods=["GET", "POST"])
def index():
    # Load previous progress
    
    # Initialize session data
    if "hash_score" not in session:
        session["hash_score"] = 0
        session["hash_total"] = 0

    if request.method == "POST":
        correct_algo = request.form.get("correct_algo")
        user_choice = request.form.get("algo_choice")
        session["hash_total"] += 1
        
        if user_choice == correct_algo:
            session["hash_score"] += 1
            result = "✅ Correct!"
        else:
            result = f"❌ Wrong. It was {correct_algo.upper()}."
        
        # Save progress after each attempt
        current_percentage = (session["hash_score"] / session["hash_total"]) * 100
        completed = session["hash_score"] >= 10  # Complete after 10 correct answers
        

        
        # Generate new challenge after answer
        word, algo, hashed_word = generate_hash_challenge()
        return render_template("hashgame.html", 
                             hashed_word=hashed_word,
                             correct_algo=algo, 
                             result=result,
                             score=session["hash_score"],
                             total=session["hash_total"],
                             )
    
    # First load
    word, algo, hashed_word = generate_hash_challenge()
    return render_template("hashgame.html", 
                         hashed_word=hashed_word,
                         correct_algo=algo,
                         score=session.get("hash_score", 0),
                         total=session.get("hash_total", 0),
                         )

def generate_hash_challenge():
    word = random.choice(WORDS)
    algo = random.choice(list(HASH_ALGOS.keys()))
    hashed_word = HASH_ALGOS[algo](word)
    return word, algo, hashed_word