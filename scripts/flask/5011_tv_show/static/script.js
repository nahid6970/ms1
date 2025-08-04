function openAddShowModal() {
    document.getElementById('addShowModal').style.display = 'block';
    document.body.classList.add('modal-open');
}

function closeAddShowModal() {
    document.getElementById('addShowModal').style.display = 'none';
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

    // Set the rating radio button
    const ratingRadios = document.querySelectorAll('#editShowModal input[name="rating"]');
    ratingRadios.forEach(radio => {
        if (parseInt(radio.value) === show.rating) {
            radio.checked = true;
        } else {
            radio.checked = false;
        }
    });

    document.getElementById('editShowForm').action = `/edit_show/${show.id}`;

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

// Settings Modal Functions
function openSettingsModal() {
    document.getElementById('settingsModal').style.display = 'block';
    document.body.classList.add('modal-open');
}

function closeSettingsModal() {
    document.getElementById('settingsModal').style.display = 'none';
    document.body.classList.remove('modal-open');
}

// Toggle Table View
document.addEventListener('DOMContentLoaded', () => {
    const tableViewToggle = document.getElementById('tableViewToggle');
    const body = document.body;

    // Load preference from localStorage
    const isTableViewEnabled = localStorage.getItem('tableViewEnabled') === 'true';
    if (isTableViewEnabled) {
        body.classList.add('table-view-active');
        tableViewToggle.checked = true;
    }

    // Save preference to localStorage on change
    tableViewToggle.addEventListener('change', () => {
        if (tableViewToggle.checked) {
            body.classList.add('table-view-active');
            localStorage.setItem('tableViewEnabled', 'true');
        } else {
            body.classList.remove('table-view-active');
            localStorage.setItem('tableViewEnabled', 'false');
        }
    });

    // Add click listener for show cards
    document.querySelectorAll('.show-card').forEach(card => {
        card.addEventListener('click', (event) => {
            // Check if the click wasn't on an edit/delete button
            if (!event.target.classList.contains('btn-edit') &&
                !event.target.classList.contains('btn-delete')) {
                const showId = card.dataset.showId;
                if (showId) {
                    window.location.href = `/show/${showId}`;
                }
            }
        });
    });
});

// Close modal if user clicks outside of it
window.onclick = function(event) {
    const addModal = document.getElementById('addShowModal');
    const editShowModal = document.getElementById('editShowModal');
    const editEpisodeModal = document.getElementById('editEpisodeModal');
    const settingsModal = document.getElementById('settingsModal');

    if (event.target == addModal) {
        addModal.style.display = 'none';
        document.body.classList.remove('modal-open');
    } else if (event.target == editShowModal) {
        editShowModal.style.display = 'none';
        document.body.classList.remove('modal-open');
    } else if (event.target == editEpisodeModal) {
        editEpisodeModal.style.display = 'none';
        document.body.classList.remove('modal-open');
    } else if (event.target == settingsModal) {
        settingsModal.style.display = 'none';
        document.body.classList.remove('modal-open');
    }
}