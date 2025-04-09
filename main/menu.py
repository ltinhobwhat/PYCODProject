from flask import Flask, render_template, redirect, url_for

app = Flask(__name__)

@app.route('/')
def menu():
    return render_template('menu.html')

@app.route('/start_game/<int:game_number>')
def start_game(game_number):
    return f"Game {game_number} started!"

@app.route('/save_game')
def save_game():
    return "Game saved!"

@app.route('/end_game')
def end_game():
    return "Game ended!"

if __name__ == '__main__':
    app.run(debug=True)
