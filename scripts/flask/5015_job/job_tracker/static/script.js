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

// Close sort menu when clicking on a sort option
document.addEventListener('DOMContentLoaded', function() {
    const sortItems = document.querySelectorAll('.sort-menu-item');
    sortItems.forEach(item => {
        item.addEventListener('click', function() {
            document.getElementById('sortMenuDropdown').classList.remove('show');
        });
    });
});

// Form validation and enhancements
document.addEventListener('DOMContentLoaded', function() {

    

});