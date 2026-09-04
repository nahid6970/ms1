const discoverForm = document.getElementById('discoverSearchForm');
const discoverQuery = document.getElementById('discoverQuery');
const discoverType = document.getElementById('discoverType');
const discoverSort = document.getElementById('discoverSort');
const discoverLimit = document.getElementById('discoverLimit');
const discoverResults = document.getElementById('discoverResults');
const discoverStatus = document.getElementById('discoverStatus');
const discoverPagination = document.getElementById('discoverPagination');
const discoverPrevious = document.getElementById('discoverPrevious');
const discoverNext = document.getElementById('discoverNext');
const discoverPageLabel = document.getElementById('discoverPageLabel');
let discoverItems = [];
let discoverPage = 1;

const savedDiscoverType = localStorage.getItem('discoverType');
const savedDiscoverSort = localStorage.getItem('discoverSort');
const savedDiscoverLimit = localStorage.getItem('discoverLimit');
if (savedDiscoverType) discoverType.value = savedDiscoverType;
if (savedDiscoverSort) discoverSort.value = savedDiscoverSort;
if (savedDiscoverLimit) discoverLimit.value = savedDiscoverLimit;

function escapeHtml(value) {
    return String(value || '').replace(/[&<>'"]/g, character => ({
        '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;'
    }[character]));
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
                <span class="discover-meta">${escapeHtml(item.year || 'Year unknown')} · ★ ${item.rating.toFixed(1)}</span>
                <p class="discover-overview">${escapeHtml(item.overview)}</p>
                <button class="modal-btn ${item.media_type === 'movie' ? 'modal-btn-orange' : 'modal-btn-blue'} discover-add-button${item.already_added ? ' discover-added' : ''}" data-tmdb-id="${item.tmdb_id}" data-media-type="${item.media_type}" title="${item.already_added ? 'Already added' : `Add to ${item.media_type === 'movie' ? 'Movies' : 'Shows'}`}" aria-label="${item.already_added ? 'Already added' : `Add to ${item.media_type === 'movie' ? 'Movies' : 'Shows'}`}"${item.already_added ? ' disabled' : ''}>
                    ${item.already_added ? '<svg viewBox="0 0 24 24" aria-hidden="true"><polyline points="20 6 9 17 4 12"></polyline></svg>' : '<svg viewBox="0 0 24 24" aria-hidden="true"><line x1="12" y1="5" x2="12" y2="19"></line><line x1="5" y1="12" x2="19" y2="12"></line></svg>'}
                </button>
                </div>
            </div>
        </article>
    `).join('');
}

function sortDiscoverResults(results) {
    const sorted = [...results];
    if (discoverSort.value === 'relevance') return sorted;
    sorted.sort((first, second) => {
        const firstYear = Number.parseInt(first.year, 10);
        const secondYear = Number.parseInt(second.year, 10);
        const firstKnown = Number.isNaN(firstYear);
        const secondKnown = Number.isNaN(secondYear);
        if (firstKnown !== secondKnown) return firstKnown ? 1 : -1;
        if (firstKnown && secondKnown) return 0;
        return discoverSort.value === 'oldest' ? firstYear - secondYear : secondYear - firstYear;
    });
    return sorted;
}

function updateDiscoverPagination(data) {
    discoverPagination.hidden = !(data.has_previous || data.has_next);
    discoverPrevious.disabled = !data.has_previous;
    discoverNext.disabled = !data.has_next;
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
    if (!query) return;
    discoverStatus.textContent = 'Searching TMDb...';
    discoverResults.innerHTML = '';
    try {
        const limit = Math.max(1, Math.min(100, Number.parseInt(discoverLimit.value, 10) || 20));
        discoverLimit.value = limit;
        localStorage.setItem('discoverLimit', limit);
        localStorage.setItem('discoverType', discoverType.value);
        discoverPage = page;
        const response = await fetch(`/api/discover/search?q=${encodeURIComponent(query)}&type=${discoverType.value}&limit=${limit}&page=${page}`);
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
    if (discoverQuery.value.trim()) performDiscoverSearch(1);
});

discoverPrevious.addEventListener('click', () => performDiscoverSearch(discoverPage - 1));
discoverNext.addEventListener('click', () => performDiscoverSearch(discoverPage + 1));

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
            body: JSON.stringify({
                tmdb_id: button.dataset.tmdbId,
                media_type: button.dataset.mediaType
            })
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
