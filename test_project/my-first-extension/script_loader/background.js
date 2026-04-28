const DEFAULT_FALLBACK_SETTINGS = {
  localServerUrl: 'http://192.168.0.101:5000/',
  siteUrl: 'https://nahid6970.github.io/db/5000_myhome/myhome',
  mode: 'local'
};

const NEW_TAB_URLS = new Set([
  'chrome://newtab/',
  'chrome://new-tab-page/',
  'about:newtab'
]);
const CHROME_NEW_TAB_URL = 'chrome://newtab/';

function normalizeUrl(url) {
  if (!url) {
    return '';
  }

  return url.trim();
}

function getFallbackSettings(result) {
  return {
    localServerUrl: normalizeUrl(result.fallbackSettings?.localServerUrl) || DEFAULT_FALLBACK_SETTINGS.localServerUrl,
    siteUrl: normalizeUrl(result.fallbackSettings?.siteUrl) || DEFAULT_FALLBACK_SETTINGS.siteUrl,
    mode: ['local', 'site', 'chrome'].includes(result.fallbackSettings?.mode)
      ? result.fallbackSettings.mode
      : DEFAULT_FALLBACK_SETTINGS.mode
  };
}

function getModeTargetUrl(fallbackSettings) {
  if (fallbackSettings.mode === 'site') {
    return fallbackSettings.siteUrl;
  }

  if (fallbackSettings.mode === 'chrome') {
    return CHROME_NEW_TAB_URL;
  }

  return fallbackSettings.localServerUrl;
}

function redirectToModeTarget(tabId, fallbackSettings, reason) {
  const targetUrl = getModeTargetUrl(fallbackSettings);
  console.log(reason, targetUrl);
  chrome.tabs.update(tabId, { url: targetUrl });
}

function handleNewTabRedirect(tab) {
  const candidateUrl = tab.pendingUrl || tab.url || '';

  if (!NEW_TAB_URLS.has(candidateUrl)) {
    return;
  }

  chrome.storage.local.get(['enabledScripts', 'fallbackSettings'], (result) => {
    const enabledScripts = result.enabledScripts || {};
    const fallbackSettings = getFallbackSettings(result);

    if (!enabledScripts['user_scripts/local_server_fallback.js']) {
      return;
    }

    if (fallbackSettings.mode === 'chrome') {
      return;
    }

    redirectToModeTarget(tab.id, fallbackSettings, 'Redirecting new tab using fallback mode:');
  });
}

// Listen for tab updates
chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
  // Handle local server fallback redirection
  if (changeInfo.status === 'complete' && tab.url) {
    chrome.storage.local.get(['enabledScripts', 'fallbackSettings'], (result) => {
      const enabledScripts = result.enabledScripts || {};
      const fallbackSettings = getFallbackSettings(result);
      const localServerUrl = fallbackSettings.localServerUrl;
      
      // Check if local server fallback script is enabled
      if (enabledScripts['user_scripts/local_server_fallback.js'] && 
          localServerUrl &&
          tab.url.startsWith(localServerUrl)) {
        if (fallbackSettings.mode === 'site' || fallbackSettings.mode === 'chrome') {
          redirectToModeTarget(tabId, fallbackSettings, 'Fallback mode bypassing local server, redirecting to:');
          return;
        }
        
        // Check if this is a Chrome error page
        chrome.scripting.executeScript({
          target: { tabId: tabId },
          func: () => {
            return document.title.includes("This site can't be reached") || 
                   document.title.includes("ERR_") ||
                   document.body.innerText.includes("ERR_CONNECTION_REFUSED");
          }
        }).then((results) => {
          if (results && results[0] && results[0].result) {
            redirectToModeTarget(tabId, { ...fallbackSettings, mode: 'site' }, 'Local server unavailable, redirecting to fallback:');
          }
        }).catch(() => {
          // If we can't execute script (likely an error page), redirect anyway
          redirectToModeTarget(tabId, { ...fallbackSettings, mode: 'site' }, 'Cannot execute script on error page, redirecting to fallback:');
        });
      }
    });
  }

  if (changeInfo.status === 'complete' && tab.url && tab.url.startsWith('http')) {
    // Get enabled scripts from storage
    chrome.storage.local.get(['enabledScripts'], (result) => {
      const enabledScripts = result.enabledScripts || {};
      
      console.log('Tab updated:', tab.url);
      console.log('Enabled scripts:', enabledScripts);

      // Inject each enabled script (except the fallback script which is handled above)
      for (const scriptPath in enabledScripts) {
        if (enabledScripts[scriptPath] && scriptPath !== 'user_scripts/local_server_fallback.js') {
          console.log(`Injecting script: ${scriptPath}`);
          
          chrome.scripting.executeScript({
            target: { tabId: tabId },
            files: [scriptPath]
          }).then(() => {
            console.log(`Successfully injected: ${scriptPath}`);
          }).catch(err => {
            console.error(`Failed to inject ${scriptPath}:`, err);
          });
        }
      }
    });
  }
});

// Listen for extension installation
chrome.runtime.onInstalled.addListener(() => {
  console.log('Script Manager Extension installed');
  chrome.storage.local.get(['fallbackSettings'], (result) => {
    if (!result.fallbackSettings) {
      chrome.storage.local.set({ fallbackSettings: DEFAULT_FALLBACK_SETTINGS });
    }
  });
});

chrome.tabs.onCreated.addListener((tab) => {
  handleNewTabRedirect(tab);
});

// Optional: Listen for storage changes to debug
chrome.storage.onChanged.addListener((changes, namespace) => {
  console.log('Storage changed:', changes);
});
