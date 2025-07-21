// RAG Settings Fix - Add this to your index.html

// RAG Settings Management
const DEFAULT_RAG_SETTINGS = {
  rag_enabled: true,
  rag_max_results: 3
};

function saveRAGSettings() {
  const ragEnabled = document.getElementById('rag-enabled');
  const ragMaxResultsSlider = document.getElementById('rag-max-results-slider');
  
  if (ragEnabled && ragMaxResultsSlider) {
    const settings = {
      rag_enabled: ragEnabled.checked,
      rag_max_results: parseInt(ragMaxResultsSlider.value, 10)
    };
    
    console.log('Saving RAG settings:', settings);
    localStorage.setItem('ollamaRAGSettings', JSON.stringify(settings));
    
    // Save to server
    saveRAGSettingsToServer(settings);
  }
}

async function saveRAGSettingsToServer(ragSettings) {
  try {
    // Load current instructions
    let currentInstructions = [];
    try {
      const saved = localStorage.getItem('ollamaSettings');
      if (saved) {
        const settings = JSON.parse(saved);
        currentInstructions = settings.instructions || [];
      }
    } catch (e) {
      console.log('No existing settings found');
    }

    const currentSettings = {
      instructions: currentInstructions,
      rag_enabled: ragSettings.rag_enabled,
      rag_max_results: ragSettings.rag_max_results
    };

    console.log('Saving to server:', currentSettings);

    const response = await fetch('/api/settings/save', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ settings: currentSettings })
    });
    
    const data = await response.json();
    if (data.success) {
      console.log('RAG settings saved to server successfully');
      // Update local storage with complete settings
      localStorage.setItem('ollamaSettings', JSON.stringify(currentSettings));
    } else {
      console.error('Failed to save RAG settings to server:', data);
    }
  } catch (error) {
    console.error('RAG settings save error:', error);
  }
}

function loadRAGSettings() {
  // Load from local storage
  let ragSettings = null;
  try {
    const localRAGSettings = localStorage.getItem('ollamaRAGSettings');
    if (localRAGSettings) {
      ragSettings = JSON.parse(localRAGSettings);
    }
  } catch (error) {
    console.log('Error loading RAG settings:', error);
  }

  const settingsToApply = ragSettings || DEFAULT_RAG_SETTINGS;

  const ragEnabled = document.getElementById('rag-enabled');
  const ragMaxResultsSlider = document.getElementById('rag-max-results-slider');
  const ragMaxResultsValue = document.getElementById('rag-max-results-value');

  console.log('Loading RAG settings:', settingsToApply);

  if (ragEnabled) {
    ragEnabled.checked = settingsToApply.rag_enabled !== false;
    console.log('RAG enabled set to:', ragEnabled.checked);
  }
  if (ragMaxResultsSlider && ragMaxResultsValue) {
    ragMaxResultsSlider.value = settingsToApply.rag_max_results || 3;
    ragMaxResultsValue.textContent = settingsToApply.rag_max_results || 3;
  }

  // Load knowledge base status
  loadRAGStatus();
}

async function loadRAGStatus() {
  const statusDiv = document.getElementById('rag-status');
  if (!statusDiv) return;

  try {
    const response = await fetch('/api/rag/documents');
    if (response.ok) {
      const data = await response.json();
      const docCount = data.documents.length;
      const totalChunks = data.documents.reduce((sum, doc) => sum + doc.chunk_count, 0);
      
      statusDiv.innerHTML = `
        <div class="d-flex justify-content-between">
          <span><strong>${docCount}</strong> documents</span>
          <span><strong>${totalChunks}</strong> chunks</span>
        </div>
        <small class="text-muted">Knowledge base is ${docCount > 0 ? 'ready' : 'empty'}</small>
      `;
    } else {
      statusDiv.innerHTML = '<span class="text-warning">⚠️ Unable to load status</span>';
    }
  } catch (error) {
    statusDiv.innerHTML = '<span class="text-danger">❌ Connection error</span>';
  }
}

function resetRAGSettings() {
  const ragEnabled = document.getElementById('rag-enabled');
  const ragMaxResultsSlider = document.getElementById('rag-max-results-slider');
  
  if (ragEnabled) ragEnabled.checked = DEFAULT_RAG_SETTINGS.rag_enabled;
  if (ragMaxResultsSlider) ragMaxResultsSlider.value = DEFAULT_RAG_SETTINGS.rag_max_results;
  
  saveRAGSettings();
  loadRAGSettings();
}

// Initialize RAG event listeners
function initializeRAGEventListeners() {
  const ragEnabled = document.getElementById('rag-enabled');
  const ragMaxResultsSlider = document.getElementById('rag-max-results-slider');
  const ragMaxResultsValue = document.getElementById('rag-max-results-value');

  if (ragEnabled) {
    // Remove existing listeners to prevent duplicates
    ragEnabled.removeEventListener('change', saveRAGSettings);
    ragEnabled.addEventListener('change', function() {
      console.log('RAG toggle changed to:', this.checked);
      saveRAGSettings();
    });
  }

  if (ragMaxResultsSlider && ragMaxResultsValue) {
    ragMaxResultsSlider.removeEventListener('input', handleRAGSliderChange);
    ragMaxResultsSlider.addEventListener('input', handleRAGSliderChange);
  }
}

function handleRAGSliderChange(e) {
  const ragMaxResultsValue = document.getElementById('rag-max-results-value');
  if (ragMaxResultsValue) {
    ragMaxResultsValue.textContent = e.target.value;
  }
  console.log('RAG max results changed to:', e.target.value);
  saveRAGSettings();
}

// Make functions globally available
window.resetRAGSettings = resetRAGSettings;
window.loadRAGSettings = loadRAGSettings;
window.initializeRAGEventListeners = initializeRAGEventListeners;