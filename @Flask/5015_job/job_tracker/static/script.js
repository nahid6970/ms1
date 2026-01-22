function togglePastDeadlines() {
    const checkbox = document.getElementById('hidePastDeadlines');
    localStorage.setItem('hidePastDeadlines', checkbox.checked);
    const url = new URL(window.location.href);
    if (checkbox.checked) {
        url.searchParams.set('hide_past', 'true');
    } else {
        url.searchParams.delete('hide_past');
    }
    window.location.href = url.toString();
}

// Modal functions
function openAddJobModal() {
    document.getElementById('addJobModal').style.display = 'block';
}

function closeAddJobModal() {
    document.getElementById('addJobModal').style.display = 'none';
}

function openEditJobModal(jobId) {
    fetch(`/edit_job/${jobId}`)
        .then(response => response.json())
        .then(job => {
            document.getElementById('editJobForm').action = `/edit_job/${jobId}`;
            document.getElementById('editCompany').value = job.company;
            document.getElementById('editPosition').value = job.position;
            document.getElementById('editJobUrl').value = job.job_url || '';
            document.getElementById('editAppliedDate').value = job.applied_date || '';
            document.getElementById('editDeadline').value = job.deadline || '';
            document.getElementById('editStatus').value = job.status;
            document.getElementById('editNotes').value = job.notes || '';
            
            document.getElementById('editJobModal').style.display = 'block';
        })
        .catch(error => {
            console.error('Error fetching job data:', error);
            alert('Error loading job data');
        });
}

function closeEditJobModal() {
    document.getElementById('editJobModal').style.display = 'none';
}

// Sort menu toggle
function toggleSortMenu() {
    const dropdown = document.getElementById('sortMenuDropdown');
    dropdown.classList.toggle('show');
}

// Close modals when clicking outside
window.onclick = function(event) {
    const addModal = document.getElementById('addJobModal');
    const editModal = document.getElementById('editJobModal');
    const sortDropdown = document.getElementById('sortMenuDropdown');
    
    if (event.target == addModal) {
        addModal.style.display = 'none';
    }
    if (event.target == editModal) {
        editModal.style.display = 'none';
    }
    if (!event.target.matches('.sort-menu-button') && !event.target.matches('.sort-chevron')) {
        if (sortDropdown && sortDropdown.classList.contains('show')) {
            sortDropdown.classList.remove('show');
        }
    }
}

document.addEventListener('DOMContentLoaded', function() {
    // "Hide Past Deadlines" checkbox
    const checkbox = document.getElementById('hidePastDeadlines');
    const hidePastDeadlines = localStorage.getItem('hidePastDeadlines');
    const url = new URL(window.location.href);
    const hidePastParam = url.searchParams.get('hide_past');

    if (hidePastDeadlines === 'true') {
        checkbox.checked = true;
        if (hidePastParam !== 'true') {
            url.searchParams.set('hide_past', 'true');
            window.location.href = url.toString();
        }
    }

    // Sort menu items
    const sortItems = document.querySelectorAll('.sort-menu-item');
    sortItems.forEach(item => {
        item.addEventListener('click', function() {
            document.getElementById('sortMenuDropdown').classList.remove('show');
        });
    });

    // Auto-fill applied date
    const statusSelects = document.querySelectorAll('select[name="status"]');
    statusSelects.forEach(select => {
        select.addEventListener('change', function() {
            const appliedDateInput = this.closest('form').querySelector('input[name="applied_date"]');
            if (this.value === 'Applied' && appliedDateInput && !appliedDateInput.value) {
                const today = new Date().toISOString().split('T')[0];
                appliedDateInput.value = today;
            }
        });
    });
});
