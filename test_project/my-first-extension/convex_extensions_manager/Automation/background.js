const CONVEX_URL = "https://joyous-stingray-672.convex.cloud";
const EXTENSION_NAME = 'click_automation_extension'; // unique name per extension

async function convexFetch(type, path, args) {
  if (CONVEX_URL === "YOUR_CONVEX_URL_HERE" || !CONVEX_URL) {
    throw new Error("Convex URL not configured in background.js");
  }
  const url = `${CONVEX_URL}/api/${type}`;
  const response = await fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      path,
      args,
      format: "json"
    })
  });
  if (!response.ok) {
    const text = await response.text();
    throw new Error(`Convex HTTP error (${response.status}): ${text}`);
  }
  const result = await response.json();
  if (result && (result.status === "error" || result.errorMessage !== undefined)) {
    throw new Error(result.errorMessage || "Convex error");
  }
  return result.value;
}

async function sendDataToConvex(data) {
  try {
    const result = await convexFetch("mutation", "functions:save", { extensionName: EXTENSION_NAME, data });
    return { success: true, result };
  } catch (error) {
    return { success: false, error: error.message };
  }
}

async function loadDataFromConvex() {
  try {
    const data = await convexFetch("query", "functions:get", { extensionName: EXTENSION_NAME });
    return { success: true, data };
  } catch (error) {
    return { success: false, error: error.message };
  }
}

// Auto-save on storage changes (Only save config to prevent spamming logs)
chrome.storage.local.onChanged.addListener((changes) => {
  if (changes.steps || changes.loopCount || changes.loopDelay) {
    chrome.storage.local.get(['steps', 'loopCount', 'loopDelay'], (items) => {
      if (items.steps && items.steps.length > 0) {
        sendDataToConvex(items);
      }
    });
  }
});

// Handle manual backup/restore and Element Picker logic
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.action === 'saveToConvex') {
    sendDataToConvex(message.data)
      .then(result => sendResponse(result))
      .catch(error => sendResponse({ success: false, error: error.message }));
    return true;
  }
  if (message.action === 'loadFromConvex') {
    loadDataFromConvex()
      .then(result => sendResponse(result))
      .catch(error => sendResponse({ success: false, error: error.message }));
    return true;
  }
  if (message.action === 'elementPicked') {
    // Fetch currently picking step and update storage
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
