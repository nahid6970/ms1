import json
import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, jsonify
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)

@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATA_FILE = os.path.join(BASE_DIR, 'data.json')
ROOT_MOVIES_FOLDER = r"D:\Downloads\@Radarr" 

def load_data():
    try:
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)

def scan_for_missing_movies():
    """Scan the root folder for TV show directories that aren't in the JSON file"""
    if not os.path.exists(ROOT_MOVIES_FOLDER):
        return []
    
    movies = load_data()
    existing_paths = {movie.get('directory_path', '').lower() for movie in movies if movie.get('directory_path')}
    missing_movies = []
    
    try:
        for item in os.listdir(ROOT_MOVIES_FOLDER):
            item_path = os.path.join(ROOT_MOVIES_FOLDER, item)
            if os.path.isdir(item_path):
                # Check if this directory path is already in our movies
                if item_path.lower() not in existing_paths:
                    # Check if the directory contains video files
                    has_movie_files = False
                    for root, _, files in os.walk(item_path):
                        for filename in files:
                            _, ext = os.path.splitext(filename)
                            if ext.lower() in ['.mp4', '.mkv', '.avi', '.mov', '.webm']:
                                has_movie_files = True
                                break
                        if has_movie_files:
                            break
                    
                    if has_movie_files:
                        missing_movies.append({
                            'movie_name': item,
                            'full_path': item_path
                        })
    except Exception as e:
        print(f"Error scanning root folder: {e}")
    
    return missing_movies

def scan_and_update_movie_files():
    print("Scanning for new movie files...")
    movies = load_data()
    updated_movies = False
    for movie in movies:
        if 'directory_path' in movie and movie['directory_path']:
            dir_path = movie['directory_path']
            if os.path.isdir(dir_path):
                existing_file_titles = {f['title'] for f in movie['files']}
                files_added = False
                for root, _, files in os.walk(dir_path):
                    for filename in files:
                        name, ext = os.path.splitext(filename)
                        if ext.lower() in ['.mp4', '.mkv', '.avi', '.mov', '.webm']:
                            if name not in existing_file_titles:
                                new_file = {
                                    'id': len(movie['files']) + 1,
                                    'title': name,
                                    'added_date': datetime.now().isoformat()
                                }
                                movie['files'].insert(0, new_file)
                                existing_file_titles.add(name)
                                updated_movies = True
                                files_added = True
            else:
                print(f"Directory not found for {movie['title']}: {dir_path}")
    if updated_movies:
        save_data(movies)
        print("New movie files found and updated.")
    else:
        print("No new movie files found.")

scheduler = BackgroundScheduler()
scheduler.add_job(func=scan_and_update_movie_files, trigger="interval", hours=1)
scheduler.start()

@app.route('/')
def index():
    sort_by = request.args.get('sort_by', 'title')
    order = request.args.get('order', 'asc')
    query = request.args.get('query')

    movies = load_data()

    # Filter movies based on query
    if query:
        movies = [movie for movie in movies if query.lower() in movie['title'].lower()]

    

    # Sort movies
    if sort_by == 'title':
        movies.sort(key=lambda x: x['title'].lower(), reverse=(order == 'desc'))
    elif sort_by == 'year':
        movies.sort(key=lambda x: int(x['year']) if x['year'].isdigit() else 0, reverse=(order == 'desc'))
    elif sort_by == 'rating':
        movies.sort(key=lambda x: float(x.get('rating', -1)) if x.get('rating') is not None else -1, reverse=(order == 'desc'))
    elif sort_by == 'added': # Sort by ID for 'added' order
        movies.sort(key=lambda x: x['id'], reverse=(order == 'desc'))

    next_order = 'desc' if order == 'asc' else 'asc'

    return render_template('index.html', movies=movies, sort_by=sort_by, order=order, next_order=next_order, query=query)

@app.route('/movie/<int:movie_id>')
def movie(movie_id):
    sort_files = request.args.get('sort_files', 'default')
    order = request.args.get('order', 'asc')
    
    movies = load_data()
    movie = next((m for m in movies if m['id'] == movie_id), None)
    if movie:
        
        next_order = 'desc' if order == 'asc' else 'asc'
        return render_template('show.html', movie=movie, sort_files=sort_files, order=order, next_order=next_order)
    return 'Movie not found', 404

@app.route('/add_movie', methods=['GET', 'POST'])
def add_movie():
    if request.method == 'POST':
        movies = load_data()
        new_movie = {
            'id': len(movies) + 1,
            'title': request.form['title'],
            'year': request.form.get('year', ''),
            'cover_image': request.form.get('cover_image', ''),
            'directory_path': request.form.get('directory_path', ''),
            'rating': request.form.get('rating', None),
            'files': []
        }
        movies.append(new_movie)
        save_data(movies)
        return redirect(url_for('index'))
    return render_template('add_movie.html')

@app.route('/edit_movie/<int:movie_id>', methods=['GET', 'POST'])
def edit_movie(movie_id):
    movies = load_data()
    movie = next((m for m in movies if m['id'] == movie_id), None)
    if not movie:
        return 'Movie not found', 404
    if request.method == 'POST':
        movie['title'] = request.form['title']
        movie['year'] = request.form.get('year', '')
        movie['cover_image'] = request.form.get('cover_image', '')
        movie['directory_path'] = request.form.get('directory_path', '')
        movie['rating'] = request.form.get('rating', None)
        save_data(movies)
        return redirect(url_for('index'))
    else:
        return jsonify(movie)

@app.route('/delete_movie/<int:movie_id>')
def delete_movie(movie_id):
    movies = load_data()
    movies = [m for m in movies if m['id'] != movie_id]
    save_data(movies)
    return redirect(url_for('index'))









@app.route('/scan_manual_movie/<int:movie_id>')
def scan_manual_movie(movie_id):
    scan_and_update_movie_files()
    return redirect(url_for('movie', movie_id=movie_id))

@app.route('/scan_all_movies')
def scan_all_movies():
    scan_and_update_movie_files()
    return redirect(url_for('index'))

@app.route('/open_movie_folder/<int:movie_id>')
def open_movie_folder(movie_id):
    import subprocess
    import sys
    
    movies = load_data()
    movie = next((m for m in movies if m['id'] == movie_id), None)
    
    if movie and movie.get('directory_path'):
        folder_path = movie['directory_path']
        try:
            if sys.platform == 'win32':
                # Windows - ignore exit code since explorer sometimes returns non-zero even when successful
                subprocess.run(['explorer', folder_path], check=False)
            elif sys.platform == 'darwin':
                # macOS
                subprocess.run(['open', folder_path], check=True)
            else:
                # Linux
                subprocess.run(['xdg-open', folder_path], check=True)
            return jsonify({'success': True, 'message': 'Folder opened successfully'})
        except Exception as e:
            return jsonify({'success': False, 'message': f'Error: {str(e)}'})
    
    return jsonify({'success': False, 'message': 'Movie not found or no directory path'})

@app.route('/sync_movies')
def sync_movies():
    missing_movies = scan_for_missing_movies()
    return render_template('sync_movies.html', missing_movies=missing_movies)

@app.route('/add_missing_movie', methods=['POST'])
def add_missing_movie():
    movie_name = request.form.get('movie_name')
    full_path = request.form.get('full_path')
    
    if movie_name and full_path and os.path.exists(full_path):
        movies = load_data()
        
        # Create new movie entry
        new_movie = {
            'id': max([movie['id'] for movie in movies], default=0) + 1,
            'title': movie_name,
            'year': '',
            'cover_image': '',
            'directory_path': full_path,
            'rating': None,
            'files': []
        }
        
        # Scan for files in this directory
        existing_file_titles = set()
        for root, _, files in os.walk(full_path):
            for filename in files:
                name, ext = os.path.splitext(filename)
                if ext.lower() in ['.mp4', '.mkv', '.avi', '.mov', '.webm']:
                    if name not in existing_file_titles:
                        file_entry = {
                            'id': len(new_movie['files']) + 1,
                            'title': name,
                            'added_date': datetime.now().isoformat()
                        }
                        new_movie['files'].append(file_entry)
                        existing_file_titles.add(name)
        
        movies.append(new_movie)
        save_data(movies)
    
    return redirect(url_for('sync_movies'))

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True, port=5013)