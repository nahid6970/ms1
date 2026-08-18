chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'scan') {
    scrollToLoadAll().then(() => {
      const channels = Array.from(document.querySelectorAll('ytd-channel-renderer'));
      const data = channels.map(c => ({
        name: c.querySelector('#text')?.textContent?.trim(),
        url: c.querySelector('a#main-link')?.href
      })).filter(c => c.name && c.url);
      sendResponse({ channels: data });
    });

    // Return true to keep the message channel open for the async response
    return true;
  }
});

/**
 * Repeatedly scrolls to the bottom of the page and waits for new
 * ytd-channel-renderer elements to appear, until no new ones load.
 */
async function scrollToLoadAll() {
  let previousCount = 0;
  let unchangedRounds = 0;

  while (unchangedRounds < 3) {
    window.scrollTo(0, document.documentElement.scrollHeight);

    // Wait for YouTube to render the next batch
    await sleep(1500);

    const currentCount = document.querySelectorAll('ytd-channel-renderer').length;

    if (currentCount === previousCount) {
      unchangedRounds++;
    } else {
      unchangedRounds = 0;
      previousCount = currentCount;
    }
  }

  // Scroll back to top so the user isn't left at the bottom
  window.scrollTo(0, 0);
}

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}
