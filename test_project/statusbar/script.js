async function updateUsage() {
    try {
        const response = await fetch('http://127.0.0.1:4050/usage');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();

        const cpuProgressBar = document.getElementById('cpu-progress');
        const cpuValue = document.getElementById('cpu-value');
        const ramProgressBar = document.getElementById('ram-progress');
        const ramValue = document.getElementById('ram-value');

        cpuProgressBar.style.width = data.cpu_usage + '%';
        cpuValue.textContent = data.cpu_usage.toFixed(1) + '%';

        ramProgressBar.style.width = data.ram_usage + '%';
        ramValue.textContent = data.ram_usage.toFixed(1) + '%';

    } catch (error) {
        console.error('Error fetching usage data:', error);
        // Optionally, display an error message on the status bar
        const cpuValue = document.getElementById('cpu-value');
        const ramValue = document.getElementById('ram-value');
        cpuValue.textContent = 'Error';
        ramValue.textContent = 'Error';
    }
}

// Update usage every 2 seconds
setInterval(updateUsage, 2000);

// Initial update
updateUsage();