function updateUsage() {
    // Simulate CPU and RAM usage for demonstration purposes
    // In a real application, you would fetch these values from a backend API or system monitoring tool.
    const cpuUsage = Math.floor(Math.random() * 100);
    const ramUsage = Math.floor(Math.random() * 100);

    const cpuProgressBar = document.getElementById('cpu-progress');
    const cpuValue = document.getElementById('cpu-value');
    const ramProgressBar = document.getElementById('ram-progress');
    const ramValue = document.getElementById('ram-value');

    cpuProgressBar.style.width = cpuUsage + '%';
    cpuValue.textContent = cpuUsage + '%';

    ramProgressBar.style.width = ramUsage + '%';
    ramValue.textContent = ramUsage + '%';
}

// Update usage every 2 seconds
setInterval(updateUsage, 2000);

// Initial update
updateUsage();