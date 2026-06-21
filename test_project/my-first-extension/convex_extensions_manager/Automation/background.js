// Handle Element Picker logic (requires background service worker as relay between content and popup)
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.action === 'elementPicked') {
    chrome.storage.local.get(['steps', 'pickingStepId'], (data) => {
      const steps = data.steps || [];
      const stepId = data.pickingStepId;
      if (stepId !== undefined && stepId !== null) {
        const updatedSteps = steps.map(step => {
          if (step.id === stepId) {
            return { ...step, selector: message.selector };
          }
          return step;
        });
        chrome.storage.local.set({ steps: updatedSteps, pickingStepId: null }, () => {
          sendResponse({ success: true });
        });
      } else {
        sendResponse({ success: false, error: "No active picking step recorded." });
      }
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
});
