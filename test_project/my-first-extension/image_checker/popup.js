document.addEventListener('DOMContentLoaded', function() {
    const toggleBtn = document.getElementById('toggleMode');
    const clearBtn = document.getElementById('clearAll');
    const status = document.getElementById('status');
    
    // Function to refresh UI state
    function refreshUIState() {
        chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
            const tabId = tabs[0].id;
            
            // Check current mode status
            chrome.storage.local.get([`checkingMode_${tabId}`], function(result) {
                const isActive = result[`checkingMode_${tabId}`] || false;
                updateUI(isActive);
            });
        });
    }
    
    // Initial load
    refreshUIState();
    
    // Refresh state when popup becomes visible (in case ESC was pressed)
    document.addEventListener('visibilitychange', function() {
        if (!document.hidden) {
            refreshUIState();
        }
    });
    
    // Also refresh periodically while popup is open
    const refreshInterval = setInterval(refreshUIState, 1000);
    
    // Clean up interval when popup closes
    window.addEventListener('beforeunload', function() {
        clearInterval(refreshInterval);
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
    
    // Import functionality
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

    // Settings functionality
    const settingsToggle = document.getElementById('settingsToggle');
    const settingsContent = document.getElementById('settingsContent');
    const checkmarkSize = document.getElementById('checkmarkSize');
    const sizeValue = document.getElementById('sizeValue');
    const checkmarkColor = document.getElementById('checkmarkColor');
    const textColor = document.getElementById('textColor');
    const enableBorder = document.getElementById('enableBorder');
    const borderColor = document.getElementById('borderColor');
    const borderWidth = document.getElementById('borderWidth');
    const borderValue = document.getElementById('borderValue');
    const resetSettings = document.getElementById('resetSettings');
    const applySettings = document.getElementById('applySettings');

    // Toggle settings panel
    settingsToggle.addEventListener('click', function() {
        settingsContent.classList.toggle('show');
        settingsToggle.textContent = settingsContent.classList.contains('show') ? 
            '⚙️ Hide Settings' : '⚙️ Settings';
    });

    // Load saved settings
    chrome.storage.local.get(['imageCheckerSettings'], function(result) {
        const settings = result.imageCheckerSettings || getDefaultSettings();
        loadSettingsToUI(settings);
    });

    // Update size value display
    checkmarkSize.addEventListener('input', function() {
        sizeValue.textContent = this.value + '%';
    });

    // Update border width display
    borderWidth.addEventListener('input', function() {
        borderValue.textContent = this.value + 'px';
    });

    // Reset to default settings
    resetSettings.addEventListener('click', function() {
        const defaults = getDefaultSettings();
        loadSettingsToUI(defaults);
        saveSettings(defaults);
    });

    // Apply settings
    applySettings.addEventListener('click', function() {
        const settings = {
            checkmarkSize: parseInt(checkmarkSize.value),
            checkmarkColor: checkmarkColor.value,
            textColor: textColor.value,
            enableBorder: enableBorder.checked,
            borderColor: borderColor.value,
            borderWidth: parseInt(borderWidth.value)
        };
        
        saveSettings(settings);
        
        // Send settings to content script
        chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
            chrome.tabs.sendMessage(tabs[0].id, {
                action: 'updateSettings',
                settings: settings
            });
        });
        
        // Show confirmation
        const originalText = applySettings.textContent;
        applySettings.textContent = 'Applied!';
        applySettings.style.background = '#4CAF50';
        setTimeout(() => {
            applySettings.textContent = originalText;
            applySettings.style.background = '#2196F3';
        }, 1000);
    });

    function getDefaultSettings() {
        return {
            checkmarkSize: 15,
            checkmarkColor: '#4CAF50',
            textColor: '#ffffff',
            enableBorder: false,
            borderColor: '#4CAF50',
            borderWidth: 3
        };
    }

    function loadSettingsToUI(settings) {
        checkmarkSize.value = settings.checkmarkSize;
        sizeValue.textContent = settings.checkmarkSize + '%';
        checkmarkColor.value = settings.checkmarkColor;
        textColor.value = settings.textColor;
        enableBorder.checked = settings.enableBorder;
        borderColor.value = settings.borderColor;
        borderWidth.value = settings.borderWidth;
        borderValue.textContent = settings.borderWidth + 'px';
    }

    function saveSettings(settings) {
        chrome.storage.local.set({ imageCheckerSettings: settings });
    }

    function updateUI(isActive) {
        if (isActive) {
            toggleBtn.textContent = 'Stop Mode';
            toggleBtn.style.background = '#ff4444';
            status.textContent = 'Click on images to mark them!';
        } else {
            toggleBtn.textContent = 'Start Mode';
            toggleBtn.style.background = '#f44336';
            status.textContent = 'Click to activate image checking';
        }
    }
});