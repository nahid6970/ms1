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

    const importBtn = document.getElementById('importData');
    const fileInput = document.getElementById('fileInput');
    
    importBtn.addEventListener('click', function() {
        fileInput.click();
    });
    
    fileInput.addEventListener('change', function(event) {
        const file = event.target.files[0];
        if (!file) return;
        
        const reader = new FileReader();
        reader.onload = function(e) {
            try {
                const importData = JSON.parse(e.target.result);
                
                // Validate the data structure
                if (importData.data && typeof importData.data === 'object') {
                    // Merge with existing data or replace
                    chrome.storage.local.get(['checkedElements'], function(result) {
                        const existingData = result.checkedElements || {};
                        
                        // Ask user if they want to merge or replace
                        const shouldMerge = confirm(
                            `Import ${importData.totalPages || Object.keys(importData.data).length} pages of data?\n\n` +
                            'Click OK to MERGE with existing data\n' +
                            'Click Cancel to REPLACE all existing data'
                        );
                        
                        let finalData;
                        if (shouldMerge) {
                            // Merge data
                            finalData = { ...existingData };
                            Object.keys(importData.data).forEach(pageUrl => {
                                if (finalData[pageUrl]) {
                                    // Merge page data, avoiding duplicates
                                    const existingIds = new Set(finalData[pageUrl].map(item => item.id));
                                    importData.data[pageUrl].forEach(item => {
                                        if (!existingIds.has(item.id)) {
                                            finalData[pageUrl].push(item);
                                        }
                                    });
                                } else {
                                    finalData[pageUrl] = importData.data[pageUrl];
                                }
                            });
                        } else {
                            // Replace all data
                            finalData = importData.data;
                        }
                        
                        // Save to storage
                        chrome.storage.local.set({ checkedElements: finalData }, function() {
                            alert('Data imported successfully! Refresh the page to see restored checkmarks.');
                            
                            // Refresh current tab to show imported checkmarks
                            chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
                                chrome.tabs.reload(tabs[0].id);
                            });
                        });
                    });
                } else {
                    alert('Invalid file format. Please select a valid Image Checker export file.');
                }
            } catch (error) {
                alert('Error reading file. Please make sure it\'s a valid JSON file.');
            }
        };
        
        reader.readAsText(file);
        
        // Reset file input
        fileInput.value = '';
    });
    
    function updateUI(isActive) {
        if (isActive) {
            toggleBtn.textContent = 'Stop Mode';
            toggleBtn.style.background = '#ff4444';
            status.textContent = 'Click on images to mark them!';
        } else {
            toggleBtn.textContent = 'Start Mode';
            toggleBtn.style.background = '#4CAF50';
            status.textContent = 'Click to activate image checking';
        }
    }
});