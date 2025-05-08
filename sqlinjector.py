from flask import Blueprint, render_template, request, session

sqlinjector_bp = Blueprint('sqlinjector', __name__, template_folder='templates')

LEVELS = {
    1: "Bypass login with ' OR '1'='1",
    2: "Bypass login using comment '--",
    3: "Bypass login injecting in the password only"
}

@sqlinjector_bp.route("/", methods=["GET", "POST"])
def index():
    if "level" not in session:
        session["level"] = 1

    success = False
    query = None
    level = session["level"]
    hint = LEVELS[level]

    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}';"

        if level == 1 and ("' OR '1'='1" in username or "' OR '1'='1" in password):
            success = True
        elif level == 2 and ("--" in username or "--" in password):
            success = True
        elif level == 3 and "' OR '1'='1" in password:
            success = True

        if success:
            session["level"] += 1
            if session["level"] > len(LEVELS):
                session["level"] = 1  # reset after last level
            result = "✅ Injection successful! Moving to next level."
        else:
            result = "❌ Injection failed. Try again!"

        return render_template("sqlinjector.html", query=query, success=success, result=result, level=level, hint=hint)

    return render_template("sqlinjector.html", query=query, success=success, level=level, hint=hint)
@sqlinjector_bp.route("/reset")
def reset_levels():
    session["level"] = 1
    return redirect(url_for('sqlinjector.index'))
@sqlinjector_bp.route("/defender", methods=["GET", "POST"])
def defender():
    options = [
        "Use parameterized queries (prepared statements)",
        "Escape user input manually",
        "Trust user input, it’s harmless"
    ]
    correct = "Use parameterized queries (prepared statements)"
    result = None

    if request.method == "POST":
        choice = request.form.get("defense_choice")
        if choice == correct:
            result = "✅ Correct! Always use prepared statements."
        else:
            result = "❌ Wrong. The safest way is to use parameterized queries."

    return render_template("defender.html", options=options, result=result)
