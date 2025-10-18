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
    document.getElementById('editShowSonarrUrl').value = show.sonarr_url || '';
    document.getElementById('editShowStatus').value = show.status || 'Continuing';

    // Set the rating radio button
    const ratingRadios = document.querySelectorAll('#editShowModal input[name="rating"]');
    
    // First, clear all radio buttons
    ratingRadios.forEach(radio => {
        radio.checked = false;
    });
    
    // Then set the correct one if rating exists
    if (show.rating !== null && show.rating !== undefined && show.rating !== '') {
        ratingRadios.forEach(radio => {
            // Convert both values to strings for comparison to handle different data types
            if (radio.value === String(show.rating)) {
                radio.checked = true;
            }
        });
    }

    document.getElementById('editShowForm').action = `/edit_show/${show.id}`;

    // Save scroll position before opening modal
    localStorage.setItem('scrollPosition', window.scrollY);

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

// Server-side Folder Opening Function
function openFolderViaServer(event, showId) {
    event.preventDefault(); // Prevent default link behavior
    
    fetch(`/open_folder/${showId}`)
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

    // Restore scroll position if it was saved
    const savedScrollPosition = localStorage.getItem('scrollPosition');
    if (savedScrollPosition !== null) {
        window.scrollTo(0, parseInt(savedScrollPosition));
        localStorage.removeItem('scrollPosition');
    }

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

    // Context Menu functionality
    const contextMenu = document.getElementById('contextMenu');
    const contextEdit = document.getElementById('contextEdit');
    const contextDelete = document.getElementById('contextDelete');
    let currentShowId = null;

    if (contextMenu && contextEdit && contextDelete) {
        // Show context menu on right-click
        document.querySelectorAll('.show-card').forEach(card => {
            card.addEventListener('contextmenu', (event) => {
                event.preventDefault();
                event.stopPropagation();
                
                currentShowId = card.dataset.showId;
                console.log('Right-clicked on show:', currentShowId);
                
                // Position the context menu using clientX/clientY for viewport coordinates
                const x = event.clientX;
                const y = event.clientY;
                
                // Get menu dimensions
                contextMenu.style.display = 'block';
                const menuWidth = contextMenu.offsetWidth;
                const menuHeight = contextMenu.offsetHeight;
                
                // Adjust position if menu would go off screen
                const windowWidth = window.innerWidth;
                const windowHeight = window.innerHeight;
                
                let left = x;
                let top = y;
                
                // Check if menu goes off right edge
                if (x + menuWidth > windowWidth) {
                    left = windowWidth - menuWidth - 5;
                }
                
                // Check if menu goes off bottom edge
                if (y + menuHeight > windowHeight) {
                    top = windowHeight - menuHeight - 5;
                }
                
                contextMenu.style.left = left + 'px';
                contextMenu.style.top = top + 'px';
            });
        });

        // Handle Edit click
        contextEdit.addEventListener('click', (event) => {
            event.stopPropagation();
            if (currentShowId) {
                openEditShowModal(parseInt(currentShowId));
            }
            contextMenu.style.display = 'none';
        });

        // Handle Delete click
        contextDelete.addEventListener('click', (event) => {
            event.stopPropagation();
            if (currentShowId) {
                if (confirm('Are you sure you want to delete this show?')) {
                    window.location.href = `/delete_show/${currentShowId}`;
                }
            }
            contextMenu.style.display = 'none';
        });

        // Hide context menu on click anywhere else
        document.addEventListener('click', (event) => {
            if (!contextMenu.contains(event.target)) {
                contextMenu.style.display = 'none';
            }
        });

        // Hide context menu on scroll
        document.addEventListener('scroll', () => {
            contextMenu.style.display = 'none';
        });
    }
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