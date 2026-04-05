document.addEventListener('DOMContentLoaded', function () {
    const toggleBtn = document.getElementById('toggleMode');
    const clearBtn = document.getElementById('clearAll');
    const status = document.getElementById('status');

    // Function to refresh UI state
    function refreshUIState() {
        // Check global mode status
        chrome.storage.local.get(['checkingMode_global'], function (result) {
            const isActive = result.checkingMode_global || false;
            updateUI(isActive);
        });
    }

    // Initial load
    refreshUIState();

    // Refresh state when popup becomes visible (in case ESC was pressed)
    document.addEventListener('visibilitychange', function () {
        if (!document.hidden) {
            refreshUIState();
        }
    });

    // Also refresh periodically while popup is open
    const refreshInterval = setInterval(refreshUIState, 1000);

    // Clean up interval when popup closes
    window.addEventListener('beforeunload', function () {
        clearInterval(refreshInterval);
    });

    toggleBtn.addEventListener('click', function () {
        chrome.storage.local.get(['checkingMode_global'], function (result) {
            const currentMode = result.checkingMode_global || false;
            const newMode = !currentMode;

            // Save new mode globally
            chrome.storage.local.set({ checkingMode_global: newMode });

            // Send message to all tabs (or at least the active one)
            chrome.tabs.query({}, function (tabs) {
                tabs.forEach(tab => {
                    chrome.tabs.sendMessage(tab.id, {
                        action: 'toggleCheckingMode',
                        enabled: newMode
                    }).catch(() => { }); // Ignore errors for tabs where content script isn't running
                });
            });

            updateUI(newMode);
        });
    });

    clearBtn.addEventListener('click', function () {
        chrome.tabs.query({ active: true, currentWindow: true }, function (tabs) {
            chrome.tabs.sendMessage(tabs[0].id, {
                action: 'clearAllCheckmarks'
            });
        });
    });

    const reloadBtn = document.getElementById('reloadExtension');
    if (reloadBtn) {
        reloadBtn.addEventListener('click', function () {
            chrome.runtime.reload();
        });
    }


    // Save to Convex button
    const saveToConvexBtn = document.getElementById('saveToConvex');
    if (saveToConvexBtn) {
        saveToConvexBtn.addEventListener('click', function () {
            const originalText = saveToConvexBtn.textContent;
            const originalBg = saveToConvexBtn.style.background;
            
            saveToConvexBtn.textContent = '⏳ Saving...';
            saveToConvexBtn.disabled = true;
            
            chrome.storage.local.get(null, function (items) {
                // Send message to background script to save
                chrome.runtime.sendMessage({
                    action: 'saveToConvex',
                    data: items
                }, function (response) {
                    saveToConvexBtn.disabled = false;
                    
                    if (response && response.success !== false) {
                        // Success
                        saveToConvexBtn.textContent = '✅ Saved!';
                        saveToConvexBtn.style.background = '#4CAF50';
                        setTimeout(() => {
                            saveToConvexBtn.textContent = originalText;
                            saveToConvexBtn.style.background = originalBg;
                        }, 2000);
                    } else {
                        // Failed
                        saveToConvexBtn.textContent = '❌ Failed';
                        saveToConvexBtn.style.background = '#f44336';
                        setTimeout(() => {
                            saveToConvexBtn.textContent = originalText;
                            saveToConvexBtn.style.background = originalBg;
                        }, 2000);
                    }
                });
            });
        });
    }

    // Load from Convex button
    const loadFromConvexBtn = document.getElementById('loadFromConvex');
    if (loadFromConvexBtn) {
        loadFromConvexBtn.addEventListener('click', function () {
            const originalText = loadFromConvexBtn.textContent;
            const originalBg = loadFromConvexBtn.style.background;
            
            loadFromConvexBtn.textContent = '⏳ Loading...';
            loadFromConvexBtn.disabled = true;
            
            chrome.runtime.sendMessage({
                action: 'loadFromConvex'
            }, function (response) {
                loadFromConvexBtn.disabled = false;
                
                if (response && response.success !== false && response.data) {
                    chrome.storage.local.set(response.data, () => {
                        loadFromConvexBtn.textContent = '✅ Loaded!';
                        loadFromConvexBtn.style.background = '#4CAF50';
                        
                        
                        
                        // Notify active tab to refresh
                        chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
                            if (tabs[0]) {
                                chrome.tabs.reload(tabs[0].id);
                            }
                        });

                        setTimeout(() => {
                            loadFromConvexBtn.textContent = originalText;
                            loadFromConvexBtn.style.background = originalBg;
                        }, 2000);
                    });
                } else {
                    loadFromConvexBtn.textContent = '❌ Failed';
                    loadFromConvexBtn.style.background = '#f44336';
                    
                    setTimeout(() => {
                        loadFromConvexBtn.textContent = originalText;
                        loadFromConvexBtn.style.background = originalBg;
                    }, 2000);
                }
            });
        });
    }


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
    const excludedDomainsInput = document.getElementById('excludedDomains');
    const saveExclusionsBtn = document.getElementById('saveExclusions');

    // Toggle settings panel
    settingsToggle.addEventListener('click', function () {
        settingsContent.classList.toggle('show');
        settingsToggle.textContent = settingsContent.classList.contains('show') ?
            '⚙️ Hide Settings' : '⚙️ Settings';
    });

    // Load saved settings
    chrome.storage.local.get(['imageCheckerSettings', 'excludedDomains'], function (result) {
        const settings = result.imageCheckerSettings || getDefaultSettings();
        loadSettingsToUI(settings);
        
        if (result.excludedDomains) {
            excludedDomainsInput.value = result.excludedDomains.join('\n');
        }
    });

    // Save Exclusions
    saveExclusionsBtn.addEventListener('click', () => {
        const domains = excludedDomainsInput.value
            .split('\n')
            .map(d => d.trim())
            .filter(d => d.length > 0);

        chrome.storage.local.set({ excludedDomains: domains }, () => {
            const originalText = saveExclusionsBtn.textContent;
            saveExclusionsBtn.textContent = '✅ Saved!';
            saveExclusionsBtn.style.background = '#4CAF50';
            setTimeout(() => {
                saveExclusionsBtn.textContent = originalText;
                saveExclusionsBtn.style.background = '';
            }, 2000);
        });
    });

    // Update size value display
    checkmarkSize.addEventListener('input', function () {
        sizeValue.textContent = this.value + '%';
    });

    // Update border width display
    borderWidth.addEventListener('input', function () {
        borderValue.textContent = this.value + 'px';
    });

    // Reset to default settings
    resetSettings.addEventListener('click', function () {
        const defaults = getDefaultSettings();
        loadSettingsToUI(defaults);
        saveSettings(defaults);
    });

    // Apply settings
    applySettings.addEventListener('click', function () {
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
        chrome.tabs.query({ active: true, currentWindow: true }, function (tabs) {
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