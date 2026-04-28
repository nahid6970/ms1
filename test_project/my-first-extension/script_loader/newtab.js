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

function setStatus(message, url) {
  const statusText = document.getElementById('statusText');
  statusText.innerHTML = `${message}<br><br><span class="link">${url}</span>`;
}

function redirectTo(url) {
  setStatus('Redirecting to:', url);
  window.location.replace(url);
}

chrome.storage.local.get(['enabledScripts', 'fallbackSettings'], (result) => {
  const enabledScripts = result.enabledScripts || {};
  const fallbackSettings = getFallbackSettings(result);
  const isFallbackEnabled = Boolean(enabledScripts['user_scripts/local_server_fallback.js']);

  if (!isFallbackEnabled) {
    redirectTo(fallbackSettings.siteUrl);
    return;
  }

  if (fallbackSettings.mode === 'site') {
    redirectTo(fallbackSettings.siteUrl);
    return;
  }

  redirectTo(fallbackSettings.localServerUrl);
});
