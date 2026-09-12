(() => {
    let items = [];
    let filter = 'all';
    let timeFilter = 'all';
    let skipComplete = false;
    const body = document.getElementById('agendaTableBody');
    const search = document.getElementById('agendaSearch');

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

    function render() {
        const query = (search.value || '').trim().toLocaleLowerCase();
        const visible = items.filter(item => {
            const type = item.type.toLocaleLowerCase();
            const filterMatch = filter === 'all' || filter === type || (filter === 'scheduled' && !item.completed) || (filter === 'complete' && item.completed);
            const timeMatch = timeFilter === 'all' || (timeFilter === 'today' && isToday(item.release_date)) || (timeFilter === 'afterwards' && isAfterwards(item.release_date));
            return filterMatch && timeMatch && (!skipComplete || !item.completed) && (!query || item.title.toLocaleLowerCase().includes(query));
        });
        if (!visible.length) {
            body.innerHTML = '<tr><td colspan="8" class="agenda-empty">No matching scheduled items.</td></tr>';
            return;
        }
        body.innerHTML = visible.map(item => {
            const typeClass = item.type === 'TV' ? 'agenda-type-tv' : 'agenda-type-movie';
            const statusClass = item.completed ? 'agenda-status-complete' : 'agenda-status-scheduled';
            const action = item.completed ? '' : `<button class="agenda-run" data-id="${item.id}" data-type="${item.type}" title="Run now">▶</button>`;
            return `<tr>
                <td class="agenda-title">${esc(item.title)}</td>
                <td><span class="agenda-badge ${typeClass}">${item.type}</span></td>
                <td class="agenda-date">${item.release_date ? formatDate(item.release_date) : 'Not available'}</td>
                <td>${esc(item.task)}</td><td>${esc(item.cadence)}</td>
                <td><span class="agenda-badge ${statusClass}">${esc(item.status)}</span></td>
                <td class="agenda-details">${esc(item.details)}</td><td>${action}</td>
            </tr>`;
        }).join('');
    }

    async function load() {
        body.innerHTML = '<tr><td colspan="8" class="agenda-empty">Loading agenda...</td></tr>';
        try {
            const response = await fetch('/api/agenda');
            const data = await response.json();
            if (!response.ok || !data.success) throw new Error(data.message || 'Unable to load agenda');
            items = data.items || [];
            render();
        } catch (error) { body.innerHTML = `<tr><td colspan="8" class="agenda-empty agenda-error">${esc(error.message)}</td></tr>`; }
    }

    document.querySelectorAll('.agenda-filter:not(.agenda-skip-complete)').forEach(button => button.addEventListener('click', () => {
        if (button.classList.contains('agenda-time-filter')) {
            document.querySelectorAll('.agenda-time-filter').forEach(item => item.classList.remove('active'));
            button.classList.add('active'); timeFilter = button.dataset.timeFilter; render(); return;
        }
        document.querySelectorAll('.agenda-filter:not(.agenda-time-filter):not(.agenda-skip-complete)').forEach(item => item.classList.remove('active'));
        button.classList.add('active'); filter = button.dataset.filter; render();
    }));
    document.querySelector('.agenda-skip-complete').addEventListener('click', event => {
        skipComplete = !skipComplete;
        event.currentTarget.classList.toggle('active', skipComplete);
        event.currentTarget.setAttribute('aria-pressed', String(skipComplete));
        render();
    });
    search.addEventListener('input', render);
    document.getElementById('agendaRefresh').addEventListener('click', load);
    body.addEventListener('click', async event => {
        const button = event.target.closest('.agenda-run');
        if (!button) return;
        button.disabled = true;
        const endpoint = button.dataset.type === 'TV' ? `/api/show/${button.dataset.id}/episodes/run_scheduled` : `/api/movie/${button.dataset.id}/metadata/run_scheduled`;
        try { await fetch(endpoint, {method:'POST'}); await load(); } catch (_) { button.disabled = false; }
    });
    load();
})();
