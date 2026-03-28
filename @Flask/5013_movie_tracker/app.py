import json
import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, jsonify, send_from_directory
import requests
import hashlib
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)

@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATA_FILE = r"C:\@delta\db\5013_movie_tracker\data.json"
ROOT_MOVIES_FOLDER = r"D:\Downloads\@Radarr"
IMAGE_CACHE_DIR = r"C:\@delta\output\radarr_img"

os.makedirs(IMAGE_CACHE_DIR, exist_ok=True)

def get_cached_image(url):
    if not url: return url
    url_hash = hashlib.md5(url.encode()).hexdigest()
    ext = url.split('.')[-1].split('?')[0][:4]
    cached_path = os.path.join(IMAGE_CACHE_DIR, f"{url_hash}.{ext}")
    if os.path.exists(cached_path): return f"/cached_image/{url_hash}.{ext}"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            with open(cached_path, 'wb') as f: f.write(response.content)
            return f"/cached_image/{url_hash}.{ext}"
    except: pass
    return url

def load_data():
    try:
        with open(DATA_FILE, 'r') as f: return json.load(f)
    except: return []

def save_data(data):
    with open(DATA_FILE, 'w') as f: json.dump(data, f, indent=4)

def scan_and_add_missing_movies():
    if not os.path.exists(ROOT_MOVIES_FOLDER): return
    movies = load_data()
    existing_paths = {m.get('directory_path', '').lower() for m in movies if m.get('directory_path')}
    added_count = 0
    try:
        for item in os.listdir(ROOT_MOVIES_FOLDER):
            item_path = os.path.join(ROOT_MOVIES_FOLDER, item)
            if os.path.isdir(item_path) and item_path.lower() not in existing_paths:
                new_movie = {
                    'id': max([m['id'] for m in movies], default=0) + 1,
                    'title': item,
                    'year': '',
                    'cover_image': '',
                    'directory_path': item_path,
                    'rating': None,
                    'seen': False,
                    'added_date': datetime.now().isoformat(),
                    'files': []
                }
                for root, _, files in os.walk(item_path):
                    for filename in files:
                        name, ext = os.path.splitext(filename)
                        if ext.lower() in ['.mp4', '.mkv', '.avi', '.mov', '.webm']:
                            new_movie['files'].append({'title': filename})
                movies.append(new_movie)
                added_count += 1
        if added_count > 0: save_data(movies)
    except: pass

@app.route('/cached_image/<filename>')
def cached_image(filename):
    return send_from_directory(IMAGE_CACHE_DIR, filename)

@app.route('/')
def index():
    sort_by = request.args.get('sort_by', 'title')
    order = request.args.get('order', 'asc')
    query = request.args.get('query')
    movies = load_data()
    if query:
        movies = [m for m in movies if query.lower() in m['title'].lower()]
    for movie in movies:
        movie['cover_image'] = get_cached_image(movie.get('cover_image', ''))
    
    if sort_by == 'title': movies.sort(key=lambda x: x['title'].lower(), reverse=(order == 'desc'))
    elif sort_by == 'year': movies.sort(key=lambda x: int(x['year']) if str(x['year']).isdigit() else 0, reverse=(order == 'desc'))
    elif sort_by == 'rating': movies.sort(key=lambda x: float(x.get('rating', -1)) if x.get('rating') is not None else -1, reverse=(order == 'desc'))
    elif sort_by == 'added': movies.sort(key=lambda x: x['id'], reverse=(order == 'desc'))
    
    return render_template('index.html', movies=movies, sort_by=sort_by, order=order, next_order=('desc' if order == 'asc' else 'asc'), query=query)

@app.route('/add_movie', methods=['POST'])
def add_movie():
    movies = load_data()
    new_movie = {
        'id': max([m['id'] for m in movies], default=0) + 1,
        'title': request.form['title'],
        'year': request.form.get('year', ''),
        'cover_image': request.form.get('cover_image', ''),
        'directory_path': request.form.get('directory_path', ''),
        'rating': request.form.get('rating', None),
        'seen': False,
        'added_date': datetime.now().isoformat(),
        'files': []
    }
    movies.append(new_movie)
    save_data(movies)
    return redirect(url_for('index'))

@app.route('/edit_movie/<int:movie_id>', methods=['GET', 'POST'])
def edit_movie(movie_id):
    movies = load_data()
    movie = next((m for m in movies if m['id'] == movie_id), None)
    if not movie: return jsonify({'success': False}), 404
    if request.method == 'POST':
        movie['title'] = request.form['title']
        movie['year'] = request.form.get('year', '')
        movie['cover_image'] = request.form.get('cover_image', '')
        movie['directory_path'] = request.form.get('directory_path', '')
        movie['rating'] = request.form.get('rating', None)
        movie['radarr_id'] = request.form.get('radarr_id', '')
        save_data(movies)
        return jsonify({'success': True})
    return jsonify(movie)

@app.route('/delete_movie/<int:movie_id>')
def delete_movie(movie_id):
    movies = load_data()
    movies = [m for m in movies if m['id'] != movie_id]
    save_data(movies)
    return jsonify({'success': True})

@app.route('/toggle_seen/<int:movie_id>', methods=['POST'])
def toggle_seen(movie_id):
    movies = load_data()
    movie = next((m for m in movies if m['id'] == movie_id), None)
    if movie:
        movie['seen'] = not movie.get('seen', False)
        save_data(movies)
        return jsonify({'success': True, 'seen': movie['seen']})
    return jsonify({'success': False}), 404

@app.route('/sync_movies')
def sync_movies():
    scan_and_add_missing_movies()
    return jsonify({'success': True})

@app.route('/open_movie_folder/<int:movie_id>')
def open_movie_folder(movie_id):
    import subprocess, sys
    movies = load_data()
    movie = next((m for m in movies if m['id'] == movie_id), None)
    if movie and movie.get('directory_path'):
        try:
            if sys.platform == 'win32': subprocess.run(['explorer', movie['directory_path']], check=False)
            else: subprocess.run(['xdg-open' if sys.platform.startswith('linux') else 'open', movie['directory_path']], check=True)
            return jsonify({'success': True})
        except: pass
    return jsonify({'success': False})

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True, port=5013)
