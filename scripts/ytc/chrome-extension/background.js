// Listen for messages from popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'extractSubtitles') {
    extractSubtitles(request.data)
      .then(() => sendResponse({ success: true }))
      .catch((error) => sendResponse({ success: false, error: error.message }));
    return true; // Keep channel open for async response
  }
});

async function extractSubtitles(data) {
  const { url, language, format, autoSub, useTimeline, startTime, endTime, saveDir } = data;
  
  // Build yt-dlp command
  const cmd = ['yt-dlp', '--skip-download', '--write-subs'];
  
  // Auto-generated subtitles
  if (autoSub) {
    cmd.push('--write-auto-subs');
  }
  
  // Format conversion
  if (format === 'txt') {
    cmd.push('--convert-subs', 'srt'); // Download as SRT first, convert later
  } else {
    cmd.push('--convert-subs', format);
  }
  
  // Language selection
  if (language === 'bn') {
    cmd.push('--sub-langs', 'bn');
  } else if (language === 'hi') {
    cmd.push('--sub-langs', 'hi');
  } else if (language === 'all') {
    cmd.push('--sub-langs', 'all');
  } else {
    cmd.push('--sub-langs', 'en.*');
  }
  
  // Output path
  cmd.push('-o', `${saveDir}/%(title)s.%(ext)s`);
  
  // Add URL
  cmd.push(url);
  
  // Send to native host
  const response = await chrome.runtime.sendNativeMessage(
    'com.ytc.subtitle_extractor',
    {
      command: cmd,
      format: format,
      useTimeline: useTimeline,
      startTime: startTime,
      endTime: endTime,
      saveDir: saveDir
    }
  );
  
  if (!response.success) {
    throw new Error(response.error || 'Unknown error');
  }
  
  return response;
}
