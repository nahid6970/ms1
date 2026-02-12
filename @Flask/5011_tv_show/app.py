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
DATA_FILE = r"C:\@delta\db\5011_tv_show\data.json"
ROOT_SHOWS_FOLDER = r"D:\Downloads\@Sonarr"
IMAGE_CACHE_DIR = r"C:\@delta\output\sonarr_img"

os.makedirs(IMAGE_CACHE_DIR, exist_ok=True)

def get_cached_image(url):
    if not url:
        return url
    url_hash = hashlib.md5(url.encode()).hexdigest()
    ext = url.split('.')[-1].split('?')[0][:4]
    cached_path = os.path.join(IMAGE_CACHE_DIR, f"{url_hash}.{ext}")
    
    if os.path.exists(cached_path):
        return f"/cached_image/{url_hash}.{ext}"
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            with open(cached_path, 'wb') as f:
                f.write(response.content)
            return f"/cached_image/{url_hash}.{ext}"
    except:
        pass
    return url

def load_data():
    try:
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)

def scan_for_missing_shows():
    """Scan the root folder for TV show directories that aren't in the JSON file"""
    if not os.path.exists(ROOT_SHOWS_FOLDER):
        return []
    
    shows = load_data()
    existing_paths = {show.get('directory_path', '').lower() for show in shows if show.get('directory_path')}
    
    missing_shows = []
    
    try:
        for item in os.listdir(ROOT_SHOWS_FOLDER):
            item_path = os.path.join(ROOT_SHOWS_FOLDER, item)
            if os.path.isdir(item_path):
                # Check if this directory path is already in our shows
                if item_path.lower() not in existing_paths:
                    # Check if the directory contains video files
                    has_videos = False
                    for root, _, files in os.walk(item_path):
                        for filename in files:
                            _, ext = os.path.splitext(filename)
                            if ext.lower() in ['.mp4', '.mkv', '.avi', '.mov', '.webm']:
                                has_videos = True
                                break
                        if has_videos:
                            break
                    
                    if has_videos:
                        missing_shows.append({
                            'folder_name': item,
                            'full_path': item_path
                        })
    except Exception as e:
        print(f"Error scanning root folder: {e}")
    
    return missing_shows

def update_existing_episodes_with_notify():
    """Add notify field to existing episodes that don't have it"""
    print("Updating existing episodes with notify field...")
    shows = load_data()
    updated = False
    
    for show in shows:
        for episode in show.get('episodes', []):
            if 'notify' not in episode:
                episode['notify'] = 'unseen'
                updated = True
    
    if updated:
        save_data(shows)
        print("Episodes updated with notify field.")
    else:
        print("All episodes already have notify field.")

def scan_and_update_episodes():
    print("Scanning for new episodes...")
    shows = load_data()
    updated_shows = False
    for show in shows:
        if 'directory_path' in show and show['directory_path']:
            dir_path = show['directory_path']
            if os.path.isdir(dir_path):
                existing_episode_titles = {e['title'] for e in show['episodes']}
                episodes_added = False
                for root, _, files in os.walk(dir_path):
                    for filename in files:
                        name, ext = os.path.splitext(filename)
                        if ext.lower() in ['.mp4', '.mkv', '.avi', '.mov', '.webm']:
                            if name not in existing_episode_titles:
                                new_episode = {
                                    'id': len(show['episodes']) + 1,
                                    'title': name,
                                    'watched': False,
                                    'added_date': datetime.now().isoformat(),
                                    'notify': 'unseen'
                                }
                                show['episodes'].insert(0, new_episode)
                                existing_episode_titles.add(name)
                                updated_shows = True
                                episodes_added = True
                
                # Re-apply current sort order if episodes were added and sort is alphabetical
                if episodes_added and show.get('episode_sort_type') == 'alphabetical':
                    order = show.get('episode_sort_order', 'asc')
                    show['episodes'].sort(key=lambda x: x['title'].lower(), reverse=(order == 'desc'))
            else:
                print(f"Directory not found for {show['title']}: {dir_path}")
    if updated_shows:
        save_data(shows)
        print("New episodes found and updated.")
    else:
        print("No new episodes found.")

def scan_and_add_missing_shows():
    """Combined function: scan existing shows for new episodes AND auto-add missing shows"""
    print("Starting combined scan: episodes + missing shows...")
    
    # First, scan existing shows for new episodes
    scan_and_update_episodes()
    
    # Then, auto-add any missing shows
    missing_shows = scan_for_missing_shows()
    shows = load_data()
    added_count = 0
    
    for missing_show in missing_shows:
        folder_name = missing_show['folder_name']
        full_path = missing_show['full_path']
        
        if os.path.exists(full_path):
            print(f"Auto-adding missing show: {folder_name}")
            # Create new show entry
            new_show = {
                'id': max([show['id'] for show in shows], default=0) + 1,
                'title': folder_name,
                'year': '',
                'cover_image': '',
                'directory_path': full_path,
                'rating': None,
                'status': 'Continuing',
                'episodes': []
            }
            
            # Scan for episodes in this directory
            existing_episode_titles = set()
            for root, _, files in os.walk(full_path):
                for filename in files:
                    name, ext = os.path.splitext(filename)
                    if ext.lower() in ['.mp4', '.mkv', '.avi', '.mov', '.webm']:
                        if name not in existing_episode_titles:
                            episode = {
                                'id': len(new_show['episodes']) + 1,
                                'title': name,
                                'watched': False,
                                'added_date': datetime.now().isoformat(),
                                'notify': 'unseen'
                            }
                            new_show['episodes'].append(episode)
                            existing_episode_titles.add(name)
            
            # Sort episodes by title (newest first by default)
            new_show['episodes'].reverse()
            
            shows.append(new_show)
            added_count += 1
    
    if added_count > 0:
        save_data(shows)
        print(f"Auto-added {added_count} missing shows.")
    else:
        print("No missing shows found to add.")
    
    print("Combined scan completed.")

scheduler = BackgroundScheduler()
scheduler.add_job(func=scan_and_add_missing_shows, trigger="interval", hours=1)
scheduler.start()

@app.route('/cached_image/<filename>')
def cached_image(filename):
    return send_from_directory(IMAGE_CACHE_DIR, filename)

@app.route('/')
def index():
    sort_by = request.args.get('sort_by', 'title')
    order = request.args.get('order', 'asc')
    query = request.args.get('query')

    shows = load_data()

    # Filter shows based on query
    if query:
        shows = [show for show in shows if query.lower() in show['title'].lower()]

    # Calculate watched and total episodes, and last episode added date
    for show in shows:
        show['cover_image'] = get_cached_image(show.get('cover_image', ''))
        watched_episodes = sum(1 for episode in show.get('episodes', []) if episode.get('watched'))
        total_episodes = len(show.get('episodes', []))
        show['watched_count'] = watched_episodes
        show['total_count'] = total_episodes
        
        # Find the most recent episode added date
        episodes = show.get('episodes', [])
        if episodes:
            # Get the most recent added_date from all episodes
            recent_dates = []
            for episode in episodes:
                if 'added_date' in episode:
                    try:
                        recent_dates.append(datetime.fromisoformat(episode['added_date']))
                    except:
                        pass
            
            if recent_dates:
                latest_date = max(recent_dates)
                show['last_episode_added'] = latest_date.strftime('%d %B, %Y')
            else:
                show['last_episode_added'] = 'Unknown'
        else:
            show['last_episode_added'] = 'No episodes'

    # Sort shows
    if sort_by == 'title':
        shows.sort(key=lambda x: x['title'].lower(), reverse=(order == 'desc'))
    elif sort_by == 'year':
        shows.sort(key=lambda x: int(x['year']) if x['year'].isdigit() else 0, reverse=(order == 'desc'))
    elif sort_by == 'rating':
        shows.sort(key=lambda x: float(x.get('rating', -1)) if x.get('rating') is not None else -1, reverse=(order == 'desc'))
    elif sort_by == 'added': # Sort by ID for 'added' order
        shows.sort(key=lambda x: x['id'], reverse=(order == 'desc'))
    elif sort_by == 'last_episode': # Sort by most recent episode
        def get_last_episode_time(show):
            episodes = show.get('episodes', [])
            if not episodes:
                return datetime.min.isoformat()  # Shows with no episodes go to the end
            
            # Get the most recent episode (first in array since new episodes are inserted at index 0)
            latest_episode = episodes[0]
            
            # Use added_date if available, otherwise fall back to a default time based on episode ID
            if 'added_date' in latest_episode:
                return latest_episode['added_date']
            else:
                # For older episodes without added_date, use episode ID as a proxy for recency
                # Higher ID = more recent
                return f"1970-01-01T00:00:{latest_episode['id']:06d}"
        
        shows.sort(key=get_last_episode_time, reverse=(order == 'desc'))

    next_order = 'desc' if order == 'asc' else 'asc'

    return render_template('index.html', shows=shows, sort_by=sort_by, order=order, next_order=next_order, query=query)

@app.route('/show/<int:show_id>')
def show(show_id):
    sort_episodes = request.args.get('sort_episodes', 'default')
    order = request.args.get('order', 'asc')
    
    shows = load_data()
    show = next((s for s in shows if s['id'] == show_id), None)
    if show:
        show['cover_image'] = get_cached_image(show.get('cover_image', ''))
        # Initialize sort preferences if they don't exist
        if 'episode_sort_type' not in show:
            show['episode_sort_type'] = 'default'
        if 'episode_sort_order' not in show:
            show['episode_sort_order'] = 'asc'
        
        # If sort parameters are provided, update and save
        if sort_episodes != 'default':
            show['episode_sort_type'] = sort_episodes
            show['episode_sort_order'] = order
            show['episodes'].sort(key=lambda x: x['title'].lower(), reverse=(order == 'desc'))
            save_data(shows)
        else:
            # Use stored preferences
            sort_episodes = show['episode_sort_type']
            order = show['episode_sort_order']
            # Apply stored sort if it's alphabetical
            if sort_episodes == 'alphabetical':
                show['episodes'].sort(key=lambda x: x['title'].lower(), reverse=(order == 'desc'))
        
        next_order = 'desc' if order == 'asc' else 'asc'
        return render_template('show.html', show=show, sort_episodes=sort_episodes, order=order, next_order=next_order)
    return 'Show not found', 404

@app.route('/add_show', methods=['GET', 'POST'])
def add_show():
    if request.method == 'POST':
        shows = load_data()
        new_show = {
            'id': len(shows) + 1,
            'title': request.form['title'],
            'year': request.form.get('year', ''),
            'cover_image': request.form.get('cover_image', ''),
            'directory_path': request.form.get('directory_path', ''),
            'rating': request.form.get('rating', None), # Add rating field
            'status': request.form.get('status', 'Continuing'), # Add status field
            'episodes': []
        }
        shows.append(new_show)
        save_data(shows)
        return redirect(url_for('index'))
    return render_template('add_show.html')

@app.route('/edit_show/<int:show_id>', methods=['GET', 'POST'])
def edit_show(show_id):
    shows = load_data()
    show = next((s for s in shows if s['id'] == show_id), None)
    if not show:
        return 'Show not found', 404
    if request.method == 'POST':
        show['title'] = request.form['title']
        show['year'] = request.form.get('year', '')
        show['cover_image'] = request.form.get('cover_image', '')
        show['directory_path'] = request.form.get('directory_path', '')
        show['rating'] = request.form.get('rating', None) # Update rating field
        show['status'] = request.form.get('status', 'Continuing') # Update status field
        show['sonarr_url'] = request.form.get('sonarr_url', '')
        save_data(shows)
        return redirect(url_for('index'))
    else:
        return jsonify(show)

@app.route('/delete_show/<int:show_id>')
def delete_show(show_id):
    shows = load_data()
    shows = [s for s in shows if s['id'] != show_id]
    save_data(shows)
    return redirect(url_for('index'))

@app.route('/add_episode/<int:show_id>', methods=['POST'])
def add_episode(show_id):
    shows = load_data()
    show = next((s for s in shows if s['id'] == show_id), None)
    if show:
        new_episode = {
            'id': len(show['episodes']) + 1,
            'title': request.form['title'],
            'watched': False,
            'added_date': datetime.now().isoformat(),
            'notify': 'unseen'
        }
        show['episodes'].insert(0, new_episode)
        
        # Re-apply current sort order if it's alphabetical
        if show.get('episode_sort_type') == 'alphabetical':
            order = show.get('episode_sort_order', 'asc')
            show['episodes'].sort(key=lambda x: x['title'].lower(), reverse=(order == 'desc'))
        
        save_data(shows)
        return redirect(url_for('show', show_id=show_id))
    return 'Show not found', 404

@app.route('/edit_episode/<int:show_id>/<int:episode_id>', methods=['GET', 'POST'])
def edit_episode(show_id, episode_id):
    shows = load_data()
    show = next((s for s in shows if s['id'] == show_id), None)
    if not show:
        return 'Show not found', 404
    episode = next((e for e in show['episodes'] if e['id'] == episode_id), None)
    if not episode:
        return 'Episode not found', 404
    if request.method == 'POST':
        episode['title'] = request.form['title']
        save_data(shows)
        return redirect(url_for('show', show_id=show_id))
    else:
        return jsonify(episode)

@app.route('/delete_episode/<int:show_id>/<int:episode_id>')
def delete_episode(show_id, episode_id):
    shows = load_data()
    show = next((s for s in shows if s['id'] == show_id), None)
    if show:
        show['episodes'] = [e for e in show['episodes'] if e['id'] != episode_id]
        save_data(shows)
        return redirect(url_for('show', show_id=show_id))
    return 'Show not found', 404

@app.route('/toggle_watched/<int:show_id>/<int:episode_id>')
def toggle_watched(show_id, episode_id):
    shows = load_data()
    show = next((s for s in shows if s['id'] == show_id), None)
    if show:
        episode = next((e for e in show['episodes'] if e['id'] == episode_id), None)
        if episode:
            episode['watched'] = not episode['watched']
            save_data(shows)
            return redirect(url_for('show', show_id=show_id))
    return 'Episode not found', 404

@app.route('/scan_manual/<int:show_id>')
def scan_manual(show_id):
    scan_and_update_episodes()
    return redirect(url_for('show', show_id=show_id))

@app.route('/scan_all')
def scan_all():
    scan_and_update_episodes()
    return redirect(url_for('index'))

@app.route('/scan_and_add_all')
def scan_and_add_all():
    """Manual trigger for combined scan function"""
    scan_and_add_missing_shows()
    return redirect(url_for('index'))

@app.route('/open_folder/<int:show_id>')
def open_folder(show_id):
    import subprocess
    import sys
    
    shows = load_data()
    show = next((s for s in shows if s['id'] == show_id), None)
    
    if show and show.get('directory_path'):
        folder_path = show['directory_path']
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
    
    return jsonify({'success': False, 'message': 'Show not found or no directory path'})

@app.route('/sync_shows')
def sync_shows():
    missing_shows = scan_for_missing_shows()
    return render_template('sync_shows.html', missing_shows=missing_shows)

@app.route('/auto_add_all_shows', methods=['POST'])
def auto_add_all_shows():
    """Automatically add all missing shows to the library"""
    missing_shows = scan_for_missing_shows()
    shows = load_data()
    added_count = 0
    
    for missing_show in missing_shows:
        folder_name = missing_show['folder_name']
        full_path = missing_show['full_path']
        
        if os.path.exists(full_path):
            # Create new show entry
            new_show = {
                'id': max([show['id'] for show in shows], default=0) + 1,
                'title': folder_name,
                'year': '',
                'cover_image': '',
                'directory_path': full_path,
                'rating': None,
                'status': 'Continuing',
                'episodes': []
            }
            
            # Scan for episodes in this directory
            existing_episode_titles = set()
            for root, _, files in os.walk(full_path):
                for filename in files:
                    name, ext = os.path.splitext(filename)
                    if ext.lower() in ['.mp4', '.mkv', '.avi', '.mov', '.webm']:
                        if name not in existing_episode_titles:
                            episode = {
                                'id': len(new_show['episodes']) + 1,
                                'title': name,
                                'watched': False,
                                'added_date': datetime.now().isoformat(),
                                'notify': 'unseen'
                            }
                            new_show['episodes'].append(episode)
                            existing_episode_titles.add(name)
            
            # Sort episodes by title (newest first by default)
            new_show['episodes'].reverse()
            
            shows.append(new_show)
            added_count += 1
    
    if added_count > 0:
        save_data(shows)
    
    return redirect(url_for('sync_shows'))

@app.route('/rescan_library', methods=['POST'])
def rescan_library():
    """Rescan the entire library for new episodes"""
    scan_and_update_episodes()
    return redirect(url_for('sync_shows'))

@app.route('/add_missing_show', methods=['POST'])
def add_missing_show():
    folder_name = request.form.get('folder_name')
    full_path = request.form.get('full_path')
    
    if folder_name and full_path and os.path.exists(full_path):
        shows = load_data()
        
        # Create new show entry
        new_show = {
            'id': max([show['id'] for show in shows], default=0) + 1,
            'title': folder_name,
            'year': '',
            'cover_image': '',
            'directory_path': full_path,
            'rating': None,
            'status': 'Continuing', # Default status for synced shows
            'episodes': []
        }
        
        # Scan for episodes in this directory
        existing_episode_titles = set()
        for root, _, files in os.walk(full_path):
            for filename in files:
                name, ext = os.path.splitext(filename)
                if ext.lower() in ['.mp4', '.mkv', '.avi', '.mov', '.webm']:
                    if name not in existing_episode_titles:
                        episode = {
                            'id': len(new_show['episodes']) + 1,
                            'title': name,
                            'watched': False,
                            'added_date': datetime.now().isoformat(),
                            'notify': 'unseen'
                        }
                        new_show['episodes'].append(episode)
                        existing_episode_titles.add(name)
        
        # Sort episodes by title (newest first by default)
        new_show['episodes'].reverse()
        
        shows.append(new_show)
        save_data(shows)
    
    return redirect(url_for('sync_shows'))

@app.route('/update_notify_fields')
def update_notify_fields():
    """Route to update existing episodes with notify field"""
    update_existing_episodes_with_notify()
    return redirect(url_for('index'))

@app.route('/toggle_notify/<int:show_id>/<int:episode_id>')
def toggle_notify(show_id, episode_id):
    """Toggle notify status between 'seen' and 'unseen'"""
    shows = load_data()
    show = next((s for s in shows if s['id'] == show_id), None)
    if show:
        episode = next((e for e in show['episodes'] if e['id'] == episode_id), None)
        if episode:
            # Toggle between 'seen' and 'unseen'
            current_status = episode.get('notify', 'unseen')
            episode['notify'] = 'seen' if current_status == 'unseen' else 'unseen'
            save_data(shows)
            return redirect(url_for('show', show_id=show_id))
    return 'Episode not found', 404

@app.route('/mark_notify_seen/<int:show_id>/<int:episode_id>')
def mark_notify_seen(show_id, episode_id):
    """Mark episode notify status as 'seen'"""
    shows = load_data()
    show = next((s for s in shows if s['id'] == show_id), None)
    if show:
        episode = next((e for e in show['episodes'] if e['id'] == episode_id), None)
        if episode:
            episode['notify'] = 'seen'
            save_data(shows)
            return jsonify({'success': True, 'notify': 'seen'})
    return jsonify({'success': False, 'message': 'Episode not found'}), 404

@app.route('/mark_notify_unseen/<int:show_id>/<int:episode_id>')
def mark_notify_unseen(show_id, episode_id):
    """Mark episode notify status as 'unseen'"""
    shows = load_data()
    show = next((s for s in shows if s['id'] == show_id), None)
    if show:
        episode = next((e for e in show['episodes'] if e['id'] == episode_id), None)
        if episode:
            episode['notify'] = 'unseen'
            save_data(shows)
            return jsonify({'success': True, 'notify': 'unseen'})
    return jsonify({'success': False, 'message': 'Episode not found'}), 404

@app.route('/api/unseen_count')
def get_unseen_count():
    """Get count of all unseen episodes across all shows"""
    shows = load_data()
    unseen_count = 0
    
    for show in shows:
        for episode in show.get('episodes', []):
            if episode.get('notify', 'unseen') == 'unseen':
                unseen_count += 1
    
    return jsonify({'unseen_count': unseen_count})

@app.route('/api/mark_all_seen', methods=['POST'])
def mark_all_episodes_seen():
    """Mark all episodes as seen"""
    shows = load_data()
    updated_count = 0
    
    for show in shows:
        for episode in show.get('episodes', []):
            if episode.get('notify', 'unseen') == 'unseen':
                episode['notify'] = 'seen'
                updated_count += 1
    
    if updated_count > 0:
        save_data(shows)
    
    return jsonify({'success': True, 'updated_count': updated_count})

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True, port=5011)