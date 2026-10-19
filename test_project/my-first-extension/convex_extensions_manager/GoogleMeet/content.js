(() => {
  let previousActive = null;
  let candidateActive = null;
  let candidateSince = 0;
  let lastName = '';
  let transitionTimer = null;

  function isInMeeting() {
    const labels = [...document.querySelectorAll('[aria-label]')]
      .map((element) => (element.getAttribute('aria-label') || '').toLowerCase());
    const hasLeaveControl = labels.some((label) =>
      /leave call|end call|hang up|leave meeting/.test(label));
    const hasMeetingSurface = Boolean(
      document.querySelector('[data-call-ended="false"], [jsname="Qx7uuf"], [data-meeting-title]') ||
      document.querySelector('[data-is-muted], [data-self-name]')
    );
    return hasLeaveControl || hasMeetingSurface;
  }

  function getMeetingName() {
    const heading = document.querySelector('[data-meeting-title], [role="heading"]');
    const headingName = heading?.textContent?.trim();
    if (headingName && headingName.length < 180) return headingName;

    const title = (document.title || '').replace(/\s*[-–|]\s*Google Meet\s*$/i, '').trim();
    if (title && !/^meet\s*[-–|]/i.test(title)) return title;
    const code = location.pathname.match(/\/([a-z]{3}-[a-z]{4}-[a-z]{3})/i)?.[1];
    return code ? `Google Meet (${code})` : 'Google Meet';
  }

  function report() {
    const active = isInMeeting();
    const name = getMeetingName();
    if (active !== candidateActive) {
      candidateActive = active;
      candidateSince = Date.now();
      clearTimeout(transitionTimer);
      // Meet's controls can briefly disappear while its call UI rerenders.
      transitionTimer = setTimeout(report, active ? 4000 : 12000);
      return;
    }

    const requiredStableMs = active ? 4000 : 12000;
    if (active !== previousActive && Date.now() - candidateSince < requiredStableMs) {
      clearTimeout(transitionTimer);
      transitionTimer = setTimeout(report, requiredStableMs - (Date.now() - candidateSince));
      return;
    }

    if (active !== previousActive || (active && name !== lastName)) {
      previousActive = active;
      lastName = name;
      chrome.runtime.sendMessage({ action: 'meetingState', active, name, url: location.href, observedAt: Date.now() }).catch(() => {});
    }
  }

  report();
  new MutationObserver(report).observe(document.documentElement, {
    subtree: true,
    childList: true,
    attributes: true,
    attributeFilter: ['aria-label', 'data-meeting-title', 'data-call-ended']
  });
  setInterval(report, 5000);
  window.addEventListener('beforeunload', () => {
    chrome.runtime.sendMessage({ action: 'meetingTabClosing', observedAt: Date.now() }).catch(() => {});
  });
})();
