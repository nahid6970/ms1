(() => {
    let items = [];
    const savedState = (() => { try { return JSON.parse(localStorage.getItem('agendaFilters') || '{}'); } catch (_) { return {}; } })();
    let filter = savedState.filter || 'all';
    let timeFilters = new Set(Array.isArray(savedState.timeFilters) && savedState.timeFilters.length ? savedState.timeFilters : ['all']);
    let skipComplete = !!savedState.skipComplete;
    const body = document.getElementById('agendaTableBody');
    const search = document.getElementById('agendaSearch');
    if (savedState.search) search.value = savedState.search;

    function saveState() {
        localStorage.setItem('agendaFilters', JSON.stringify({filter, timeFilters: [...timeFilters], skipComplete, search: search.value}));
    }

    function syncFilterButtons() {
        document.querySelectorAll('.agenda-time-filter').forEach(button => button.classList.toggle('active', timeFilters.has(button.dataset.timeFilter)));
        document.querySelectorAll('.agenda-filter:not(.agenda-time-filter):not(.agenda-skip-complete)').forEach(button => button.classList.toggle('active', button.dataset.filter === filter));
        const skipButton = document.querySelector('.agenda-skip-complete');
        if (skipButton) { skipButton.classList.toggle('active', skipComplete); skipButton.setAttribute('aria-pressed', String(skipComplete)); }
        const moviePendingButton = document.querySelector('.agenda-movie-pending');
        if (moviePendingButton) { moviePendingButton.classList.toggle('active', filter === 'movie-pending'); moviePendingButton.setAttribute('aria-pressed', String(filter === 'movie-pending')); }
    }

    const esc = value => String(value || '').replace(/[&<>'"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[c]));
    const formatDate = value => {
        if (!value) return '—';
        const date = new Date(value);
        return Number.isNaN(date.getTime()) ? value : `${date.toLocaleDateString(undefined, {day:'2-digit', month:'short', year:'numeric'})} · ${date.toLocaleTimeString(undefined, {hour:'numeric', minute:'2-digit'})}`;
    };

    function isToday(value) {
        if (!value) return false;
        const date = new Date(value);
        const now = new Date();
        return !Number.isNaN(date.getTime()) && date.toDateString() === now.toDateString();
    }

    function isAfterwards(value) {
        if (!value) return false;
        const date = new Date(value);
        const now = new Date();
        return !Number.isNaN(date.getTime()) && date > new Date(now.getFullYear(), now.getMonth(), now.getDate() + 1);
    }

    function renderCadenceIcon(item) {
        const cadence = String(item.cadence || '').toLowerCase();
        if (cadence === 'complete') {
            return '<span class="agenda-detail-cadence agenda-cadence-complete" title="Complete" aria-label="Complete"><svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="9"></circle><path d="m8 12 2.5 2.5L16 9"></path></svg></span>';
        }
        const label = cadence === 'weekly' ? 'Weekly' : cadence === 'monthly' ? 'Monthly' : 'Daily';
        const svg = cadence === 'weekly'
            ? '<svg viewBox="0 0 24 24"><rect x="4" y="5" width="16" height="15" rx="1"></rect><path d="M8 3v4M16 3v4M4 10h16"></path></svg>'
            : cadence === 'monthly'
                ? '<svg viewBox="0 0 24 24"><rect x="4" y="5" width="16" height="15" rx="1"></rect><path d="M8 3v4M16 3v4M4 10h16M8 14h.01M12 14h.01M16 14h.01M8 17h.01M12 17h.01M16 17h.01"></path></svg>'
                : '<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="9"></circle><path d="M12 7v5l3 2"></path></svg>';
        return `<span class="agenda-detail-cadence agenda-cadence-${cadence}" title="${label}" aria-label="${label}">${svg}</span>`;
    }

    function renderDetails(item) {
        if (item.completed) {
            return '';
        }
        const nextRun = item.next_run ? new Date(item.next_run) : null;
        const scheduledDate = nextRun && !Number.isNaN(nextRun.getTime())
            ? `${nextRun.toLocaleDateString(undefined, {day: '2-digit', month: 'short', year: 'numeric'})} · ${nextRun.toLocaleTimeString(undefined, {hour: 'numeric', minute: '2-digit'})}`
            : '';
        return `<span class="agenda-scheduled-text">${scheduledDate}</span>`;
    }

    function render() {
        const query = (search.value || '').trim().toLocaleLowerCase();
        const visible = items.filter(item => {
            const type = item.type.toLocaleLowerCase();
            const filterMatch = filter === 'all' || filter === type || (filter === 'movie-pending' && type === 'movie' && !item.completed) || (filter === 'scheduled' && !item.completed) || (filter === 'complete' && item.completed);
            const timeMatch = timeFilters.has('all') || (timeFilters.has('today') && isToday(item.release_date)) || (timeFilters.has('afterwards') && isAfterwards(item.release_date));
            return filterMatch && timeMatch && (!skipComplete || !item.skip_complete) && (!query || item.title.toLocaleLowerCase().includes(query));
        });
        if (!visible.length) {
        body.innerHTML = '<tr><td colspan="4" class="agenda-empty">No matching scheduled items.</td></tr>';
            return;
        }
        body.innerHTML = visible.map(item => {
            const statusIcon = item.completed
                ? '<span class="agenda-status-icon agenda-status-complete" title="Complete" aria-label="Complete"><svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="9"></circle><path d="m8 12 2.5 2.5L16 9"></path></svg></span>'
                : '<span class="agenda-status-icon agenda-status-scheduled" title="Scheduled" aria-label="Scheduled"><svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="9"></circle><path d="M10 8.5v7l5-3.5z"></path></svg></span>';
            const scheduleAction = item.completed ? '' : `<button class="agenda-title-run agenda-run" data-id="${item.id}" data-type="${item.type}" title="Scheduled run: ${esc(item.next_run || '')} · Run now" aria-label="Run now"><svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="9"></circle><path d="M12 7v5l3 2"></path></svg></button>`;
            const titleIcons = `<span class="agenda-title-icons">${item.completed ? statusIcon : `${scheduleAction}${statusIcon}${renderCadenceIcon(item)}`}</span>`;
            return `<tr>
                <td class="agenda-title ${item.type === 'TV' ? 'agenda-title-tv' : 'agenda-title-movie'}"><span>${esc(item.title)}</span></td>
                <td class="agenda-icon-cell">${titleIcons}</td>
                <td class="agenda-date">${item.release_date ? formatDate(item.release_date) : 'Not available'}</td>
                <td class="agenda-details">${renderDetails(item)}</td>
            </tr>`;
        }).join('');
    }

    async function load() {
        body.innerHTML = '<tr><td colspan="4" class="agenda-empty">Loading agenda...</td></tr>';
        try {
            const response = await fetch('/api/agenda');
            const data = await response.json();
            if (!response.ok || !data.success) throw new Error(data.message || 'Unable to load agenda');
            items = data.items || [];
            render();
        } catch (error) { body.innerHTML = `<tr><td colspan="4" class="agenda-empty agenda-error">${esc(error.message)}</td></tr>`; }
    }

    document.querySelectorAll('.agenda-filter:not(.agenda-skip-complete)').forEach(button => button.addEventListener('click', () => {
        if (button.classList.contains('agenda-time-filter')) {
            const selected = button.dataset.timeFilter;
            if (selected === 'all') {
                timeFilters = new Set(['all']);
            } else {
                timeFilters.delete('all');
                timeFilters.has(selected) ? timeFilters.delete(selected) : timeFilters.add(selected);
                if (!timeFilters.size) timeFilters.add('all');
            }
            saveState(); syncFilterButtons(); render(); return;
        }
        document.querySelectorAll('.agenda-filter:not(.agenda-time-filter):not(.agenda-skip-complete)').forEach(item => item.classList.remove('active'));
        filter = button.dataset.filter === 'movie-pending' && filter === 'movie-pending' ? 'all' : button.dataset.filter;
        syncFilterButtons(); saveState(); render();
    }));
    document.querySelector('.agenda-skip-complete').addEventListener('click', event => {
        skipComplete = !skipComplete;
        saveState();
        event.currentTarget.classList.toggle('active', skipComplete);
        event.currentTarget.setAttribute('aria-pressed', String(skipComplete));
        render();
    });
    search.addEventListener('input', () => { saveState(); render(); });
    document.getElementById('agendaRefresh').addEventListener('click', load);
    body.addEventListener('click', async event => {
        const button = event.target.closest('.agenda-run');
        if (!button) return;
        button.disabled = true;
        const endpoint = button.dataset.type === 'TV' ? `/api/show/${button.dataset.id}/episodes/run_scheduled` : `/api/movie/${button.dataset.id}/metadata/run_scheduled`;
        try { await fetch(endpoint, {method:'POST'}); await load(); } catch (_) { button.disabled = false; }
    });
    syncFilterButtons();
    load();
})();
