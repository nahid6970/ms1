// Fix for settings menu and model dropdown issues
// Add this script to fix the broken functionality

document.addEventListener('DOMContentLoaded', function() {
    console.log('Initializing settings and model functionality...');
    
    // Get DOM elements
    const modelSelect = document.getElementById("model-select");
    const settingsBtn = document.getElementById("settings-btn");
    const settingsModal = new bootstrap.Modal(document.getElementById('settingsModal'));
    
    // Model loading functionality
    async function fetchModels() {
        console.log('Fetching models...');
        try {
            const response = await fetch("/api/tags");
            const data = await response.json();
            const savedModel = loadSelectedModel();
            
            // Clear existing options
            modelSelect.innerHTML = '';
            
            let modelFound = false;
            data.models.forEach(model => {
                const option = document.createElement("option");
                option.value = model.name;
                option.textContent = model.name;
                modelSelect.appendChild(option);
                
                // Check if this is the previously saved model
                if (savedModel === model.name) {
                    option.selected = true;
                    modelFound = true;
                }
            });
            
            // If saved model wasn't found but we have models, select the first one
            if (!modelFound && data.models.length > 0) {
                modelSelect.selectedIndex = 0;
                saveSelectedModel(data.models[0].name);
            }
            
            console.log(`Loaded ${data.models.length} models`);
        } catch (error) {
            console.error("Error fetching models:", error);
            modelSelect.innerHTML = '<option value="">Error loading models</option>';
        }
    }
    
    // Model selection change handler
    if (modelSelect) {
        modelSelect.addEventListener('change', (e) => {
            console.log('Model changed to:', e.target.value);
            saveSelectedModel(e.target.value);
        });
    }
    
    // Settings button click handler
    if (settingsBtn) {
        // Remove any existing listeners to prevent duplicates
        settingsBtn.replaceWith(settingsBtn.cloneNode(true));
        const newSettingsBtn = document.getElementById("settings-btn");
        
        newSettingsBtn.addEventListener("click", () => {
            console.log('Settings button clicked');
            try {
                // Load model settings
                if (typeof loadModelSettings === 'function') {
                    loadModelSettings();
                }
                
                // Load RAG settings if available
                if (typeof window.loadRAGSettings === 'function') {
                    window.loadRAGSettings();
                    // Initialize RAG event listeners
                    setTimeout(() => {
                        if (typeof window.initializeRAGEventListeners === 'function') {
                            window.initializeRAGEventListeners();
                        }
                    }, 100);
                }
                
                // Show the modal
                settingsModal.show();
            } catch (error) {
                console.error('Error opening settings:', error);
                alert('Error opening settings: ' + error.message);
            }
        });
    }
    
    // Helper functions for model persistence
    function saveSelectedModel(modelName) {
        localStorage.setItem('selectedOllamaModel', modelName);
    }

    function loadSelectedModel() {
        return localStorage.getItem('selectedOllamaModel');
    }
    
    // Initialize everything
    fetchModels();
    
    console.log('Settings and model functionality initialized');
});

// Make functions globally available
window.fetchModels = fetchModels;