const DEFAULT_FALLBACK_SETTINGS = {
  localServerUrl: 'http://192.168.0.101:5000/',
  siteUrl: 'https://nahid6970.github.io/db/5000_myhome/myhome',
  mode: 'local'
};

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
    mode: result.fallbackSettings?.mode === 'site' ? 'site' : DEFAULT_FALLBACK_SETTINGS.mode
  };
}

function redirectToSite(tabId, siteUrl, reason) {
  console.log(reason, siteUrl);
  chrome.tabs.update(tabId, { url: siteUrl });
}

// Listen for tab updates
chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
  // Handle local server fallback redirection
  if (changeInfo.status === 'complete' && tab.url) {
    chrome.storage.local.get(['enabledScripts', 'fallbackSettings'], (result) => {
      const enabledScripts = result.enabledScripts || {};
      const fallbackSettings = getFallbackSettings(result);
      const localServerUrl = fallbackSettings.localServerUrl;
      const siteUrl = fallbackSettings.siteUrl;
      
      // Check if local server fallback script is enabled
      if (enabledScripts['user_scripts/local_server_fallback.js'] && 
          localServerUrl &&
          tab.url.startsWith(localServerUrl)) {
        if (fallbackSettings.mode === 'site') {
          redirectToSite(tabId, siteUrl, 'Fallback mode set to site, redirecting immediately to:');
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
            redirectToSite(tabId, siteUrl, 'Local server unavailable, redirecting to fallback:');
          }
        }).catch(() => {
          // If we can't execute script (likely an error page), redirect anyway
          redirectToSite(tabId, siteUrl, 'Cannot execute script on error page, redirecting to fallback:');
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

// Optional: Listen for storage changes to debug
chrome.storage.onChanged.addListener((changes, namespace) => {
  console.log('Storage changed:', changes);
});
