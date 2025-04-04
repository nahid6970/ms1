from flask import Flask, render_template_string, request, redirect
import sqlite3
import os

app = Flask(__name__)
DB_PATH = r"C:\msBackups\gameARR\game.db"

# Ensure database exists and add 'rating' column if it doesn't exist
def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Check if the 'rating' column exists, and if not, add it
    try:
        c.execute('''SELECT rating FROM games LIMIT 1''')
    except sqlite3.OperationalError:
        c.execute('''ALTER TABLE games ADD COLUMN rating INTEGER''')
    
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def index():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, name, year, image, rating FROM games")
    games = c.fetchall()
    conn.close()
    return render_template_string(HTML_TEMPLATE, games=games)

@app.route('/add', methods=['POST'])
def add_game():
    name = request.form['name']
    year = request.form['year']
    image = request.form['image']
    rating = int(request.form['rating'])  # Ensure rating is an integer
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO games (name, year, image, rating) VALUES (?, ?, ?, ?)", (name, year, image, rating))
    conn.commit()
    conn.close()
    
    return redirect('/')

@app.route('/edit/<int:game_id>', methods=['GET', 'POST'])
def edit_game(game_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    if request.method == 'POST':
        name = request.form['name']
        year = request.form['year']
        image = request.form['image']
        rating = int(request.form['rating'])
        c.execute("UPDATE games SET name = ?, year = ?, image = ?, rating = ? WHERE id = ?", (name, year, image, rating, game_id))
        conn.commit()
        conn.close()
        return redirect('/')
    else:
        c.execute("SELECT name, year, image, rating FROM games WHERE id = ?", (game_id,))
        game = c.fetchone()
        conn.close()
        return render_template_string(EDIT_TEMPLATE, game=game, game_id=game_id)

@app.route('/delete/<int:game_id>', methods=['GET'])
def delete_game(game_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM games WHERE id = ?", (game_id,))
    conn.commit()
    conn.close()
    return redirect('/')

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GameARR</title>
    <style>
        body { font-family: Arial, sans-serif; background: #1c1c1c; color: white; text-align: center; }
        .container { max-width: 1200px; margin: auto; padding: 20px; }
        h1 { font-size: 3em; margin-bottom: 20px; }

        /* Game List Styling */
        .game-list { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 20px; padding: 20px; }
        .game { background: #2c2c2c; padding: 15px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3); transition: transform 0.3s ease; }
        .game:hover { transform: scale(1.05); }
        .game img { width: 100%; height: auto; border-radius: 10px; }
        .game h2 { font-size: 1.5em; color: #e0e0e0; margin-top: 10px; }
        .game p { font-size: 1.2em; color: gold; }

        /* Form Styling */
        .form-container { display: none; margin: 20px auto; padding: 20px; background: #333; border-radius: 10px; width: 400px; }
        .form-container input { margin: 10px 0; padding: 10px; width: 100%; background: #444; border: 1px solid #666; border-radius: 5px; color: #ddd; }
        .form-container input:focus { border-color: #28a745; outline: none; }
        .form-container button { background: #28a745; color: white; padding: 10px 20px; border: none; cursor: pointer; border-radius: 5px; margin-top: 10px; width: 100%; }
        .form-container button:hover { background: #218838; }

        /* Button Styling */
        .button { padding: 10px 15px; margin: 5px; border-radius: 5px; text-decoration: none; font-weight: bold; }
        .edit-button { background: #007bff; color: white; }
        .edit-button:hover { background: #0056b3; }
        .delete-button { background: #dc3545; color: white; }
        .delete-button:hover { background: #c82333; }

        /* General Layout Styling */
        .toggle-form-btn { background: #007bff; color: white; padding: 10px 20px; border-radius: 5px; font-size: 1.2em; cursor: pointer; margin-bottom: 30px; }
        .toggle-form-btn:hover { background: #0056b3; }
    </style>
        <script>
            function toggleForm() {
                var form = document.getElementById("gameForm");
                if (form.style.display === "none" || form.style.display === "") {
                    form.style.display = "block";
                } else {
                    form.style.display = "none";
                }
            }
        </script>
</head>
<body>
    <div class="container">
        <h1>GameARR</h1>
        <button class="toggle-form-btn" onclick="toggleForm()">Add Game</button>
        <div class="form-container" id="gameForm">
            <form action="/add" method="post">
                <input type="text" name="name" placeholder="Game Name" required><br>
                <input type="number" name="year" placeholder="Year" required><br>
                <input type="text" name="image" placeholder="Image URL" required><br>
                <input type="number" name="rating" placeholder="Rating (1-5)" min="1" max="5" required><br>
                <button type="submit">Save</button>
            </form>
        </div>
        <div class="game-list">
            {% for game in games %}
            <div class="game">
                <img src="{{ game[3] }}" alt="{{ game[1] }}">
                <h2>{{ game[1] }} ({{ game[2] }})</h2>
                <p class="rating">{{ game[4] }}/5⭐</p>
                <a href="/edit/{{ game[0] }}" class="button edit-button">Edit</a>
                <a href="/delete/{{ game[0] }}" class="button delete-button">Delete</a>
            </div>
            {% endfor %}
        </div>
    </div>
</body>
</html>
"""

EDIT_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Edit Game</title>
    <style>
        body { font-family: Arial, sans-serif; background: #1c1c1c; color: white; text-align: center; }
        .container { max-width: 800px; margin: auto; padding: 20px; }
        h1 { font-size: 2.5em; margin-bottom: 20px; }
        .form-container { background: #333; padding: 20px; border-radius: 10px; width: 400px; margin: auto; }
        .form-container input { margin: 10px 0; padding: 10px; width: 100%; background: #444; border: 1px solid #666; border-radius: 5px; color: #ddd; }
        .form-container input:focus { border-color: #28a745; outline: none; }
        .form-container button { background: #28a745; color: white; padding: 10px 20px; border: none; cursor: pointer; border-radius: 5px; margin-top: 10px; width: 100%; }
        .form-container button:hover { background: #218838; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Edit Game</h1>
        <form action="/edit/{{ game_id }}" method="post">
            <input type="text" name="name" value="{{ game[0] }}" required><br>
            <input type="number" name="year" value="{{ game[1] }}" required><br>
            <input type="text" name="image" value="{{ game[2] }}" required><br>
            <input type="number" name="rating" value="{{ game[3] }}" min="1" max="5" required><br>
            <button type="submit">Save</button>
        </form>
    </div>
</body>
</html>
"""



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5005, debug=True)
