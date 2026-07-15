// This script runs on YouTube pages.
// It injects a tiny script into the page context to intercept the 'fetch' calls
// that YouTube makes to get subtitle data (timedtext).

console.log('YTC: Interceptor active');

function injectScript() {
  const script = document.createElement('script');
  script.src = chrome.runtime.getURL('inject.js');
  (document.head || document.documentElement).appendChild(script);
  script.onload = () => script.remove();
}

injectScript();

// Listen for the captured subtitle data from the injected script
window.addEventListener('YTC_SUBTITLES_CAPTURED', (event) => {
  const { url, content } = event.detail;
  console.log('YTC: Subtitles intercepted!', url.substring(0, 50) + '...');
  
  // Clean the VTT/XML content to plain text
  const cleanContent = parseSubtitles(content);
  
  // Extract video ID from timedtext URL
  const match = url.match(/[?&]v=([a-zA-Z0-9_-]{11})/);
  const videoId = match ? match[1] : '';

  // Store in local storage for the popup to display
  chrome.storage.local.set({ 
    interceptedSubtitles: cleanContent,
    lastInterceptTime: Date.now(),
    interceptedVideoId: videoId
  });
});

function parseSubtitles(text) {
  if (!text) return '';
  
  // Handle JSON3 format
  if (text.trim().startsWith('{')) {
    try {
      const data = JSON.parse(text);
      return data.events
        ?.filter(e => e.segs)
        .map(e => e.segs.map(s => s.utf8).join('').trim())
        .filter(l => l)
        .join('\n') || '';
    } catch (e) {}
  }

  // Handle XML/SRV format
  if (text.includes('<?xml') || text.includes('<transcript>')) {
    return text.replace(/<[^>]+>/g, (m) => (m === '</p>' || m === ' />' || m === '</text>') ? '\n' : '')
      .replace(/&amp;/g, '&').replace(/&quot;/g, '"').replace(/&apos;/g, "'")
      .replace(/&lt;/g, '<').replace(/&gt;/g, '>')
      .split('\n').map(l => l.trim()).filter(l => l).join('\n');
  }

  // Handle VTT/SRT
  const lines = [];
  for (const l of text.split('\n')) {
    const t = l.trim();
    if (!t || t.startsWith('WEBVTT') || t.includes('-->') || /^\d+$/.test(t)) continue;
    const c = t.replace(/<[^>]+>/g, '').trim();
    if (c && lines[lines.length - 1] !== c) lines.push(c);
  }
  return lines.join('\n');
}
