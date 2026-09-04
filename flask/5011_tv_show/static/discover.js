const discoverForm = document.getElementById('discoverSearchForm');
const discoverQuery = document.getElementById('discoverQuery');
const discoverType = document.getElementById('discoverType');
const discoverSort = document.getElementById('discoverSort');
const discoverResults = document.getElementById('discoverResults');
const discoverStatus = document.getElementById('discoverStatus');
let discoverItems = [];

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
            <img src="${escapeHtml(item.poster_url)}" alt="${escapeHtml(item.title)} poster" onerror="this.style.visibility='hidden'">
            <div class="discover-card-content">
                <span class="discover-type">${item.media_type === 'movie' ? 'Movie' : 'TV Show'}</span>
                <h2>${escapeHtml(item.title)}</h2>
                <p class="discover-meta">${escapeHtml(item.year || 'Year unknown')} · ★ ${item.rating.toFixed(1)}</p>
                <p class="discover-overview">${escapeHtml(item.overview)}</p>
                <button class="modal-btn ${item.media_type === 'movie' ? 'modal-btn-orange' : 'modal-btn-blue'} discover-add-button" data-tmdb-id="${item.tmdb_id}" data-media-type="${item.media_type}">
                    Add to ${item.media_type === 'movie' ? 'Movies' : 'Shows'}
                </button>
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

discoverSort.addEventListener('change', () => renderDiscoverResults(sortDiscoverResults(discoverItems)));

discoverForm.addEventListener('submit', async event => {
    event.preventDefault();
    const query = discoverQuery.value.trim();
    if (!query) return;
    discoverStatus.textContent = 'Searching TMDb...';
    discoverResults.innerHTML = '';
    try {
        const response = await fetch(`/api/discover/search?q=${encodeURIComponent(query)}&type=${discoverType.value}`);
        const data = await response.json();
        if (!response.ok || !data.success) throw new Error(data.message || 'Search failed');
        discoverItems = data.results;
        discoverStatus.textContent = `${data.results.length} result${data.results.length === 1 ? '' : 's'} found`;
        renderDiscoverResults(sortDiscoverResults(discoverItems));
    } catch (error) {
        discoverStatus.textContent = error.message;
        discoverResults.innerHTML = '';
    }
});

discoverResults.addEventListener('click', async event => {
    const button = event.target.closest('.discover-add-button');
    if (!button) return;
    button.disabled = true;
    button.textContent = 'Adding...';
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
        button.textContent = 'Added';
        button.classList.add('discover-added');
        discoverStatus.textContent = data.message;
    } catch (error) {
        button.disabled = false;
        button.textContent = `Add to ${button.dataset.mediaType === 'movie' ? 'Movies' : 'Shows'}`;
        discoverStatus.textContent = error.message;
    }
});
