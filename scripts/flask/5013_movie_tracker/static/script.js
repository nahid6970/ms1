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

    // Set the rating radio button
    const ratingRadios = document.querySelectorAll('#editMovieModal input[name="rating"]');
    
    // First, clear all radio buttons
    ratingRadios.forEach(radio => {
        radio.checked = false;
    });
    
    // Then set the correct one if rating exists
    if (movie.rating !== null && movie.rating !== undefined && movie.rating !== '') {
        ratingRadios.forEach(radio => {
            // Convert both values to strings for comparison to handle different data types
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

// Settings Modal Functions
function openSettingsModal() {
    document.getElementById('settingsModal').style.display = 'block';
    document.body.classList.add('modal-open');
}

function closeSettingsModal() {
    document.getElementById('settingsModal').style.display = 'none';
    document.body.classList.remove('modal-open');
}

// Server-side Folder Opening Function
function openFolder(movieId) {
    fetch(`/open_movie_folder/${movieId}`)
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

// Toggle Table View and Default Home Page
document.addEventListener('DOMContentLoaded', () => {
    const tableViewToggle = document.getElementById('tableViewToggle');
    const defaultHomePageSelect = document.getElementById('defaultHomePage');
    const html = document.documentElement;

    // Load table view preference from localStorage
    const isTableViewEnabled = localStorage.getItem('tableViewEnabled') === 'true';
    if (isTableViewEnabled) {
        html.classList.add('table-view-active');
        tableViewToggle.checked = true;
    }

    // Load default home page preference from localStorage
    const defaultHomePage = localStorage.getItem('defaultHomePage') || 'default';
    defaultHomePageSelect.value = defaultHomePage;

    // Save table view preference to localStorage on change
    tableViewToggle.addEventListener('change', () => {
        if (tableViewToggle.checked) {
            html.classList.add('table-view-active');
            localStorage.setItem('tableViewEnabled', 'true');
        } else {
            html.classList.remove('table-view-active');
            localStorage.setItem('tableViewEnabled', 'false');
        }
    });

    // Save default home page preference to localStorage on change
    defaultHomePageSelect.addEventListener('change', () => {
        localStorage.setItem('defaultHomePage', defaultHomePageSelect.value);
    });



    // Add click listener for movie cards
    document.querySelectorAll('.movie-card').forEach(card => {
        card.addEventListener('click', (event) => {
            // Check if the click wasn't on an edit/delete button
            if (!event.target.classList.contains('btn-edit') &&
                !event.target.classList.contains('btn-delete')) {
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
            const movieId = button.dataset.movieId;
            if (confirm('Are you sure you want to delete this movie?')) {
                fetch(`/delete_movie/${movieId}`, {
                    method: 'GET', // Or 'DELETE', but the route is defined with GET
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