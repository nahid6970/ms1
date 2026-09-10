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
let discoverItems = [];
let discoverPage  = 1;

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
    search: 'Search', popular: 'Popular', top_rated: 'Top Rated', trending_month: 'Trending'
};
const regionLabelMap = {
    none: '', hollywood: 'Hollywood', bollywood: 'Bollywood',
    tamil_telugu: 'South', anime: 'Anime'
};

function syncPresetPanel() {
    const modeVal   = discoverPreset.value;
    const regionVal = discoverRegion.value;

    // Update button label: "Popular · Bollywood" or just "Search"
    const modeText   = modeLabelMap[modeVal]   || modeVal;
    const regionText = regionLabelMap[regionVal] || '';
    if (dcPresetLabel) dcPresetLabel.textContent = regionText ? `${modeText} · ${regionText}` : modeText;

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
                <button class="modal-btn ${item.media_type === 'movie' ? 'modal-btn-orange' : 'modal-btn-blue'} discover-add-button${item.already_added ? ' discover-added' : ''}" data-tmdb-id="${item.tmdb_id}" data-media-type="${item.media_type}" title="${item.already_added ? 'Already added' : `Add to ${item.media_type === 'movie' ? 'Movies' : 'Shows'}`}" aria-label="${item.already_added ? 'Already added' : `Add to ${item.media_type === 'movie' ? 'Movies' : 'Shows'}`}"${item.already_added ? ' disabled' : ''}>
                    ${item.already_added
                        ? '<svg viewBox="0 0 24 24" aria-hidden="true"><polyline points="20 6 9 17 4 12"></polyline></svg>'
                        : '<svg viewBox="0 0 24 24" aria-hidden="true"><line x1="12" y1="5" x2="12" y2="19"></line><line x1="5" y1="12" x2="19" y2="12"></line></svg>'}
                </button>
                </div>
            </div>
        </article>
    `).join('');
}

function sortDiscoverResults(results) {
    const sorted = [...results];
    if (discoverSort.value === 'relevance') return sorted;
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
