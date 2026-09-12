import sys, os
# 1. Add the absolute path to the folder containing install_deps.py
UTILITY_PATH = r"C:\@delta\ms1"
if UTILITY_PATH not in sys.path: sys.path.append(UTILITY_PATH)

# 2. Import and run the bootstrap
import install_deps
install_deps.bootstrap(__file__)

import json
import os
import re
import calendar
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import time
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
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATA_FILE = r"C:\@delta\db\5011_tv_show\data.json"
TIMESTAMPS_FILE = r"C:\@delta\db\5011_tv_show\timestamps.json"
MOVIES_FILE = r"C:\@delta\db\5011_tv_show\movies.json"
IMAGE_CACHE_DIR = r"C:\@delta\output\sonarr_img"
SETTINGS_FILE = r"C:\@delta\db\5011_tv_show\settings.json"
BANGLADESH_TZ = ZoneInfo('Asia/Dhaka')

os.makedirs(IMAGE_CACHE_DIR, exist_ok=True)

def load_settings():
    default_settings = {
        "tmdb_api_key": "",
        "default_shows_sort": "title",
        "default_shows_order": "asc",
        "default_movies_sort": "title",
        "default_movies_order": "asc",
        "storage_scan_interval_minutes": 60,
        "sonarr_url": "http://192.168.0.101:8989",
        "sonarr_api_key": "",
        "root_shows_folder": r"C:\Users\nahid\Downloads\@sonarr",
        "radarr_url": "http://192.168.0.101:7878",
        "radarr_api_key": "",
        "root_movies_folder": r"C:\Users\nahid\Downloads\@radarr",
        "episode_file_icons_enabled": True,
        "auto_schedule_start_time": "01:00",
        "auto_schedule_end_time": "23:00",
        "discover_image_scale": 1
    }
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, 'r') as f:
                loaded = json.load(f)
                default_settings.update(loaded)
                return default_settings
        except:
            pass
    return default_settings

def save_settings(settings):
    os.makedirs(os.path.dirname(SETTINGS_FILE), exist_ok=True)
    with open(SETTINGS_FILE, 'w') as f:
        json.dump(settings, f, indent=4)

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

def load_timestamps():
    """Load per-show volatile timestamps (episodes_updated_at, last_run_result,
    episode_update_last_run) from a separate file that is NOT git-tracked."""
    try:
        with open(TIMESTAMPS_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_timestamps(ts):
    os.makedirs(os.path.dirname(TIMESTAMPS_FILE), exist_ok=True)
    with open(TIMESTAMPS_FILE, 'w') as f:
        json.dump(ts, f, indent=4)

def get_show_ts(show_id):
    """Return the timestamp entry for a single show (or empty dict)."""
    return load_timestamps().get(str(show_id), {})

def set_show_ts(show_id, **kwargs):
    """Merge kwargs into the timestamp entry for show_id and persist."""
    ts = load_timestamps()
    key = str(show_id)
    entry = ts.get(key, {})
    entry.update(kwargs)
    ts[key] = entry
    save_timestamps(ts)

def load_movies():
    try:
        with open(MOVIES_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_movies(movies):
    os.makedirs(os.path.dirname(MOVIES_FILE), exist_ok=True)
    with open(MOVIES_FILE, 'w') as f:
        json.dump(movies, f, indent=4)

def tmdb_request(path, params=None):
    """Request data from TMDb using the key configured in Settings."""
    api_key = load_settings().get('tmdb_api_key', '').strip()
    if not api_key:
        return None, 'TMDb API Key is not configured in Settings'

    request_params = dict(params or {})
    request_params['api_key'] = api_key
    try:
        response = requests.get(
            f'https://api.themoviedb.org/3/{path.lstrip("/")}',
            params=request_params,
            timeout=15
        )
        if response.status_code != 200:
            return None, f'TMDb returned HTTP {response.status_code}'
        return response.json(), None
    except requests.exceptions.RequestException as error:
        return None, f'Unable to reach TMDb: {error}'

def tmdb_poster_url(path):
    return f'https://image.tmdb.org/t/p/w500{path}' if path else ''

def tmdb_year(value):
    return str(value or '')[:4]

def tmdb_genres(details):
    return [genre.get('name') for genre in details.get('genres', []) if genre.get('name')]

def tmdb_digital_release_date(tmdb_id):
    """Return the earliest digital release date listed by TMDb, if any."""
    release_data, error = tmdb_request(f'movie/{int(tmdb_id)}/release_dates')
    if error or not release_data:
        return ''

    digital_dates = []
    for country in release_data.get('results', []):
        for release in country.get('release_dates', []):
            if str(release.get('type')) == '4' and release.get('release_date'):
                digital_dates.append(release['release_date'][:10])
    return min(digital_dates) if digital_dates else ''

def tmdb_five_star_rating(score):
    """Convert TMDb's 0-10 score to the app's whole-number 1-5 scale."""
    numeric_score = float(score or 0)
    if numeric_score <= 0:
        return None
    return max(1, min(5, int((numeric_score / 2) + 0.5)))

def migrate_tmdb_ratings(items):
    """Convert older imported TMDb scores that were stored as app ratings."""
    changed = False
    for item in items:
        rating = item.get('rating')
        if not item.get('tmdb_id') or item.get('tmdb_rating') is not None or rating is None:
            continue
        try:
            numeric_rating = float(rating)
        except (TypeError, ValueError):
            continue
        if numeric_rating > 5:
            item['tmdb_rating'] = numeric_rating
            item['rating'] = tmdb_five_star_rating(numeric_rating)
            changed = True
    return changed

def catalog_match_key(title, year):
    normalized_title = re.sub(r'[^a-z0-9]+', '', str(title or '').casefold())
    normalized_year = str(year or '')[:4]
    return f'{normalized_title}:{normalized_year}'

def tvmaze_request(path, params=None):
    try:
        response = requests.get(
            f'https://api.tvmaze.com/{path.lstrip("/")}',
            params=params or {},
            timeout=15
        )
        if response.status_code != 200:
            return None, f'TVmaze returned HTTP {response.status_code}'
        return response.json(), None
    except requests.exceptions.RequestException as error:
        return None, f'Unable to reach TVmaze: {error}'

def tvmaze_show_for_catalog_item(show):
    stored_tvmaze_id = show.get('tvmaze_id')
    if stored_tvmaze_id:
        candidate, error = tvmaze_request(f"shows/{int(stored_tvmaze_id)}")
        if candidate and not error:
            return candidate, None

    for external_key in ('imdb', 'tvdb'):
        external_id = (show.get('external_ids') or {}).get(external_key)
        if external_id:
            candidate, error = tvmaze_request('lookup/shows', {external_key: external_id})
            if candidate and not error:
                return candidate, None

    title = str(show.get('title', '')).strip()
    queries = [title]
    for separator in (':', ' - ', ' – '):
        if separator in title:
            queries.append(title.split(separator, 1)[0].strip())
    queries = list(dict.fromkeys(query for query in queries if query))

    matches = []
    last_error = None
    for query in queries:
        matches, error = tvmaze_request('search/shows', {'q': query})
        if error:
            last_error = error
            continue
        if matches:
            break
    if last_error and not matches:
        return None, last_error
    target_title = str(show.get('title', '')).casefold().strip()
    target_year = str(show.get('year', ''))[:4]
    ranked = []
    for match in matches or []:
        candidate = match.get('show') or {}
        candidate_title = str(candidate.get('name', '')).casefold().strip()
        premiered_year = str(candidate.get('premiered') or '')[:4]
        title_match = candidate_title == target_title
        year_match = bool(target_year and premiered_year == target_year)
        ranked.append((0 if title_match else 1, 0 if year_match else 1, -float(match.get('score') or 0), candidate))
    if not ranked:
        return None, f'No TVmaze show found for {show.get("title", "this show")}'
    ranked.sort(key=lambda item: item[:3])
    return ranked[0][3], None

def tvmaze_status(tvmaze_show):
    """Map TVmaze's show status to the app's continuing/ended labels."""
    return 'Ended' if str((tvmaze_show or {}).get('status', '')).casefold() == 'ended' else 'Continuing'

def bangladesh_airtime(source_episode):
    """Return an episode's TVmaze air time converted to Bangladesh time."""
    source_airtime = source_episode.get('airtime') or ''
    airstamp = source_episode.get('airstamp')
    if not airstamp:
        return source_airtime
    try:
        parsed = datetime.fromisoformat(str(airstamp).replace('Z', '+00:00'))
        if parsed.tzinfo is None:
            return source_airtime
        return parsed.astimezone(BANGLADESH_TZ).strftime('%H:%M')
    except (TypeError, ValueError):
        return source_airtime

def merge_tvmaze_episodes(show, tvmaze_show, episodes):
    existing_episodes = show.get('episodes', [])
    by_number = {
        (episode.get('season_number'), episode.get('episode_number')): episode
        for episode in existing_episodes
        if episode.get('season_number') is not None and episode.get('episode_number') is not None
    }
    added = 0
    updated = 0
    for source_episode in episodes or []:
        season_number = source_episode.get('season')
        episode_number = source_episode.get('number')
        if season_number is None or episode_number is None:
            continue
        key = (season_number, episode_number)
        target = by_number.get(key)
        metadata = {
            'season_number': season_number,
            'episode_number': episode_number,
            'title': source_episode.get('name') or f'S{season_number:02d}E{episode_number:02d}',
            'air_date': source_episode.get('airdate') or '',
            'airtime': bangladesh_airtime(source_episode),
            'air_datetime': source_episode.get('airstamp') or '',
            'overview': re.sub(r'<[^>]+>', '', source_episode.get('summary') or '').strip(),
            'still_image': (source_episode.get('image') or {}).get('original') or (source_episode.get('image') or {}).get('medium') or '',
            'tvmaze_episode_id': source_episode.get('id')
        }
        if target:
            target.update(metadata)
            updated += 1
        else:
            metadata.update({
                'id': max([episode.get('id', 0) for episode in existing_episodes], default=0) + 1,
                'watched': False,
                'notify': 'unseen'
            })
            existing_episodes.append(metadata)
            by_number[key] = metadata
            added += 1
    sort_episode_list(show)
    show['episodes'] = existing_episodes
    show['tvmaze_id'] = tvmaze_show.get('id')
    return added, updated

def sort_episode_list(show):
    """Apply a persisted, deterministic sort to a show's episode list."""
    episodes = show.get('episodes', [])
    sort_type = show.get('episode_sort_type', 'default')
    order = show.get('episode_sort_order', 'asc')
    reverse = order == 'desc'
    if sort_type == 'alphabetical':
        episodes.sort(key=lambda episode: str(episode.get('title', '')).casefold(), reverse=reverse)
    else:
        def episode_key(episode):
            season = episode.get('season_number')
            number = episode.get('episode_number')
            if season is not None and number is not None:
                return (0, int(season), int(number), str(episode.get('title', '')).casefold())
            return (1, int(episode.get('id', 0)), 0, str(episode.get('title', '')).casefold())
        episodes.sort(key=episode_key, reverse=reverse)

def scan_for_missing_shows():
    """Scan the root folder for TV show directories that aren't in the JSON file"""
    settings = load_settings()
    root_folder = settings.get('root_shows_folder', r"C:\Users\nahid\Downloads\@sonarr")
    if not os.path.exists(root_folder):
        return []
    
    shows = load_data()
    existing_paths = {show.get('directory_path', '').lower() for show in shows if show.get('directory_path')}
    
    missing_shows = []
    
    try:
        for item in os.listdir(root_folder):
            item_path = os.path.join(root_folder, item)
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
    VIDEO_EXTS = {'.mp4', '.mkv', '.avi', '.mov', '.webm', '.m4v', '.ts'}
    SXXEXX = re.compile(r'[Ss](\d{1,2})[Ee](\d{1,2})')
    DATE_PAT = re.compile(r'(\d{4}-\d{2}-\d{2})')

    for show in shows:
        if 'directory_path' in show and show['directory_path']:
            dir_path = show['directory_path']
            if not os.path.isdir(dir_path):
                print(f"Directory not found for {show['title']}: {dir_path}")
                continue

            # Build lookup: (season, episode) -> episode object
            by_number = {
                (int(ep['season_number']), int(ep['episode_number'])): ep
                for ep in show['episodes']
                if ep.get('season_number') is not None and ep.get('episode_number') is not None
            }
            # Build lookup: air_date string -> episode object (for date-match mode)
            by_date = {
                ep['air_date']: ep
                for ep in show['episodes']
                if ep.get('air_date')
            }
            existing_titles = {ep['title'] for ep in show['episodes']}
            episodes_added = False

            for root, _, files in os.walk(dir_path):
                for filename in files:
                    name, ext = os.path.splitext(filename)
                    if ext.lower() not in VIDEO_EXTS:
                        continue

                    matched = False
                    scan_mode = show.get('scan_mode', 'sxxexx')

                    # --- Date match (YYYY-MM-DD in filename) ---
                    if scan_mode == 'date':
                        dm = DATE_PAT.search(name)
                        if dm:
                            date_key = dm.group(1)
                            if date_key in by_date:
                                ep = by_date[date_key]
                                if not ep.get('has_file'):
                                    ep['has_file'] = True
                                    ep['file_name'] = name
                                    updated_shows = True
                                matched = True
                            else:
                                # Date found but no TVmaze episode yet — add as raw
                                new_ep = {
                                    'id': max((ep.get('id', 0) for ep in show['episodes']), default=0) + 1,
                                    'title': name,
                                    'air_date': date_key,
                                    'has_file': True,
                                    'file_name': name,
                                    'watched': False,
                                    'added_date': datetime.now().isoformat(),
                                    'notify': 'unseen'
                                }
                                show['episodes'].insert(0, new_ep)
                                by_date[date_key] = new_ep
                                existing_titles.add(name)
                                updated_shows = True
                                episodes_added = True
                                matched = True

                    # --- Try SxxExx match (default mode) ---
                    elif scan_mode != 'title':
                        m = SXXEXX.search(name)
                        if m:
                            key = (int(m.group(1)), int(m.group(2)))
                            if key in by_number:
                                ep = by_number[key]
                                if not ep.get('has_file'):
                                    ep['has_file'] = True
                                    ep['file_name'] = name
                                    updated_shows = True
                                matched = True
                            else:
                                new_ep = {
                                    'id': max((ep.get('id', 0) for ep in show['episodes']), default=0) + 1,
                                    'title': name,
                                    'season_number': key[0],
                                    'episode_number': key[1],
                                    'has_file': True,
                                    'file_name': name,
                                    'watched': False,
                                    'added_date': datetime.now().isoformat(),
                                    'notify': 'unseen'
                                }
                                show['episodes'].insert(0, new_ep)
                                by_number[key] = new_ep
                                existing_titles.add(name)
                                updated_shows = True
                                episodes_added = True
                                matched = True

                    # --- Fall back to exact title match ---
                    if not matched and name not in existing_titles:
                        new_ep = {
                            'id': max((ep.get('id', 0) for ep in show['episodes']), default=0) + 1,
                            'title': name,
                            'has_file': True,
                            'file_name': name,
                            'watched': False,
                            'added_date': datetime.now().isoformat(),
                            'notify': 'unseen'
                        }
                        show['episodes'].insert(0, new_ep)
                        existing_titles.add(name)
                        updated_shows = True
                        episodes_added = True

            if episodes_added and show.get('episode_sort_type') == 'alphabetical':
                order = show.get('episode_sort_order', 'asc')
                show['episodes'].sort(key=lambda x: x['title'].lower(), reverse=(order == 'desc'))

    if updated_shows:
        save_data(shows)
        print("New episodes found and updated.")
    else:
        print("No new episodes found.")

def scan_and_add_missing_shows():
    """Combined function: scan existing shows for new episodes AND auto-add missing shows"""
    print("Starting combined scan: episodes + missing shows...")

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
            
            # Populate TVmaze episodes first so the later storage scan can
            # attach matching files instead of creating raw duplicate episodes.
            tvmaze_show, tvmaze_error = tvmaze_show_for_catalog_item(new_show)
            if tvmaze_show and not tvmaze_error:
                tvmaze_episodes, episodes_error = tvmaze_request(
                    f"shows/{tvmaze_show['id']}/episodes", {'specials': 1}
                )
                if tvmaze_episodes and not episodes_error:
                    merge_tvmaze_episodes(new_show, tvmaze_show, tvmaze_episodes)

            # If TVmaze cannot identify the folder, retain the old raw-file
            # fallback so the show is still visible and can be matched later.
            if not new_show['episodes']:
                existing_episode_titles = set()
                for root, _, files in os.walk(full_path):
                    for filename in files:
                        name, ext = os.path.splitext(filename)
                        if ext.lower() in ['.mp4', '.mkv', '.avi', '.mov', '.webm'] and name not in existing_episode_titles:
                            new_show['episodes'].append({
                                'id': len(new_show['episodes']) + 1,
                                'title': name,
                                'watched': False,
                                'added_date': datetime.now().isoformat(),
                                'notify': 'unseen'
                            })
                            existing_episode_titles.add(name)
                new_show['episodes'].reverse()
            
            shows.append(new_show)
            added_count += 1
    
    if added_count > 0:
        save_data(shows)
        print(f"Auto-added {added_count} missing shows.")
    else:
        print("No missing shows found to add.")

    # Always run the same complete storage scan used by the Scan Storage
    # button, after newly discovered folders have been added.
    scan_and_update_episodes()
    
    print("Combined scan completed.")

def sync_radarr_movies():
    """Fetch downloaded movies from Radarr and upsert them into movies.json.
    Returns (added, updated, error_message)."""
    settings = load_settings()
    radarr_url = settings.get('radarr_url', 'http://192.168.0.101:7878').rstrip('/')
    api_key = settings.get('radarr_api_key', '')

    if not api_key:
        return 0, 0, 'Radarr API Key not configured in Settings'

    headers = {
        'X-Api-Key': api_key,
        'Content-Type': 'application/json'
    }

    try:
        response = requests.get(f"{radarr_url}/api/v3/movie", headers=headers, timeout=15)
        if response.status_code != 200:
            return 0, 0, f'Failed to get movies from Radarr: HTTP {response.status_code}'

        radarr_movies = response.json()
        movies = load_movies()
        added = 0
        updated = 0

        for rm in radarr_movies:
            # Only track movies that actually have files on disk (like the shows app tracks existing shows)
            if not rm.get('hasFile'):
                continue

            title = (rm.get('title') or '').strip()
            if not title:
                continue

            tmdb_id = rm.get('tmdbId')
            imdb_id = rm.get('imdbId')
            year = rm.get('year')
            path = rm.get('path', '')

            poster = ''
            for img in (rm.get('images') or []):
                if img.get('coverType') == 'poster':
                    poster = img.get('remoteUrl') or img.get('url') or ''
                    break

            # Find existing local movie by tmdb_id or path
            existing = None
            for m in movies:
                if tmdb_id and m.get('tmdb_id') == tmdb_id:
                    existing = m
                    break
                if path and m.get('directory_path') and os.path.normpath(m.get('directory_path', '')).lower() == os.path.normpath(path).lower():
                    existing = m
                    break

            if existing:
                existing['title'] = title
                existing['year'] = str(year) if year else existing.get('year', '')
                if poster:
                    existing['cover_image'] = poster
                if path:
                    existing['directory_path'] = path
                existing['radarr_id'] = rm.get('id')
                if imdb_id:
                    external_ids = existing.get('external_ids')
                    if not isinstance(external_ids, dict):
                        external_ids = {}
                        existing['external_ids'] = external_ids
                    external_ids['imdb'] = imdb_id
                existing['status'] = rm.get('status', existing.get('status', ''))
                updated += 1
            else:
                movies.append({
                    'id': max([m.get('id', 0) for m in movies], default=0) + 1,
                    'tmdb_id': tmdb_id,
                    'external_ids': {'imdb': imdb_id} if imdb_id else {},
                    'radarr_id': rm.get('id'),
                    'title': title,
                    'year': str(year) if year else '',
                    'cover_image': poster,
                    'directory_path': path,
                    'rating': None,
                    'status': rm.get('status', ''),
                    'watched': False,
                    'added_date': datetime.now().isoformat()
                })
                added += 1

        if added or updated:
            save_movies(movies)

        return added, updated, None

    except requests.exceptions.RequestException as e:
        return 0, 0, f'Network error communicating with Radarr: {str(e)}'

def run_scheduled_episode_updates():
    """Refresh shows whose daily update time matches the local server time."""
def run_show_episode_update(show, now=None):
    """Run episode update for a single show. Returns (added, updated, error_message)."""
    if now is None:
        now = datetime.now()
    tvmaze_show, error = tvmaze_show_for_catalog_item(show)
    if error:
        return 0, 0, error
    episodes, error = tvmaze_request(f"shows/{tvmaze_show['id']}/episodes", {'specials': 1})
    if error:
        return 0, 0, error
    added, updated = merge_tvmaze_episodes(show, tvmaze_show, episodes)
    if not show.get('lock_status'):
        show['status'] = tvmaze_status(tvmaze_show)
        tmdb_details, tmdb_error = resolve_tmdb_for_show(show, tvmaze_show)
        if tmdb_details and not tmdb_error:
            tmdb_image = tmdb_poster_url(tmdb_details.get('poster_path'))
            if tmdb_image:
                show['cover_image'] = tmdb_image
            tmdb_score = round(float(tmdb_details.get('vote_average') or 0), 1)
            if tmdb_score > 0:
                show['tmdb_rating'] = tmdb_score
        else:
            if not show.get('cover_image'):
                tvmaze_img = (tvmaze_show.get('image') or {})
                tvmaze_poster = tvmaze_img.get('original') or tvmaze_img.get('medium')
                if tvmaze_poster:
                    show['cover_image'] = tvmaze_poster
    set_show_ts(show['id'],
                episodes_updated_at=now.isoformat(),
                last_run_result={
                    'timestamp': now.isoformat(),
                    'added': added,
                    'updated': updated,
                    'error': None,
                })
    return added, updated, None


def get_last_due_date(show, now):
    """
    Return the most recent date on which this show's update was due,
    or None if it isn't due yet today.
    """
    update_time_str = show.get('episode_update_time', '').strip()
    if not update_time_str:
        return None
    try:
        h, m = int(update_time_str.split(':')[0]), int(update_time_str.split(':')[1])
    except (ValueError, IndexError):
        return None

    frequency = show.get('episode_update_frequency', 'daily')
    today = now.date()
    scheduled_today = now.replace(hour=h, minute=m, second=0, microsecond=0)

    if frequency == 'daily':
        # Due every day — last due date is today if time has passed, else yesterday
        if now >= scheduled_today:
            return today
        return today - timedelta(days=1)

    elif frequency == 'weekly':
        try:
            target_weekday = int(show.get('episode_update_weekday', now.weekday()))
        except (TypeError, ValueError):
            target_weekday = now.weekday()
        # Walk back to find the most recent occurrence of target_weekday
        days_back = (today.weekday() - target_weekday) % 7
        candidate = today - timedelta(days=days_back)
        candidate_dt = now.replace(year=candidate.year, month=candidate.month, day=candidate.day,
                                   hour=h, minute=m, second=0, microsecond=0)
        if now >= candidate_dt:
            return candidate
        # Time hasn't passed yet on this week's day — go back one more week
        return candidate - timedelta(weeks=1)

    elif frequency == 'monthly':
        try:
            target_day = max(1, min(31, int(show.get('episode_update_month_day', now.day))))
        except (TypeError, ValueError):
            target_day = now.day
        # Try this month first
        current_month_last_day = calendar.monthrange(today.year, today.month)[1]
        candidate = today.replace(day=min(target_day, current_month_last_day))
        candidate_dt = now.replace(year=candidate.year, month=candidate.month, day=candidate.day,
                                   hour=h, minute=m, second=0, microsecond=0)
        if now >= candidate_dt:
            return candidate
        # Time hasn't passed yet — go back one month
        first_of_month = today.replace(day=1)
        prev_month_last = first_of_month - timedelta(days=1)
        previous_month_last_day = calendar.monthrange(prev_month_last.year, prev_month_last.month)[1]
        return prev_month_last.replace(day=min(target_day, previous_month_last_day))

    return None


def run_scheduled_episode_updates():
    """Refresh shows whose scheduled update time has passed — catches up missed runs.
    Shows are processed one at a time with a short delay to avoid hammering APIs."""
    now = datetime.now()
    shows = load_data()

    # Collect IDs of shows that are due — don't run yet
    due_show_ids = []
    for show in shows:
        update_time_str = show.get('episode_update_time', '').strip()
        if not update_time_str:
            continue
        last_due = get_last_due_date(show, now)
        if last_due is None:
            continue
        last_run_str = get_show_ts(show['id']).get('episode_update_last_run', '')
        if last_run_str:
            try:
                if datetime.strptime(last_run_str, '%Y-%m-%d').date() >= last_due:
                    continue
            except ValueError:
                pass
        due_show_ids.append(show['id'])

    if not due_show_ids:
        return

    # Process due shows one by one with a delay between each
    for i, show_id in enumerate(due_show_ids):
        if i > 0:
            time.sleep(3)  # 3-second gap between shows — keeps API rate limits happy
        # Reload fresh data each iteration so we always write the latest state
        shows = load_data()
        show = next((s for s in shows if s['id'] == show_id), None)
        if not show:
            continue
        added, updated, error = run_show_episode_update(show, now)
        if error:
            set_show_ts(show_id, last_run_result={'timestamp': now.isoformat(), 'added': 0, 'updated': 0, 'error': error})
        set_show_ts(show_id, episode_update_last_run=now.date().isoformat())
        save_data(shows)  # Save after each show so progress survives a restart

scheduler = BackgroundScheduler()
scheduler.add_job(
    func=scan_and_add_missing_shows,
    trigger="interval",
    minutes=load_settings().get('storage_scan_interval_minutes', 60),
    id='storage_scan',
    replace_existing=True,
    coalesce=True,
    max_instances=1
)
scheduler.add_job(func=sync_radarr_movies, trigger="interval", hours=1)
scheduler.add_job(func=run_scheduled_episode_updates, trigger="interval", minutes=1, id='scheduled_episode_updates', replace_existing=True, max_instances=1)
scheduler.start()

@app.route('/cached_image/<filename>')
def cached_image(filename):
    return send_from_directory(IMAGE_CACHE_DIR, filename)

@app.route('/discover')
def discover_page():
    return render_template('discover.html')

@app.route('/api/show-schedules')
def show_schedules():
    ts = load_timestamps()
    schedules = [{
        'show_id': show.get('id'),
        'title': show.get('title', 'Untitled'),
        'status': show.get('status', 'Continuing'),
        'update_time': show.get('episode_update_time') or '',
        'frequency': show.get('episode_update_frequency', 'daily'),
        'weekday': show.get('episode_update_weekday', 0),
        'month_day': show.get('episode_update_month_day', 1),
        'last_run': (ts.get(str(show.get('id')), {}).get('episode_update_last_run') or ''),
        'last_run_result': (ts.get(str(show.get('id')), {}).get('last_run_result') or None),
    } for show in load_data()]
    schedules.sort(key=lambda item: (not bool(item['update_time']), item['update_time'], item['title'].casefold()))
    return jsonify({'success': True, 'schedules': schedules})


@app.route('/api/show-schedules/bulk', methods=['POST'])
def update_all_show_schedules():
    """Save per-show frequencies and auto-fill missing schedule values."""
    payload = request.get_json(silent=True) or {}
    requested = payload.get('schedules')
    if not isinstance(requested, list):
        return jsonify({'success': False, 'message': 'Schedule choices are required'}), 400
    frequency_by_id = {}
    for item in requested:
        try:
            show_id = int(item.get('show_id'))
        except (TypeError, ValueError, AttributeError):
            continue
        frequency = str(item.get('frequency', 'daily')).strip().lower()
        if frequency in {'none', 'daily', 'weekly', 'monthly'}:
            frequency_by_id[show_id] = frequency

    shows = load_data()
    settings = load_settings()
    try:
        start_minutes = datetime.strptime(settings.get('auto_schedule_start_time', '01:00'), '%H:%M').hour * 60 + datetime.strptime(settings.get('auto_schedule_start_time', '01:00'), '%H:%M').minute
        end_minutes = datetime.strptime(settings.get('auto_schedule_end_time', '23:00'), '%H:%M').hour * 60 + datetime.strptime(settings.get('auto_schedule_end_time', '23:00'), '%H:%M').minute
        if start_minutes >= end_minutes:
            raise ValueError
    except (TypeError, ValueError):
        start_minutes, end_minutes = 60, 23 * 60
    active_targets = [
        show for show in shows
        if show.get('id') in frequency_by_id
        and frequency_by_id[show.get('id')] != 'none'
    ]
    active_target_index = {show.get('id'): index for index, show in enumerate(active_targets)}
    active_target_span = max(1, len(active_targets) - 1)
    updated = 0
    for show in shows:
        show_id = show.get('id')
        if show_id not in frequency_by_id:
            continue
        slot_index = active_target_index.get(show_id, 0)
        if frequency_by_id[show_id] == 'none':
            show['episode_update_time'] = ''
            show['episode_update_frequency'] = 'daily'
            updated += 1
            continue
        show['episode_update_frequency'] = frequency_by_id[show_id]
        # Reschedule every active show evenly across the configured window.
        slot_minutes = round(start_minutes + ((end_minutes - start_minutes) * slot_index / active_target_span))
        show['episode_update_time'] = f'{(slot_minutes // 60) % 24:02d}:{slot_minutes % 60:02d}'
        if show['episode_update_frequency'] == 'weekly':
            show['episode_update_weekday'] = slot_index % 7
        if show['episode_update_frequency'] == 'monthly':
            show['episode_update_month_day'] = (slot_index % 28) + 1
        updated += 1
    save_data(shows)
    return jsonify({'success': True, 'updated': updated})


@app.route('/api/show/<int:show_id>/episodes/run_scheduled', methods=['POST'])
def run_scheduled_now(show_id):
    """Manually trigger a scheduled episode update for a single show."""
    shows = load_data()
    show = next((s for s in shows if s['id'] == show_id), None)
    if not show:
        return jsonify({'success': False, 'message': 'Show not found'}), 404
    now = datetime.now()
    added, updated, error = run_show_episode_update(show, now)
    if error:
        set_show_ts(show_id, last_run_result={'timestamp': now.isoformat(), 'added': 0, 'updated': 0, 'error': error})
        save_data(shows)
        return jsonify({'success': False, 'message': error}), 502
    set_show_ts(show_id, episode_update_last_run=now.date().isoformat())
    save_data(shows)
    return jsonify({
        'success': True,
        'message': f'{added} added, {updated} updated.',
        'added': added,
        'updated': updated,
        'timestamp': now.isoformat(),
    })

@app.route('/api/show/<int:show_id>/episodes/clear_run_stats', methods=['POST'])
def clear_run_stats(show_id):
    shows = load_data()
    show = next((s for s in shows if s['id'] == show_id), None)
    if not show:
        return jsonify({'success': False, 'message': 'Show not found'}), 404
    ts = load_timestamps()
    entry = ts.get(str(show_id), {})
    entry.pop('last_run_result', None)
    entry.pop('episode_update_last_run', None)
    ts[str(show_id)] = entry
    save_timestamps(ts)
    return jsonify({'success': True})

@app.route('/api/shows/clear_all_run_stats', methods=['POST'])
def clear_all_run_stats():
    ts = load_timestamps()
    for key in list(ts.keys()):
        ts[key].pop('last_run_result', None)
        ts[key].pop('episode_update_last_run', None)
    save_timestamps(ts)
    return jsonify({'success': True})

@app.route('/api/discover/search')
def discover_search():
    query = request.args.get('q', '').strip()
    media_type = request.args.get('type', 'all').strip().lower()
    preset = request.args.get('preset', 'search').strip().lower()
    region = request.args.get('region', 'none').strip().lower()
    try:
        result_limit = max(1, min(100, int(request.args.get('limit', 20))))
    except (TypeError, ValueError):
        result_limit = 20
    try:
        result_page = max(1, int(request.args.get('page', 1)))
    except (TypeError, ValueError):
        result_page = 1
    if media_type not in {'all', 'movie', 'tv'}:
        return jsonify({'success': False, 'message': 'Invalid content type'}), 400
    if preset not in {'search', 'popular', 'top_rated', 'trending_month', 'recent_releases'}:
        return jsonify({'success': False, 'message': 'Invalid discovery mode'}), 400
    if region not in {'none', 'hollywood', 'bollywood', 'tamil_telugu', 'anime', 'korean', 'chinese', 'japanese_live', 'animation', 'documentary_reality'}:
        return jsonify({'success': False, 'message': 'Invalid region'}), 400
    if preset == 'search' and not query:
        return jsonify({'success': False, 'message': 'Enter a title or choose a discovery mode'}), 400

    # Language/genre filter derived from region param
    region_lang_map = {
        'none':        [],
        'hollywood':   [{'with_original_language': 'en'}],
        'bollywood':   [{'with_original_language': 'hi'}],
        'tamil_telugu':[{'with_original_language': 'ta'}, {'with_original_language': 'te'}],
        'anime':       [{'with_original_language': 'ja', 'with_genres': '16'}],
        'korean':      [{'with_original_language': 'ko'}],
        'chinese':     [{'with_original_language': 'zh'}],
        'japanese_live':[{'with_original_language': 'ja', 'without_genres': '16'}],
        'animation':   [{'with_genres': '16', 'without_original_language': 'ja'}],
        'documentary_reality': [{'with_genres': '99'}, {'with_genres': '10764'}],
    }
    region_filters = region_lang_map[region]  # list of extra param dicts (1 or 2 for tamil_telugu)

    def make_sources(endpoint_movie, endpoint_tv, base_params):
        """Expand endpoints × region filters into a sources list."""
        srcs = []
        filters = region_filters if region_filters else [{}]
        if media_type in ('all', 'movie'):
            for rf in filters:
                srcs.append((endpoint_movie, {**base_params, **rf}, 'movie'))
        if media_type in ('all', 'tv'):
            for rf in filters:
                srcs.append((endpoint_tv, {**base_params, **rf}, 'tv'))
        return srcs

    if preset == 'search':
        # Search ignores region (TMDb search doesn't support language filter meaningfully)
        sources = [('search/multi' if media_type == 'all' else f'search/{media_type}', {}, None)]
    elif preset == 'trending_month':
        today = datetime.now().date()
        month_start = today.replace(day=1).isoformat()
        month_end   = today.isoformat()
        sources = make_sources(
            'discover/movie',
            'discover/tv',
            {'sort_by': 'popularity.desc',
             'primary_release_date.gte': month_start, 'primary_release_date.lte': month_end,
             'first_air_date.gte': month_start,        'first_air_date.lte': month_end}
        )
        # movie and tv need different date keys — rebuild properly
        sources = []
        filters = region_filters if region_filters else [{}]
        if media_type in ('all', 'movie'):
            for rf in filters:
                sources.append(('discover/movie', {'sort_by': 'popularity.desc',
                    'primary_release_date.gte': month_start,
                    'primary_release_date.lte': month_end, **rf}, 'movie'))
        if media_type in ('all', 'tv'):
            for rf in filters:
                sources.append(('discover/tv', {'sort_by': 'popularity.desc',
                    'first_air_date.gte': month_start,
                    'first_air_date.lte': month_end, **rf}, 'tv'))
    elif preset == 'recent_releases':
        sources = []
        filters = region_filters if region_filters else [{}]
        if media_type in ('all', 'movie'):
            for rf in filters:
                sources.append(('discover/movie', {'sort_by': 'primary_release_date.desc', **rf}, 'movie'))
        if media_type in ('all', 'tv'):
            for rf in filters:
                sources.append(('discover/tv', {'sort_by': 'first_air_date.desc', **rf}, 'tv'))
    elif preset == 'top_rated':
        if region == 'none':
            # Use dedicated top_rated endpoints when no region filter
            if media_type == 'all':
                sources = [('movie/top_rated', {}, 'movie'), ('tv/top_rated', {}, 'tv')]
            else:
                sources = [(f'{media_type}/top_rated', {}, media_type)]
        else:
            sources = make_sources('discover/movie', 'discover/tv',
                                   {'sort_by': 'vote_average.desc', 'vote_count.gte': '100'})
    else:  # popular
        sources = make_sources('discover/movie', 'discover/tv', {'sort_by': 'popularity.desc'})

    results = {'results': [], 'total_results': 0, 'total_pages': 0}
    start_index = (result_page - 1) * result_limit
    source_page_size = 20 * len(sources)
    first_tmdb_page = (start_index // source_page_size) + 1
    last_tmdb_page = ((start_index + result_limit - 1) // source_page_size) + 1
    for tmdb_page in range(first_tmdb_page, last_tmdb_page + 1):
        for endpoint, source_params, forced_type in sources:
            params = {
                **source_params,
                'include_adult': 'false',
                'language': 'en-US',
                'page': tmdb_page
            }
            if preset == 'search':
                params['query'] = query
            page_results, error = tmdb_request(endpoint, params)
            if error:
                return jsonify({'success': False, 'message': error}), 502
            filtered_page_results = []
            for item in page_results.get('results', []):
                # Keep Japanese-original animation in the dedicated Anime filter.
                if region == 'animation' and item.get('original_language') == 'ja':
                    continue
                if forced_type and 'media_type' not in item:
                    item['media_type'] = forced_type
                filtered_page_results.append(item)
            results['results'].extend(filtered_page_results)
            if tmdb_page == first_tmdb_page:
                results['total_results'] += page_results.get('total_results', 0)
            results['total_pages'] = max(results['total_pages'], page_results.get('total_pages', 0))

    if preset == 'top_rated':
        results['results'].sort(key=lambda item: float(item.get('vote_average') or 0), reverse=True)
    elif preset in {'popular', 'trending_month', 'recent_releases'}:
        if preset == 'recent_releases':
            results['results'].sort(key=lambda item: item.get('release_date') or item.get('first_air_date') or '', reverse=True)
        else:
            results['results'].sort(key=lambda item: float(item.get('popularity') or 0), reverse=True)

    local_start = start_index % source_page_size
    page_items = results['results'][local_start:local_start + result_limit]

    normalized = []
    existing_catalog = {'movie': load_movies(), 'tv': load_data()}
    existing_tmdb_ids = {
        item_type: {str(item.get('tmdb_id')) for item in items if item.get('tmdb_id') is not None}
        for item_type, items in existing_catalog.items()
    }
    existing_match_keys = {
        item_type: {catalog_match_key(item.get('title'), item.get('year')) for item in items}
        for item_type, items in existing_catalog.items()
    }
    existing_tvmaze_ids = {
        str(item.get('tmdb_id')): item.get('tvmaze_id')
        for item in existing_catalog['tv']
        if item.get('tmdb_id') is not None and item.get('tvmaze_id')
    }
    existing_tvmaze_match_ids = {
        catalog_match_key(item.get('title'), item.get('year')): item.get('tvmaze_id')
        for item in existing_catalog['tv']
        if item.get('tvmaze_id')
    }
    for item in page_items:
        item_type = item.get('media_type', media_type)
        if item_type not in {'movie', 'tv'}:
            continue
        title = item.get('title') if item_type == 'movie' else item.get('name')
        release_date = item.get('release_date') if item_type == 'movie' else item.get('first_air_date')
        normalized_year = tmdb_year(release_date)
        catalog_key = catalog_match_key(title, normalized_year)
        normalized.append({
            'tmdb_id': item.get('id'),
            'media_type': item_type,
            'title': title or 'Untitled',
            'year': normalized_year,
            'release_date': release_date or '',
            'overview': item.get('overview') or 'No overview available.',
            'poster_url': tmdb_poster_url(item.get('poster_path')),
            'rating': round(float(item.get('vote_average') or 0), 1),
            'already_added': str(item.get('id')) in existing_tmdb_ids[item_type] or catalog_key in existing_match_keys[item_type],
            'tvmaze_id': (existing_tvmaze_ids.get(str(item.get('id'))) or existing_tvmaze_match_ids.get(catalog_key)) if item_type == 'tv' else None
        })

    return jsonify({
        'success': True,
        'results': normalized,
        'page': result_page,
        'total_results': results['total_results'],
        'has_previous': result_page > 1,
        'has_next': result_page * result_limit < results['total_results']
    })

@app.route('/api/discover/add', methods=['POST'])
def discover_add():
    payload = request.json or {}
    media_type = payload.get('media_type')
    tmdb_id = payload.get('tmdb_id')
    if media_type not in {'movie', 'tv'} or not str(tmdb_id).isdigit():
        return jsonify({'success': False, 'message': 'A valid movie or TV result is required'}), 400

    details, error = tmdb_request(f'{media_type}/{int(tmdb_id)}', {'language': 'en-US'})
    if error:
        return jsonify({'success': False, 'message': error}), 502

    title = (details.get('title') if media_type == 'movie' else details.get('name')) or 'Untitled'
    year = tmdb_year(details.get('release_date') if media_type == 'movie' else details.get('first_air_date'))
    poster = tmdb_poster_url(details.get('poster_path'))
    tmdb_rating = round(float(details.get('vote_average') or 0), 1)
    rating = tmdb_five_star_rating(tmdb_rating)
    external_ids = {'tmdb': int(tmdb_id)}
    if details.get('imdb_id'):
        external_ids['imdb'] = details['imdb_id']

    if media_type == 'movie':
        movies = load_movies()
        if any(
            str(movie.get('tmdb_id')) == str(tmdb_id)
            or catalog_match_key(movie.get('title'), movie.get('year')) == catalog_match_key(title, year)
            for movie in movies
        ):
            return jsonify({'success': False, 'message': f'{title} is already in your movies'}), 409
        movies.append({
            'id': max([movie.get('id', 0) for movie in movies], default=0) + 1,
            'tmdb_id': int(tmdb_id),
            'external_ids': external_ids,
            'radarr_id': None,
            'title': title,
            'year': year,
            'release_date': details.get('release_date') or '',
            'digital_release_date': tmdb_digital_release_date(tmdb_id),
            'overview': details.get('overview', ''),
            'cover_image': poster,
            'directory_path': '',
            'genres': tmdb_genres(details),
            'runtime': details.get('runtime'),
            'rating': rating,
            'tmdb_rating': tmdb_rating,
            'status': 'Released' if details.get('status') == 'Released' else 'Missing',
            'watched': False,
            'added_date': datetime.now().isoformat()
        })
        save_movies(movies)
    else:
        shows = load_data()
        if any(
            str(show.get('tmdb_id')) == str(tmdb_id)
            or catalog_match_key(show.get('title'), show.get('year')) == catalog_match_key(title, year)
            for show in shows
        ):
            return jsonify({'success': False, 'message': f'{title} is already in your shows'}), 409
        new_show = {
            'id': max([show.get('id', 0) for show in shows], default=0) + 1,
            'tmdb_id': int(tmdb_id),
            'external_ids': external_ids,
            'title': title,
            'year': year,
            'overview': details.get('overview', ''),
            'cover_image': poster,
            'directory_path': '',
            'genres': tmdb_genres(details),
            'rating': rating,
            'tmdb_rating': tmdb_rating,
            'status': 'Ended' if details.get('status') == 'Ended' else 'Continuing',
            'episodes': []
        }
        tvmaze_show, tvmaze_error = tvmaze_show_for_catalog_item(new_show)
        if tvmaze_show and not tvmaze_error:
            new_show['status'] = tvmaze_status(tvmaze_show)
            new_show['tvmaze_id'] = tvmaze_show.get('id')
        shows.append(new_show)
        save_data(shows)

    return jsonify({'success': True, 'message': f'{title} added to your {"movies" if media_type == "movie" else "shows"}'})


def resolve_tmdb_for_show(show, tvmaze_show):
    """
    Fetch TMDb details for a show.
    Uses show['tmdb_id'] if present; otherwise tries to find it via
    TVmaze externals (thetvdb → TMDb /find, then imdb → TMDb /find).
    Updates show['tmdb_id'] in-place if discovered.
    Returns (tmdb_details_dict_or_None, error_str_or_None).
    """
    tmdb_id = show.get('tmdb_id')

    # Try to discover tmdb_id via TVmaze externals if not already stored
    if not tmdb_id and tvmaze_show:
        externals = tvmaze_show.get('externals') or {}
        tvdb_id = externals.get('thetvdb')
        imdb_id = externals.get('imdb')

        if tvdb_id:
            result, err = tmdb_request('find/' + str(tvdb_id), {'external_source': 'tvdb_id'})
            if not err and result:
                tv_results = result.get('tv_results') or []
                if tv_results:
                    tmdb_id = tv_results[0].get('id')

        if not tmdb_id and imdb_id:
            result, err = tmdb_request('find/' + str(imdb_id), {'external_source': 'imdb_id'})
            if not err and result:
                tv_results = result.get('tv_results') or []
                if tv_results:
                    tmdb_id = tv_results[0].get('id')

        if tmdb_id:
            show['tmdb_id'] = tmdb_id

    if not tmdb_id:
        return None, None  # No TMDb ID available — not an error

    details, error = tmdb_request(f'tv/{int(tmdb_id)}', {'language': 'en-US'})
    return details, error


@app.route('/api/show/<int:show_id>/episodes/update', methods=['POST'])
def update_show_episodes(show_id):
    shows = load_data()
    show = next((item for item in shows if item.get('id') == show_id), None)
    if not show:
        return jsonify({'success': False, 'message': 'Show not found'}), 404

    tvmaze_show, error = tvmaze_show_for_catalog_item(show)
    if error:
        return jsonify({'success': False, 'message': error}), 502
    episodes, error = tvmaze_request(f"shows/{tvmaze_show['id']}/episodes", {'specials': 1})
    if error:
        return jsonify({'success': False, 'message': error}), 502

    added, updated = merge_tvmaze_episodes(show, tvmaze_show, episodes)
    show['status'] = tvmaze_status(tvmaze_show)
    tmdb_details, tmdb_error = resolve_tmdb_for_show(show, tvmaze_show)
    if tmdb_details and not tmdb_error:
        tmdb_image = tmdb_poster_url(tmdb_details.get('poster_path'))
        if tmdb_image:
            show['cover_image'] = tmdb_image
        tmdb_score = round(float(tmdb_details.get('vote_average') or 0), 1)
        if tmdb_score > 0:
            show['tmdb_rating'] = tmdb_score
    else:
        # Fall back to TVmaze poster if no cover yet
        if not show.get('cover_image'):
            tvmaze_img = (tvmaze_show.get('image') or {})
            tvmaze_poster = tvmaze_img.get('original') or tvmaze_img.get('medium')
            if tvmaze_poster:
                show['cover_image'] = tvmaze_poster
    show['episode_source'] = 'tvmaze'
    set_show_ts(show['id'], episodes_updated_at=datetime.now().isoformat())
    save_data(shows)
    return jsonify({
        'success': True,
        'message': f'Updated {show["title"]}: {added} episodes added, {updated} updated.',
        'added': added,
        'updated': updated,
        'show': {
            'id':          show['id'],
            'title':       show.get('title', ''),
            'year':        show.get('year', ''),
            'cover_image': show.get('cover_image', ''),
            'status':      show.get('status', 'Continuing'),
            'rating':      show.get('rating'),
            'tmdb_rating': show.get('tmdb_rating'),
        }
    })

@app.route('/')
def index():
    settings = load_settings()
    sort_by = request.args.get('sort_by') or settings.get('default_shows_sort', 'title')
    order = request.args.get('order') or settings.get('default_shows_order', 'asc')
    query = request.args.get('query')

    shows = load_data()
    if migrate_tmdb_ratings(shows):
        save_data(shows)

    # Filter shows based on query
    if query:
        shows = [show for show in shows if query.lower() in show['title'].lower()]

    # Calculate watched and total episodes, and last episode added date
    for show in shows:
        show['cover_image'] = get_cached_image(show.get('cover_image', ''))
        today = datetime.now().date().isoformat()
        released_episode_list = [
            episode for episode in show.get('episodes', [])
            if not episode.get('air_date') or str(episode.get('air_date')) <= today
        ]
        show['watched_count'] = sum(1 for episode in released_episode_list if episode.get('watched'))
        show['watched_total_count'] = sum(1 for episode in show.get('episodes', []) if episode.get('watched'))
        show['total_count'] = len(show.get('episodes', []))
        show['released_count'] = len(released_episode_list)
        
        # Display the latest aired date from TVmaze; this remains useful for
        # shows imported before the local added_date field existed.
        episodes = show.get('episodes', [])
        if episodes:
            aired_dates = []
            for episode in episodes:
                air_date = episode.get('air_date')
                if air_date:
                    try:
                        parsed = datetime.strptime(str(air_date), '%Y-%m-%d').date()
                        if parsed <= datetime.now().date():
                            aired_dates.append(parsed)
                    except (TypeError, ValueError):
                        pass

            if aired_dates:
                show['last_episode_added'] = max(aired_dates).strftime('%d %B, %Y')
            else:
                show['last_episode_added'] = 'No aired episodes'
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
        now_local = datetime.now(BANGLADESH_TZ).replace(tzinfo=None)
        def get_last_episode_time(show):
            episodes = show.get('episodes', [])
            if not episodes:
                return (0, float('-inf'))

            timestamps = []
            for episode in episodes:
                local_air_datetime = None

                # Priority 1: use air_datetime (UTC airstamp) → convert to Bangladesh.
                # This is the authoritative source — air_date alone is the US-local
                # date from TVmaze and can be a day behind the Bangladesh date.
                air_datetime_str = episode.get('air_datetime') or ''
                if air_datetime_str:
                    try:
                        parsed_utc = datetime.fromisoformat(
                            str(air_datetime_str).replace('Z', '+00:00')
                        )
                        if parsed_utc.tzinfo is not None:
                            local_air_datetime = parsed_utc.astimezone(BANGLADESH_TZ).replace(tzinfo=None)
                    except (TypeError, ValueError):
                        pass

                # Priority 2: fall back to combining air_date + airtime (both already
                # stored as Bangladesh values for newer episodes, or date-only).
                if local_air_datetime is None:
                    air_date_str = episode.get('air_date')
                    airtime_str = episode.get('airtime') or ''
                    if air_date_str and airtime_str:
                        try:
                            local_air_datetime = datetime.strptime(
                                f'{air_date_str} {airtime_str}', '%Y-%m-%d %H:%M'
                            )
                        except (TypeError, ValueError):
                            pass

                if local_air_datetime is not None:
                    if local_air_datetime > now_local:
                        continue
                    timestamps.append((0, local_air_datetime.timestamp()))
                    continue

                # Priority 3: date-only fallback
                air_date_str = episode.get('air_date')
                if air_date_str:
                    try:
                        local_air_date = datetime.strptime(str(air_date_str), '%Y-%m-%d')
                        if local_air_date.date() > now_local.date():
                            continue
                        timestamps.append((0, local_air_date.timestamp()))
                    except (TypeError, ValueError):
                        timestamps.append((1, str(air_date_str)))
                elif episode.get('id') is not None:
                    timestamps.append((0, int(episode['id'])))
            return max(timestamps, default=(0, float('-inf')))
        
        shows.sort(key=get_last_episode_time, reverse=(order == 'desc'))

    elif sort_by == 'next_episode': # Sort by next upcoming episode after last released
        now_local = datetime.now(BANGLADESH_TZ).replace(tzinfo=None)
        def get_next_episode_time(show):
            episodes = show.get('episodes', [])
            future_timestamps = []
            for episode in episodes:
                local_air_datetime = None

                air_datetime_str = episode.get('air_datetime') or ''
                if air_datetime_str:
                    try:
                        parsed_utc = datetime.fromisoformat(
                            str(air_datetime_str).replace('Z', '+00:00')
                        )
                        if parsed_utc.tzinfo is not None:
                            local_air_datetime = parsed_utc.astimezone(BANGLADESH_TZ).replace(tzinfo=None)
                    except (TypeError, ValueError):
                        pass

                if local_air_datetime is None:
                    air_date_str = episode.get('air_date')
                    airtime_str = episode.get('airtime') or ''
                    if air_date_str and airtime_str:
                        try:
                            local_air_datetime = datetime.strptime(
                                f'{air_date_str} {airtime_str}', '%Y-%m-%d %H:%M'
                            )
                        except (TypeError, ValueError):
                            pass

                if local_air_datetime is not None:
                    if local_air_datetime > now_local:
                        future_timestamps.append((0, local_air_datetime.timestamp()))
                    continue

                air_date_str = episode.get('air_date')
                if air_date_str:
                    try:
                        local_air_date = datetime.strptime(str(air_date_str), '%Y-%m-%d')
                        if local_air_date.date() > now_local.date():
                            future_timestamps.append((0, local_air_date.timestamp()))
                    except (TypeError, ValueError):
                        pass

            # Shows with no upcoming episodes sort to the end
            return min(future_timestamps, default=(1, float('inf')))

        shows.sort(key=get_next_episode_time, reverse=(order == 'desc'))

    next_order = 'desc' if order == 'asc' else 'asc'

    return render_template('index.html', shows=shows, sort_by=sort_by, order=order, next_order=next_order, query=query)

@app.route('/movies')
def movies_page():
    settings = load_settings()
    sort_by = request.args.get('sort_by') or settings.get('default_movies_sort', 'title')
    order = request.args.get('order') or settings.get('default_movies_order', 'asc')
    query = request.args.get('query')

    movies = load_movies()
    if migrate_tmdb_ratings(movies):
        save_movies(movies)

    # Filter movies based on query
    if query:
        movies = [movie for movie in movies if query.lower() in movie['title'].lower()]

    # Cache cover images
    for movie in movies:
        movie['cover_image'] = get_cached_image(movie.get('cover_image', ''))

    # Sort movies
    if sort_by == 'title':
        movies.sort(key=lambda x: x['title'].lower(), reverse=(order == 'desc'))
    elif sort_by == 'year':
        movies.sort(
            key=lambda x: (
                int(x.get('year')) if str(x.get('year', '')).isdigit() else 0,
                str(x.get('release_date') or '')
            ),
            reverse=(order == 'desc')
        )
    elif sort_by == 'rating':
        movies.sort(key=lambda x: float(x.get('rating', -1)) if x.get('rating') is not None and str(x.get('rating')).replace('.', '', 1).isdigit() else -1, reverse=(order == 'desc'))
    elif sort_by == 'added':
        movies.sort(key=lambda x: x['id'], reverse=(order == 'desc'))

    next_order = 'desc' if order == 'asc' else 'asc'

    return render_template('movies.html', movies=movies, sort_by=sort_by, order=order, next_order=next_order, query=query, radarr_url=settings.get('radarr_url', 'http://192.168.0.101:7878').rstrip('/'))

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
        show['lock_status'] = request.form.get('lock_status') == '1'
        show['sonarr_url'] = request.form.get('sonarr_url', '')
        show['episode_file_pattern'] = request.form.get('episode_file_pattern', '').strip()
        show['scan_mode'] = request.form.get('scan_mode', 'sxxexx')
        save_data(shows)
        query = request.args.get('query', '').strip()
        if request.headers.get('Accept') == 'application/json':
            return jsonify({
                'success': True,
                'show': {
                    'id':          show['id'],
                    'title':       show['title'],
                    'year':        show.get('year', ''),
                    'cover_image': show.get('cover_image', ''),
                    'status':      show.get('status', 'Continuing'),
                    'rating':      show.get('rating'),
                }
            })
        return redirect(url_for('index', query=query) if query else url_for('index'))
    else:
        sort_episode_list(show)
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
        return jsonify({'success': False, 'message': 'Show not found'}), 404
    episode = next((e for e in show['episodes'] if e['id'] == episode_id), None)
    if not episode:
        return jsonify({'success': False, 'message': 'Episode not found'}), 404
    if request.method == 'POST':
        episode['title'] = request.form['title']
        save_data(shows)
        return jsonify({'success': True})
    else:
        return jsonify(episode)

@app.route('/delete_episode/<int:show_id>/<int:episode_id>')
def delete_episode(show_id, episode_id):
    shows = load_data()
    show = next((s for s in shows if s['id'] == show_id), None)
    if show:
        show['episodes'] = [e for e in show['episodes'] if e['id'] != episode_id]
        save_data(shows)
        return jsonify({'success': True})
    return jsonify({'success': False, 'message': 'Show not found'}), 404

@app.route('/update_episode_sort/<int:show_id>', methods=['POST'])
def update_episode_sort(show_id):
    data = request.get_json()
    sort_type = data.get('sort_type', 'default') # 'alphabetical' or 'default'
    order = data.get('order', 'asc') # 'asc' or 'desc'
    
    shows = load_data()
    show = next((s for s in shows if s['id'] == show_id), None)
    
    if not show:
        return jsonify({'success': False, 'message': 'Show not found'}), 404
        
    show['episode_sort_type'] = sort_type
    show['episode_sort_order'] = order
    
    if sort_type not in {'alphabetical', 'default'}:
        sort_type = 'default'
        show['episode_sort_type'] = sort_type
    if order not in {'asc', 'desc'}:
        order = 'asc'
        show['episode_sort_order'] = order
    sort_episode_list(show)
        
    save_data(shows)
    return jsonify({'success': True, 'episodes': show['episodes']})

@app.route('/api/show/<int:show_id>/hide_future_episodes', methods=['POST'])
def toggle_hide_future_episodes(show_id):
    shows = load_data()
    show = next((s for s in shows if s['id'] == show_id), None)
    if not show:
        return jsonify({'success': False, 'message': 'Show not found'}), 404
    show['hide_future_episodes'] = not bool(show.get('hide_future_episodes', False))
    save_data(shows)
    return jsonify({'success': True, 'hide_future_episodes': show['hide_future_episodes']})

@app.route('/api/show/<int:show_id>/archive', methods=['POST'])
def toggle_archive_show(show_id):
    shows = load_data()
    show = next((s for s in shows if s['id'] == show_id), None)
    if not show:
        return jsonify({'success': False, 'message': 'Show not found'}), 404
    show['archived'] = not bool(show.get('archived', False))
    save_data(shows)
    return jsonify({'success': True, 'archived': show['archived']})

@app.route('/toggle_watched/<int:show_id>/<int:episode_id>')
def toggle_watched(show_id, episode_id):
    shows = load_data()
    show = next((s for s in shows if s['id'] == show_id), None)
    if show:
        episode = next((e for e in show['episodes'] if e['id'] == episode_id), None)
        if episode:
            episode['watched'] = not episode['watched']
            save_data(shows)
            return jsonify({'success': True, 'watched': episode['watched']})
    return jsonify({'success': False, 'message': 'Episode not found'}), 404

@app.route('/api/show/<int:show_id>/episodes/watched', methods=['POST'])
def set_all_episodes_watched(show_id):
    data = request.get_json() or {}
    watched = bool(data.get('watched'))
    shows = load_data()
    show = next((item for item in shows if item.get('id') == show_id), None)
    if not show:
        return jsonify({'success': False, 'message': 'Show not found'}), 404
    for episode in show.get('episodes', []):
        episode['watched'] = watched
    save_data(shows)
    return jsonify({'success': True, 'episodes': show.get('episodes', [])})

@app.route('/scan_manual/<int:show_id>')
def scan_manual(show_id):
    scan_and_update_episodes()
    return jsonify({'success': True})

@app.route('/scan_all')
def scan_all():
    scan_and_update_episodes()
    return jsonify({'success': True})

@app.route('/scan_and_add_all')
def scan_and_add_all():
    """Manual trigger for combined scan function"""
    scan_and_add_missing_shows()
    return jsonify({'success': True})

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

@app.route('/api/episode_file_check/<int:show_id>')
def api_episode_file_check(show_id):
    """
    Scan the show's directory_path for video files and return keys found.
    - sxxexx mode (default): returns SxxExx tokens e.g. ["S01E01", ...]
    - date mode: returns YYYY-MM-DD strings e.g. ["2026-09-04", ...]
    - title mode: returns normalised filenames (no ext)
    Also returns the scan_mode so the client knows how to match.
    """
    shows = load_data()
    show = next((s for s in shows if s['id'] == show_id), None)
    if not show:
        return jsonify({'found': [], 'has_directory': False, 'scan_mode': 'sxxexx'}), 404

    dir_path = show.get('directory_path', '')
    if not dir_path or not os.path.isdir(dir_path):
        return jsonify({'found': [], 'has_directory': False, 'scan_mode': 'sxxexx'})

    scan_mode = show.get('scan_mode', 'sxxexx')
    VIDEO_EXTS = {'.mp4', '.mkv', '.avi', '.mov', '.webm', '.m4v', '.ts'}
    found = set()

    if scan_mode == 'date':
        date_pat = re.compile(r'(\d{4}-\d{2}-\d{2})')
        for root, _, files in os.walk(dir_path):
            for filename in files:
                if os.path.splitext(filename)[1].lower() not in VIDEO_EXTS:
                    continue
                m = date_pat.search(filename)
                if m:
                    found.add(m.group(1))

    elif scan_mode == 'title':
        for root, _, files in os.walk(dir_path):
            for filename in files:
                name, ext = os.path.splitext(filename)
                if ext.lower() in VIDEO_EXTS:
                    found.add(name)

    else:  # sxxexx (default or custom pattern)
        custom_pattern = show.get('episode_file_pattern', '').strip()
        if custom_pattern:
            try:
                re.compile(custom_pattern)
                pattern = custom_pattern
            except re.error:
                pattern = r'[Ss](\d{1,2})[Ee](\d{1,2})'
        else:
            pattern = r'[Ss](\d{1,2})[Ee](\d{1,2})'

        for root, _, files in os.walk(dir_path):
            for filename in files:
                if os.path.splitext(filename)[1].lower() not in VIDEO_EXTS:
                    continue
                for m in re.finditer(pattern, filename, re.IGNORECASE):
                    if m.lastindex and m.lastindex >= 2:
                        found.add(f"S{int(m.group(1)):02d}E{int(m.group(2)):02d}")
                    elif m.lastindex == 1:
                        found.add(m.group(1).upper())
                    else:
                        found.add(m.group(0).upper())

    return jsonify({'found': sorted(found), 'has_directory': True, 'scan_mode': scan_mode})


@app.route('/api/scan_missing_episodes')
def api_scan_missing_episodes():
    shows = load_data()
    missing_episodes = []
    
    for show in shows:
        dir_path = show.get('directory_path')
        files_on_disk = set()
        
        # Only try to scan files if the directory exists
        if dir_path and os.path.isdir(dir_path):
            for root, _, files in os.walk(dir_path):
                for filename in files:
                    name, ext = os.path.splitext(filename)
                    if ext.lower() in ['.mp4', '.mkv', '.avi', '.mov', '.webm']:
                        files_on_disk.add(name)
        
        # If the directory doesn't exist, files_on_disk remains empty,
        # so all unwatched episodes will be flagged as missing.
        for episode in show.get('episodes', []):
            if not episode.get('watched'):
                if episode['title'] not in files_on_disk:
                    missing_episodes.append({
                        'show_id': show['id'],
                        'show_title': show['title'],
                        'episode_id': episode['id'],
                        'episode_title': episode['title']
                    })
    
    return jsonify(missing_episodes)

@app.route('/api/delete_episode/<int:show_id>/<int:episode_id>', methods=['POST'])
def api_delete_episode(show_id, episode_id):
    shows = load_data()
    show = next((s for s in shows if s['id'] == show_id), None)
    if show:
        show['episodes'] = [e for e in show['episodes'] if e['id'] != episode_id]
        save_data(shows)
        return jsonify({'success': True})
    return jsonify({'success': False, 'message': 'Show not found'}), 404

@app.route('/api/check_episode/<int:show_id>/<int:episode_id>', methods=['POST'])
def api_check_episode(show_id, episode_id):
    shows = load_data()
    show = next((s for s in shows if s['id'] == show_id), None)
    if show:
        episode = next((e for e in show['episodes'] if e['id'] == episode_id), None)
        if episode:
            episode['watched'] = True
            save_data(shows)
            return jsonify({'success': True})
    return jsonify({'success': False, 'message': 'Episode not found'}), 404

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

@app.route('/api/settings', methods=['GET', 'POST'])
def api_settings():
    if request.method == 'POST':
        data = request.json or {}
        settings = load_settings()
        settings['tmdb_api_key'] = data.get('tmdb_api_key', settings.get('tmdb_api_key', ''))
        settings['default_shows_sort'] = data.get('default_shows_sort', settings.get('default_shows_sort', 'title'))
        settings['default_shows_order'] = data.get('default_shows_order', settings.get('default_shows_order', 'asc'))
        settings['default_movies_sort'] = data.get('default_movies_sort', settings.get('default_movies_sort', 'title'))
        settings['default_movies_order'] = data.get('default_movies_order', settings.get('default_movies_order', 'asc'))
        try:
            scan_interval = int(data.get('storage_scan_interval_minutes', settings.get('storage_scan_interval_minutes', 60)))
        except (TypeError, ValueError):
            scan_interval = 60
        settings['storage_scan_interval_minutes'] = max(1, min(scan_interval, 10080))
        settings['sonarr_url'] = data.get('sonarr_url', settings.get('sonarr_url', 'http://192.168.0.101:8989'))
        settings['sonarr_api_key'] = data.get('sonarr_api_key', settings.get('sonarr_api_key', ''))
        settings['root_shows_folder'] = data.get('root_shows_folder', settings.get('root_shows_folder', r"C:\Users\nahid\Downloads\@sonarr"))
        settings['radarr_url'] = data.get('radarr_url', settings.get('radarr_url', 'http://192.168.0.101:7878'))
        settings['radarr_api_key'] = data.get('radarr_api_key', settings.get('radarr_api_key', ''))
        settings['root_movies_folder'] = data.get('root_movies_folder', settings.get('root_movies_folder', r"C:\Users\nahid\Downloads\@radarr"))
        settings['episode_file_icons_enabled'] = bool(data.get('episode_file_icons_enabled', settings.get('episode_file_icons_enabled', True)))
        default_start = settings.get('auto_schedule_start_time', '01:00')
        default_end = settings.get('auto_schedule_end_time', '23:00')
        start_time = str(data.get('auto_schedule_start_time', default_start)).strip()
        end_time = str(data.get('auto_schedule_end_time', default_end)).strip()
        try:
            start_value = datetime.strptime(start_time, '%H:%M')
            end_value = datetime.strptime(end_time, '%H:%M')
            if start_value >= end_value:
                raise ValueError
        except (TypeError, ValueError):
            start_time, end_time = default_start, default_end
        settings['auto_schedule_start_time'] = start_time
        settings['auto_schedule_end_time'] = end_time
        try:
            discover_image_scale = float(data.get('discover_image_scale', settings.get('discover_image_scale', 1)))
        except (TypeError, ValueError):
            discover_image_scale = 1
        if discover_image_scale not in {0.75, 1, 1.25, 1.5, 2}:
            discover_image_scale = 1
        settings['discover_image_scale'] = discover_image_scale
        save_settings(settings)
        if 'scheduler' in globals():
            scheduler.reschedule_job(
                'storage_scan',
                trigger='interval',
                minutes=settings['storage_scan_interval_minutes']
            )
            scheduler.modify_job(
                'storage_scan',
                next_run_time=datetime.now() + timedelta(minutes=settings['storage_scan_interval_minutes'])
            )
        return jsonify({'success': True})
    return jsonify(load_settings())

@app.route('/api/test_sonarr', methods=['POST'])
def api_test_sonarr():
    data = request.json or {}
    sonarr_url = data.get('sonarr_url', '').rstrip('/')
    api_key = data.get('sonarr_api_key', '')
    
    if not sonarr_url or not api_key:
        return jsonify({'success': False, 'message': 'Sonarr URL and API Key are required'}), 400
        
    headers = {
        'X-Api-Key': api_key,
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.get(f"{sonarr_url}/api/v3/system/status", headers=headers, timeout=5)
        if response.status_code == 200:
            status_data = response.json()
            version = status_data.get('version', 'Unknown')
            return jsonify({'success': True, 'message': f'Connected! Sonarr version: {version}'})
        else:
            return jsonify({'success': False, 'message': f'Failed with status code {response.status_code}. Please check API key.'})
    except requests.exceptions.RequestException as e:
        return jsonify({'success': False, 'message': f'Connection failed: {str(e)}'})

@app.route('/api/update_sonarr_paths', methods=['POST'])
def api_update_sonarr_paths():
    settings = load_settings()
    sonarr_url = settings.get('sonarr_url', 'http://192.168.0.101:8989').rstrip('/')
    api_key = settings.get('sonarr_api_key', '')
    root_folder = settings.get('root_shows_folder', r"C:\Users\nahid\Downloads\@sonarr")
    
    if not api_key:
        return jsonify({'success': False, 'message': 'Sonarr API Key not configured in Settings'}), 400
        
    headers = {
        'X-Api-Key': api_key,
        'Content-Type': 'application/json'
    }
    
    try:
        # 1. Get all series from Sonarr
        series_response = requests.get(f"{sonarr_url}/api/v3/series", headers=headers, timeout=10)
        if series_response.status_code != 200:
            return jsonify({'success': False, 'message': f'Failed to get series: HTTP {series_response.status_code}'}), 500
            
        series_list = series_response.json()
        updated_count = 0
        failed_count = 0
        
        normalized_root = os.path.normpath(root_folder).lower()
        
        # Update in Sonarr
        for series in series_list:
            current_path = series.get('path', '')
            if not current_path:
                continue
                
            norm_curr_path = os.path.normpath(current_path)
            parent_dir = os.path.dirname(norm_curr_path)
            folder_name = os.path.basename(norm_curr_path)
            
            if parent_dir.lower() != normalized_root:
                new_path = os.path.normpath(os.path.join(root_folder, folder_name))
                series['path'] = new_path
                
                put_url = f"{sonarr_url}/api/v3/series/{series['id']}?moveFiles=false"
                put_response = requests.put(put_url, headers=headers, json=series, timeout=10)
                
                if put_response.status_code in [200, 202]:
                    updated_count += 1
                else:
                    failed_count += 1
                    
        # 2. Update local data.json
        shows = load_data()
        local_updated = False
        for show in shows:
            dir_path = show.get('directory_path')
            if dir_path:
                norm_dir = os.path.normpath(dir_path)
                parent_dir = os.path.dirname(norm_dir)
                folder_name = os.path.basename(norm_dir)
                if parent_dir.lower() != normalized_root:
                    show['directory_path'] = os.path.normpath(os.path.join(root_folder, folder_name))
                    local_updated = True
                    
        if local_updated:
            save_data(shows)
            
        return jsonify({
            'success': True, 
            'message': f'Updated {updated_count} show paths in Sonarr. (Failed: {failed_count})'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error migrating paths: {str(e)}'}), 500

@app.route('/api/reset_sonarr_episode', methods=['POST'])
def api_reset_sonarr_episode():
    data = request.json or {}
    show_id = data.get('show_id')
    episode_id = data.get('episode_id')
    
    if not show_id or not episode_id:
        return jsonify({'success': False, 'message': 'Missing show_id or episode_id'}), 400
        
    shows = load_data()
    show = next((s for s in shows if s['id'] == show_id), None)
    if not show:
        return jsonify({'success': False, 'message': 'Show not found in database'}), 404
        
    episode = next((e for e in show.get('episodes', []) if e['id'] == episode_id), None)
    if not episode:
        return jsonify({'success': False, 'message': 'Episode not found in database'}), 404
        
    episode_title = episode['title']
    
    # Parse season and episode number
    import re
    match = re.search(r'[sS](\d+)[eE](\d+)', episode_title)
    if not match:
        return jsonify({'success': False, 'message': f'Could not parse Season/Episode from: {episode_title}'}), 400
        
    season_num = int(match.group(1))
    episode_num = int(match.group(2))
    
    # Load settings for Sonarr URL and API key
    settings = load_settings()
    sonarr_url = settings.get('sonarr_url', 'http://192.168.0.101:8989').rstrip('/')
    api_key = settings.get('sonarr_api_key', '')
    
    if not api_key:
        return jsonify({'success': False, 'message': 'Sonarr API Key not configured in Settings'}), 400
        
    headers = {
        'X-Api-Key': api_key,
        'Content-Type': 'application/json'
    }
    
    # 1. Find the series in Sonarr
    show_dir = show.get('directory_path')
    series_id = None
    
    try:
        series_response = requests.get(f"{sonarr_url}/api/v3/series", headers=headers, timeout=10)
        if series_response.status_code != 200:
            return jsonify({'success': False, 'message': f'Sonarr API returned status code {series_response.status_code}'}), 500
            
        series_list = series_response.json()
        
        # Match by path
        if show_dir:
            normalized_show_dir = os.path.normpath(show_dir).lower()
            for s in series_list:
                s_path = s.get('path')
                if s_path and os.path.normpath(s_path).lower() == normalized_show_dir:
                    series_id = s.get('id')
                    break
                    
        # Fallback to match by title (case insensitive)
        if not series_id:
            show_title = show['title'].lower()
            for s in series_list:
                s_title = s.get('title', '').lower()
                if s_title == show_title:
                    series_id = s.get('id')
                    break
                    
        if not series_id:
            return jsonify({'success': False, 'message': f"Could not find series in Sonarr matching path: {show_dir} or title: {show['title']}"}), 404
            
        # 2. Get episodes for this series
        episodes_response = requests.get(f"{sonarr_url}/api/v3/episode?seriesId={series_id}", headers=headers, timeout=10)
        if episodes_response.status_code != 200:
            return jsonify({'success': False, 'message': 'Failed to fetch episodes from Sonarr'}), 500
            
        sonarr_episodes = episodes_response.json()
        target_episode = None
        for ep in sonarr_episodes:
            if ep.get('seasonNumber') == season_num and ep.get('episodeNumber') == episode_num:
                target_episode = ep
                break
                
        if not target_episode:
            return jsonify({'success': False, 'message': f'Episode Season {season_num} Episode {episode_num} not found in Sonarr'}), 404
            
        target_episode_id = target_episode['id']
        
        # 3. Update monitored status in Sonarr
        target_episode['monitored'] = False
        requests.put(f"{sonarr_url}/api/v3/episode/{target_episode_id}", headers=headers, json=target_episode, timeout=10)
        
        target_episode['monitored'] = True
        put_response = requests.put(f"{sonarr_url}/api/v3/episode/{target_episode_id}", headers=headers, json=target_episode, timeout=10)
        
        if put_response.status_code != 202 and put_response.status_code != 200:
            return jsonify({'success': False, 'message': f'Failed to update episode monitored status in Sonarr: {put_response.text}'}), 500
            
        # 4. Trigger a search for the episode in Sonarr
        command_payload = {
            'name': 'EpisodeSearch',
            'episodeIds': [target_episode_id]
        }
        command_response = requests.post(f"{sonarr_url}/api/v3/command", headers=headers, json=command_payload, timeout=10)
        if command_response.status_code not in [200, 201, 202]:
            return jsonify({'success': False, 'message': f'Episode monitored but failed to trigger search in Sonarr: {command_response.text}'}), 500
            
        return jsonify({'success': True, 'message': 'Episode successfully monitored and search triggered in Sonarr'})
        
    except requests.exceptions.RequestException as e:
        return jsonify({'success': False, 'message': f'Network error communicating with Sonarr: {str(e)}'}), 500

@app.route('/api/test_radarr', methods=['POST'])
def api_test_radarr():
    data = request.json or {}
    radarr_url = data.get('radarr_url', '').rstrip('/')
    api_key = data.get('radarr_api_key', '')

    if not radarr_url or not api_key:
        return jsonify({'success': False, 'message': 'Radarr URL and API Key are required'}), 400

    headers = {
        'X-Api-Key': api_key,
        'Content-Type': 'application/json'
    }

    try:
        response = requests.get(f"{radarr_url}/api/v3/system/status", headers=headers, timeout=5)
        if response.status_code == 200:
            status_data = response.json()
            version = status_data.get('version', 'Unknown')
            return jsonify({'success': True, 'message': f'Connected! Radarr version: {version}'})
        else:
            return jsonify({'success': False, 'message': f'Failed with status code {response.status_code}. Please check API key.'})
    except requests.exceptions.RequestException as e:
        return jsonify({'success': False, 'message': f'Connection failed: {str(e)}'})

@app.route('/api/radarr/sync', methods=['POST'])
def api_radarr_sync():
    added, updated, error = sync_radarr_movies()
    if error:
        return jsonify({'success': False, 'message': error}), 500
    return jsonify({'success': True, 'message': f'Radarr sync complete: {added} movies added, {updated} updated.'})

@app.route('/api/update_radarr_paths', methods=['POST'])
def api_update_radarr_paths():
    settings = load_settings()
    radarr_url = settings.get('radarr_url', 'http://192.168.0.101:7878').rstrip('/')
    api_key = settings.get('radarr_api_key', '')
    root_folder = settings.get('root_movies_folder', r"C:\Users\nahid\Downloads\@radarr")

    if not api_key:
        return jsonify({'success': False, 'message': 'Radarr API Key not configured in Settings'}), 400

    headers = {
        'X-Api-Key': api_key,
        'Content-Type': 'application/json'
    }

    try:
        # 1. Get all movies from Radarr
        movies_response = requests.get(f"{radarr_url}/api/v3/movie", headers=headers, timeout=10)
        if movies_response.status_code != 200:
            return jsonify({'success': False, 'message': f'Failed to get movies: HTTP {movies_response.status_code}'}), 500

        movies_list = movies_response.json()
        updated_count = 0
        failed_count = 0

        normalized_root = os.path.normpath(root_folder).lower()

        # Update in Radarr
        for movie in movies_list:
            current_path = movie.get('path', '')
            if not current_path:
                continue

            norm_curr_path = os.path.normpath(current_path)
            parent_dir = os.path.dirname(norm_curr_path)
            folder_name = os.path.basename(norm_curr_path)

            if parent_dir.lower() != normalized_root:
                new_path = os.path.normpath(os.path.join(root_folder, folder_name))
                movie['path'] = new_path

                put_url = f"{radarr_url}/api/v3/movie/{movie['id']}?moveFiles=false"
                put_response = requests.put(put_url, headers=headers, json=movie, timeout=10)

                if put_response.status_code in [200, 202]:
                    updated_count += 1
                else:
                    failed_count += 1

        # 2. Update local movies.json
        movies = load_movies()
        local_updated = False
        for movie in movies:
            dir_path = movie.get('directory_path')
            if dir_path:
                norm_dir = os.path.normpath(dir_path)
                parent_dir = os.path.dirname(norm_dir)
                folder_name = os.path.basename(norm_dir)
                if parent_dir.lower() != normalized_root:
                    movie['directory_path'] = os.path.normpath(os.path.join(root_folder, folder_name))
                    local_updated = True

        if local_updated:
            save_movies(movies)

        return jsonify({
            'success': True,
            'message': f'Updated {updated_count} movie paths in Radarr. (Failed: {failed_count})'
        })

    except Exception as e:
        return jsonify({'success': False, 'message': f'Error migrating paths: {str(e)}'}), 500

@app.route('/api/movie/<int:movie_id>', methods=['GET', 'POST'])
def api_movie(movie_id):
    movies = load_movies()
    movie = next((m for m in movies if m['id'] == movie_id), None)
    if not movie:
        return jsonify({'success': False, 'message': 'Movie not found'}), 404
    if request.method == 'POST':
        movie['title'] = request.form.get('title', movie['title'])
        movie['year'] = request.form.get('year', movie.get('year', ''))
        movie['release_date'] = request.form.get('release_date', movie.get('release_date', ''))
        movie['cover_image'] = request.form.get('cover_image', movie.get('cover_image', ''))
        movie['directory_path'] = request.form.get('directory_path', movie.get('directory_path', ''))
        movie['status'] = request.form.get('status', movie.get('status', ''))
        movie['rating'] = request.form.get('rating', movie.get('rating'))
        save_movies(movies)
        return jsonify({'success': True})
    return jsonify(movie)

@app.route('/api/movie/<int:movie_id>/refresh-metadata', methods=['POST'])
def refresh_movie_metadata(movie_id):
    movies = load_movies()
    movie = next((m for m in movies if m.get('id') == movie_id), None)
    if not movie:
        return jsonify({'success': False, 'message': 'Movie not found'}), 404
    if not movie.get('tmdb_id'):
        return jsonify({'success': False, 'message': 'This movie has no TMDb ID'}), 400

    details, error = tmdb_request(f"movie/{int(movie['tmdb_id'])}", {'language': 'en-US'})
    if error:
        return jsonify({'success': False, 'message': error}), 502

    release_date = details.get('release_date') or ''
    tmdb_rating = round(float(details.get('vote_average') or 0), 1)
    movie.update({
        'title': details.get('title') or movie.get('title', 'Untitled'),
        'year': tmdb_year(release_date),
        'release_date': release_date,
        'overview': details.get('overview') or '',
        'cover_image': tmdb_poster_url(details.get('poster_path')) or movie.get('cover_image', ''),
        'genres': tmdb_genres(details),
        'runtime': details.get('runtime'),
        'rating': tmdb_five_star_rating(tmdb_rating),
        'tmdb_rating': tmdb_rating,
        'status': 'Released' if details.get('status') == 'Released' else 'Missing'
    })
    movie['digital_release_date'] = tmdb_digital_release_date(movie['tmdb_id'])
    if details.get('imdb_id'):
        external_ids = movie.get('external_ids')
        if not isinstance(external_ids, dict):
            external_ids = {}
            movie['external_ids'] = external_ids
        external_ids['imdb'] = details['imdb_id']
    save_movies(movies)
    return jsonify({'success': True, 'movie': movie})

@app.route('/api/movies/add', methods=['POST'])
def api_movies_add():
    movies = load_movies()
    movies.append({
        'id': max([m.get('id', 0) for m in movies], default=0) + 1,
        'tmdb_id': None,
        'radarr_id': None,
        'title': request.form.get('title', '').strip(),
        'year': request.form.get('year', ''),
        'cover_image': request.form.get('cover_image', ''),
        'directory_path': request.form.get('directory_path', ''),
        'rating': request.form.get('rating', None),
        'status': request.form.get('status', 'Downloaded'),
        'watched': False,
        'added_date': datetime.now().isoformat()
    })
    save_movies(movies)
    return jsonify({'success': True})

@app.route('/api/movie/<int:movie_id>/watched', methods=['POST'])
def api_movie_watched(movie_id):
    movies = load_movies()
    movie = next((m for m in movies if m['id'] == movie_id), None)
    if movie:
        movie['watched'] = not movie.get('watched', False)
        save_movies(movies)
        return jsonify({'success': True, 'watched': movie['watched']})
    return jsonify({'success': False, 'message': 'Movie not found'}), 404

@app.route('/api/movie/<int:movie_id>/delete', methods=['POST'])
def api_movie_delete(movie_id):
    movies = load_movies()
    movies = [m for m in movies if m['id'] != movie_id]
    save_movies(movies)
    return jsonify({'success': True})

@app.route('/api/movie/<int:movie_id>/open_folder')
def api_movie_open_folder(movie_id):
    import subprocess
    import sys

    movies = load_movies()
    movie = next((m for m in movies if m['id'] == movie_id), None)

    if movie and movie.get('directory_path'):
        folder_path = movie['directory_path']
        try:
            if sys.platform == 'win32':
                subprocess.run(['explorer', folder_path], check=False)
            elif sys.platform == 'darwin':
                subprocess.run(['open', folder_path], check=True)
            else:
                subprocess.run(['xdg-open', folder_path], check=True)
            return jsonify({'success': True, 'message': 'Folder opened successfully'})
        except Exception as e:
            return jsonify({'success': False, 'message': f'Error: {str(e)}'})

    return jsonify({'success': False, 'message': 'Movie not found or no directory path'})

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True, port=5011)
