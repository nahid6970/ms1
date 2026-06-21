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
});
