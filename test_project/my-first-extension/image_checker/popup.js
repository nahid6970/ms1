document.addEventListener('DOMContentLoaded', function() {
    const toggleBtn = document.getElementById('toggleMode');
    const clearBtn = document.getElementById('clearAll');
    const status = document.getElementById('status');
    
    // Get current tab and check if checking mode is active
    chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
        const tabId = tabs[0].id;
        
        // Check current mode status
        chrome.storage.local.get([`checkingMode_${tabId}`], function(result) {
            const isActive = result[`checkingMode_${tabId}`] || false;
            updateUI(isActive);
        });
    });
    
    toggleBtn.addEventListener('click', function() {
        chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
            const tabId = tabs[0].id;
            
            chrome.storage.local.get([`checkingMode_${tabId}`], function(result) {
                const currentMode = result[`checkingMode_${tabId}`] || false;
                const newMode = !currentMode;
                
                // Save new mode
                chrome.storage.local.set({[`checkingMode_${tabId}`]: newMode});
                
                // Send message to content script
                chrome.tabs.sendMessage(tabId, {
                    action: 'toggleCheckingMode',
                    enabled: newMode
                });
                
                updateUI(newMode);
            });
        });
    });
    
    clearBtn.addEventListener('click', function() {
        chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
            chrome.tabs.sendMessage(tabs[0].id, {
                action: 'clearAllCheckmarks'
            });
        });
    });
    
    const exportBtn = document.getElementById('exportData');
    exportBtn.addEventListener('click', function() {
        chrome.storage.local.get(['checkedElements'], function(result) {
            const checkedElements = result.checkedElements || {};
            
            // Create JSON data
            const exportData = {
                exportDate: new Date().toISOString(),
                totalPages: Object.keys(checkedElements).length,
                data: checkedElements
            };
            
            // Create and download file
            const blob = new Blob([JSON.stringify(exportData, null, 2)], {type: 'application/json'});
            const url = URL.createObjectURL(blob);
            
            chrome.downloads.download({
                url: url,
                filename: `image-checker-data-${new Date().toISOString().split('T')[0]}.json`,
                saveAs: true
            });
        });
    });
    
    function updateUI(isActive) {
        if (isActive) {
            toggleBtn.textContent = 'Stop Checking Mode';
            toggleBtn.classList.add('active');
            status.textContent = 'Click on images to mark them!';
        } else {
            toggleBtn.textContent = 'Start Checking Mode';
            toggleBtn.classList.remove('active');
            status.textContent = 'Click to activate image checking';
        }
    }
});