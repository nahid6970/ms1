const discoverForm       = document.getElementById('discoverSearchForm');
const discoverQuery      = document.getElementById('discoverQuery');
const discoverType       = document.getElementById('discoverType');
const discoverPreset     = document.getElementById('discoverPreset');
const discoverRegion     = document.getElementById('discoverRegion');
const discoverSort       = document.getElementById('discoverSort');
const discoverLimit      = document.getElementById('discoverLimit');
const discoverResults    = document.getElementById('discoverResults');
const discoverStatus     = document.getElementById('discoverStatus');
const discoverPagination = document.getElementById('discoverPagination');
const discoverPrevious   = document.getElementById('discoverPrevious');
const discoverNext       = document.getElementById('discoverNext');
const discoverPageLabel  = document.getElementById('discoverPageLabel');
const dcPresetBtn        = document.getElementById('dcPresetBtn');
const dcPresetMenu       = document.getElementById('dcPresetMenu');
const dcPresetLabel      = document.getElementById('dcPresetLabel');
const dcPresetModeIcon   = document.getElementById('dcPresetModeIcon');
const dcPresetRegionLabel = document.getElementById('dcPresetRegionLabel');
let discoverItems = [];
let discoverPage  = 1;

function applyDiscoverImageScale(scale) {
    const cardMinWidths = {
        '0.75': '270px',
        '1': '300px',
        '1.25': '360px',
        '1.5': '420px',
        '2': '480px'
    };
    const allowedScales = new Set(Object.keys(cardMinWidths));
    const scaleValue = String(scale ?? '1');
    document.documentElement.style.setProperty(
        '--discover-image-scale',
        allowedScales.has(scaleValue) ? scaleValue : '1'
    );
    document.documentElement.style.setProperty(
        '--discover-card-min-width',
        cardMinWidths[scaleValue] || cardMinWidths['1']
    );
}

fetch('/api/settings')
    .then(response => response.json())
    .then(settings => applyDiscoverImageScale(settings.discover_image_scale))
    .catch(() => applyDiscoverImageScale(1));

// Restore saved state
const savedType   = localStorage.getItem('discoverType');
const savedPreset = localStorage.getItem('discoverPreset');
const savedRegion = localStorage.getItem('discoverRegion');
const savedSort   = localStorage.getItem('discoverSort');
const savedLimit  = localStorage.getItem('discoverLimit');
if (savedType)   discoverType.value   = savedType;
if (savedPreset) discoverPreset.value = savedPreset;
if (savedRegion) discoverRegion.value = savedRegion;
if (savedSort)   discoverSort.value   = savedSort;
if (savedLimit)  discoverLimit.value  = savedLimit;

// Label shown on the button — mode + region summary
const modeLabelMap = {
    search: 'Search', popular: 'Popular', top_rated: 'Top Rated', trending_month: 'Trending', recent_releases: 'Recent'
};
const modeIconMap = {
    search: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="7"></circle><line x1="16.5" y1="16.5" x2="21" y2="21"></line></svg>',
    popular: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22c4.2 0 7-2.7 7-6.3 0-2.7-1.4-4.5-3.7-6.2.2 2-1 3.1-2.2 3.8.3-3.5-1.6-6.5-4.4-8.3.1 3.1-2.7 5.2-2.7 9 0 4.5 2.7 8 6 8z"></path></svg>',
    top_rated: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M8 21h8"></path><path d="M12 17v4"></path><path d="M7 4h10v4a5 5 0 0 1-10 0V4z"></path><path d="M7 6H4v2a4 4 0 0 0 4 4"></path><path d="M17 6h3v2a4 4 0 0 1-4 4"></path></svg>',
    trending_month: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 17 9 11 13 15 21 7"></polyline><polyline points="15 7 21 7 21 13"></polyline></svg>',
    recent_releases: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="17" rx="2"></rect><line x1="16" y1="2" x2="16" y2="6"></line><line x1="8" y1="2" x2="8" y2="6"></line><line x1="3" y1="10" x2="21" y2="10"></line><polyline points="12 13 12 16 14 17"></polyline></svg>'
};
const regionLabelMap = {
    none: 'All', hollywood: 'Hollywood', bollywood: 'Bollywood',
    tamil_telugu: 'South', anime: 'Anime', korean: 'Korean',
    chinese: 'Chinese', japanese_live: 'Japanese Live Action',
    animation: 'Cartoons / Animation', documentary_reality: 'Documentary / Reality'
};

function syncPresetPanel() {
    const modeVal   = discoverPreset.value;
    const regionVal = discoverRegion.value;

    const isSearchMode = modeVal === 'search';
    if (discoverForm) discoverForm.classList.toggle('discover-browse-mode', !isSearchMode);
    if (discoverQuery) {
        discoverQuery.hidden = !isSearchMode;
        discoverQuery.required = isSearchMode;
        discoverQuery.setAttribute('aria-hidden', String(!isSearchMode));
    }

    // Update button label: "Popular · Bollywood" or just "Search"
    const modeText   = modeLabelMap[modeVal]   || modeVal;
    const regionText = regionLabelMap[regionVal] || 'All';
    if (dcPresetModeIcon) dcPresetModeIcon.innerHTML = modeIconMap[modeVal] || modeIconMap.search;
    if (dcPresetLabel) dcPresetLabel.textContent = modeText;
    if (dcPresetRegionLabel) dcPresetRegionLabel.textContent = regionText;

    // Highlight active rows per group independently
    dcPresetMenu.querySelectorAll('.dc-preset-row').forEach(row => {
        const group = row.dataset.group;
        const val   = row.dataset.value;
        row.classList.toggle('active',
            (group === 'mode'   && val === modeVal) ||
            (group === 'region' && val === regionVal)
        );
    });
}
syncPresetPanel();

// Panel open/close
if (dcPresetBtn && dcPresetMenu) {
    dcPresetBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        const isOpen = dcPresetMenu.classList.toggle('open');
        dcPresetBtn.setAttribute('aria-expanded', String(isOpen));
    });

    dcPresetMenu.addEventListener('click', (e) => {
        e.stopPropagation();
        const row = e.target.closest('.dc-preset-row');
        if (!row) return;
        const group = row.dataset.group;
        const val   = row.dataset.value;

        if (group === 'mode') {
            discoverPreset.value = val;
            localStorage.setItem('discoverPreset', val);
        } else {
            discoverRegion.value = val;
            localStorage.setItem('discoverRegion', val);
        }
        syncPresetPanel();

        // Don't close — let user pick from both groups, then click outside
        // Trigger search immediately if not in search mode (or region changed)
        const isSearchMode = discoverPreset.value === 'search';
        if (!isSearchMode) {
            performDiscoverSearch(1);
        } else if (group === 'region' && discoverQuery.value.trim()) {
            performDiscoverSearch(1);
        } else if (isSearchMode && !discoverQuery.value.trim()) {
            discoverResults.innerHTML = '';
            discoverStatus.textContent = '';
            discoverPagination.hidden = true;
        }
    });

    document.addEventListener('click', (e) => {
        if (!e.target.closest('#dcPresetDropdown')) {
            dcPresetMenu.classList.remove('open');
            dcPresetBtn.setAttribute('aria-expanded', 'false');
        }
    });
}

function escapeHtml(value) {
    return String(value || '').replace(/[&<>'"]/g, c => (
        {'&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;'}[c]
    ));
}

function renderDiscoverResults(results) {
    if (!results.length) {
        discoverResults.innerHTML = '<p class="discover-empty">No movies or shows found.</p>';
        return;
    }
    discoverResults.innerHTML = results.map(item => `
        <article class="discover-card">
            <h2 class="discover-card-title">${escapeHtml(item.title)}</h2>
            <div class="discover-card-body">
                <img src="${escapeHtml(item.poster_url)}" alt="${escapeHtml(item.title)} poster" onerror="this.style.visibility='hidden'">
                <div class="discover-card-content">
                <div class="discover-card-topline">
                    <span class="discover-type">${item.media_type === 'movie' ? 'Movie' : 'TV Show'}</span>
                </div>
                <span class="discover-meta">${item.year ? `${escapeHtml(item.year)} · ` : ''}★ ${item.rating.toFixed(1)}</span>
                <p class="discover-overview">${escapeHtml(item.overview)}</p>
                <div class="discover-card-actions">
                    <button class="modal-btn ${item.media_type === 'movie' ? 'modal-btn-orange' : 'modal-btn-blue'} discover-add-button${item.already_added ? ' discover-added' : ''}" data-tmdb-id="${item.tmdb_id}" data-media-type="${item.media_type}" title="${item.already_added ? 'Already added' : `Add to ${item.media_type === 'movie' ? 'Movies' : 'Shows'}`}" aria-label="${item.already_added ? 'Already added' : `Add to ${item.media_type === 'movie' ? 'Movies' : 'Shows'}`}"${item.already_added ? ' disabled' : ''}>
                        ${item.already_added
                            ? '<svg viewBox="0 0 24 24" aria-hidden="true"><polyline points="20 6 9 17 4 12"></polyline></svg>'
                            : '<svg viewBox="0 0 24 24" aria-hidden="true"><line x1="12" y1="5" x2="12" y2="19"></line><line x1="5" y1="12" x2="19" y2="12"></line></svg>'}
                    </button>
                    <a class="modal-btn modal-btn-dark discover-external-button" href="${item.media_type === 'movie' ? `https://www.themoviedb.org/movie/${encodeURIComponent(item.tmdb_id)}` : (item.tvmaze_id ? `https://www.tvmaze.com/shows/${encodeURIComponent(item.tvmaze_id)}` : `https://www.tvmaze.com/search?q=${encodeURIComponent(item.title)}`)}" target="_blank" rel="noopener noreferrer" title="Open ${item.media_type === 'movie' ? 'on TMDb' : 'on TVMaze'}" aria-label="Open ${item.media_type === 'movie' ? 'on TMDb' : 'on TVMaze'}">
                        <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M14 3h7v7"></path><path d="M10 14 21 3"></path><path d="M21 14v5a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5"></path></svg>
                    </a>
                    <a class="modal-btn modal-btn-red discover-external-button" href="https://www.youtube.com/results?search_query=${encodeURIComponent(`${item.title} Trailer`)}" target="_blank" rel="noopener noreferrer" title="Search YouTube for ${escapeHtml(item.title)} Trailer" aria-label="Search YouTube for ${escapeHtml(item.title)} Trailer">
                        <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M22.54 6.42a2.78 2.78 0 0 0-1.94-2C18.88 4 12 4 12 4s-6.88 0-8.6.46a2.78 2.78 0 0 0-1.94 2A29 29 0 0 0 1 11.75a29 29 0 0 0 .46 5.33A2.78 2.78 0 0 0 3.4 19c1.72.46 8.6.46 8.6.46s6.88 0 8.6-.46a2.78 2.78 0 0 0 1.94-2 29 29 0 0 0 .46-5.25 29 29 0 0 0-.46-5.33Z"></path><polygon points="9.75 15.02 15.5 11.75 9.75 8.48 9.75 15.02"></polygon></svg>
                    </a>
                </div>
                </div>
            </div>
        </article>
    `).join('');
}

function sortDiscoverResults(results) {
    const sorted = [...results];
    if (discoverSort.value === 'relevance') return sorted;
    const dateSorted = sorted.every(item => item.release_date);
    if (dateSorted) {
        sorted.sort((a, b) => {
            const difference = Date.parse(b.release_date) - Date.parse(a.release_date);
            return discoverSort.value === 'oldest' ? -difference : difference;
        });
        return sorted;
    }
    sorted.sort((a, b) => {
        const ay = Number.parseInt(a.year, 10);
        const by = Number.parseInt(b.year, 10);
        const aNaN = Number.isNaN(ay);
        const bNaN = Number.isNaN(by);
        if (aNaN !== bNaN) return aNaN ? 1 : -1;
        if (aNaN && bNaN) return 0;
        return discoverSort.value === 'oldest' ? ay - by : by - ay;
    });
    return sorted;
}

function updateDiscoverPagination(data) {
    discoverPagination.hidden = !(data.has_previous || data.has_next);
    discoverPrevious.disabled = !data.has_previous;
    discoverNext.disabled     = !data.has_next;
    discoverPageLabel.textContent = `Page ${data.page}`;
}

discoverSort.addEventListener('change', () => {
    localStorage.setItem('discoverSort', discoverSort.value);
    renderDiscoverResults(sortDiscoverResults(discoverItems));
});

discoverLimit.addEventListener('change', () => {
    const limit = Math.max(1, Math.min(100, Number.parseInt(discoverLimit.value, 10) || 20));
    discoverLimit.value = limit;
    localStorage.setItem('discoverLimit', limit);
});

async function performDiscoverSearch(page = 1) {
    const query = discoverQuery.value.trim();
    if (!query && discoverPreset.value === 'search') {
        discoverStatus.textContent = 'Enter a title or choose a discovery mode.';
        return;
    }
    discoverStatus.textContent = 'Searching TMDb...';
    discoverResults.innerHTML = '';
    try {
        const limit = Math.max(1, Math.min(100, Number.parseInt(discoverLimit.value, 10) || 20));
        discoverLimit.value = limit;
        localStorage.setItem('discoverLimit', limit);
        localStorage.setItem('discoverType',   discoverType.value);
        localStorage.setItem('discoverPreset', discoverPreset.value);
        localStorage.setItem('discoverRegion', discoverRegion.value);
        discoverPage = page;
        const url = `/api/discover/search?q=${encodeURIComponent(query)}&type=${discoverType.value}&preset=${discoverPreset.value}&region=${discoverRegion.value}&limit=${limit}&page=${page}`;
        const response = await fetch(url);
        const data = await response.json();
        if (!response.ok || !data.success) throw new Error(data.message || 'Search failed');
        discoverItems = data.results;
        discoverStatus.textContent = `${data.results.length} result${data.results.length === 1 ? '' : 's'} shown of ${data.total_results} found`;
        renderDiscoverResults(sortDiscoverResults(discoverItems));
        updateDiscoverPagination(data);
    } catch (error) {
        discoverStatus.textContent = error.message;
        discoverResults.innerHTML = '';
        discoverPagination.hidden = true;
    }
}

discoverForm.addEventListener('submit', event => {
    event.preventDefault();
    performDiscoverSearch();
});

discoverType.addEventListener('change', () => {
    localStorage.setItem('discoverType', discoverType.value);
    if (discoverQuery.value.trim() || discoverPreset.value !== 'search') performDiscoverSearch(1);
});

discoverPrevious.addEventListener('click', () => performDiscoverSearch(discoverPage - 1));
discoverNext.addEventListener('click',     () => performDiscoverSearch(discoverPage + 1));

discoverResults.addEventListener('click', async event => {
    const button = event.target.closest('.discover-add-button');
    if (!button) return;
    button.disabled = true;
    button.innerHTML = '<svg class="discover-loading-icon" viewBox="0 0 24 24" aria-hidden="true"><polyline points="23 4 23 10 18 10"></polyline><polyline points="1 20 1 14 6 14"></polyline><path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"></path></svg>';
    button.title = 'Adding...';
    button.setAttribute('aria-label', 'Adding...');
    try {
        const response = await fetch('/api/discover/add', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ tmdb_id: button.dataset.tmdbId, media_type: button.dataset.mediaType })
        });
        const data = await response.json();
        if (!response.ok || !data.success) throw new Error(data.message || 'Unable to add item');
        button.innerHTML = '<svg viewBox="0 0 24 24" aria-hidden="true"><polyline points="20 6 9 17 4 12"></polyline></svg>';
        button.title = 'Already added';
        button.setAttribute('aria-label', 'Already added');
        button.classList.add('discover-added');
        discoverStatus.textContent = data.message;
    } catch (error) {
        button.disabled = false;
        button.innerHTML = '<svg viewBox="0 0 24 24" aria-hidden="true"><line x1="12" y1="5" x2="12" y2="19"></line><line x1="5" y1="12" x2="19" y2="12"></line></svg>';
        button.title = `Add to ${button.dataset.mediaType === 'movie' ? 'Movies' : 'Shows'}`;
        button.setAttribute('aria-label', button.title);
        discoverStatus.textContent = error.message;
    }
});
