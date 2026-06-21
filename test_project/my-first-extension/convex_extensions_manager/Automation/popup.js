let currentlyPickingStepId = null;

document.addEventListener('DOMContentLoaded', async () => {
  // Initialize UI components
  await initSettings();
  await renderSteps();
  startLogMonitoring();
  initConvexButtons();

  // Setup main actions
  document.getElementById('addStepBtn').addEventListener('click', addNewStep);
  document.getElementById('toggleBtn').addEventListener('click', toggleAutomation);
  document.getElementById('clearLogsBtn').addEventListener('click', clearLogs);

  // Settings inputs
  const loopCountInput = document.getElementById('loopCount');
  const loopDelayInput = document.getElementById('loopDelay');

  loopCountInput.addEventListener('change', () => {
    chrome.storage.local.set({ loopCount: parseInt(loopCountInput.value) || 1 });
  });

  loopDelayInput.addEventListener('change', () => {
    chrome.storage.local.set({ loopDelay: parseFloat(loopDelayInput.value) || 0 });
  });
});

// Settings Initialization
async function initSettings() {
  chrome.storage.local.get(['loopCount', 'loopDelay'], (data) => {
    if (data.loopCount !== undefined) {
      document.getElementById('loopCount').value = data.loopCount;
    } else {
      chrome.storage.local.set({ loopCount: 1 });
    }
    if (data.loopDelay !== undefined) {
      document.getElementById('loopDelay').value = data.loopDelay;
    } else {
      chrome.storage.local.set({ loopDelay: 1.0 }); // Default to 1.0 second
    }
  });
}

// Helper to reorder steps in storage
function reorderSteps(fromIdx, toIdx, isAbove) {
  chrome.storage.local.get('steps', (data) => {
    const steps = data.steps || [];
    const movedStep = steps[fromIdx];
    if (!movedStep) return;

    // Remove the step from its original position
    steps.splice(fromIdx, 1);
    
    // Calculate the new destination index
    let insertIdx = toIdx;
    if (fromIdx < toIdx) {
      insertIdx = isAbove ? toIdx - 1 : toIdx;
    } else {
      insertIdx = isAbove ? toIdx : toIdx + 1;
    }
    
    // Safety bounds
    insertIdx = Math.max(0, Math.min(steps.length, insertIdx));
    
    // Insert at new position
    steps.splice(insertIdx, 0, movedStep);
    
    chrome.storage.local.set({ steps }, () => {
      renderSteps();
    });
  });
}

// Render dynamic steps
async function renderSteps() {
  chrome.storage.local.get('steps', (data) => {
    const steps = data.steps || [];
    const stepsListContainer = document.getElementById('stepsList');
    stepsListContainer.innerHTML = '';

    if (steps.length === 0) {
      stepsListContainer.innerHTML = '<div class="log-placeholder" style="margin-top:15px;">No automation steps configured. Click Add Step below to start!</div>';
      return;
    }

    steps.forEach((step, idx) => {
      const stepCard = document.createElement('div');
      stepCard.className = 'step-card';
      stepCard.dataset.id = step.id;

      const isTypeAction = step.action === 'type';
      const isWaitAction = step.action === 'wait';

      stepCard.innerHTML = `
        <div class="step-row-top">
          <span class="step-index" title="Hold and drag to reorder step">${idx + 1}</span>
          <select class="step-action-select" data-id="${step.id}">
            <option value="click" ${step.action === 'click' ? 'selected' : ''}>Click</option>
            <option value="type" ${step.action === 'type' ? 'selected' : ''}>Type Text</option>
            <option value="focus" ${step.action === 'focus' ? 'selected' : ''}>Focus</option>
            <option value="clear" ${step.action === 'clear' ? 'selected' : ''}>Clear Field</option>
            <option value="wait" ${step.action === 'wait' ? 'selected' : ''}>Wait Only</option>
            <option value="navigate" ${step.action === 'navigate' ? 'selected' : ''}>Navigate</option>
            <option value="waitFor" ${step.action === 'waitFor' ? 'selected' : ''}>Wait For Element</option>
          </select>
          
          <div class="inputs-container" style="display: ${isWaitAction ? 'none' : 'flex'};">
            <div class="selector-wrapper">
              <input type="text" class="selector-input" placeholder="CSS Selector" value="${step.selector || ''}" data-id="${step.id}" />
              <button class="btn-pick" title="Pick element on page" data-id="${step.id}">🎯</button>
            </div>
            <input type="text" class="value-input" placeholder="Text to type" value="${step.value || ''}" data-id="${step.id}" style="display: ${isTypeAction ? 'block' : 'none'};" />
          </div>
          
          <div class="delay-wrapper" title="Delay (seconds) — for normal steps or max wait time for Wait For Element">
            <span class="delay-icon">⏱️</span>
            <input type="number" class="delay-input-val" placeholder="0" value="${step.delay || 0}" data-id="${step.id}" step="0.1" min="0" />
            <span class="delay-unit">s</span>
          </div>
          
          <button class="btn-delete" title="Delete Step" data-id="${step.id}">🗑️</button>
        </div>
      `;

      // Enable drag only when grabbing the step index
      const stepIndexEl = stepCard.querySelector('.step-index');
      if (stepIndexEl) {
        stepIndexEl.addEventListener('mousedown', () => {
          stepCard.draggable = true;
        });
        stepIndexEl.addEventListener('mouseup', () => {
          stepCard.draggable = false;
        });
      }

      stepCard.addEventListener('dragstart', (e) => {
        e.dataTransfer.effectAllowed = 'move';
        stepCard.classList.add('dragging');
        e.dataTransfer.setData('text/plain', idx);
      });

      stepCard.addEventListener('dragend', () => {
        stepCard.classList.remove('dragging');
        stepCard.draggable = false;
        document.querySelectorAll('.step-card').forEach(c => {
          c.classList.remove('drag-over-above', 'drag-over-below');
        });
      });

      stepCard.addEventListener('dragover', (e) => {
        e.preventDefault();
        e.dataTransfer.dropEffect = 'move';
        
        const draggingCard = document.querySelector('.step-card.dragging');
        if (!draggingCard || draggingCard === stepCard) return;

        const rect = stepCard.getBoundingClientRect();
        const midpoint = rect.top + rect.height / 2;
        if (e.clientY < midpoint) {
          stepCard.classList.add('drag-over-above');
          stepCard.classList.remove('drag-over-below');
        } else {
          stepCard.classList.add('drag-over-below');
          stepCard.classList.remove('drag-over-above');
        }
      });

      stepCard.addEventListener('dragleave', () => {
        stepCard.classList.remove('drag-over-above', 'drag-over-below');
      });

      stepCard.addEventListener('drop', (e) => {
        e.preventDefault();
        const fromIdx = parseInt(e.dataTransfer.getData('text/plain'), 10);
        const rect = stepCard.getBoundingClientRect();
        const midpoint = rect.top + rect.height / 2;
        const isAbove = e.clientY < midpoint;
        
        if (isNaN(fromIdx) || fromIdx === idx) {
          stepCard.classList.remove('drag-over-above', 'drag-over-below');
          return;
        }

        reorderSteps(fromIdx, idx, isAbove);
      });

      stepsListContainer.appendChild(stepCard);
    });

    attachStepChangeHandlers();
  });
}

function attachStepChangeHandlers() {
  // Selector inputs
  document.querySelectorAll('.selector-input').forEach(input => {
    input.addEventListener('change', (e) => {
      updateStepField(parseInt(e.target.dataset.id), 'selector', e.target.value);
    });
  });

  // Action dropdown selectors
  document.querySelectorAll('.step-action-select').forEach(select => {
    select.addEventListener('change', (e) => {
      updateStepField(parseInt(e.target.dataset.id), 'action', e.target.value);
    });
  });

  // Value inputs (for Type)
  document.querySelectorAll('.value-input').forEach(input => {
    input.addEventListener('change', (e) => {
      updateStepField(parseInt(e.target.dataset.id), 'value', e.target.value);
    });
  });

  // Delay inputs
  document.querySelectorAll('.delay-input-val').forEach(input => {
    input.addEventListener('change', (e) => {
      updateStepField(parseInt(e.target.dataset.id), 'delay', parseFloat(e.target.value) || 0);
    });
  });

  // Delete buttons
  document.querySelectorAll('.btn-delete').forEach(btn => {
    btn.addEventListener('click', (e) => {
      const stepId = parseInt(e.currentTarget.dataset.id);
      deleteStep(stepId);
    });
  });

  // Target pickers
  document.querySelectorAll('.btn-pick').forEach(btn => {
    btn.addEventListener('click', (e) => {
      const stepId = parseInt(e.currentTarget.dataset.id);
      startPickMode(stepId);
    });
  });
}

// Add a step
async function addNewStep() {
  chrome.storage.local.get('steps', (data) => {
    const steps = data.steps || [];
    const newId = steps.length > 0 ? Math.max(...steps.map(s => s.id)) + 1 : 1;
    steps.push({
      id: newId,
      action: 'click',
      selector: '',
      value: '',
      delay: 0.5 // Default to 0.5 seconds
    });
    chrome.storage.local.set({ steps }, () => {
      renderSteps();
    });
  });
}

// Update step field directly in storage
async function updateStepField(stepId, field, value) {
  chrome.storage.local.get('steps', (data) => {
    const steps = data.steps || [];
    const step = steps.find(s => s.id === stepId);
    if (step) {
      step[field] = value;
      chrome.storage.local.set({ steps }, () => {
        if (field === 'action') {
          renderSteps();
        }
      });
    }
  });
}

// Delete step
async function deleteStep(stepId) {
  chrome.storage.local.get('steps', (data) => {
    const steps = (data.steps || []).filter(s => s.id !== stepId);
    chrome.storage.local.set({ steps }, () => {
      renderSteps();
    });
  });
}

// Send message with fallback auto-injection
function sendTabMessageWithInjection(tabId, message, callback) {
  chrome.tabs.sendMessage(tabId, message, (response) => {
    if (chrome.runtime.lastError) {
      // Content script is not injected. Inject dynamically
      chrome.scripting.executeScript({
        target: { tabId: tabId },
        files: ['content.js']
      }).then(() => {
        return chrome.scripting.insertCSS({
          target: { tabId: tabId },
          files: ['content.css']
        });
      }).then(() => {
        // Retry message delivery
        chrome.tabs.sendMessage(tabId, message, (secondResponse) => {
          if (chrome.runtime.lastError) {
            console.warn("Failed to communicate with content script after injection:", chrome.runtime.lastError.message);
          } else if (callback) {
            callback(secondResponse);
          }
        });
      }).catch(err => {
        console.error("Automator injection failure:", err);
        if (message.action === 'start_picker') {
          chrome.storage.local.set({ pickingStepId: null });
        }
        alert("This page doesn't support element selection (e.g. system pages, new tabs, or extension stores). Please try on a standard web page.");
      });
    } else {
      if (callback) {
        callback(response);
      }
    }
  });
}

// Picker trigger logic
async function startPickMode(stepId) {
  chrome.storage.local.set({ pickingStepId: stepId }, async () => {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    if (!tab) return;
    
    sendTabMessageWithInjection(tab.id, { action: 'start_picker' }, () => {
      // Close popup window to allow picker visibility on site
      window.close();
    });
  });
}

// Toggle sequence
async function toggleAutomation() {
  chrome.storage.local.get('automationState', async (data) => {
    const state = data.automationState || { status: 'idle' };
    if (state.status === 'running') {
      await stopAutomation();
    } else {
      await startAutomation();
    }
  });
}

// Run sequence
async function startAutomation() {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  if (!tab) return;

  chrome.storage.local.get('automationState', (data) => {
    const state = data.automationState || { logs: [] };
    state.status = 'running';
    state.currentLoop = 0;
    state.currentStep = 0;
    state.logs = state.logs || [];
    state.logs.push(`[Popup] Initiating click automation sequence...`);
    chrome.storage.local.set({ automationState: state }, () => {
      sendTabMessageWithInjection(tab.id, { action: 'trigger_run' });
    });
  });
}

// Stop sequence
async function stopAutomation() {
  chrome.storage.local.get('automationState', (data) => {
    const state = data.automationState || { logs: [] };
    state.status = 'idle';
    state.logs = state.logs || [];
    state.logs.push(`[Popup] Stop requested by user.`);
    chrome.storage.local.set({ automationState: state }, async () => {
      const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
      if (!tab) return;
      sendTabMessageWithInjection(tab.id, { action: 'trigger_stop' });
    });
  });
}

// Log Terminal updates
function startLogMonitoring() {
  const statusBadge = document.getElementById('status-badge');
  const logsTerminal = document.getElementById('logsTerminal');
  const toggleBtn = document.getElementById('toggleBtn');

  setInterval(() => {
    chrome.storage.local.get('automationState', (data) => {
      const state = data.automationState || { status: 'idle', logs: [] };
      
      statusBadge.innerText = state.status;
      statusBadge.className = `badge ${state.status}`;

      if (toggleBtn) {
        if (state.status === 'running') {
          toggleBtn.innerText = '⏹️ Stop Automation';
          toggleBtn.className = 'btn-danger';
        } else {
          toggleBtn.innerText = '▶️ Start Automation';
          toggleBtn.className = 'btn-primary';
        }
      }

      if (state.logs && state.logs.length > 0) {
        logsTerminal.innerHTML = '';
        state.logs.forEach(log => {
          const div = document.createElement('div');
          if (log.includes('❌') || log.includes('Error')) {
            div.className = 'log-err';
          }
          div.innerText = log;
          logsTerminal.appendChild(div);
        });
        logsTerminal.scrollTop = logsTerminal.scrollHeight;
      } else {
        logsTerminal.innerHTML = '<div class="log-placeholder">No actions recorded yet. Ready...</div>';
      }
    });
  }, 400);
}

// Clear Logs
function clearLogs() {
  chrome.storage.local.get('automationState', (data) => {
    const state = data.automationState || { status: 'idle', logs: [] };
    state.logs = [];
    chrome.storage.local.set({ automationState: state });
  });
}

// Convex Backup Buttons
function initConvexButtons() {
  const saveToConvexBtn = document.getElementById('saveToConvex');
  const loadFromConvexBtn = document.getElementById('loadFromConvex');

  if (saveToConvexBtn) {
    saveToConvexBtn.addEventListener('click', function () {
      const original = saveToConvexBtn.innerHTML;
      saveToConvexBtn.innerHTML = '⏳ Saving...';

      chrome.storage.local.get(['steps', 'loopCount', 'loopDelay'], (items) => {
        chrome.runtime.sendMessage({ action: 'saveToConvex', data: items }, (response) => {
          if (response && response.success !== false) {
            saveToConvexBtn.innerHTML = '✅ Saved!';
          } else {
            saveToConvexBtn.innerHTML = '❌ Failed';
          }
          setTimeout(() => { saveToConvexBtn.innerHTML = original; }, 2000);
        });
      });
    });
  }

  if (loadFromConvexBtn) {
    loadFromConvexBtn.addEventListener('click', function () {
      const original = loadFromConvexBtn.innerHTML;
      loadFromConvexBtn.innerHTML = '⏳ Loading...';

      chrome.runtime.sendMessage({ action: 'loadFromConvex' }, (response) => {
        if (response && response.success !== false && response.data) {
          const config = response.data;
          chrome.storage.local.set(config, () => {
            loadFromConvexBtn.innerHTML = '✅ Restored!';
            initSettings();
            renderSteps();
            setTimeout(() => { loadFromConvexBtn.innerHTML = original; }, 2000);
          });
        } else {
          loadFromConvexBtn.innerHTML = '❌ Failed';
          setTimeout(() => { loadFromConvexBtn.innerHTML = original; }, 2000);
        }
      });
    });
  }
}
