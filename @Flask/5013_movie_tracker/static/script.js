function openAddMovieModal() {
    document.getElementById('addMovieModal').style.display = 'block';
    document.body.classList.add('modal-open');
}

function closeAddMovieModal() {
    document.getElementById('addMovieModal').style.display = 'none';
    document.body.classList.remove('modal-open');
}

async function openEditMovieModal(movieId) {
    const response = await fetch(`/edit_movie/${movieId}`);
    const movie = await response.json();

    document.getElementById('editMovieId').value = movie.id;
    document.getElementById('editMovieTitle').value = movie.title;
    document.getElementById('editMovieYear').value = movie.year;
    document.getElementById('editMovieCoverImage').value = movie.cover_image;
    document.getElementById('editMovieDirectoryPath').value = movie.directory_path || '';
    document.getElementById('editMovieRadarrId').value = movie.radarr_id || '';

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

    document.getElementById('editMovieForm').action = `/edit_movie/${movie.id}`;
    document.getElementById('editMovieModal').style.display = 'block';
    document.body.classList.add('modal-open');
}

function closeEditMovieModal() {
    document.getElementById('editMovieModal').style.display = 'none';
    document.body.classList.remove('modal-open');
}

function toggleSeen(movieId) {
    fetch(`/toggle_seen/${movieId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    }).then(response => {
        if (response.ok) {
            location.reload();
        }
    });
}

function openSettingsModal() {
    document.getElementById('settingsModal').style.display = 'block';
    document.body.classList.add('modal-open');
}

function closeSettingsModal() {
    document.getElementById('settingsModal').style.display = 'none';
    document.body.classList.remove('modal-open');
}

function openFolder(movieId) {
    fetch(`/open_movie_folder/${movieId}`)
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
    const tableViewToggle = document.getElementById('tableViewToggle');
    const defaultHomePageSelect = document.getElementById('defaultHomePage');
    const html = document.documentElement;

    const isTableViewEnabled = localStorage.getItem('tableViewEnabled') === 'true';
    if (isTableViewEnabled) {
        html.classList.add('table-view-active');
        if (tableViewToggle) tableViewToggle.checked = true;
    }

    const defaultHomePage = localStorage.getItem('defaultHomePage') || 'default';
    if (defaultHomePageSelect) defaultHomePageSelect.value = defaultHomePage;

    if (tableViewToggle) {
        tableViewToggle.addEventListener('change', () => {
            if (tableViewToggle.checked) {
                html.classList.add('table-view-active');
                localStorage.setItem('tableViewEnabled', 'true');
            } else {
                html.classList.remove('table-view-active');
                localStorage.setItem('tableViewEnabled', 'false');
            }
        });
    }

    if (defaultHomePageSelect) {
        defaultHomePageSelect.addEventListener('change', () => {
            localStorage.setItem('defaultHomePage', defaultHomePageSelect.value);
        });
    }

    // Live Search Functionality
    const searchInput = document.querySelector('.search-form input[name="query"]');
    const searchClear = document.getElementById('searchClear');

    function filterMovies(query) {
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

        if (searchClear) {
            searchClear.style.display = query.length > 0 ? 'block' : 'none';
        }
    }

    if (searchInput) {
        if (searchClear) {
            searchClear.style.display = searchInput.value.length > 0 ? 'block' : 'none';
        }

        searchInput.addEventListener('input', function(e) {
            filterMovies(e.target.value);
        });

        if (searchClear) {
            searchClear.addEventListener('click', function() {
                searchInput.value = '';
                filterMovies('');
                searchInput.focus();
            });
        }
    }

    document.querySelectorAll('.show-card').forEach(card => {
        card.addEventListener('click', (event) => {
            if (!event.target.closest('.show-card-buttons') && 
                !event.target.closest('.folder-button-cell')) {
                const movieId = card.dataset.movieId;
                if (movieId) {
                    window.location.href = `/movie/${movieId}`;
                }
            }
        });
    });

    document.querySelectorAll('.btn-delete').forEach(button => {
        button.addEventListener('click', (event) => {
            event.preventDefault();
            event.stopPropagation();
            const movieId = button.closest('.show-card').dataset.movieId;
            if (confirm('Are you sure you want to delete this movie?')) {
                fetch(`/delete_movie/${movieId}`, {
                    method: 'GET',
                }).then(response => {
                    if (response.ok) {
                        button.closest('.show-card').remove();
                    } else {
                        alert('Failed to delete movie.');
                    }
                });
            }
        });
    });

    const editMovieForm = document.getElementById('editMovieForm');
    if (editMovieForm) {
        editMovieForm.addEventListener('submit', function(event) {
            event.preventDefault();
            const formData = new FormData(this);
            const action = this.action;
            fetch(action, {
                method: 'POST',
                body: formData
            }).then(response => {
                if (response.ok) {
                    closeEditMovieModal();
                    location.reload();
                } else {
                    alert('Failed to save changes.');
                }
            }).catch(error => {
                console.error('Error:', error);
                alert('Failed to save changes due to a network error.');
            });
        });
    }
});

function toggleSortMenu() {
    const dropdown = document.getElementById('sortMenuDropdown');
    const button = document.querySelector('.sort-menu-button');
    dropdown.classList.toggle('show');
    button.classList.toggle('active');
}

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

window.onclick = function(event) {
    const addModal = document.getElementById('addMovieModal');
    const editMovieModal = document.getElementById('editMovieModal');
    const settingsModal = document.getElementById('settingsModal');
    if (event.target == addModal) {
        addModal.style.display = 'none';
        document.body.classList.remove('modal-open');
    } else if (event.target == editMovieModal) {
        editMovieModal.style.display = 'none';
        document.body.classList.remove('modal-open');
    } else if (event.target == settingsModal) {
        settingsModal.style.display = 'none';
        document.body.classList.remove('modal-open');
    }
}
