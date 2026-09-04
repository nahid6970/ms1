// Movies page functions
function openAddMovieModal() {
    document.getElementById('addMovieModal').style.display = 'block';
    document.body.classList.add('modal-open');
}

function closeAddMovieModal() {
    document.getElementById('addMovieModal').style.display = 'none';
    document.body.classList.remove('modal-open');
}

function closeEditMovieModal() {
    document.getElementById('editMovieModal').style.display = 'none';
    document.body.classList.remove('modal-open');
}

async function openEditMovieModal(movieId) {
    const response = await fetch(`/api/movie/${movieId}`);
    const movie = await response.json();

    document.getElementById('editMovieId').value = movie.id;
    document.getElementById('editMovieTitle').value = movie.title;
    document.getElementById('editMovieYear').value = movie.year || '';
    document.getElementById('editMovieCoverImage').value = movie.cover_image || '';
    document.getElementById('editMovieDirectoryPath').value = movie.directory_path || '';
    document.getElementById('editMovieStatus').value = movie.status || 'Downloaded';

    // Set the rating radio button
    const ratingRadios = document.querySelectorAll('#editMovieModal input[name="rating"]');
    ratingRadios.forEach(radio => {
        radio.checked = false;
    });
    if (movie.rating !== null && movie.rating !== undefined && movie.rating !== '') {
        ratingRadios.forEach(radio => {
            if (radio.value === String(movie.rating)) {
                radio.checked = true;
            }
        });
    }

    // Save scroll position before opening modal
    localStorage.setItem('scrollPosition', window.scrollY);

    document.getElementById('editMovieModal').style.display = 'block';
    document.body.classList.add('modal-open');
}

async function syncRadarrMovies(event) {
    if (event) event.preventDefault();
    const btn = document.querySelector('.radarr-sync-button');
    const originalHTML = btn.innerHTML;

    btn.innerHTML = '<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="spin"><polyline points="23 4 23 10 18 10"></polyline><polyline points="1 20 1 14 6 14"></polyline><path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"></path></svg>';
    btn.style.pointerEvents = 'none';

    try {
        const response = await fetch('/api/radarr/sync', { method: 'POST' });
        const data = await response.json();
        if (data.success) {
            alert(data.message);
            location.reload();
        } else {
            alert('Sync failed: ' + data.message);
            btn.innerHTML = originalHTML;
            btn.style.pointerEvents = 'auto';
        }
    } catch (error) {
        console.error('Error syncing Radarr:', error);
        alert('Error syncing with Radarr');
        btn.innerHTML = originalHTML;
        btn.style.pointerEvents = 'auto';
    }
}

async function refreshMovieMetadata(event, movieId, btn) {
    if (event) event.stopPropagation();
    const originalHTML = btn.innerHTML;
    btn.disabled = true;
    btn.innerHTML = '<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="spin"><polyline points="23 4 23 10 17 10"></polyline><path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"></path></svg>';
    btn.title = 'Updating metadata...';
    try {
        const response = await fetch(`/api/movie/${movieId}/refresh-metadata`, { method: 'POST' });
        const data = await response.json();
        if (!response.ok || !data.success) throw new Error(data.message || 'Unable to update metadata');
        location.reload();
    } catch (error) {
        console.error('Error refreshing movie metadata:', error);
        alert(error.message || 'Error updating movie metadata');
        btn.innerHTML = originalHTML;
        btn.disabled = false;
        btn.title = 'Update metadata from TMDb';
    }
}

async function toggleMovieWatched(movieId, btn) {
    try {
        const response = await fetch(`/api/movie/${movieId}/watched`, { method: 'POST' });
        const data = await response.json();
        if (data.success) {
            const card = btn.closest('.movie-card');
            const statusEl = card.querySelector('.movie-status');
            if (data.watched) {
                card.classList.add('completed');
                statusEl.textContent = 'Watched';
                statusEl.classList.add('all-episodes-watched');
                statusEl.classList.remove('no-episodes-watched');
                btn.innerHTML = '<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>';
                btn.title = 'Mark Unwatched';
            } else {
                card.classList.remove('completed');
                statusEl.textContent = 'Unwatched';
                statusEl.classList.remove('all-episodes-watched');
                statusEl.classList.add('no-episodes-watched');
                btn.innerHTML = '<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>';
                btn.title = 'Mark Watched';
            }
        }
    } catch (error) {
        console.error('Error toggling movie watched:', error);
    }
}

async function deleteMovie(movieId, btn) {
    if (confirm('Are you sure you want to delete this movie?')) {
        try {
            const response = await fetch(`/api/movie/${movieId}/delete`, { method: 'POST' });
            const data = await response.json();
            if (data.success) {
                const card = btn.closest('.movie-card');
                card.style.opacity = '0.4';
                card.style.pointerEvents = 'none';
                setTimeout(() => card.remove(), 400);
            }
        } catch (error) {
            console.error('Error deleting movie:', error);
        }
    }
}

function openMovieFolder(event, movieId) {
    event.preventDefault();

    fetch(`/api/movie/${movieId}/open_folder`)
        .then(response => response.json())
        .then(data => {
            if (!data.success) {
                alert(`Failed to open folder: ${data.message}`);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Failed to open folder due to network error');
        });
}

document.addEventListener('DOMContentLoaded', () => {
    // Add movie form
    const addForm = document.getElementById('addMovieForm');
    if (addForm) {
        addForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(addForm);
            try {
                const response = await fetch('/api/movies/add', { method: 'POST', body: formData });
                const data = await response.json();
                if (data.success) {
                    location.reload();
                } else {
                    alert('Failed to add movie');
                }
            } catch (error) {
                console.error('Error adding movie:', error);
                alert('Error adding movie');
            }
        });
    }

    // Edit movie form
    const editForm = document.getElementById('editMovieForm');
    if (editForm) {
        editForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const movieId = document.getElementById('editMovieId').value;
            const formData = new FormData(editForm);
            try {
                const response = await fetch(`/api/movie/${movieId}`, { method: 'POST', body: formData });
                const data = await response.json();
                if (data.success) {
                    location.reload();
                } else {
                    alert('Failed to save movie');
                }
            } catch (error) {
                console.error('Error saving movie:', error);
                alert('Error saving movie');
            }
        });
    }

    // Live search for movies
    const searchInput = document.getElementById('movieSearch');
    const searchClear = document.getElementById('movieSearchClear');

    function filterMovies(query) {
        query = query.toLowerCase().trim();
        document.querySelectorAll('.movie-card').forEach(card => {
            const title = (card.getAttribute('data-title') || '').toLowerCase();
            const year = (card.getAttribute('data-year') || '').toLowerCase();
            if (title.includes(query) || year.includes(query)) {
                card.style.display = '';
            } else {
                card.style.display = 'none';
            }
        });

        if (searchClear) {
            searchClear.style.display = query.length > 0 ? 'block' : 'none';
        }
    }

    if (searchInput) {
        searchInput.addEventListener('input', function(e) {
            filterMovies(e.target.value);
        });
    }

    if (searchClear) {
        searchClear.addEventListener('click', function() {
            searchInput.value = '';
            filterMovies('');
            searchInput.focus();
        });
    }

    // Close movie modals when clicking outside
    document.addEventListener('click', (event) => {
        const addMovieModal = document.getElementById('addMovieModal');
        const editMovieModal = document.getElementById('editMovieModal');
        if (event.target == addMovieModal) {
            addMovieModal.style.display = 'none';
            document.body.classList.remove('modal-open');
        } else if (event.target == editMovieModal) {
            editMovieModal.style.display = 'none';
            document.body.classList.remove('modal-open');
        }
    });
});
