function openAddShowModal() {
    document.getElementById('addShowModal').style.display = 'block';
    document.body.classList.add('modal-open');
}

function closeAddShowModal() {
    document.getElementById('addShowModal').style.display = 'none';
    document.body.classList.remove('modal-open');
}

function showHiddenShows() {
    console.log('Show hidden shows button clicked');
    
    // Get all hidden shows (ended and completed)
    const hiddenShows = document.querySelectorAll('.show-card.ended-completed');
    console.log('Found hidden shows:', hiddenShows.length);
    
    const hiddenShowsList = document.getElementById('hiddenShowsList');
    const hiddenShowsModal = document.getElementById('hiddenShowsModal');
    
    if (!hiddenShowsList || !hiddenShowsModal) {
        console.error('Hidden shows modal elements not found');
        return;
    }
    
    hiddenShowsList.innerHTML = '';
    
    if (hiddenShows.length === 0) {
        hiddenShowsList.innerHTML = '<p>No hidden shows found.</p>';
    } else {
        hiddenShows.forEach(card => {
            const title = card.dataset.title || 'Unknown Title';
            const year = card.dataset.year || 'Unknown Year';
            const status = card.dataset.status || 'Unknown Status';
            
            const imgElement = card.querySelector('img');
            const coverImage = imgElement ? imgElement.src : '';
            
            console.log('Show info:', {title, year, status, coverImage});
            
            const showItem = document.createElement('div');
            showItem.className = 'hidden-show-item';
            showItem.innerHTML = `
                <img src="${coverImage}" alt="${title}">
                <h4>${title}</h4>
                <p>${year}</p>
                <p>${status}</p>
            `;
            
            hiddenShowsList.appendChild(showItem);
        });
    }
    
    hiddenShowsModal.style.display = 'block';
    document.body.classList.add('modal-open');
}

function closeHiddenShowsModal() {
    document.getElementById('hiddenShowsModal').style.display = 'none';
    document.body.classList.remove('modal-open');
}

function closeHiddenShowsModal() {
    document.getElementById('hiddenShowsModal').style.display = 'none';
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

// Scan Missing Episodes Functions
async function openScanMissingModal() {
    const modal = document.getElementById('scanMissingModal');
    const list = document.getElementById('missingEpisodesList');
    
    list.innerHTML = '<p>Scanning for missing episode files...</p>';
    modal.style.display = 'block';
    document.body.classList.add('modal-open');

    try {
        const response = await fetch('/api/scan_missing_episodes');
        const missingEpisodes = await response.json();
        
        if (missingEpisodes.length === 0) {
            list.innerHTML = '<p>No missing episodes found.</p>';
        } else {
            list.innerHTML = '';
            missingEpisodes.forEach(ep => {
                const item = document.createElement('div');
                item.className = 'missing-episode-item';
                item.dataset.showId = ep.show_id;
                item.dataset.episodeId = ep.episode_id;
                
                item.innerHTML = `
                    <div class="missing-episode-info">
                        <span class="missing-show-title">${ep.show_title}</span>
                        <span class="missing-episode-title">${ep.episode_title}</span>
                    </div>
                    <div class="missing-episode-actions">
                        <button onclick="checkMissingEpisode(${ep.show_id}, ${ep.episode_id}, this)" class="btn-check" title="Mark as Watched"><svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-right: 4px;"><polyline points="20 6 9 17 4 12"></polyline></svg> Check</button>
                        <button onclick="deleteMissingEpisode(${ep.show_id}, ${ep.episode_id}, this)" class="btn-delete" title="Delete from JSON"><svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-right: 4px;"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path><line x1="10" y1="11" x2="10" y2="17"></line><line x1="14" y1="11" x2="14" y2="17"></line></svg> Del</button>
                    </div>
                `;
                list.appendChild(item);
            });
        }
    } catch (error) {
        console.error('Error scanning missing episodes:', error);
        list.innerHTML = '<p>Error occurred while scanning.</p>';
    }
}

function closeScanMissingModal() {
    document.getElementById('scanMissingModal').style.display = 'none';
    document.body.classList.remove('modal-open');
}

function closeEpisodesModal() {
    document.getElementById('episodesModal').style.display = 'none';
    document.body.classList.remove('modal-open');
}

async function openEpisodesPopup(event, showId, showTitle) {
    if (event) {
        event.stopPropagation();
        event.preventDefault();
    }
    
    const modal = document.getElementById('episodesModal');
    const titleEl = document.getElementById('episodesModalTitle');
    const listContainer = document.getElementById('episodesListContainer');

    titleEl.textContent = showTitle;
    listContainer.innerHTML = '<p style="text-align: center;">Loading episodes...</p>';
    modal.style.display = 'block';
    document.body.classList.add('modal-open');

    try {
        const response = await fetch(`/edit_show/${showId}`);
        const show = await response.json();
        
        listContainer.innerHTML = '';
        if (!show.episodes || show.episodes.length === 0) {
            listContainer.innerHTML = '<p style="text-align: center;">No episodes found.</p>';
        } else {
            const ul = document.createElement('ul');
            ul.style.listStyle = 'none';
            ul.style.padding = '0';
            
            show.episodes.forEach(ep => {
                const li = document.createElement('li');
                li.className = `episode-item ${ep.watched ? 'episode-watched' : ''}`;
                li.style.display = 'flex';
                li.style.justifyContent = 'space-between';
                li.style.alignItems = 'center';
                li.style.padding = '12px 15px';
                li.style.marginBottom = '8px';
                li.style.background = '#2a2a2a';
                li.style.borderRadius = '8px';
                if (ep.watched) li.style.background = 'rgba(29, 185, 84, 0.1)';

                li.innerHTML = `
                    <div>
                        <input type="checkbox" ${ep.watched ? 'checked' : ''} onchange="toggleWatched(${showId}, ${ep.id})">
                        <span>${ep.title}</span>
                    </div>
                    <div style="display: flex; gap: 8px;">
                        <div class="edit-dot" onclick="openEditEpisodeModal(${showId}, ${ep.id})"></div>
                        <div class="delete-dot" onclick="deleteEpisode(${showId}, ${ep.id})"></div>
                    </div>
                `;
                ul.appendChild(li);
            });
            listContainer.appendChild(ul);
        }
    } catch (error) {
        console.error('Error fetching episodes:', error);
        listContainer.innerHTML = '<p style="text-align: center; color: #ff6b6b;">Error loading episodes.</p>';
    }
}

async function checkMissingEpisode(showId, episodeId, button) {
    try {
        const response = await fetch(`/api/check_episode/${showId}/${episodeId}`, { method: 'POST' });
        const data = await response.json();
        if (data.success) {
            const item = button.closest('.missing-episode-item');
            item.style.opacity = '0.5';
            item.style.pointerEvents = 'none';
            setTimeout(() => item.remove(), 500);
        }
    } catch (error) {
        console.error('Error checking episode:', error);
    }
}

async function deleteMissingEpisode(showId, episodeId, button) {
    if (confirm('Are you sure you want to delete this episode from JSON?')) {
        try {
            const response = await fetch(`/api/delete_episode/${showId}/${episodeId}`, { method: 'POST' });
            const data = await response.json();
            if (data.success) {
                const item = button.closest('.missing-episode-item');
                item.style.opacity = '0.5';
                item.style.pointerEvents = 'none';
                setTimeout(() => item.remove(), 500);
            }
        } catch (error) {
            console.error('Error deleting episode:', error);
        }
    }
}

async function scanForEpisodes(event) {
    if (event) event.preventDefault();
    const btn = document.querySelector('.scan-button');
    const originalHTML = btn.innerHTML;
    
    btn.innerHTML = '<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="spin"><polyline points="23 4 23 10 18 10"></polyline><polyline points="1 20 1 14 6 14"></polyline><path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"></path></svg>';
    btn.style.pointerEvents = 'none';

    try {
        const response = await fetch('/scan_and_add_all');
        const data = await response.json();
        if (data.success) {
            location.reload();
        }
    } catch (error) {
        console.error('Error scanning:', error);
        btn.innerHTML = originalHTML;
        btn.style.pointerEvents = 'auto';
        alert('Error during scan');
    }
}

async function syncShow(event, showId, btn) {
    if (event) {
        event.stopPropagation();
        event.preventDefault();
    }
    
    const originalHTML = btn.innerHTML;
    btn.innerHTML = '<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="spin"><path d="M23 4v6h-6"></path><path d="M1 20v-6h6"></path><path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"></path></svg>';
    btn.style.pointerEvents = 'none';

    try {
        const response = await fetch(`/scan_manual/${showId}`);
        const data = await response.json();
        if (data.success) {
            btn.innerHTML = '<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="#4ade80" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>';
            setTimeout(() => {
                location.reload();
            }, 1000);
        }
    } catch (error) {
        console.error('Error syncing show:', error);
        btn.innerHTML = originalHTML;
        btn.style.pointerEvents = 'auto';
    }
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

// Restore scroll position immediately (before DOMContentLoaded to prevent flash)
const savedScrollPosition = localStorage.getItem('scrollPosition');
if (savedScrollPosition !== null) {
    // Set scroll position immediately
    window.scrollTo({
        top: parseInt(savedScrollPosition),
        behavior: 'instant'
    });
    localStorage.removeItem('scrollPosition');
}

// Toggle Default Home Page
document.addEventListener('DOMContentLoaded', () => {
    const defaultHomePageSelect = document.getElementById('defaultHomePage');
    const showHiddenShowsToggle = document.getElementById('showHiddenShows');
    const html = document.documentElement;

    // Load default home page preference from localStorage
    const defaultHomePage = localStorage.getItem('defaultHomePage') || 'default';
    defaultHomePageSelect.value = defaultHomePage;

    // Load show hidden shows preference from localStorage
    const showHiddenShows = localStorage.getItem('showHiddenShows') === 'true';
    console.log('Loaded showHiddenShows setting:', showHiddenShows);
    if (showHiddenShows) {
        html.classList.add('show-hidden-shows');
        showHiddenShowsToggle.checked = true;
        console.log('Added show-hidden-shows class to HTML');
    } else {
        html.classList.remove('show-hidden-shows');
        showHiddenShowsToggle.checked = false;
        console.log('Removed show-hidden-shows class from HTML');
    }

    // Save default home page preference to localStorage on change
    defaultHomePageSelect.addEventListener('change', () => {
        localStorage.setItem('defaultHomePage', defaultHomePageSelect.value);
    });

    // Save show hidden shows preference to localStorage on change
    showHiddenShowsToggle.addEventListener('change', () => {
        if (showHiddenShowsToggle.checked) {
            html.classList.add('show-hidden-shows');
            localStorage.setItem('showHiddenShows', 'true');
            console.log('Enabled show-hidden-shows');
        } else {
            html.classList.remove('show-hidden-shows');
            localStorage.setItem('showHiddenShows', 'false');
            console.log('Disabled show-hidden-shows');
        }
    });



    // Live Search Functionality
    const searchInput = document.querySelector('.search-form input[name="query"]');
    const searchClear = document.getElementById('searchClear');

    function filterShows(query) {
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

        // Show/hide clear button
        if (searchClear) {
            searchClear.style.display = query.length > 0 ? 'block' : 'none';
        }
    }

    if (searchInput) {
        // Initial check for clear button visibility (e.g. on page reload with query)
        if (searchClear) {
            searchClear.style.display = searchInput.value.length > 0 ? 'block' : 'none';
        }

        searchInput.addEventListener('input', function(e) {
            filterShows(e.target.value);
        });

        if (searchClear) {
            searchClear.addEventListener('click', function() {
                searchInput.value = '';
                filterShows('');
                searchInput.focus();
            });
        }
    }

    // Add click listener for show cards
    document.querySelectorAll('.show-card').forEach(card => {
        card.addEventListener('click', async (event) => {
            // Check if the click wasn't on a button or inside hover controls
            if (!event.target.closest('.hover-controls')) {
                const showId = card.dataset.showId;
                if (!showId) return;

                const modal = document.getElementById('episodesModal');
                const titleEl = document.getElementById('episodesModalTitle');
                const listContainer = document.getElementById('episodesListContainer');

                titleEl.textContent = card.dataset.title;
                listContainer.innerHTML = '<p style="text-align: center;">Loading episodes...</p>';
                modal.style.display = 'block';
                document.body.classList.add('modal-open');

                try {
                    const response = await fetch(`/edit_show/${showId}`); // Reusing edit_show to get data
                    const show = await response.json();
                    
                    listContainer.innerHTML = '';
                    if (!show.episodes || show.episodes.length === 0) {
                        listContainer.innerHTML = '<p style="text-align: center;">No episodes found.</p>';
                    } else {
                        const ul = document.createElement('ul');
                        ul.style.listStyle = 'none';
                        ul.style.padding = '0';
                        
                        show.episodes.forEach(ep => {
                            const li = document.createElement('li');
                            li.className = `episode-item ${ep.watched ? 'episode-watched' : ''}`;
                            li.style.display = 'flex';
                            li.style.justifyContent = 'space-between';
                            li.style.alignItems = 'center';
                            li.style.padding = '12px 15px';
                            li.style.marginBottom = '8px';
                            li.style.background = '#2a2a2a';
                            li.style.borderRadius = '8px';
                            if (ep.watched) li.style.background = 'rgba(29, 185, 84, 0.1)';

                            li.innerHTML = `
                                <div style="display: flex; align-items: center; gap: 12px;">
                                    <input type="checkbox" ${ep.watched ? 'checked' : ''} onchange="toggleWatched(${showId}, ${ep.id})">
                                    <span>${ep.title}</span>
                                </div>
                                <div style="display: flex; gap: 8px;">
                                    <div class="edit-dot" onclick="openEditEpisodeModal(${showId}, ${ep.id})" style="width: 10px; height: 10px; border-radius: 50%; background: #3498db; cursor: pointer;"></div>
                                    <div class="delete-dot" onclick="deleteEpisode(${showId}, ${ep.id})" style="width: 10px; height: 10px; border-radius: 50%; background: #e74c3c; cursor: pointer;"></div>
                                </div>
                            `;
                            ul.appendChild(li);
                        });
                        listContainer.appendChild(ul);
                    }
                } catch (error) {
                    console.error('Error fetching episodes:', error);
                    listContainer.innerHTML = '<p style="text-align: center; color: #ff6b6b;">Error loading episodes.</p>';
                }
            }
        });
    });

    // Helper functions for popup interactions
    window.toggleWatched = function(showId, episodeId) {
        fetch(`/toggle_watched/${showId}/${episodeId}`).then(() => {
            // Optional: refresh the modal or just the item
            // For simplicity, let's just update the count on main page if needed
        });
    };

    window.deleteEpisode = function(showId, episodeId) {
        if (confirm('Are you sure?')) {
            fetch(`/delete_episode/${showId}/${episodeId}`).then(() => {
                // Refresh modal content
                document.querySelector(`.show-card[data-show-id="${showId}"]`).click();
            });
        }
    };

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
    const hiddenShowsModal = document.getElementById('hiddenShowsModal');

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
    } else if (event.target == hiddenShowsModal) {
        hiddenShowsModal.style.display = 'none';
        document.body.classList.remove('modal-open');
    }
}