import os
import sqlite3
import feedparser
import requests
from bs4 import BeautifulSoup
from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = 'youtube-notifier-secret-key'
DB_FILE = 'channels.db'

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS channels (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT UNIQUE NOT NULL,
            channel_name TEXT,
            channel_id TEXT,
            thumbnail TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS videos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            channel_id TEXT,
            video_id TEXT UNIQUE,
            title TEXT,
            link TEXT,
            published TEXT,
            is_new INTEGER DEFAULT 1
        )
    ''')
    conn.commit()
    conn.close()

def extract_channel_id(url):
    url = url.strip()
    if not url.startswith('http'):
        if url.startswith('@'):
            url = f"https://www.youtube.com/{url}"
        else:
            url = f"https://www.youtube.com/@{url}"

    try:
        if 'channel/' in url:
            parts = url.split('channel/')
            channel_id = parts[1].split('/')[0].split('?')[0]
            return channel_id
        
        # Scrape page for RSS feed link or meta tag
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, 'html.parser')
            # Look for channel_id link rel="canonical" or RSS link
            rss_link = soup.find('link', rel='alternate', type='application/rss+xml')
            if rss_link and 'channel_id=' in rss_link.get('href', ''):
                return rss_link['href'].split('channel_id=')[1].split('&')[0]
            
            meta_cid = soup.find('meta', {'itemprop': 'channelId'})
            if meta_cid:
                return meta_cid.get('content')

            # Search in text for channelId
            for line in resp.text.splitlines():
                if '"channelId":"' in line:
                    start = line.find('"channelId":"') + 13
                    end = line.find('"', start)
                    if end > start:
                        return line[start:end]
    except Exception as e:
        print("Error extracting channel ID:", e)
    return None

def refresh_channel_videos(channel_id):
    rss_url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
    feed = feedparser.parse(rss_url)
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    channel_title = feed.feed.get('title', 'Unknown Channel')
    cursor.execute("UPDATE channels SET channel_name = ? WHERE channel_id = ?", (channel_title, channel_id))

    new_videos_count = 0
    for entry in feed.entries[:10]: # check latest 10 videos
        video_id = entry.get('yt_videoid', entry.get('id', ''))
        if 'vi/' in video_id:
            pass # sometimes video_id format varies
        title = entry.get('title', '')
        link = entry.get('link', '')
        published = entry.get('published', '')

        # Check if video already exists
        cursor.execute("SELECT id FROM videos WHERE video_id = ?", (video_id,))
        if not cursor.fetchone():
            cursor.execute('''
                INSERT OR IGNORE INTO videos (channel_id, video_id, title, link, published, is_new)
                VALUES (?, ?, ?, ?, ?, 1)
            ''', (channel_id, video_id, title, link, published))
            new_videos_count += 1

    conn.commit()
    conn.close()
    return new_videos_count

@app.route('/')
def index():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM channels')
    channels = cursor.fetchall()

    cursor.execute('SELECT v.*, c.channel_name FROM videos v JOIN channels c ON v.channel_id = c.channel_id ORDER BY v.published DESC LIMIT 30')
    videos = cursor.fetchall()
    
    cursor.execute('SELECT COUNT(*) as cnt FROM videos WHERE is_new = 1')
    unread_count = cursor.fetchone()['cnt']
    
    conn.close()
    return render_template('index.html', channels=channels, videos=videos, unread_count=unread_count)

@app.route('/channels', methods=['GET', 'POST'])
def manage_channels():
    if request.method == 'POST':
        url = request.form.get('url', '').strip()
        if not url:
            flash('Please enter a valid YouTube channel URL or handle.', 'danger')
            return redirect(url_for('manage_channels'))
        
        channel_id = extract_channel_id(url)
        if not channel_id:
            flash('Could not resolve YouTube Channel ID. Please check the URL.', 'danger')
            return redirect(url_for('manage_channels'))
        
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        try:
            cursor.execute('INSERT INTO channels (url, channel_id, channel_name) VALUES (?, ?, ?)', 
                           (url, channel_id, 'Fetching...'))
            conn.commit()
            refresh_channel_videos(channel_id)
            flash('Channel added and synced successfully!', 'success')
        except sqlite3.IntegrityError:
            flash('Channel already exists in your list.', 'warning')
        finally:
            conn.close()
            
        return redirect(url_for('manage_channels'))

    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM channels')
    channels = cursor.fetchall()
    conn.close()
    return render_template('channels.html', channels=channels)

@app.route('/delete/<int:channel_id>', methods=['POST'])
def delete_channel(channel_id):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('SELECT channel_id FROM channels WHERE id = ?', (channel_id,))
    row = cursor.fetchone()
    if row:
        cid = row[0]
        cursor.execute('DELETE FROM channels WHERE id = ?', (channel_id,))
        cursor.execute('DELETE FROM videos WHERE channel_id = ?', (cid,))
        conn.commit()
        flash('Channel removed successfully.', 'info')
    conn.close()
    return redirect(url_for('manage_channels'))

@app.route('/refresh')
def refresh_all():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('SELECT channel_id FROM channels')
    channels = cursor.fetchall()
    conn.close()

    total_new = 0
    for (cid,) in channels:
        total_new += refresh_channel_videos(cid)
    
    flash(f'Refreshed all channels! Found {total_new} new video(s).', 'success')
    return redirect(url_for('index'))

@app.route('/toggle-read/<int:video_id>', methods=['POST'])
def toggle_read(video_id):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('UPDATE videos SET is_new = NOT is_new WHERE id = ?', (video_id,))
    conn.commit()
    conn.close()
    return '', 204

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)
