let pickerActive = false;
let hoveredElement = null;
let isAutomating = false;
let stopRequested = false;

// Helpers to read/write storage
function getStorageData() {
  return new Promise((resolve) => {
    chrome.storage.local.get(null, (items) => resolve(items));
  });
}

function updateState(status, loopIndex, stepIndex) {
  chrome.storage.local.get('automationState', (data) => {
    const state = data.automationState || { logs: [] };
    state.status = status;
    state.currentLoop = loopIndex;
    state.currentStep = stepIndex;
    chrome.storage.local.set({ automationState: state });
  });
}

function logMessage(text, isError = false) {
  const timestamp = new Date().toLocaleTimeString();
  const logLine = `[${timestamp}] ${isError ? '❌ ' : ''}${text}`;
  
  chrome.storage.local.get('automationState', (data) => {
    const state = data.automationState || { status: 'idle', currentLoop: 0, currentStep: 0, logs: [] };
    if (!state.logs) state.logs = [];
    state.logs.push(logLine);
    // Keep max 100 logs
    if (state.logs.length > 100) state.logs.shift();
    chrome.storage.local.set({ automationState: state });
  });
}

// Generate unique selector
function getUniqueSelector(el) {
  if (!(el instanceof Element)) return '';
  if (el.id) {
    return '#' + CSS.escape(el.id);
  }
  if (el.tagName.toLowerCase() === 'html') return 'html';
  if (el.tagName.toLowerCase() === 'body') return 'body';

  const parts = [];
  while (el && el.nodeType === Node.ELEMENT_NODE) {
    let selector = el.nodeName.toLowerCase();
    if (el.id) {
      selector += '#' + CSS.escape(el.id);
      parts.unshift(selector);
      break;
    } else {
      let sib = el, nth = 1;
      while (sib = sib.previousElementSibling) {
        if (sib.nodeName.toLowerCase() === selector) nth++;
      }
      selector += `:nth-of-type(${nth})`;
    }
    parts.unshift(selector);
    el = el.parentNode;
  }
  return parts.join(' > ');
}

// Picker event handlers
function onPickerMouseOver(e) {
  if (hoveredElement) {
    hoveredElement.classList.remove('automation-highlight');
  }
  hoveredElement = e.target;
  if (hoveredElement.id === 'automation-picker-toast') {
    hoveredElement = null;
    return;
  }
  hoveredElement.classList.add('automation-highlight');
}

function onPickerMouseOut(e) {
  if (hoveredElement) {
    hoveredElement.classList.remove('automation-highlight');
    hoveredElement = null;
  }
}

function onPickerClick(e) {
  e.preventDefault();
  e.stopPropagation();
  
  const selector = getUniqueSelector(e.target);
  chrome.runtime.sendMessage({ action: 'elementPicked', selector: selector });
  
  stopPicker();
}

function onPickerKeyDown(e) {
  if (e.key === 'Escape') {
    stopPicker();
  }
}

function startPicker() {
  if (pickerActive) return;
  pickerActive = true;
  
  const toast = document.createElement('div');
  toast.id = 'automation-picker-toast';
  toast.innerText = '🎯 Click an element on the page to pick it. Press Esc to cancel.';
  document.body.appendChild(toast);
  
  document.addEventListener('mouseover', onPickerMouseOver, true);
  document.addEventListener('mouseout', onPickerMouseOut, true);
  document.addEventListener('click', onPickerClick, true);
  document.addEventListener('keydown', onPickerKeyDown, true);
}

function stopPicker() {
  if (!pickerActive) return;
  pickerActive = false;
  
  if (hoveredElement) {
    hoveredElement.classList.remove('automation-highlight');
  }
  const toast = document.getElementById('automation-picker-toast');
  if (toast) toast.remove();
  
  document.removeEventListener('mouseover', onPickerMouseOver, true);
  document.removeEventListener('mouseout', onPickerMouseOut, true);
  document.removeEventListener('click', onPickerClick, true);
  document.removeEventListener('keydown', onPickerKeyDown, true);
}

// Execution triggers
const delayMs = ms => new Promise(res => setTimeout(res, ms));

async function runAutomation(startLoop = 0, startStep = 0) {
  if (isAutomating) return;
  isAutomating = true;
  stopRequested = false;

  const data = await getStorageData();
  const steps = data.steps || [];
  const loopCount = parseInt(data.loopCount) || 1;
  const loopDelay = parseInt(data.loopDelay) || 0;

  if (steps.length === 0) {
    logMessage("No steps configured to run.", true);
    isAutomating = false;
    updateState("idle", 0, 0);
    return;
  }

  logMessage(`Starting sequence (Loops: ${loopCount === -1 ? 'Infinite' : loopCount})...`);

  let currentLoop = startLoop;
  while ((loopCount === -1 || currentLoop < loopCount) && !stopRequested) {
    logMessage(`♻️ Starting Loop ${currentLoop + 1}`);
    
    const startIndex = (currentLoop === startLoop) ? startStep : 0;
    for (let i = startIndex; i < steps.length; i++) {
      if (stopRequested) break;
      const step = steps[i];
      updateState("running", currentLoop, i);
      
      logMessage(`[Step ${i + 1}] Waiting ${step.delay}ms...`);
      await delayMs(step.delay);
      
      if (stopRequested) break;
      
      try {
        if (step.action === 'wait') {
          logMessage(`[Step ${i + 1}] Wait step completed.`);
          continue;
        }

        const el = document.querySelector(step.selector);
        if (!el) {
          throw new Error(`Element not found for selector: "${step.selector}"`);
        }

        // Flash target element to show execution visual
        el.classList.add('automation-highlight');
        setTimeout(() => el.classList.remove('automation-highlight'), 500);
        el.scrollIntoView({ block: 'center', behavior: 'smooth' });

        if (step.action === 'click') {
          logMessage(`[Step ${i + 1}] Clicking "${step.selector}"`);
          el.focus();
          
          // Trigger natural event path
          const mousedown = new MouseEvent('mousedown', { bubbles: true, cancelable: true, view: window });
          const mouseup = new MouseEvent('mouseup', { bubbles: true, cancelable: true, view: window });
          el.dispatchEvent(mousedown);
          el.dispatchEvent(mouseup);
          el.click();
        } else if (step.action === 'type') {
          logMessage(`[Step ${i + 1}] Typing "${step.value}" in "${step.selector}"`);
          el.focus();
          el.value = step.value;
          el.dispatchEvent(new Event('input', { bubbles: true }));
          el.dispatchEvent(new Event('change', { bubbles: true }));
        } else if (step.action === 'focus') {
          logMessage(`[Step ${i + 1}] Focusing "${step.selector}"`);
          el.focus();
        } else if (step.action === 'clear') {
          logMessage(`[Step ${i + 1}] Clearing input "${step.selector}"`);
          el.focus();
          el.value = '';
          el.dispatchEvent(new Event('input', { bubbles: true }));
          el.dispatchEvent(new Event('change', { bubbles: true }));
        }
      } catch (err) {
        logMessage(`[Step ${i + 1}] Error: ${err.message}`, true);
      }
    }
    
    if (stopRequested) break;
    currentLoop++;
    
    if (loopCount === -1 || currentLoop < loopCount) {
      logMessage(`Loop ${currentLoop} complete. Delaying ${loopDelay}ms before next loop.`);
      await delayMs(loopDelay);
    }
  }

  isAutomating = false;
  if (stopRequested) {
    updateState("idle", 0, 0);
    logMessage("⏹️ Automation stopped.");
  } else {
    updateState("idle", 0, 0);
    logMessage("✅ Automation sequence completed!");
  }
}

// Global Message Listener
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.action === 'start_picker') {
    startPicker();
    sendResponse({ success: true });
  } else if (message.action === 'trigger_run') {
    runAutomation();
    sendResponse({ success: true });
  } else if (message.action === 'trigger_stop') {
    stopRequested = true;
    sendResponse({ success: true });
  }
});

// Automatic resume check
window.addEventListener('load', () => {
  setTimeout(async () => {
    const data = await getStorageData();
    if (data.automationState && data.automationState.status === 'running') {
      logMessage("🔄 Tab navigation/reload detected. Resuming click automation sequence...");
      runAutomation(data.automationState.currentLoop, data.automationState.currentStep);
    }
  }, 1000);
});
