// Listen for messages from popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'fetchSubtitles') {
    fetchDirectAPI(request.url)
      .then((content) => {
        chrome.storage.local.set({ 
          interceptedSubtitles: content,
          lastInterceptTime: Date.now()
        });
        sendResponse({ success: true, content });
      })
      .catch((error) => {
        console.error('DEBUG: fetchSubtitles error:', error);
        sendResponse({ success: false, error: error.message || 'Unknown error during fetch' });
      });
    return true;
  }
  
  if (request.action === 'injectToAIStudio') {
    injectToAIStudio(request.prompt, request.subtitles);
    sendResponse({ success: true });
  }
});

async function fetchDirectAPI(url) {
  const match = url.match(/(?:v=|youtu\.be\/)([a-zA-Z0-9_-]{11})/);
  if (!match) throw new Error('Not a valid YouTube URL');
  const videoId = match[1];

  const tabs = await chrome.tabs.query({ active: true, currentWindow: true });
  const tabId = (tabs[0] && tabs[0].url.includes(videoId)) ? tabs[0].id : null;

  if (!tabId) throw new Error('Please keep the YouTube video tab active.');

  // 1. Try to get tracks from tab memory using multiple potential paths
  const results = await chrome.scripting.executeScript({
    target: { tabId: tabId },
    func: () => {
      try {
        // Path 1: Standard player response
        let tracks = window.ytInitialPlayerResponse?.captions?.playerCaptionsTracklistRenderer?.captionTracks;
        
        // Path 2: ytplayer config (older/different versions)
        if (!tracks) {
          const cfg = window.ytplayer?.config?.args?.player_response;
          if (cfg) {
            const parsed = JSON.parse(cfg);
            tracks = parsed.captions?.playerCaptionsTracklistRenderer?.captionTracks;
          }
        }
        
        // Path 3: Try to find any object containing captionTracks in window
        if (!tracks) {
          // This is a bit heavy but can be a last resort
          for (const key in window) {
            if (key.startsWith('yt') && window[key]?.captions?.playerCaptionsTracklistRenderer?.captionTracks) {
              tracks = window[key].captions.playerCaptionsTracklistRenderer.captionTracks;
              break;
            }
          }
        }

        return tracks || [];
      } catch (e) { return null; }
    }
  });

  let tracks = results?.[0]?.result || [];
  let baseUrl = '';

  if (tracks.length > 0) {
    // Pick English or first available
    const track = tracks.find(t => t.languageCode === 'en') || tracks[0];
    baseUrl = track.baseUrl;
  }

  // 2. Fallback to background HTML fetch
  if (!baseUrl) {
    try {
      const res = await fetch(`https://www.youtube.com/watch?v=${videoId}`);
      const html = await res.text();
      const jsonMatch = html.match(/"captionTracks":(\[.*?\])/);
      if (jsonMatch) {
        const captions = JSON.parse(jsonMatch[1]);
        baseUrl = captions[0]?.baseUrl;
      }
    } catch (e) {
      console.warn('DEBUG: Background HTML fetch failed:', e);
    }
  }

  if (!baseUrl) throw new Error('No subtitle tracks detected. Try turning CC on in the player first.');

  // 3. Fetch content via tab context
  const subUrl = baseUrl + (baseUrl.includes('?') ? '&' : '?') + 'fmt=vtt';
  const fetchResult = await chrome.scripting.executeScript({
    target: { tabId: tabId },
    args: [subUrl],
    func: async (url) => {
      try {
        const r = await fetch(url);
        if (!r.ok) return null;
        return await r.text();
      } catch (e) { return null; }
    }
  });

  const vttText = fetchResult?.[0]?.result;
  if (!vttText || vttText.length < 100) throw new Error('Empty or invalid subtitle response from YouTube.');

  // 4. Clean text
  const lines = [];
  const rawLines = vttText.split('\n');
  for (const line of rawLines) {
    const t = line.trim();
    if (!t || t.startsWith('WEBVTT') || t.includes('-->') || /^\d+$/.test(t) || t.startsWith('Kind:') || t.startsWith('Language:')) continue;
    const clean = t.replace(/<[^>]+>/g, '').trim();
    if (clean && lines[lines.length - 1] !== clean) lines.push(clean);
  }
  
  const finalContent = lines.join('\n');
  if (!finalContent) throw new Error('Could not extract any readable text from subtitles.');
  
  return finalContent;
}

async function injectToAIStudio(prompt, subtitles) {
  const tab = await chrome.tabs.create({ url: 'https://aistudio.google.com/prompts/new_chat' });

  chrome.tabs.onUpdated.addListener(function listener(tabId, info) {
    if (tabId === tab.id && info.status === 'complete') {
      chrome.tabs.onUpdated.removeListener(listener);

      chrome.scripting.executeScript({
        target: { tabId: tab.id },
        args: [prompt, subtitles],
        func: (promptText, subtitleText) => {
          const tryInject = () => {
            const editor = document.querySelector('div[contenteditable="true"]') ||
                           document.querySelector('textarea') ||
                           document.querySelector('.prompt-textarea') ||
                           document.querySelector('ms-prompt-input');

            if (editor) {
              editor.focus();
              if (editor.getAttribute('contenteditable') === 'true') {
                document.execCommand('insertText', false, promptText || '');
              } else {
                editor.value = promptText || '';
                editor.dispatchEvent(new Event('input', { bubbles: true }));
              }

              const blob = new Blob([subtitleText], { type: 'text/plain' });
              const file = new File([blob], 'subtitles.txt', { type: 'text/plain' });
              const dataTransfer = new DataTransfer();
              dataTransfer.items.add(file);

              const dropEvent = new DragEvent('drop', {
                bubbles: true,
                cancelable: true,
                dataTransfer: dataTransfer
              });

              editor.dispatchEvent(dropEvent);
              return true;
            }
            return false;
          };

          let attempts = 0;
          const interval = setInterval(() => {
            if (tryInject() || attempts > 30) clearInterval(interval);
            attempts++;
          }, 800);
        }
      });
    }
  });
}
