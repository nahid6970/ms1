from flask import Flask, render_template, request, redirect
import sqlite3
import os

app = Flask(__name__)
DB_PATH = r"C:\msBackups\gameARR\game.db"

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
                                    progression INTEGER DEFAULT 0,
                                    url TEXT)''')
    conn.commit()
    conn.close()
init_db() # Call init_db() first

def recreate_table():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    try:
        # Check if the old 'games' table exists
        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='games'")
        old_table_exists = c.fetchone() is not None

        if old_table_exists:
            # Create a new table with the correct schema
            c.execute('''CREATE TABLE IF NOT EXISTS games_new (
                                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                                            name TEXT,
                                            year INTEGER,
                                            image TEXT,
                                            rating REAL,
                                            progression INTEGER DEFAULT 0,
                                            url TEXT
                                        )''')
            # Copy data from the old table to the new one, handling the missing 'url' column
            c.execute('''INSERT INTO games_new (id, name, year, image, rating, progression)
                                        SELECT id, name, year, image, rating, progression FROM games''')
            # Drop the old table
            c.execute('DROP TABLE games')
            # Rename the new table to the original name
            c.execute('ALTER TABLE games_new RENAME TO games')
            conn.commit()
        else:
            # If the old table doesn't exist, the new table with the 'url' column is already created by init_db
            pass # Or you could log a message

    except sqlite3.OperationalError as e:
        print(f"An error occurred during table recreation: {e}")
        conn.rollback()
    finally:
        conn.close()

recreate_table() # Call recreate_table() after init_db()

# ... rest of your Flask routes and code ...

@app.route('/')
def index():
    sort_by = request.args.get('sort_by', 'name')
    order = request.args.get('order', 'asc')
    query = request.args.get('query') # Get the search query
    # Toggle order for next click
    next_order = 'desc' if order == 'asc' else 'asc'
    if sort_by not in ['name', 'year', 'rating']:
        sort_by = 'name'
    order_clause = 'ASC' if order == 'asc' else 'DESC'
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    sql_query = f"SELECT id, name, year, image, CAST(rating AS INTEGER) AS rating, progression, url FROM games"
    if query:
        sql_query += f" WHERE name LIKE ?"
        c.execute(sql_query + f" ORDER BY {sort_by} COLLATE NOCASE {order_clause}", ('%' + query + '%',))
        games = c.fetchall()
    else:
        c.execute(sql_query + f" ORDER BY {sort_by} COLLATE NOCASE {order_clause}")
        games = c.fetchall()

    conn.close()
    return render_template('index.html', games=games, sort_by=sort_by, order=order, next_order=next_order, query=query) # Pass query to the template

@app.route('/add', methods=['POST'])
def add_game():
    name = request.form['name']
    year = request.form['year']
    image = request.form['image']
    url = request.form['url']
    rating_str = request.form.get('rating') # Use .get() for optional fields
    progression_str = request.form.get('progression', '').strip() # Get value or empty string, strip whitespace
    # Handle optional rating
    rating = None # Default to None if not provided or invalid
    if rating_str and rating_str.isdigit(): # Check if it exists and contains only digits
        try:
            rating = int(rating_str)
        except ValueError:
            pass # Keep rating as None if conversion fails
    # Handle progression, defaulting to 0
    if progression_str.isdigit(): # Check if it contains only digits (handles empty string correctly)
        try:
            progression = int(progression_str)
        except ValueError:
            progression = 0 # Should not happen if isdigit() is true, but safe fallback
    else:
        progression = 0 # Default to 0 if not provided, empty, or not digits

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id FROM games WHERE name = ?", (name,))
    existing_game = c.fetchone()

    if existing_game:
        conn.close()
        # Fetch current games again to display the list with the error
        c = sqlite3.connect(DB_PATH).cursor()
        c.execute(f"SELECT id, name, year, image, CAST(rating AS INTEGER) AS rating, progression, url FROM games ORDER BY name COLLATE NOCASE ASC") # Example default sort
        games = c.fetchall()
        c.connection.close()
        return render_template('index.html', games=games, sort_by='name', order='asc', next_order='desc', error="A game with this name already exists.")
    else:
        c.execute("INSERT INTO games (name, year, image, rating, progression, url) VALUES (?, ?, ?, ?, ?, ?)",
                    (name, year, image, rating, progression, url))
        conn.commit()
        conn.close()
        return redirect('/')

@app.route('/search')
def search_games():
    query = request.args.get('query')
    if query:
        return redirect(f'/?query={query}') # Redirect to the index page with the query
    else:
        return redirect('/')

@app.route('/edit/<int:game_id>', methods=['GET', 'POST'])
def edit_game(game_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    if request.method == 'POST':
        name = request.form['name']
        year = request.form['year']
        image = request.form['image']
        url = request.form['url']
        rating_str = request.form.get('rating')
        rating = None
        if rating_str and rating_str.isdigit():
            try:
                rating = int(rating_str)
            except ValueError:
                pass

        progression_str = request.form.get('progression', '').strip()
        if progression_str.isdigit():
            try:
                progression = int(progression_str)
            except ValueError:
                progression = 0
        else:
            progression = 0

        # Check if a game with the new name already exists (excluding the current game being edited)
        c.execute("SELECT id FROM games WHERE name = ? AND id != ?", (name, game_id))
        existing_game = c.fetchone()

        if existing_game:
            conn.close()
            c.execute("SELECT name, year, image, rating, progression, url FROM games WHERE id = ?", (game_id,))
            game_data = c.fetchone()
            return render_template('edit_game.html', game=game_data, game_id=game_id, error="A game with this name already exists.")
        else:
            c.execute("UPDATE games SET name = ?, year = ?, image = ?, rating = ?, progression = ?, url = ? WHERE id = ?",
                        (name, year, image, rating, progression, url, game_id))
            conn.commit()
            conn.close()
            return redirect('/')
    else:
        c.execute("SELECT name, year, image, rating, progression, url FROM games WHERE id = ?", (game_id,))
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