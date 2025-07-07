function searchGoogle() {
  var query = document.getElementById('searchQuery').value;
  if (query) {
      window.location.href = 'https://www.google.com/search?q=' + encodeURIComponent(query);
  }
}

function checkEnter(event) {
  if (event.key === 'Enter') {
      searchGoogle();
  }
}

function updateDateTime() {
  const now = new Date();
  const optionsDate = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
  const optionsTime = { hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: true };
  document.getElementById('currentDate').innerText = now.toLocaleDateString('en-US', optionsDate);
  document.getElementById('currentTime').innerText = now.toLocaleTimeString('en-US', optionsTime);
}

// Update the date and time on page load
updateDateTime();

// Update the time every second
setInterval(updateDateTime, 1000);
