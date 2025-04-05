from flask import Flask, render_template, request, redirect
import sqlite3
import os

app = Flask(__name__)
DB_PATH = r"C:\msBackups\gameARR\game.db"

def recreate_table():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # Create a new table with the correct schema
    c.execute('''CREATE TABLE IF NOT EXISTS games_new (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT,
                        year INTEGER,
                        image TEXT,
                        rating REAL,
                        progression INTEGER DEFAULT 0
                    )''')
    # Copy data from the old table to the new one
    c.execute('''INSERT INTO games_new (id, name, year, image, rating, progression)
                    SELECT id, name, year, image, rating, progression FROM games''')
    # Drop the old table
    c.execute('DROP TABLE games')
    # Rename the new table to the original name
    c.execute('ALTER TABLE games_new RENAME TO games')
    conn.commit()
    conn.close()
recreate_table()

# Ensure database exists and creates the necessary table
def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS games (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT,
                        year TEXT,
                        image TEXT,
                        rating INTEGER,
                        progression INTEGER DEFAULT 0)''')
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
    c.execute(f"SELECT id, name, year, image, CAST(rating AS INTEGER) AS rating, progression FROM games ORDER BY {sort_by} COLLATE NOCASE {order_clause}")
    games = c.fetchall()

    conn.close()
    return render_template('index.html', games=games, sort_by=sort_by, order=order, next_order=next_order)

@app.route('/add', methods=['POST'])
def add_game():
    name = request.form['name']
    year = request.form['year']
    image = request.form['image']
    rating = request.form['rating']
    progression = int(request.form['progression'])  # Store progression as integer
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO games (name, year, image, rating, progression) VALUES (?, ?, ?, ?, ?)", (name, year, image, rating, progression))
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
        progression = int(request.form['progression'])  # Update progression as integer
        c.execute("UPDATE games SET name = ?, year = ?, image = ?, rating = ?, progression = ? WHERE id = ?",
                  (name, year, image, rating, progression, game_id))
        conn.commit()
        conn.close()
        return redirect('/')
    else:
        c.execute("SELECT name, year, image, rating, progression FROM games WHERE id = ?", (game_id,))
        game = c.fetchone()

        conn.close()
        return render_template('edit_game.html', game=game, game_id=game_id)

@app.route('/delete/<int:game_id>')
def delete_game(game_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM games WHERE id = ?", (game_id,))
    conn.commit()
    conn.close()
    return redirect('/')

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5005, debug=True)