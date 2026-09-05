function openAddShowModal() {
    document.getElementById('addShowModal').style.display = 'block';
    document.body.classList.add('modal-open');
}

function closeAddShowModal() {
    document.getElementById('addShowModal').style.display = 'none';
    document.body.classList.remove('modal-open');
}

function showHiddenShows() {
    console.log('Show hidden shows button clicked');
    
    // Get all hidden shows (ended and completed)
    const hiddenShows = document.querySelectorAll('.show-card.ended-completed');
    console.log('Found hidden shows:', hiddenShows.length);
    
    const hiddenShowsList = document.getElementById('hiddenShowsList');
    const hiddenShowsModal = document.getElementById('hiddenShowsModal');
    
    if (!hiddenShowsList || !hiddenShowsModal) {
        console.error('Hidden shows modal elements not found');
        return;
    }
    
    hiddenShowsList.innerHTML = '';
    
    if (hiddenShows.length === 0) {
        hiddenShowsList.innerHTML = '<p>No hidden shows found.</p>';
    } else {
        hiddenShows.forEach(card => {
            const title = card.dataset.title || 'Unknown Title';
            const year = card.dataset.year || 'Unknown Year';
            const status = card.dataset.status || 'Unknown Status';
            
            const imgElement = card.querySelector('img');
            const coverImage = imgElement ? imgElement.src : '';
            
            console.log('Show info:', {title, year, status, coverImage});
            
            const showItem = document.createElement('div');
            showItem.className = 'hidden-show-item';
            showItem.innerHTML = `
                <img src="${coverImage}" alt="${title}">
                <div class="hidden-show-item-info">
                    <h4>${title}</h4>
                    <p>${year}</p>
                    <p class="status">${status}</p>
                </div>
            `;
            
            hiddenShowsList.appendChild(showItem);
        });
    }
    
    hiddenShowsModal.style.display = 'block';
    document.body.classList.add('modal-open');
}

function closeHiddenShowsModal() {
    document.getElementById('hiddenShowsModal').style.display = 'none';
    document.body.classList.remove('modal-open');
}

function closeHiddenShowsModal() {
    document.getElementById('hiddenShowsModal').style.display = 'none';
    document.body.classList.remove('modal-open');
}

async function openEditShowModal(showId) {
    const response = await fetch(`/edit_show/${showId}`);
    const show = await response.json();

    document.getElementById('editShowId').value = show.id;
    document.getElementById('editShowTitle').value = show.title;
    document.getElementById('editShowYear').value = show.year;
    document.getElementById('editShowCoverImage').value = show.cover_image;
    document.getElementById('editShowDirectoryPath').value = show.directory_path || '';
    document.getElementById('editShowSonarrUrl').value = show.sonarr_url || '';
    document.getElementById('editShowEpisodeUpdateTime').value = show.episode_update_time || '';
    document.getElementById('editShowEpisodeUpdateFrequency').value = show.episode_update_frequency || 'daily';
    document.getElementById('editShowEpisodeUpdateWeekday').value = String(show.episode_update_weekday ?? ((new Date().getDay() + 6) % 7));
    document.getElementById('editShowEpisodeUpdateMonthDay').value = show.episode_update_month_day || new Date().getDate();
    updateScheduleOptionVisibility();
    document.getElementById('editShowStatus').value = show.status || 'Continuing';

    // Set the rating radio button
    const ratingRadios = document.querySelectorAll('#editShowModal input[name="rating"]');
    
    // First, clear all radio buttons
    ratingRadios.forEach(radio => {
        radio.checked = false;
    });
    
    // Then set the correct one if rating exists
    if (show.rating !== null && show.rating !== undefined && show.rating !== '') {
        ratingRadios.forEach(radio => {
            // Convert both values to strings for comparison to handle different data types
            if (radio.value === String(show.rating)) {
                radio.checked = true;
            }
        });
    }

    document.getElementById('editShowForm').action = `/edit_show/${show.id}`;

    // Save scroll position before opening modal
    localStorage.setItem('scrollPosition', window.scrollY);

    document.getElementById('editShowModal').style.display = 'block';
    document.body.classList.add('modal-open');
}

function closeEditShowModal() {
    document.getElementById('editShowModal').style.display = 'none';
    document.body.classList.remove('modal-open');
}

async function openEditEpisodeModal(showId, episodeId) {
    const response = await fetch(`/edit_episode/${showId}/${episodeId}`);
    const episode = await response.json();

    document.getElementById('editEpisodeShowId').value = showId;
    document.getElementById('editEpisodeId').value = episode.id;
    document.getElementById('editEpisodeTitle').value = episode.title;
    document.getElementById('editEpisodeForm').action = `/edit_episode/${showId}/${episode.id}`;

    document.getElementById('editEpisodeModal').style.display = 'block';
    document.body.classList.add('modal-open');
}

function closeEditEpisodeModal() {
    document.getElementById('editEpisodeModal').style.display = 'none';
    document.body.classList.remove('modal-open');
}

// Scan Missing Episodes Functions
async function openScanMissingModal() {
    const modal = document.getElementById('scanMissingModal');
    const list = document.getElementById('missingEpisodesList');
    const searchInput = document.getElementById('missingEpisodesSearch');
    
    if (searchInput) searchInput.value = '';
    list.innerHTML = '<p>Scanning for missing episode files...</p>';
    modal.style.display = 'block';
    document.body.classList.add('modal-open');

    try {
        const response = await fetch('/api/scan_missing_episodes');
        const missingEpisodes = await response.json();
        
        if (missingEpisodes.length === 0) {
            list.innerHTML = '<p>No missing episodes found.</p>';
        } else {
            list.innerHTML = '';
            missingEpisodes.forEach(ep => {
                const item = document.createElement('div');
                item.className = 'missing-episode-item';
                item.dataset.showId = ep.show_id;
                item.dataset.episodeId = ep.episode_id;
                
                item.innerHTML = `
                    <div class="missing-episode-info">
                        <span class="missing-show-title">${ep.show_title}</span>
                        <span class="missing-episode-title">${ep.episode_title}</span>
                    </div>
                    <div class="missing-episode-actions">
                        <button onclick="resetSonarrEpisode(${ep.show_id}, ${ep.episode_id}, this)" class="btn-sync" title="Reset and Search in Sonarr" style="background-color: #0084ff; color: white;"><svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-right: 4px;"><path d="M23 4v6h-6"></path><path d="M1 20v-6h6"></path><path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"></path></svg> Sonarr</button>
                        <button onclick="checkMissingEpisode(${ep.show_id}, ${ep.episode_id}, this)" class="btn-check" title="Mark as Watched"><svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-right: 4px;"><polyline points="20 6 9 17 4 12"></polyline></svg> Check</button>
                        <button onclick="deleteMissingEpisode(${ep.show_id}, ${ep.episode_id}, this)" class="btn-delete" title="Delete from JSON"><svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-right: 4px;"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path><line x1="10" y1="11" x2="10" y2="17"></line><line x1="14" y1="11" x2="14" y2="17"></line></svg> Del</button>
                    </div>
                `;
                list.appendChild(item);
            });
        }
    } catch (error) {
        console.error('Error scanning missing episodes:', error);
        list.innerHTML = '<p>Error occurred while scanning.</p>';
    }
}

function closeScanMissingModal() {
    document.getElementById('scanMissingModal').style.display = 'none';
    document.body.classList.remove('modal-open');
}

// Global variables for episodes modal
let currentEpisodes = [];
let currentShowIdForEpisodes = null;

function escapeEpisodeText(value) {
    return String(value || '').replace(/[&<>'"]/g, character => ({
        '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;'
    }[character]));
}

function updateScheduleOptionVisibility() {
    const frequency = document.getElementById('editShowEpisodeUpdateFrequency')?.value;
    const weeklyRow = document.getElementById('weeklyUpdateDayRow');
    const monthlyRow = document.getElementById('monthlyUpdateDayRow');
    if (weeklyRow) weeklyRow.hidden = frequency !== 'weekly';
    if (monthlyRow) monthlyRow.hidden = frequency !== 'monthly';
}

async function openScheduledUpdatesModal() {
    const modal = document.getElementById('scheduledUpdatesModal');
    const list = document.getElementById('scheduledUpdatesList');
    if (!modal || !list) return;
    modal.style.display = 'block';
    document.body.classList.add('modal-open');
    list.innerHTML = '<p class="schedule-empty">Loading schedules...</p>';
    try {
        const response = await fetch('/api/show-schedules');
        const data = await response.json();
        if (!response.ok || !data.success) throw new Error(data.message || 'Unable to load schedules');
        list.innerHTML = data.schedules.map(schedule => `
            <div class="scheduled-update-row">
                <span class="scheduled-update-title">${escapeEpisodeText(schedule.title)}</span>
                ${schedule.update_time
                    ? `<span class="scheduled-update-time">${schedule.frequency === 'weekly' ? ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'][schedule.weekday] + ' · ' : schedule.frequency === 'monthly' ? 'Day ' + schedule.month_day + ' · ' : ''}${schedule.update_time}</span>`
                    : '<span class="scheduled-update-disabled">Not scheduled</span>'}
            </div>
        `).join('') || '<p class="schedule-empty">No shows found.</p>';
    } catch (error) {
        list.innerHTML = `<p class="schedule-empty">${escapeEpisodeText(error.message)}</p>`;
    }
}

function closeScheduledUpdatesModal() {
    const modal = document.getElementById('scheduledUpdatesModal');
    if (modal) modal.style.display = 'none';
    document.body.classList.remove('modal-open');
}

function formatEpisodeAirDate(airDate) {
    if (!airDate) return '';
    const date = new Date(`${airDate}T00:00:00`);
    return Number.isNaN(date.getTime()) ? airDate : date.toLocaleDateString(undefined, {
        day: '2-digit', month: 'short', year: 'numeric'
    });
}

function isReleasedAndUnwatched(episode) {
    if (episode.watched || !episode.air_date) return false;
    const now = new Date();
    const today = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')}`;
    return String(episode.air_date) < today;
}

function isEpisodeCountedAsReleased(episode) {
    if (!episode.air_date) return true;
    const now = new Date();
    const today = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')}`;
    return String(episode.air_date) <= today;
}

function updateShowProgressBadge(showCard, episodes) {
    const countEl = showCard?.querySelector('.episode-count');
    if (!countEl) return;
    const releasedEpisodes = episodes.filter(isEpisodeCountedAsReleased);
    const total = releasedEpisodes.length;
    const watchedCount = releasedEpisodes.filter(episode => episode.watched).length;
    const releasedCount = total;
    const releasedWatched = releasedCount > 0 && episodes
        .filter(isEpisodeCountedAsReleased)
        .every(episode => episode.watched);
    const allEpisodesWatched = episodes.length > 0 && episodes.every(episode => episode.watched);
    countEl.textContent = `${watchedCount}/${total}`;
    countEl.classList.remove('no-episodes-watched', 'some-episodes-watched', 'all-episodes-watched');
    countEl.classList.add(watchedCount === 0 ? 'no-episodes-watched' : releasedWatched ? 'all-episodes-watched' : 'some-episodes-watched');
    showCard.dataset.releasedCount = releasedCount;
    showCard.classList.toggle('completed', releasedWatched);
    showCard.classList.toggle('ended-completed', allEpisodesWatched && showCard.dataset.status === 'Ended');
}

function copyEpisodeLabel(showId, episodeId, dotEl) {
    const ep = currentEpisodes.find(e => e.id === episodeId);
    if (!ep) return;
    const showTitle = document.getElementById('episodesModalTitle').textContent.trim();
    const code = ep.season_number != null && ep.episode_number != null
        ? `S${String(ep.season_number).padStart(2, '0')}E${String(ep.episode_number).padStart(2, '0')}`
        : '';
    const label = [showTitle, code, ep.title].filter(Boolean).join(' ');

    // try modern clipboard API first, fall back to execCommand
    const flash = () => {
        if (!dotEl) return;
        dotEl.style.background = '#27ae60';
        dotEl.title = 'Copied!';
        setTimeout(() => { dotEl.style.background = '#3498db'; dotEl.title = 'Copy episode label'; }, 1200);
    };

    if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(label).then(flash).catch(() => fallbackCopy(label, flash));
    } else {
        fallbackCopy(label, flash);
    }
}

function fallbackCopy(text, callback) {
    const ta = document.createElement('textarea');
    ta.value = text;
    ta.style.cssText = 'position:fixed;top:-9999px;left:-9999px;opacity:0';
    document.body.appendChild(ta);
    ta.focus();
    ta.select();
    try { document.execCommand('copy'); } catch(e) {}
    document.body.removeChild(ta);
    if (callback) callback();
}

function renderEpisodes(episodes, showId) {
    const listContainer = document.getElementById('episodesListContainer');
    listContainer.innerHTML = '';
    
    if (!episodes || episodes.length === 0) {
        listContainer.innerHTML = '<p style="text-align: center;">No episodes found.</p>';
        return;
    }

    const ul = document.createElement('ul');
    ul.style.listStyle = 'none';
    ul.style.padding = '0';
    
    episodes.forEach(ep => {
        const li = document.createElement('li');
        li.className = `episode-item ${ep.watched ? 'episode-watched' : ''}${isReleasedAndUnwatched(ep) ? ' episode-released-unwatched' : ''}`;
        li.dataset.episodeId = ep.id;

        const episodeNumber = ep.season_number != null && ep.episode_number != null
            ? `S${String(ep.season_number).padStart(2, '0')}E${String(ep.episode_number).padStart(2, '0')}`
            : '';
        const airDate = formatEpisodeAirDate(ep.air_date);
        li.innerHTML = `
            <div class="episode-main-info">
                <input type="checkbox" ${ep.watched ? 'checked' : ''} onclick="handleEpisodeCheckboxClick(event, ${showId}, ${ep.id}, this)">
                <div class="episode-title-block">
                    <span class="episode-number">${episodeNumber}</span>
                    <span class="episode-title">${escapeEpisodeText(ep.title)}</span>
                    ${airDate ? `<span class="episode-airdate">Air date: ${airDate}</span>` : ''}
                </div>
            </div>
            <div style="display: flex; gap: 8px;">
                <div class="edit-dot" onclick="copyEpisodeLabel(${showId}, ${ep.id}, this)" title="Copy episode label" style="width: 10px; height: 10px; border-radius: 50%; background: #3498db; cursor: pointer;"></div>
                <div class="delete-dot" onclick="deleteEpisode(${showId}, ${ep.id})" style="width: 10px; height: 10px; border-radius: 50%; background: #e74c3c; cursor: pointer;"></div>
            </div>
        `;
        ul.appendChild(li);
    });
    listContainer.appendChild(ul);
    updateBulkEpisodeButton(episodes);
}

function updateBulkEpisodeButton(episodes) {
    const button = document.getElementById('toggleAllEpisodes');
    if (!button) return;
    const allWatched = episodes.length > 0 && episodes.every(episode => episode.watched);
    button.title = allWatched ? 'Mark all episodes as unwatched' : 'Mark all episodes as watched';
    button.setAttribute('aria-label', button.title);
    button.innerHTML = allWatched
        ? '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="3" y="3" width="18" height="18" rx="2"></rect><line x1="8" y1="8" x2="16" y2="16"></line><line x1="16" y1="8" x2="8" y2="16"></line></svg>'
        : '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="3" y="3" width="18" height="18" rx="2"></rect><polyline points="7 12 10 15 17 8"></polyline></svg>';
}

function updateSortButtonUI(sortType, sortOrder) {
    const sortTypeSelect = document.getElementById('episodeSortType');
    const sortOrderSelect = document.getElementById('episodeSortOrder');
    if (sortTypeSelect) sortTypeSelect.value = sortType || 'default';
    if (sortOrderSelect) sortOrderSelect.value = sortOrder || 'asc';
}

function closeEpisodesModal() {
    document.getElementById('episodesModal').style.display = 'none';
    document.body.classList.remove('modal-open');
    currentEpisodes = [];
    currentShowIdForEpisodes = null;
}

async function openEpisodesPopup(event, showId, showTitle) {
    if (event) {
        event.stopPropagation();
        event.preventDefault();
    }
    
    const modal = document.getElementById('episodesModal');
    const titleEl = document.getElementById('episodesModalTitle');
    const listContainer = document.getElementById('episodesListContainer');

    titleEl.textContent = showTitle;
    listContainer.innerHTML = '<p style="text-align: center;">Loading episodes...</p>';
    modal.style.display = 'block';
    document.body.classList.add('modal-open');

    try {
        const response = await fetch(`/edit_show/${showId}`);
        const show = await response.json();
        
        currentEpisodes = show.episodes || [];
        currentShowIdForEpisodes = showId;
        
        updateSortButtonUI(show.episode_sort_type, show.episode_sort_order);
        renderEpisodes(currentEpisodes, showId);
    } catch (error) {
        console.error('Error fetching episodes:', error);
        listContainer.innerHTML = '<p style="text-align: center; color: #ff6b6b;">Error loading episodes.</p>';
    }
}

async function checkMissingEpisode(showId, episodeId, button) {
    try {
        const response = await fetch(`/api/check_episode/${showId}/${episodeId}`, { method: 'POST' });
        const data = await response.json();
        if (data.success) {
            const item = button.closest('.missing-episode-item');
            item.style.opacity = '0.5';
            item.style.pointerEvents = 'none';
            setTimeout(() => item.remove(), 500);
        }
    } catch (error) {
        console.error('Error checking episode:', error);
    }
}

async function deleteMissingEpisode(showId, episodeId, button) {
    if (confirm('Are you sure you want to delete this episode from JSON?')) {
        try {
            const response = await fetch(`/api/delete_episode/${showId}/${episodeId}`, { method: 'POST' });
            const data = await response.json();
            if (data.success) {
                const item = button.closest('.missing-episode-item');
                item.style.opacity = '0.5';
                item.style.pointerEvents = 'none';
                setTimeout(() => item.remove(), 500);
            }
        } catch (error) {
            console.error('Error deleting episode:', error);
        }
    }
}

async function scanForEpisodes(event) {
    if (event) event.preventDefault();
    const btn = document.querySelector('.scan-button');
    const originalHTML = btn.innerHTML;
    
    btn.innerHTML = '<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="spin"><polyline points="23 4 23 10 18 10"></polyline><polyline points="1 20 1 14 6 14"></polyline><path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"></path></svg>';
    btn.style.pointerEvents = 'none';

    try {
        const response = await fetch('/scan_and_add_all');
        const data = await response.json();
        if (data.success) {
            location.reload();
        }
    } catch (error) {
        console.error('Error scanning:', error);
        btn.innerHTML = originalHTML;
        btn.style.pointerEvents = 'auto';
        alert('Error during scan');
    }
}

async function syncShow(event, showId, btn) {
    if (event) {
        event.stopPropagation();
        event.preventDefault();
    }
    
    const originalHTML = btn.innerHTML;
    btn.innerHTML = '<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="spin"><path d="M23 4v6h-6"></path><path d="M1 20v-6h6"></path><path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"></path></svg>';
    btn.style.pointerEvents = 'none';

    try {
        const response = await fetch(`/scan_manual/${showId}`);
        const data = await response.json();
        if (data.success) {
            btn.innerHTML = '<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="#4ade80" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>';
            setTimeout(() => {
                location.reload();
            }, 1000);
        }
    } catch (error) {
        console.error('Error syncing show:', error);
        btn.innerHTML = originalHTML;
        btn.style.pointerEvents = 'auto';
    }
}

// Settings Modal Functions
async function openSettingsModal() {
    // Clear status spans
    const sonarrStatusSpan = document.getElementById('sonarrTestStatus');
    if (sonarrStatusSpan) {
        sonarrStatusSpan.textContent = '';
        sonarrStatusSpan.style.color = '';
    }
    const radarrStatusSpan = document.getElementById('radarrTestStatus');
    if (radarrStatusSpan) {
        radarrStatusSpan.textContent = '';
        radarrStatusSpan.style.color = '';
    }
    
    try {
        const response = await fetch('/api/settings');
        const settings = await response.json();
        
        const tmdbKeyInput = document.getElementById('tmdbApiKey');
        const defaultShowsSortInput = document.getElementById('defaultShowsSort');
        const defaultShowsOrderInput = document.getElementById('defaultShowsOrder');
        const defaultMoviesSortInput = document.getElementById('defaultMoviesSort');
        const defaultMoviesOrderInput = document.getElementById('defaultMoviesOrder');
        const sonarrUrlInput = document.getElementById('sonarrApiUrl');
        const sonarrKeyInput = document.getElementById('sonarrApiKey');
        const showsFolderInput = document.getElementById('rootShowsFolder');
        const radarrUrlInput = document.getElementById('radarrApiUrl');
        const radarrKeyInput = document.getElementById('radarrApiKey');
        const moviesFolderInput = document.getElementById('rootMoviesFolder');
        
        if (tmdbKeyInput) tmdbKeyInput.value = settings.tmdb_api_key || '';
        if (defaultShowsSortInput) defaultShowsSortInput.value = settings.default_shows_sort || 'title';
        if (defaultShowsOrderInput) defaultShowsOrderInput.value = settings.default_shows_order || 'asc';
        if (defaultMoviesSortInput) defaultMoviesSortInput.value = settings.default_movies_sort || 'title';
        if (defaultMoviesOrderInput) defaultMoviesOrderInput.value = settings.default_movies_order || 'asc';
        if (sonarrUrlInput) sonarrUrlInput.value = settings.sonarr_url || 'http://192.168.0.101:8989';
        if (sonarrKeyInput) sonarrKeyInput.value = settings.sonarr_api_key || '';
        if (showsFolderInput) showsFolderInput.value = settings.root_shows_folder || 'C:\\Users\\nahid\\Downloads\\@sonarr';
        if (radarrUrlInput) radarrUrlInput.value = settings.radarr_url || 'http://192.168.0.101:7878';
        if (radarrKeyInput) radarrKeyInput.value = settings.radarr_api_key || '';
        if (moviesFolderInput) moviesFolderInput.value = settings.root_movies_folder || 'C:\\Users\\nahid\\Downloads\\@radarr';
    } catch (e) {
        console.error('Error loading settings:', e);
    }

    document.getElementById('settingsModal').style.display = 'block';
    document.body.classList.add('modal-open');
}

function closeSettingsModal() {
    document.getElementById('settingsModal').style.display = 'none';
    document.body.classList.remove('modal-open');
}

async function testSonarrConnection() {
    const url = document.getElementById('sonarrApiUrl').value;
    const apiKey = document.getElementById('sonarrApiKey').value;
    const statusSpan = document.getElementById('sonarrTestStatus');
    
    if (!statusSpan) return;
    
    statusSpan.textContent = 'Testing connection...';
    statusSpan.style.color = '#e0e0e0';
    
    try {
        const response = await fetch('/api/test_sonarr', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                sonarr_url: url,
                sonarr_api_key: apiKey
            })
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
        statusSpan.textContent = 'Error connecting to application server';
        statusSpan.style.color = '#ff6b6b';
    }
}

async function syncSonarrPaths(button) {
    const originalText = button.textContent;
    button.textContent = 'Updating...';
    button.disabled = true;
    button.style.opacity = '0.7';
    
    try {
        const response = await fetch('/api/update_sonarr_paths', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
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

async function testRadarrConnection() {
    const url = document.getElementById('radarrApiUrl').value;
    const apiKey = document.getElementById('radarrApiKey').value;
    const statusSpan = document.getElementById('radarrTestStatus');
    
    if (!statusSpan) return;
    
    statusSpan.textContent = 'Testing connection...';
    statusSpan.style.color = '#e0e0e0';
    
    try {
        const response = await fetch('/api/test_radarr', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                radarr_url: url,
                radarr_api_key: apiKey
            })
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
        console.error('Error testing Radarr connection:', e);
        statusSpan.textContent = 'Error connecting to application server';
        statusSpan.style.color = '#ff6b6b';
    }
}

async function syncRadarrPaths(button) {
    const originalText = button.textContent;
    button.textContent = 'Updating...';
    button.disabled = true;
    button.style.opacity = '0.7';
    
    try {
        const response = await fetch('/api/update_radarr_paths', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        const data = await response.json();
        alert(data.message);
    } catch (e) {
        console.error('Error migrating Radarr paths:', e);
        alert('Failed to connect to server');
    } finally {
        button.textContent = originalText;
        button.disabled = false;
        button.style.opacity = '1';
    }
}

async function saveSettings() {
    const tmdbApiKey = document.getElementById('tmdbApiKey').value.trim();
    const defaultShowsSort = document.getElementById('defaultShowsSort').value;
    const defaultShowsOrder = document.getElementById('defaultShowsOrder').value;
    const defaultMoviesSort = document.getElementById('defaultMoviesSort').value;
    const defaultMoviesOrder = document.getElementById('defaultMoviesOrder').value;
    const sonarrUrl = document.getElementById('sonarrApiUrl').value;
    const sonarrApiKey = document.getElementById('sonarrApiKey').value;
    const showsFolder = document.getElementById('rootShowsFolder').value;
    const radarrUrl = document.getElementById('radarrApiUrl').value;
    const radarrApiKey = document.getElementById('radarrApiKey').value;
    const moviesFolder = document.getElementById('rootMoviesFolder').value;
    
    try {
        const response = await fetch('/api/settings', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                tmdb_api_key: tmdbApiKey,
                default_shows_sort: defaultShowsSort,
                default_shows_order: defaultShowsOrder,
                default_movies_sort: defaultMoviesSort,
                default_movies_order: defaultMoviesOrder,
                sonarr_url: sonarrUrl,
                sonarr_api_key: sonarrApiKey,
                root_shows_folder: showsFolder,
                radarr_url: radarrUrl,
                radarr_api_key: radarrApiKey,
                root_movies_folder: moviesFolder
            })
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

async function resetSonarrEpisode(showId, episodeId, button) {
    const originalContent = button.innerHTML;
    button.disabled = true;
    button.innerHTML = 'Resetting...';
    try {
        const response = await fetch('/api/reset_sonarr_episode', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ show_id: showId, episode_id: episodeId })
        });
        const data = await response.json();
        if (data.success) {
            button.style.backgroundColor = '#4ade80';
            button.innerHTML = 'Success!';
            setTimeout(() => {
                button.style.backgroundColor = '#0084ff';
                button.innerHTML = originalContent;
                button.disabled = false;
            }, 2000);
        } else {
            alert('Failed: ' + data.message);
            button.innerHTML = originalContent;
            button.disabled = false;
        }
    } catch (error) {
        console.error('Error resetting Sonarr episode:', error);
        alert('Network error resetting episode');
        button.innerHTML = originalContent;
        button.disabled = false;
    }
}

// Server-side Folder Opening Function
function openFolderViaServer(event, showId) {
    event.preventDefault(); // Prevent default link behavior
    
    fetch(`/open_folder/${showId}`)
        .then(response => response.json())
        .then(data => {
            if (!data.success) {
                alert(`Failed to open folder: ${data.message}`);
            }
            // If successful, no need to show anything - folder should open
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Failed to open folder due to network error');
        });
}

// Restore scroll position immediately (before DOMContentLoaded to prevent flash)
const savedScrollPosition = localStorage.getItem('scrollPosition');
if (savedScrollPosition !== null) {
    // Set scroll position immediately
    window.scrollTo({
        top: parseInt(savedScrollPosition),
        behavior: 'instant'
    });
    localStorage.removeItem('scrollPosition');
}

// Load the persisted visibility preference for hidden shows.
document.addEventListener('DOMContentLoaded', () => {
    const showHiddenShowsToggle = document.getElementById('showHiddenShows');
    const html = document.documentElement;
    const scheduleFrequency = document.getElementById('editShowEpisodeUpdateFrequency');
    if (scheduleFrequency) {
        scheduleFrequency.addEventListener('change', updateScheduleOptionVisibility);
        updateScheduleOptionVisibility();
    }

    // Load show hidden shows preference from localStorage
    const showHiddenShows = localStorage.getItem('showHiddenShows') === 'true';
    console.log('Loaded showHiddenShows setting:', showHiddenShows);
    if (showHiddenShows) {
        html.classList.add('show-hidden-shows');
        showHiddenShowsToggle.checked = true;
        console.log('Added show-hidden-shows class to HTML');
    } else {
        html.classList.remove('show-hidden-shows');
        showHiddenShowsToggle.checked = false;
        console.log('Removed show-hidden-shows class from HTML');
    }

    // Save show hidden shows preference to localStorage on change
    showHiddenShowsToggle.addEventListener('change', () => {
        if (showHiddenShowsToggle.checked) {
            html.classList.add('show-hidden-shows');
            localStorage.setItem('showHiddenShows', 'true');
            console.log('Enabled show-hidden-shows');
        } else {
            html.classList.remove('show-hidden-shows');
            localStorage.setItem('showHiddenShows', 'false');
            console.log('Disabled show-hidden-shows');
        }
    });



    // Live Search Functionality
    const searchInput = document.querySelector('.search-form input[name="query"]');
    const searchClear = document.getElementById('searchClear');

    function filterShows(query) {
        const showCards = document.querySelectorAll('.show-card');
        query = query.toLowerCase().trim();
        
        showCards.forEach(card => {
            const title = (card.getAttribute('data-title') || "").toLowerCase();
            const year = (card.getAttribute('data-year') || "").toLowerCase();
            
            if (title.includes(query) || year.includes(query)) {
                card.style.display = ''; 
            } else {
                card.style.display = 'none';
            }
        });

        // Show/hide clear button
        if (searchClear) {
            searchClear.style.display = query.length > 0 ? 'block' : 'none';
        }
    }

    if (searchInput) {
        // Initial check for clear button visibility (e.g. on page reload with query)
        if (searchClear) {
            searchClear.style.display = searchInput.value.length > 0 ? 'block' : 'none';
        }

        searchInput.addEventListener('input', function(e) {
            filterShows(e.target.value);
        });

        if (searchClear) {
            searchClear.addEventListener('click', function() {
                searchInput.value = '';
                filterShows('');
                searchInput.focus();
            });
        }
    }

    // Add click listener for show cards
    document.querySelectorAll('.show-card').forEach(card => {
        card.addEventListener('click', async (event) => {
            // Check if the click wasn't on a button or inside hover controls
            if (!event.target.closest('.hover-controls')) {
                const showId = card.dataset.showId;
                const showTitle = card.dataset.title;
                if (!showId) return;
                
                // Use the consolidated function to open the popup
                openEpisodesPopup(event, showId, showTitle);
            }
        });
    });

    // Episode sorting logic
    const sortTypeSelect = document.getElementById('episodeSortType');
    const sortOrderSelect = document.getElementById('episodeSortOrder');
    async function saveEpisodeSort() {
            if (!currentShowIdForEpisodes) return;
            const newSortType = sortTypeSelect.value;
            const newOrder = sortOrderSelect.value;
            try {
                const response = await fetch(`/update_episode_sort/${currentShowIdForEpisodes}`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ sort_type: newSortType, order: newOrder })
                });
                
                const data = await response.json();
                if (data.success) {
                    currentEpisodes = data.episodes;
                    updateSortButtonUI(newSortType, newOrder);
                    renderEpisodes(currentEpisodes, currentShowIdForEpisodes);
                }
            } catch (error) {
                console.error('Error updating episode sort:', error);
            }
    }
    if (sortTypeSelect && sortOrderSelect) {
        sortTypeSelect.addEventListener('change', saveEpisodeSort);
        sortOrderSelect.addEventListener('change', saveEpisodeSort);
    }

    async function setAllEpisodesWatched(watched) {
        if (!currentShowIdForEpisodes) return;
        try {
            const response = await fetch(`/api/show/${currentShowIdForEpisodes}/episodes/watched`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ watched })
            });
            const data = await response.json();
            if (!response.ok || !data.success) throw new Error(data.message || 'Unable to update episodes');
            currentEpisodes = data.episodes;
            renderEpisodes(currentEpisodes, currentShowIdForEpisodes);

            const showCard = document.querySelector(`.show-card[data-show-id="${currentShowIdForEpisodes}"]`);
            updateShowProgressBadge(showCard, currentEpisodes);
        } catch (error) {
            console.error('Error updating all episodes:', error);
            alert(error.message);
        }
    }

    const toggleAllEpisodes = document.getElementById('toggleAllEpisodes');
    if (toggleAllEpisodes) toggleAllEpisodes.addEventListener('click', () => {
        const allWatched = currentEpisodes.length > 0 && currentEpisodes.every(episode => episode.watched);
        setAllEpisodesWatched(!allWatched);
    });

    const refreshOpenEpisodes = document.getElementById('refreshOpenEpisodes');
    if (refreshOpenEpisodes) refreshOpenEpisodes.addEventListener('click', event => {
        refreshEpisodesInModal(event, refreshOpenEpisodes);
    });

    // Helper functions for popup interactions
    window.handleEpisodeCheckboxClick = async function(event, showId, episodeId, checkbox) {
        event.preventDefault();
        const clickedIndex = currentEpisodes.findIndex(episode => episode.id === episodeId);
        if (clickedIndex < 0) return;

        const targetWatched = !currentEpisodes[clickedIndex].watched;
        const selectedEpisodes = event.shiftKey
            ? currentEpisodes.slice(clickedIndex)
            : [currentEpisodes[clickedIndex]];
        const changes = selectedEpisodes.filter(episode => Boolean(episode.watched) !== targetWatched);

        selectedEpisodes.forEach(episode => {
            const item = document.querySelector(`#episodesListContainer .episode-item[data-episode-id="${episode.id}"]`);
            const itemCheckbox = item?.querySelector('input[type="checkbox"]');
            if (itemCheckbox) itemCheckbox.checked = targetWatched;
        });

        try {
            for (const episode of changes) {
                const response = await fetch(`/toggle_watched/${showId}/${episode.id}`);
                const data = await response.json();
                if (!response.ok || !data.success || data.watched !== targetWatched) {
                    throw new Error('Unable to update episode status');
                }
                episode.watched = targetWatched;
            }
            renderEpisodes(currentEpisodes, showId);
            updateShowProgressBadge(document.querySelector(`.show-card[data-show-id="${showId}"]`), currentEpisodes);
        } catch (error) {
            renderEpisodes(currentEpisodes, showId);
            alert(error.message);
        }
    };

    window.toggleWatched = function(showId, episodeId, checkbox) {
        fetch(`/toggle_watched/${showId}/${episodeId}`)
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Update global state
                    const ep = currentEpisodes.find(e => e.id === episodeId);
                    if (ep) ep.watched = data.watched;
                    updateBulkEpisodeButton(currentEpisodes);

                    // 1. Update episode item in modal
                    const li = checkbox.closest('.episode-item');
                    if (data.watched) {
                        li.classList.add('episode-watched');
                    } else {
                        li.classList.remove('episode-watched');
                    }
                    li.classList.toggle('episode-released-unwatched', ep ? isReleasedAndUnwatched(ep) : false);

                    // 2. Update show card on main page
                    const showCard = document.querySelector(`.show-card[data-show-id="${showId}"]`);
                    updateShowProgressBadge(showCard, currentEpisodes);
                }
            });
    };

    window.deleteEpisode = function(showId, episodeId) {
        if (confirm('Are you sure?')) {
            fetch(`/delete_episode/${showId}/${episodeId}`).then(response => response.json()).then(data => {
                if (data.success) {
                    // Update global state and re-render
                    currentEpisodes = currentEpisodes.filter(e => e.id !== episodeId);
                    renderEpisodes(currentEpisodes, showId);
                    
                    // Update show card count (simple reload for now or manual update)
                    // For simplicity, we can let it be, but a full card update would be better.
                    // Let's just update the total count on the card.
                    const showCard = document.querySelector(`.show-card[data-show-id="${showId}"]`);
                    updateShowProgressBadge(showCard, currentEpisodes);
                }
            });
        }
    };

    // Context Menu functionality
    const contextMenu = document.getElementById('contextMenu');
    const contextEdit = document.getElementById('contextEdit');
    const contextDelete = document.getElementById('contextDelete');
    let currentShowId = null;

    if (contextMenu && contextEdit && contextDelete) {
        // Show context menu on right-click
        document.querySelectorAll('.show-card').forEach(card => {
            card.addEventListener('contextmenu', (event) => {
                event.preventDefault();
                event.stopPropagation();
                
                currentShowId = card.dataset.showId;
                console.log('Right-clicked on show:', currentShowId);
                
                // Position the context menu using clientX/clientY for viewport coordinates
                const x = event.clientX;
                const y = event.clientY;
                
                // Get menu dimensions
                contextMenu.style.display = 'block';
                const menuWidth = contextMenu.offsetWidth;
                const menuHeight = contextMenu.offsetHeight;
                
                // Adjust position if menu would go off screen
                const windowWidth = window.innerWidth;
                const windowHeight = window.innerHeight;
                
                let left = x;
                let top = y;
                
                // Check if menu goes off right edge
                if (x + menuWidth > windowWidth) {
                    left = windowWidth - menuWidth - 5;
                }
                
                // Check if menu goes off bottom edge
                if (y + menuHeight > windowHeight) {
                    top = windowHeight - menuHeight - 5;
                }
                
                contextMenu.style.left = left + 'px';
                contextMenu.style.top = top + 'px';
            });
        });

        // Handle Edit click
        contextEdit.addEventListener('click', (event) => {
            event.stopPropagation();
            if (currentShowId) {
                openEditShowModal(parseInt(currentShowId));
            }
            contextMenu.style.display = 'none';
        });

        // Handle Delete click
        contextDelete.addEventListener('click', (event) => {
            event.stopPropagation();
            if (currentShowId) {
                if (confirm('Are you sure you want to delete this show?')) {
                    window.location.href = `/delete_show/${currentShowId}`;
                }
            }
            contextMenu.style.display = 'none';
        });

        // Hide context menu on click anywhere else
        document.addEventListener('click', (event) => {
            if (!contextMenu.contains(event.target)) {
                contextMenu.style.display = 'none';
            }
        });

        // Hide context menu on scroll
        document.addEventListener('scroll', () => {
            contextMenu.style.display = 'none';
        });
    }

    // Search missing episodes
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

// Sort Menu Functions
function toggleSortMenu() {
    const dropdown = document.getElementById('sortMenuDropdown');
    const button = document.querySelector('.sort-menu-button');
    
    dropdown.classList.toggle('show');
    button.classList.toggle('active');
}

// Close sort menu when clicking outside
document.addEventListener('click', function(event) {
    const sortContainer = document.querySelector('.sort-menu-container');
    if (sortContainer && !sortContainer.contains(event.target)) {
        const dropdown = document.getElementById('sortMenuDropdown');
        const button = document.querySelector('.sort-menu-button');
        if (dropdown && button) {
            dropdown.classList.remove('show');
            button.classList.remove('active');
        }
    }
});

// Close modal if user clicks outside of it
window.onclick = function(event) {
    const addModal = document.getElementById('addShowModal');
    const editShowModal = document.getElementById('editShowModal');
    const settingsModal = document.getElementById('settingsModal');
    const hiddenShowsModal = document.getElementById('hiddenShowsModal');
    const scanMissingModal = document.getElementById('scanMissingModal');
    const episodesModal = document.getElementById('episodesModal');
    const scheduledUpdatesModal = document.getElementById('scheduledUpdatesModal');

    if (event.target == addModal) {
        addModal.style.display = 'none';
        document.body.classList.remove('modal-open');
    } else if (event.target == editShowModal) {
        editShowModal.style.display = 'none';
        document.body.classList.remove('modal-open');
    } else if (event.target == settingsModal) {
        settingsModal.style.display = 'none';
        document.body.classList.remove('modal-open');
    } else if (event.target == hiddenShowsModal) {
        hiddenShowsModal.style.display = 'none';
        document.body.classList.remove('modal-open');
    } else if (event.target == scanMissingModal) {
        scanMissingModal.style.display = 'none';
        document.body.classList.remove('modal-open');
    } else if (event.target == episodesModal) {
        episodesModal.style.display = 'none';
        document.body.classList.remove('modal-open');
    } else if (event.target == scheduledUpdatesModal) {
        closeScheduledUpdatesModal();
    }
}

async function updateShowEpisodes(event, showId, btn) {
    if (event) {
        event.stopPropagation();
        event.preventDefault();
    }
    const originalHTML = btn.innerHTML;
    btn.disabled = true;
    btn.innerHTML = '<svg class="discover-loading-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="23 4 23 10 18 10"></polyline><polyline points="1 20 1 14 6 14"></polyline><path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"></path></svg>';
    try {
        const response = await fetch(`/api/show/${showId}/episodes/update`, {method: 'POST'});
        const data = await response.json();
        if (!response.ok || !data.success) throw new Error(data.message || 'Episode update failed');
        btn.innerHTML = '<svg viewBox="0 0 24 24" fill="none" stroke="#4ade80" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>';
        alert(data.message);
    } catch (error) {
        btn.innerHTML = originalHTML;
        alert(error.message);
    } finally {
        btn.disabled = false;
    }
}

async function refreshEpisodesInModal(event, btn) {
    if (event) {
        event.stopPropagation();
        event.preventDefault();
    }
    if (!currentShowIdForEpisodes) return;
    const originalHTML = btn.innerHTML;
    btn.disabled = true;
    btn.innerHTML = '<svg class="discover-loading-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="23 4 23 10 18 10"></polyline><polyline points="1 20 1 14 6 14"></polyline><path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"></path></svg>';
    try {
        const response = await fetch(`/api/show/${currentShowIdForEpisodes}/episodes/update`, {method: 'POST'});
        const data = await response.json();
        if (!response.ok || !data.success) throw new Error(data.message || 'Episode update failed');
        const showResponse = await fetch(`/edit_show/${currentShowIdForEpisodes}`);
        const show = await showResponse.json();
        currentEpisodes = show.episodes || [];
        updateSortButtonUI(show.episode_sort_type, show.episode_sort_order);
        renderEpisodes(currentEpisodes, currentShowIdForEpisodes);
        btn.innerHTML = '<svg viewBox="0 0 24 24" aria-hidden="true"><polyline points="20 6 9 17 4 12"></polyline></svg>';
        setTimeout(() => { if (btn.disabled) btn.innerHTML = originalHTML; }, 1400);
    } catch (error) {
        btn.innerHTML = originalHTML;
        alert(error.message);
    } finally {
        btn.disabled = false;
    }
}
