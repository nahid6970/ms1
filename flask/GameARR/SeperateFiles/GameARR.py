from flask import Flask, render_template, request, redirect
import sqlite3
import os

app = Flask(__name__)
DB_PATH = r"C:\msBackups\gameARR\game.db"

# Ensure database exists and creates the necessary table
def recreate_table():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS games_new (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                name TEXT UNIQUE,
                                year INTEGER,
                                image TEXT,
                                rating REAL,
                                progression TEXT,
                                url TEXT,
                                collection TEXT

                            )''')
    c.execute('''INSERT INTO games_new (id, name, year, image, rating, progression, url, collection)
                            SELECT id, name, year, image, rating,
                                   CASE progression
                                       WHEN 0 THEN 'Unplayed'
                                       WHEN 50 THEN 'Unfinished'
                                       WHEN 100 THEN 'Complete'
                                       ELSE CAST(progression AS TEXT)
                                   END, url FROM games''') # Convert existing progression
    c.execute('DROP TABLE games')
    c.execute('ALTER TABLE games_new RENAME TO games')
    conn.commit()
    conn.close()

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS games (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                name TEXT UNIQUE,
                                year TEXT,
                                image TEXT,
                                rating INTEGER,
                                progression TEXT DEFAULT 'Unplayed',
                                url TEXT,
                                collection TEXT DEFAULT ''
                                )''')
    conn.commit()
    conn.close()

init_db()
try:
    recreate_table()
except sqlite3.OperationalError:
    # Handle case where the table might not have existed initially
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    try:
        c.execute("ALTER TABLE games ADD COLUMN progression TEXT DEFAULT 'Unplayed'")
        conn.commit()
    except sqlite3.OperationalError:
        pass # Column might already exist
    finally:
        conn.close()


@app.route('/')
def index():
    sort_by = request.args.get('sort_by', 'name')
    order = request.args.get('order', 'asc')
    query = request.args.get('query') # Get the search query
    collection_filter = request.args.get('collection')
    # Toggle order for next click
    next_order = 'desc' if order == 'asc' else 'asc'
    if sort_by not in ['name', 'year', 'rating']:
        sort_by = 'name'
    order_clause = 'ASC' if order == 'asc' else 'DESC'
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    sql_query = f"SELECT id, name, year, image, CAST(rating AS INTEGER) AS rating, progression, url, collection FROM games"
    conditions = []
    params = []
    if query:
        conditions.append("name LIKE ?")
        params.append('%' + query + '%')
    if collection_filter:
        conditions.append("collection = ?")
        params.append(collection_filter)

    if conditions:
        sql_query += " WHERE " + " AND ".join(conditions)

    sql_query += f" ORDER BY {sort_by} COLLATE NOCASE {order_clause}"
    c.execute(sql_query, tuple(params))
    games = c.fetchall()
    c.execute("SELECT COUNT(*) FROM games")
    total_games = c.fetchone()[0]
    c.execute("SELECT DISTINCT collection FROM games WHERE collection != '' ORDER BY collection COLLATE NOCASE")
    collections = [row[0] for row in c.fetchall()]
    conn.close()
    return render_template('index.html', games=games, sort_by=sort_by, order=order, next_order=next_order, query=query, total_games=total_games, collections=collections, current_collection_filter=collection_filter)

@app.route('/add', methods=['POST'])
def add_game():
    name = request.form['name']
    year = request.form['year']
    image = request.form['image']
    url = request.form['url'] or 'http://192.168.0.101:5005'  # Default URL if empty
    rating_str = request.form.get('rating')
    progression = request.form.get('progression')
    collection = request.form.get('collection', '').strip()

    rating = None
    if rating_str and rating_str.isdigit():
        try:
            rating = int(rating_str)
        except ValueError:
            pass

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id FROM games WHERE name = ?", (name,))
    existing_game = c.fetchone()

    if existing_game:
        conn.close()
        c = sqlite3.connect(DB_PATH).cursor()
        c.execute(f"SELECT id, name, year, image, CAST(rating AS INTEGER) AS rating, progression, url, collection FROM games ORDER BY name COLLATE NOCASE ASC")
        games = c.fetchall()
        c.connection.close()
        return render_template('index.html', games=games, sort_by='name', order='asc', next_order='desc', error="A game with this name already exists.")
    else:
        c.execute("INSERT INTO games (name, year, image, rating, progression, url, collection) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (name, year, image, rating, progression, url, collection))
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

        progression = request.form.get('progression') # Get progression as string
        collection = request.form.get('collection', '').strip()

        # Check if a game with the new name already exists (excluding the current game being edited)
        c.execute("SELECT id FROM games WHERE name = ? AND id != ?", (name, game_id))
        existing_game = c.fetchone()

        if existing_game:
            conn.close()
            c.execute("SELECT name, year, image, rating, progression, url, collection FROM games WHERE id = ?", (game_id,))
            game_data = c.fetchone()
            return render_template('edit_game.html', game=game_data, game_id=game_id, error="A game with this name already exists.")
        else:
            c.execute("UPDATE games SET name = ?, year = ?, image = ?, rating = ?, progression = ?, url = ?, collection = ? WHERE id = ?",
                      (name, year, image, rating, progression, url, collection, game_id))
            conn.commit()
            conn.close()
            return redirect('/')
    else:
        c.execute("SELECT name, year, image, rating, progression, url, collection FROM games WHERE id = ?", (game_id,))
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