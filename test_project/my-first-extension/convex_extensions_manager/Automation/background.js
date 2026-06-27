// Handle Element Picker logic (requires background service worker as relay between content and popup)
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.action === 'elementPicked') {
    chrome.storage.local.get(['steps', 'pickingStepId', 'projects', 'activeProjectId'], (data) => {
      const steps = data.steps || [];
      const stepIdStr = String(data.pickingStepId || '');
      const projects = data.projects || [];
      const activeId = data.activeProjectId;
      
      if (!stepIdStr) {
        sendResponse({ success: false, error: "No active picking step recorded." });
        return;
      }

      let updatedSteps = [...steps];

      const pickedSelector = message.selector || '';
      const pickedTagName = message.tagName || '';
      const pickedText = message.text || '';

      const applyPickedSelection = (item, selectorMode) => {
        const nextItem = { ...item };
        if (selectorMode === 'text') {
          nextItem.selectorMode = 'text';
          nextItem.selector = pickedTagName || pickedSelector;
          nextItem.selectorText = pickedText;
        } else {
          nextItem.selector = pickedSelector;
        }
        return nextItem;
      };

      if (stepIdStr.startsWith('cond_')) {
        // Format: cond_stepId_condType_condIdx
        const parts = stepIdStr.split('_');
        const sId = parseInt(parts[1], 10);
        const condType = parts[2]; // 'conditions' or 'elseIfConditions'
        const condIdx = parseInt(parts[3], 10);
        updatedSteps = steps.map(step => {
          if (step.id === sId && step[condType] && step[condType][condIdx]) {
            const updatedConds = [...step[condType]];
            updatedConds[condIdx] = { ...updatedConds[condIdx], selector: pickedSelector };
            return { ...step, [condType]: updatedConds };
          }
          return step;
        });
      } else if (stepIdStr.startsWith('substep_')) {
        // Format: substep_stepId_subStepType_subIdx
        const parts = stepIdStr.split('_');
        const sId = parseInt(parts[1], 10);
        const subStepType = parts[2]; // 'thenSteps' or 'elseSteps'
        const subIdx = parseInt(parts[3], 10);
        updatedSteps = steps.map(step => {
          if (step.id === sId && step[subStepType] && step[subStepType][subIdx]) {
            const updatedSubs = [...step[subStepType]];
            const selectorMode = updatedSubs[subIdx].selectorMode || 'css';
            updatedSubs[subIdx] = applyPickedSelection(updatedSubs[subIdx], selectorMode);
            return { ...step, [subStepType]: updatedSubs };
          }
          return step;
        });
      } else {
        // Standard step ID
        const sId = parseInt(stepIdStr, 10);
        updatedSteps = steps.map(step => {
          if (step.id === sId) {
            const selectorMode = step.selectorMode || 'css';
            return applyPickedSelection(step, selectorMode);
          }
          return step;
        });
      }

      // Sync to the active project in projects list
      const activeProj = projects.find(p => p.id === activeId);
      if (activeProj) {
        activeProj.steps = updatedSteps;
      }

      chrome.storage.local.set({ steps: updatedSteps, projects, pickingStepId: null }, () => {
        sendResponse({ success: true });

        // Auto-reopen the extension popup window programmatically in Manifest V3 (Chrome 127+)
        if (chrome.action && typeof chrome.action.openPopup === 'function') {
          chrome.action.openPopup().catch(err => {
            console.warn("Automatic popup reopening is only supported in newer Chromium environments or under policy gestures:", err.message);
          });
        }
      });
    });
    return true;
  }

  if (message.action === 'notify_timeout') {
    const title = message.title || 'ClickFlow timeout';
    const messageText = message.message || 'A configured wait timed out.';

    chrome.notifications.create({
      type: 'basic',
      iconUrl: 'icons/clickflow-icon128.png',
      title,
      message: messageText
    }, () => {
      if (chrome.runtime.lastError) {
        console.warn('Notification failed:', chrome.runtime.lastError.message);
      }
      sendResponse({ success: true });
    });

    return true;
  }

  if (message.action === 'notify_complete') {
    const title = message.title || 'ClickFlow complete';
    const messageText = message.message || 'Automation completed successfully.';

    chrome.notifications.create({
      type: 'basic',
      iconUrl: 'icons/clickflow-icon128.png',
      title,
      message: messageText
    }, () => {
      if (chrome.runtime.lastError) {
        console.warn('Notification failed:', chrome.runtime.lastError.message);
      }
      sendResponse({ success: true });
    });

    return true;
  }
});

let blinkInterval = null;
let showGreen = true;

// Update the extension icon state dynamically (running = blink, idle = normal)
function updateIconState(isRunning) {
  if (!isRunning) {
    if (blinkInterval) {
      clearInterval(blinkInterval);
      blinkInterval = null;
    }
    // Reset to default paths
    chrome.action.setIcon({
      path: {
        "16": "icons/icon-16.png",
        "48": "icons/icon-48.png",
        "128": "icons/icon-128.png"
      }
    });
  } else {
    // If it's already running, don't restart the interval!
    if (blinkInterval) return;

    // Start blinking between green and red
    showGreen = true;
    const toggleIcon = () => {
      if (showGreen) {
        chrome.action.setIcon({
          path: {
            "16": "icons/icon-green-16.png",
            "48": "icons/icon-green-48.png",
            "128": "icons/icon-green-128.png"
          }
        });
      } else {
        chrome.action.setIcon({
          path: {
            "16": "icons/icon-red-16.png",
            "48": "icons/icon-red-48.png",
            "128": "icons/icon-red-128.png"
          }
        });
      }
      showGreen = !showGreen;
    };
    
    toggleIcon(); // Show immediately
    blinkInterval = setInterval(toggleIcon, 1000); // Toggle every 1 second
  }
}

// Watch for automationState changes to update the icon
chrome.storage.onChanged.addListener((changes, areaName) => {
  if (areaName === 'local' && changes.automationState) {
    const status = changes.automationState.newValue?.status;
    updateIconState(status === 'running');
  }
});

// Initialize the icon state on background script startup
chrome.storage.local.get('automationState', (data) => {
  const status = data.automationState?.status;
  updateIconState(status === 'running');
});

