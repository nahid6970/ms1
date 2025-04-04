from flask import Flask, render_template_string, request, redirect
import sqlite3
import os

app = Flask(__name__)
DB_PATH = r"C:\msBackups\gameARR\game.db"

# Ensure database exists
def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS games (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    year TEXT,  -- Changed to TEXT to allow full date format
                    image TEXT,
                    rating INTEGER)''')
    conn.commit()
    conn.close()



init_db()

@app.route('/')
def index():
    sort_by = request.args.get('sort_by', 'name')
    order = request.args.get('order', 'asc')

    # Toggle order for next click
    next_order = 'desc' if order == 'asc' else 'asc'

    if sort_by not in ['name', 'year', 'rating']:
        sort_by = 'name'

    order_clause = 'ASC' if order == 'asc' else 'DESC'

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(f"SELECT id, name, year, image, rating FROM games ORDER BY {sort_by} COLLATE NOCASE {order_clause}")
    games = c.fetchall()
    conn.close()

    return render_template_string(HTML_TEMPLATE, games=games, sort_by=sort_by, order=order, next_order=next_order)


@app.route('/add', methods=['POST'])
def add_game():
    name = request.form['name']
    year = request.form['year']
    image = request.form['image']
    rating = request.form['rating']

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
        rating = request.form['rating']
        c.execute("UPDATE games SET name = ?, year = ?, image = ?, rating = ? WHERE id = ?", 
                  (name, year, image, rating, game_id))
        conn.commit()
        conn.close()
        return redirect('/')
    else:
        c.execute("SELECT name, year, image, rating FROM games WHERE id = ?", (game_id,))
        game = c.fetchone()
        conn.close()
        return render_template_string(EDIT_TEMPLATE, game=game, game_id=game_id)

@app.route('/delete/<int:game_id>')
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
        # .container { max-width: 900px; margin: auto; padding: 20px; }
        .container { margin: auto; padding: 20px; }
        .game-list { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 20px; padding: 20px; }
        .game { background: #2c2c2c; padding: 15px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3); transition: transform 0.3s ease; }
        .game:hover { transform: scale(1.05); }
        .game img { width: 100%; height: auto; border-radius: 10px; }
        .game h2 { font-size: 1.5em; color: #e0e0e0; margin-top: 10px; }
        .game p { font-size: 1.2em; color: gold; }
        .form-container { display: none; background: #333; padding: 10px; border-radius: 10px; margin: 20px auto; }
        input { margin: 5px; padding: 8px; width: 90%; }
        .btn { padding: 8px 12px; border: none; cursor: pointer; border-radius: 5px; }
        .btn-add { background: #28a745; color: white; }
        .btn-edit { background: #007bff; color: white; }
        .btn-delete { background: #dc3545; color: white; }
<style>
    .top-controls { margin-bottom: 20px; }
    .top-controls button, .top-controls .sort-btn {
        background: #28a745;
        color: white;
        padding: 10px 14px;
        margin: 0 5px;
        border: none;
        border-radius: 4px;
        text-decoration: none;
        font-weight: bold;
        transition: transform 0.2s, background 0.2s;
    }

    .top-controls .sort-btn:hover,
    .top-controls button:hover {
        transform: scale(1.05);
        background: #218838;
    }
</style>
    </style>
    <script>
        function toggleForm() {
            var form = document.getElementById("gameForm");
            form.style.display = (form.style.display === "none" || form.style.display === "") ? "block" : "none";
        }
    </script>
</head>
<body>
    <div class="container">
        <h1>GameARR</h1>
<div class="top-controls">
    <button onclick="toggleForm()">Add Game</button>
    <a href="/?sort_by=name&order={{ next_order }}" class="sort-btn">Sort by Name</a>
    <a href="/?sort_by=year&order={{ next_order }}" class="sort-btn">Sort by Year</a>
    <a href="/?sort_by=rating&order={{ next_order }}" class="sort-btn">Sort by Rating</a>
</div>

        <div class="form-container" id="gameForm">
            <form action="/add" method="post">
                <input type="text" name="name" placeholder="Game Name" required><br>
                <input type="number" name="year" placeholder="Year" required><br>
                <input type="text" name="image" placeholder="Image URL" required><br>
                <input type="number" name="rating" placeholder="Rating (1-5)" required min="1" max="5"><br>
                <button type="submit" class="btn btn-add">Save</button>
            </form>
        </div>
        <div class="game-list">
        {% for game in games %}
<div class="game">
    <img src="{{ game[3] }}" alt="{{ game[1] }}">
    <h2>{{ game[1] }}</h2>
    <p style="color: #bbb; font-style: italic;">{{ game[2] }}</p>  <!-- Year on a new line -->
    <p>{{ game[4] }}/5 ⭐</p>
                <a href="/edit/{{ game[0] }}" class="btn btn-edit">Edit</a>
                <a href="/delete/{{ game[0] }}" class="btn btn-delete">Delete</a>
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
        .form-container { background: #333; padding: 10px; border-radius: 5px; }
        input { margin: 5px; padding: 8px; width: 90%; }
        button { background: #28a745; color: white; padding: 10px; border: none; cursor: pointer; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Edit Game</h1>
        <form action="/edit/{{ game_id }}" method="post">
            <input type="text" name="name" value="{{ game[0] }}" required><br>
            <input type="number" name="year" value="{{ game[1] }}" required><br>
            <input type="text" name="image" value="{{ game[2] }}" required><br>
            <input type="number" name="rating" value="{{ game[3] }}" required min="1" max="5"><br>
            <button type="submit">Save</button>
        </form>
    </div>
</body>
</html>
"""

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5005, debug=True)
