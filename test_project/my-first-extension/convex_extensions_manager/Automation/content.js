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

function notifyTimeout(title, message) {
  chrome.runtime.sendMessage({
    action: 'notify_timeout',
    title,
    message
  }, () => {
    void chrome.runtime.lastError;
  });
}

function isElementVisible(el) {
  if (!(el instanceof Element)) return false;
  const style = window.getComputedStyle(el);
  if (!style) return false;
  if (style.display === 'none' || style.visibility === 'hidden' || style.visibility === 'collapse') return false;
  if (parseFloat(style.opacity || '1') <= 0) return false;
  if (el.hidden) return false;
  return el.getClientRects().length > 0;
}

function isElementClickable(el) {
  if (!isElementVisible(el)) return false;
  if (el.matches(':disabled')) return false;
  if (el.getAttribute('aria-disabled') === 'true') return false;
  const style = window.getComputedStyle(el);
  if (style && style.pointerEvents === 'none') return false;
  return true;
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

// Stop element picker mode
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

async function interruptibleDelay(seconds) {
  if (seconds <= 0) return;
  const ms = seconds * 1000;
  const chunk = 100; // Check state and stop requests every 100ms

  // Use a more robust delay that fights Chrome throttling when minimized/background
  const startTime = Date.now();
  let waited = 0;

  while (waited < ms) {
    if (stopRequested) break;

    const remaining = ms - waited;
    const timeToWait = Math.min(chunk, remaining);

    await delayMs(timeToWait);
    waited = Date.now() - startTime;

    // Force a small yield to help keep execution alive in minimized window
    if (document.visibilityState === 'hidden') {
      await delayMs(10);
    }
  }
}

async function resolveSelector(selector, timeoutSeconds, { matchMode = 'css', requireVisible = false, allowInfiniteWait = false } = {}) {
  const timeoutMs = timeoutSeconds > 0 ? timeoutSeconds * 1000 : 0;
  const startTime = Date.now();

  while (true) {
    if (stopRequested) {
      return { status: 'stopped', element: null };
    }

    let element = null;
    try {
      if (matchMode === 'visible' || matchMode === 'clickable') {
        const candidates = Array.from(document.querySelectorAll(selector));
        element = candidates.find((candidate) => {
          if (matchMode === 'visible') {
            return isElementVisible(candidate);
          }
          return isElementClickable(candidate);
        }) || null;
      } else {
        element = document.querySelector(selector);
      }
    } catch (err) {
      throw new Error(`Invalid selector "${selector}": ${err.message}`);
    }

    if (element && (!requireVisible || element.offsetParent !== null)) {
      return { status: 'found', element };
    }

    if (timeoutMs === 0 && !allowInfiniteWait) {
      return { status: 'not_found', element: null };
    }

    if (timeoutMs > 0 && Date.now() - startTime >= timeoutMs) {
      return { status: 'timeout', element: null };
    }

    await delayMs(500);
  }
}

// Helpers for condition evaluations
async function evaluateCondition(cond) {
  if (!cond) return false;
  const type = cond.type;
  const selector = cond.selector;
  const targetValue = cond.value || '';

  try {
    if (type === 'exists') {
      const el = document.querySelector(selector);
      return !!el;
    }
    if (type === 'visible') {
      const el = document.querySelector(selector);
      return el ? isElementVisible(el) : false;
    }
    if (type === 'clickable') {
      const el = document.querySelector(selector);
      return el ? isElementClickable(el) : false;
    }
    if (type === 'text_contains') {
      const el = document.querySelector(selector);
      if (!el) return false;
      const text = el.textContent || el.innerText || '';
      return text.toLowerCase().includes(targetValue.toLowerCase());
    }
    if (type === 'text_equals') {
      const el = document.querySelector(selector);
      if (!el) return false;
      const text = (el.textContent || el.innerText || '').trim();
      return text.toLowerCase() === targetValue.trim().toLowerCase();
    }
    if (type === 'url_contains') {
      return window.location.href.toLowerCase().includes(targetValue.toLowerCase());
    }
    if (type === 'url_equals') {
      return window.location.href.trim().toLowerCase() === targetValue.trim().toLowerCase();
    }
    if (type === 'value_contains') {
      const el = document.querySelector(selector);
      if (!el || el.value === undefined) return false;
      return String(el.value).toLowerCase().includes(targetValue.toLowerCase());
    }
    if (type === 'value_equals') {
      const el = document.querySelector(selector);
      if (!el || el.value === undefined) return false;
      return String(el.value).trim().toLowerCase() === targetValue.trim().toLowerCase();
    }
  } catch (err) {
    console.error('Condition evaluation error:', err);
    return false;
  }
  return false;
}

async function evaluateConditionsList(conditions, logicMode) {
  if (!conditions || conditions.length === 0) return true;

  const results = [];
  for (const cond of conditions) {
    const res = await evaluateCondition(cond);
    results.push(res);
  }

  if (logicMode === 'any') {
    return results.some(r => r === true);
  } else {
    return results.every(r => r === true);
  }
}

async function evaluateConcurrentConditions(step, timeoutSeconds) {
  const timeoutMs = timeoutSeconds > 0 ? timeoutSeconds * 1000 : 0;
  const startTime = Date.now();

  const thenConds = step.conditions || [];
  const thenMode = step.logicMode || 'all';

  const elseIfConds = step.elseIfConditions || [];
  const elseIfMode = step.elseIfLogicMode || 'all';

  while (true) {
    if (stopRequested) return { outcome: 'else' };

    // 1. Check IF (THEN) conditions
    const thenPassed = await evaluateConditionsList(thenConds, thenMode);
    if (thenPassed && thenConds.length > 0) {
      return { outcome: 'then' };
    }

    // 2. Check ELSE-IF conditions
    const elseIfPassed = await evaluateConditionsList(elseIfConds, elseIfMode);
    if (elseIfPassed && elseIfConds.length > 0) {
      return { outcome: 'elseIf' };
    }

    // Default outcome if no conditions are configured
    if (thenConds.length === 0 && elseIfConds.length === 0) {
      return { outcome: 'then' };
    }

    if (timeoutMs === 0) {
      if (thenPassed) return { outcome: 'then' };
      if (elseIfPassed) return { outcome: 'elseIf' };
      return { outcome: 'else' };
    }

    if (Date.now() - startTime >= timeoutMs) {
      // Re-evaluate one final time on expiration
      const finalThen = await evaluateConditionsList(thenConds, thenMode);
      if (finalThen) return { outcome: 'then' };
      const finalElseIf = await evaluateConditionsList(elseIfConds, elseIfMode);
      if (finalElseIf) return { outcome: 'elseIf' };
      return { outcome: 'else' };
    }

    await delayMs(500);
  }
}

// Nested branching & standard actions executors
async function executeStandardAction(step, label, waitTimeout, selectorMode) {
  if (step.action === 'wait') {
    logMessage(`[Step ${label}] Wait step completed.`);
    return false;
  }

  if (step.action === 'waitFor') {
    logMessage(`[Step ${label}] Waiting for element: ${step.selector}`);
    const result = await resolveSelector(step.selector, waitTimeout, {
      matchMode: selectorMode,
      requireVisible: true,
      allowInfiniteWait: true
    });

    if (result.status === 'found') {
      const el = result.element;
      logMessage(`[Step ${label}] Element found and visible!`);
      el.classList.add('automation-highlight');
      setTimeout(() => el.classList.remove('automation-highlight'), 800);
    } else if (result.status === 'timeout') {
      logMessage(`[Step ${label}] Timeout waiting for element`, true);
      notifyTimeout(
        'ClickFlow timeout',
        `Step ${label} did not find a matching element within ${waitTimeout}s.`
      );
    }
    return false;
  }

  if (step.action === 'navigate') {
    logMessage(`[Step ${label}] Navigating to: ${step.selector || step.value}`);
    if (step.selector) {
      const navResult = await resolveSelector(step.selector, waitTimeout, {
        matchMode: selectorMode,
        requireVisible: false,
        allowInfiniteWait: false
      });

      if (navResult.status === 'timeout') {
        logMessage(`[Step ${label}] Timeout waiting for element`, true);
        notifyTimeout(
          'ClickFlow timeout',
          `Step ${label} did not find a matching element within ${waitTimeout}s.`
        );
        return false;
      }

      if (navResult.status === 'not_found') {
        const navEl = document.querySelector(step.selector);
        if (navEl) navEl.click();
        else window.location.href = step.selector;
        return true;
      }

      const navEl = navResult.element;
      if (navEl) navEl.click();
      else window.location.href = step.selector;
    } else if (step.value) {
      window.location.href = step.value;
    }
    return true;
  }

  const result = await resolveSelector(step.selector, waitTimeout, {
    matchMode: selectorMode,
    requireVisible: false,
    allowInfiniteWait: false
  });

  if (result.status === 'timeout') {
    logMessage(`[Step ${label}] Timeout waiting for element`, true);
    notifyTimeout(
      'ClickFlow timeout',
      `Step ${label} did not find a matching element within ${waitTimeout}s.`
    );
    return false;
  }

  if (result.status === 'not_found') {
    throw new Error(`Element not found for selector: "${step.selector}"`);
  }

  if (result.status === 'stopped') {
    return false;
  }

  const el = result.element;
  el.classList.add('automation-highlight');
  setTimeout(() => el.classList.remove('automation-highlight'), 500);
  el.scrollIntoView({ block: 'center', behavior: 'smooth' });

  if (step.action === 'click') {
    logMessage(`[Step ${label}] Clicking "${step.selector}"`);
    el.focus();
    const mousedown = new MouseEvent('mousedown', { bubbles: true, cancelable: true, view: window });
    const mouseup = new MouseEvent('mouseup', { bubbles: true, cancelable: true, view: window });
    el.dispatchEvent(mousedown);
    el.dispatchEvent(mouseup);
    el.click();
  } else if (step.action === 'type') {
    logMessage(`[Step ${label}] Typing "${step.value}" in "${step.selector}"`);
    el.focus();
    el.value = step.value;
    el.dispatchEvent(new Event('input', { bubbles: true }));
    el.dispatchEvent(new Event('change', { bubbles: true }));
  } else if (step.action === 'focus') {
    logMessage(`[Step ${label}] Focusing "${step.selector}"`);
    el.focus();
  } else if (step.action === 'clear') {
    logMessage(`[Step ${label}] Clearing input "${step.selector}"`);
    el.focus();
    el.value = '';
    el.dispatchEvent(new Event('input', { bubbles: true }));
    el.dispatchEvent(new Event('change', { bubbles: true }));
  }
  return false;
}

async function executeSubStepsList(subSteps, currentLoop, parentLabel, waitTimeout) {
  for (let idx = 0; idx < subSteps.length; idx++) {
    if (stopRequested) break;
    const step = subSteps[idx];
    const selectorMode = step.selectorMode || 'css';
    const label = `${parentLabel}.${idx + 1}`;

    logMessage(`[Step ${label}] Waiting ${step.delay}s...`);
    await interruptibleDelay(step.delay);

    if (stopRequested) break;

    try {
      if (step.action === 'branch') {
        logMessage(`[Step ${label}] Evaluating nested branch...`);
        const timeoutVal = step.timeout !== undefined ? parseFloat(step.timeout) : 0;
        const result = await evaluateConcurrentConditions(step, timeoutVal);

        if (result.outcome === 'then') {
          logMessage(`[Step ${label}] Nested branch IF condition met.`);
          if (step.thenSteps && step.thenSteps.length > 0) {
            const nav = await executeSubStepsList(step.thenSteps, currentLoop, `${label} > THEN`, waitTimeout);
            if (nav) return true;
          }
        } else if (result.outcome === 'elseIf') {
          logMessage(`[Step ${label}] Nested branch ELSE-IF condition met.`);
          if (step.elseIfSteps && step.elseIfSteps.length > 0) {
            const nav = await executeSubStepsList(step.elseIfSteps, currentLoop, `${label} > ELSEIF`, waitTimeout);
            if (nav) return true;
          }
        } else {
          logMessage(`[Step ${label}] Nested branch fallback ELSE triggered.`);
          if (step.elseSteps && step.elseSteps.length > 0) {
            const nav = await executeSubStepsList(step.elseSteps, currentLoop, `${label} > ELSE`, waitTimeout);
            if (nav) return true;
          }
        }
        continue;
      }

      const didNav = await executeStandardAction(step, label, waitTimeout, selectorMode);
      if (didNav) {
        return true;
      }
    } catch (err) {
      logMessage(`[Step ${label}] Error: ${err.message}`, true);
    }
  }
  return false;
}

async function executeStepsList(stepsList, currentLoop, startStepIndex, waitTimeout) {
  for (let i = startStepIndex; i < stepsList.length; i++) {
    if (stopRequested) break;
    const step = stepsList[i];
    const selectorMode = step.selectorMode || 'css';
    
    updateState("running", currentLoop, i);

    logMessage(`[Step ${i + 1}] Waiting ${step.delay || 0}s...`);
    await interruptibleDelay(step.delay || 0);

    if (stopRequested) break;

    try {
      if (step.action === 'branch') {
        logMessage(`[Step ${i + 1}] Evaluating branch step...`);
        const timeoutVal = step.timeout !== undefined ? parseFloat(step.timeout) : 0;
        const result = await evaluateConcurrentConditions(step, timeoutVal);
        
        if (result.outcome === 'then') {
          logMessage(`[Step ${i + 1}] IF condition met. Executing THEN steps.`);
          if (step.thenSteps && step.thenSteps.length > 0) {
            const nav = await executeSubStepsList(step.thenSteps, currentLoop, `${i + 1} > THEN`, waitTimeout);
            if (nav) return true;
          }
        } else if (result.outcome === 'elseIf') {
          logMessage(`[Step ${i + 1}] ELSE-IF condition met. Executing ELSE-IF steps.`);
          if (step.elseIfSteps && step.elseIfSteps.length > 0) {
            const nav = await executeSubStepsList(step.elseIfSteps, currentLoop, `${i + 1} > ELSEIF`, waitTimeout);
            if (nav) return true;
          }
        } else {
          logMessage(`[Step ${i + 1}] Timeout or conditions failed. Executing ELSE fallback steps.`);
          if (step.elseSteps && step.elseSteps.length > 0) {
            const nav = await executeSubStepsList(step.elseSteps, currentLoop, `${i + 1} > ELSE`, waitTimeout);
            if (nav) return true;
          }
        }
        continue;
      }

      const didNav = await executeStandardAction(step, i + 1, waitTimeout, selectorMode);
      if (didNav) {
        return true;
      }
    } catch (err) {
      logMessage(`[Step ${i + 1}] Error: ${err.message}`, true);
    }
  }
  return false;
}

async function runAutomation(startLoop = 0, startStep = 0) {
  if (isAutomating) return;
  isAutomating = true;
  stopRequested = false;

  const data = await getStorageData();
  const steps = data.steps || [];
  const loopCount = parseInt(data.loopCount) || 1;
  const loopDelay = parseFloat(data.loopDelay) || 0;
  const waitTimeout = parseFloat(data.waitTimeout) || 0;

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
    const didNav = await executeStepsList(steps, currentLoop, startIndex, waitTimeout);
    if (didNav) {
      return; // Stop execution - page reload handler will resume
    }
    
    if (stopRequested) break;
    currentLoop++;
    
    if (loopCount === -1 || currentLoop < loopCount) {
      logMessage(`Loop ${currentLoop} complete. Delaying ${loopDelay}s before next loop.`);
      await interruptibleDelay(loopDelay);
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

// Listen to storage changes to sync stop signal instantly
chrome.storage.onChanged.addListener((changes) => {
  if (changes.automationState) {
    const newValue = changes.automationState.newValue;
    if (newValue && newValue.status === 'idle') {
      stopRequested = true;
    }
  }
});

// Keep page alive when minimized by periodically waking up
let keepAliveInterval = null;

function startKeepAlive() {
  if (keepAliveInterval) return;
  keepAliveInterval = setInterval(() => {
    if (isAutomating && document.visibilityState === 'hidden') {
      // Minimal activity to reduce throttling
      void document.title; // Force micro task
    }
  }, 800);
}

function stopKeepAlive() {
  if (keepAliveInterval) {
    clearInterval(keepAliveInterval);
    keepAliveInterval = null;
  }
}

// Global Message Listener
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.action === 'start_picker') {
    startPicker();
    sendResponse({ success: true });
  } else if (message.action === 'trigger_run') {
    startKeepAlive();
    runAutomation();
    sendResponse({ success: true });
  } else if (message.action === 'trigger_stop') {
    stopRequested = true;
    stopKeepAlive();
    sendResponse({ success: true });
  }
});

// Automatic resume check after navigation
window.addEventListener('load', () => {
  setTimeout(async () => {
    const data = await getStorageData();
    const state = data.automationState;

    if (state && state.status === 'running') {
      const nextStep = (state.currentStep || 0) + 1; // Advance past the navigation step
      logMessage(`🔄 Page loaded. Resuming from step ${nextStep + 1}...`);
      
      startKeepAlive();
      runAutomation(state.currentLoop, nextStep);
    }
  }, 800);
});

// Also handle visibility changes (minimize / restore)
document.addEventListener('visibilitychange', () => {
  if (isAutomating) {
    if (document.visibilityState === 'visible') {
      logMessage("🌐 Browser window restored.");
    } else {
      logMessage("📉 Browser minimized - continuing in background...");
    }
  }
});
