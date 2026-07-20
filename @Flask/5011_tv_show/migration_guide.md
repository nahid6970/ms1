# Integration Migration Guide (Sonarr to Radarr Example)

This guide documents the changes made to the TV Show Dashboard (configured for Sonarr) to allow you to easily apply the same patterns to your Radarr dashboard.

---

## 1. Backend Changes (`app.py`)

### A. Settings Storage & Defaults
We added a configuration file `settings.json` to persist the connection parameters and root folders.

Add the following near the top of your `app.py`:
```python
SETTINGS_FILE = r"C:\@delta\db\5011_tv_show\settings.json" # Adjust path for Radarr

def load_settings():
    default_settings = {
        "sonarr_url": "http://192.168.0.101:7878", # Default Radarr port is 7878
        "sonarr_api_key": "",
        "root_shows_folder": r"C:\Users\nahid\Downloads\@radarr" # Adjust to your Radarr download folder
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
```

### B. Dynamically Using the Root Folder
Wherever the root folder was hardcoded (e.g. `ROOT_SHOWS_FOLDER`), replace it by fetching the value dynamically from the settings:
```python
settings = load_settings()
root_folder = settings.get('root_shows_folder', r"C:\Users\nahid\Downloads\@radarr")
```

### C. Added API Routes
Add these three endpoints to handle settings CRUD, connection verification, and bulk path updating:

```python
# 1. Save and Get Settings
@app.route('/api/settings', methods=['GET', 'POST'])
def api_settings():
    if request.method == 'POST':
        data = request.json or {}
        settings = load_settings()
        settings['sonarr_url'] = data.get('sonarr_url', settings.get('sonarr_url'))
        settings['sonarr_api_key'] = data.get('sonarr_api_key', settings.get('sonarr_api_key'))
        settings['root_shows_folder'] = data.get('root_shows_folder', settings.get('root_shows_folder'))
        save_settings(settings)
        return jsonify({'success': True})
    return jsonify(load_settings())

# 2. Test Connection to API
@app.route('/api/test_sonarr', methods=['POST'])
def api_test_sonarr():
    data = request.json or {}
    sonarr_url = data.get('sonarr_url', '').rstrip('/')
    api_key = data.get('sonarr_api_key', '')
    
    if not sonarr_url or not api_key:
        return jsonify({'success': False, 'message': 'Radarr URL and API Key are required'}), 400
        
    headers = {
        'X-Api-Key': api_key,
        'Content-Type': 'application/json'
    }
    
    try:
        # For Radarr, status endpoint is '/api/v3/system/status'
        response = requests.get(f"{sonarr_url}/api/v3/system/status", headers=headers, timeout=5)
        if response.status_code == 200:
            status_data = response.json()
            version = status_data.get('version', 'Unknown')
            return jsonify({'success': True, 'message': f'Connected! Radarr version: {version}'})
        else:
            return jsonify({'success': False, 'message': f'Failed with status code {response.status_code}. Check API key.'})
    except requests.exceptions.RequestException as e:
        return jsonify({'success': False, 'message': f'Connection failed: {str(e)}'})

# 3. Migrate Paths inside Radarr and local database
@app.route('/api/update_sonarr_paths', methods=['POST'])
def api_update_sonarr_paths():
    settings = load_settings()
    sonarr_url = settings.get('sonarr_url', '').rstrip('/')
    api_key = settings.get('sonarr_api_key', '')
    root_folder = settings.get('root_shows_folder', '')
    
    if not api_key:
        return jsonify({'success': False, 'message': 'API Key not configured in Settings'}), 400
        
    headers = {
        'X-Api-Key': api_key,
        'Content-Type': 'application/json'
    }
    
    try:
        # Get all movies/series from Radarr
        # For Radarr, endpoint is '/api/v3/movie'
        series_response = requests.get(f"{sonarr_url}/api/v3/movie", headers=headers, timeout=10)
        if series_response.status_code != 200:
            return jsonify({'success': False, 'message': f'Failed to get items: HTTP {series_response.status_code}'}), 500
            
        items_list = series_response.json()
        updated_count = 0
        failed_count = 0
        normalized_root = os.path.normpath(root_folder).lower()
        
        # Update inside Radarr
        for item in items_list:
            current_path = item.get('path', '')
            if not current_path:
                continue
                
            norm_curr_path = os.path.normpath(current_path)
            parent_dir = os.path.dirname(norm_curr_path)
            folder_name = os.path.basename(norm_curr_path)
            
            if parent_dir.lower() != normalized_root:
                new_path = os.path.normpath(os.path.join(root_folder, folder_name))
                item['path'] = new_path
                
                # PUT /api/v3/movie/{id} (or movie)
                put_url = f"{sonarr_url}/api/v3/movie/{item['id']}?moveFiles=false"
                put_response = requests.put(put_url, headers=headers, json=item, timeout=10)
                
                if put_response.status_code in [200, 202]:
                    updated_count += 1
                else:
                    failed_count += 1
                    
        # Update inside local data.json
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
            'message': f'Updated {updated_count} paths in Radarr. (Failed: {failed_count})'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error migrating paths: {str(e)}'}), 500
```

---

## 2. Styling Rules (`style.css`)

Add these stylesheet rules to keep modal settings input layouts consistent and responsive:
```css
.setting-item { 
    display: flex; 
    justify-content: space-between; 
    align-items: center; 
    padding: 12px 0; 
    border-bottom: 1px solid #222; 
}

.setting-item label { 
    margin-bottom: 0; 
    color: #eee; 
    font-size: 0.95rem; 
}

.setting-input, .setting-select {
    width: 320px !important;
    padding: 8px 12px !important;
    margin: 0 !important;
    background: #252525 !important;
    border: 1px solid #333 !important;
    color: white !important;
    border-radius: 6px !important;
    box-sizing: border-box !important;
    font-size: 0.9rem !important;
    transition: border-color 0.2s, box-shadow 0.2s !important;
}

.setting-input:focus, .setting-select:focus {
    border-color: #0084ff !important;
    outline: none !important;
    box-shadow: 0 0 5px rgba(0, 132, 255, 0.4) !important;
}
```

---

## 3. UI Modifications (`index.html`)

### A. Settings Modal Layout
Replace your settings modal markup to structure it cleanly and add the connection testing & path migration elements:

```html
    <!-- The Settings Modal -->
    <div id="settingsModal" class="modal">
        <div class="modal-content" style="max-width: 500px; padding: 25px; border-radius: 12px; background: #1c1c1c; border: 1px solid #333; position: relative;">
            <span class="close" onclick="closeSettingsModal()">&times;</span>
            <h2 style="margin-top: 0; border-bottom: 1px solid #333; padding-bottom: 12px; font-size: 1.5rem; text-align: left;">Settings</h2>
            
            <!-- General Settings -->
            <div style="margin-bottom: 25px;">
                <h3 style="font-size: 1rem; color: #1db954; text-align: left; margin: 0 0 12px 0; text-transform: uppercase; letter-spacing: 1px;">General</h3>
                
                <div class="setting-item">
                    <label for="defaultHomePage">Default Home Page</label>
                    <select id="defaultHomePage" class="setting-select">
                        <option value="default">Default (Title A-Z)</option>
                        <option value="last_episode">Last Added</option>
                    </select>
                </div>
                
                <div class="setting-item">
                    <label for="showHiddenShows">Show Hidden Items</label>
                    <label class="switch">
                        <input type="checkbox" id="showHiddenShows">
                        <span class="slider round"></span>
                    </label>
                </div>
            </div>
            
            <!-- Connection Settings -->
            <div style="margin-bottom: 20px;">
                <h3 style="font-size: 1rem; color: #0084ff; text-align: left; margin: 0 0 12px 0; text-transform: uppercase; letter-spacing: 1px;">Radarr Connection</h3>
                
                <div class="setting-item">
                    <label for="sonarrApiUrl">Radarr URL</label>
                    <input type="text" id="sonarrApiUrl" class="setting-input" placeholder="http://192.168.0.101:7878">
                </div>
                
                <div class="setting-item">
                    <label for="sonarrApiKey">Radarr API Key</label>
                    <input type="password" id="sonarrApiKey" class="setting-input" placeholder="Paste API Key here">
                </div>
                
                <div class="setting-item">
                    <label for="rootShowsFolder">Movies Download Path</label>
                    <div style="display: flex; flex-direction: column; align-items: flex-end; gap: 6px;">
                        <input type="text" id="rootShowsFolder" class="setting-input" placeholder="C:\Users\nahid\Downloads\@radarr">
                        <button onclick="syncSonarrPaths(this)" class="add-button" style="padding: 4px 10px; font-size: 11px; background-color: #f2994a; color: white; border-radius: 4px; font-weight: bold; width: fit-content; border: none; cursor: pointer;">Update Paths in Radarr & DB</button>
                    </div>
                </div>
            </div>
            
            <!-- Footer Controls -->
            <div style="margin-top: 20px; border-top: 1px solid #333; padding-top: 15px; display: flex; justify-content: space-between; align-items: center; min-height: 40px;">
                <span id="testConnectionStatus" style="font-size: 13px; font-weight: bold; text-align: left; max-width: 50%; display: inline-block;"></span>
                <div style="display: flex; gap: 10px;">
                    <button onclick="testSonarrConnection()" class="add-button" style="padding: 8px 16px; font-size: 14px; background-color: #0084ff; color: white; border-radius: 4px; font-weight: bold;">Test Connection</button>
                    <button onclick="saveSonarrSettings()" class="add-button" style="padding: 8px 16px; font-size: 14px; background-color: #1db954; color: white; border-radius: 4px; font-weight: bold;">Save Settings</button>
                </div>
            </div>
        </div>
    </div>
```

### B. Missing Window Search Box
Modify the Missing Items modal template by adding a header search bar container:
```html
    <!-- Scan Missing Items Modal -->
    <div id="scanMissingModal" class="modal">
        <div class="modal-content missing-modal-content">
            <span class="close" onclick="closeScanMissingModal()">&times;</span>
            <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #333; padding-bottom: 12px; margin-bottom: 15px; padding-right: 30px;">
                <h2 style="margin: 0;">Missing Items</h2>
                <input type="text" id="missingEpisodesSearch" placeholder="Search missing items..." style="background: #252525; color: white; border: 1px solid #333; border-radius: 6px; padding: 6px 12px; width: 240px; margin: 0; box-sizing: border-box; font-size: 0.9rem;">
            </div>
            <div id="missingEpisodesList" class="missing-episodes-list">
                <p>Scanning...</p>
            </div>
        </div>
    </div>
```

---

## 4. Frontend Logic Changes (`script.js`)

Add or replace these script handlers to coordinate setting saving, API testing, bulk path migration, and modal search inputs filtering:

```javascript
// 1. Reset inputs & clear status span when opening Settings Modal
async function openSettingsModal() {
    const statusSpan = document.getElementById('testConnectionStatus');
    if (statusSpan) {
        statusSpan.textContent = '';
        statusSpan.style.color = '';
    }
    
    try {
        const response = await fetch('/api/settings');
        const settings = await response.json();
        
        const urlInput = document.getElementById('sonarrApiUrl');
        const keyInput = document.getElementById('sonarrApiKey');
        const folderInput = document.getElementById('rootShowsFolder');
        
        if (urlInput) urlInput.value = settings.sonarr_url || 'http://192.168.0.101:7878';
        if (keyInput) keyInput.value = settings.sonarr_api_key || '';
        if (folderInput) folderInput.value = settings.root_shows_folder || 'C:\\Users\\nahid\\Downloads\\@radarr';
    } catch (e) {
        console.error('Error loading settings:', e);
    }

    document.getElementById('settingsModal').style.display = 'block';
    document.body.classList.add('modal-open');
}

// 2. Validate API key and URL connection
async function testSonarrConnection() {
    const url = document.getElementById('sonarrApiUrl').value;
    const apiKey = document.getElementById('sonarrApiKey').value;
    const statusSpan = document.getElementById('testConnectionStatus');
    
    if (!statusSpan) return;
    
    statusSpan.textContent = 'Testing connection...';
    statusSpan.style.color = '#e0e0e0';
    
    try {
        const response = await fetch('/api/test_sonarr', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ sonarr_url: url, sonarr_api_key: apiKey })
        });
        
        const data = await response.json();
        if (data.success) {
            statusSpan.textContent = data.message;
            statusSpan.style.color = '#4ade80';
        } else {
            statusSpan.textContent = data.message;
            statusSpan.style.color = '#ff6b6b';
        }
    } catch (e) {
        console.error('Error testing connection:', e);
        statusSpan.textContent = 'Connection error';
        statusSpan.style.color = '#ff6b6b';
    }
}

// 3. Migrate paths in Radarr & DB
async function syncSonarrPaths(button) {
    const originalText = button.textContent;
    button.textContent = 'Updating...';
    button.disabled = true;
    button.style.opacity = '0.7';
    
    try {
        const response = await fetch('/api/update_sonarr_paths', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });
        const data = await response.json();
        alert(data.message);
    } catch (e) {
        console.error('Error migrating paths:', e);
        alert('Failed to connect to server');
    } finally {
        button.textContent = originalText;
        button.disabled = false;
        button.style.opacity = '1';
    }
}

// 4. Save connection parameters
async function saveSonarrSettings() {
    const url = document.getElementById('sonarrApiUrl').value;
    const apiKey = document.getElementById('sonarrApiKey').value;
    const folder = document.getElementById('rootShowsFolder').value;
    
    try {
        const response = await fetch('/api/settings', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ sonarr_url: url, sonarr_api_key: apiKey, root_shows_folder: folder })
        });
        const data = await response.json();
        if (data.success) {
            alert('Settings saved successfully!');
            closeSettingsModal();
        } else {
            alert('Failed to save settings');
        }
    } catch (e) {
        console.error('Error saving settings:', e);
        alert('Error saving settings');
    }
}

// 5. Clear Search Bar on Missing Modal Open
async function openScanMissingModal() {
    const modal = document.getElementById('scanMissingModal');
    const list = document.getElementById('missingEpisodesList');
    const searchInput = document.getElementById('missingEpisodesSearch');
    
    if (searchInput) searchInput.value = '';
    list.innerHTML = '<p>Scanning for missing files...</p>';
    modal.style.display = 'block';
    document.body.classList.add('modal-open');
    // Rest of your fetch list population code...
}

// 6. Connect listener in DOMContentLoaded initialization
document.addEventListener('DOMContentLoaded', () => {
    // Other setup...

    const missingSearch = document.getElementById('missingEpisodesSearch');
    if (missingSearch) {
        missingSearch.addEventListener('input', function(e) {
            const query = e.target.value.toLowerCase().trim();
            const items = document.querySelectorAll('.missing-episode-item');
            items.forEach(item => {
                const showTitle = (item.querySelector('.missing-show-title')?.textContent || '').toLowerCase();
                const epTitle = (item.querySelector('.missing-episode-title')?.textContent || '').toLowerCase();
                if (showTitle.includes(query) || epTitle.includes(query)) {
                    item.style.display = '';
                } else {
                    item.style.display = 'none';
                }
            });
        });
    }
});
```
