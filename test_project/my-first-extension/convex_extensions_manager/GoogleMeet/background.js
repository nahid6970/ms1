// Configure this with the Convex deployment URL used by the extension workspace.
const CONVEX_URL = 'https://joyous-stingray-672.convex.cloud';
const EXTENSION_NAME = 'google_meet_timesheet';
const MAX_MEETINGS = 5000;

async function readState() {
  return chrome.storage.local.get({ meetings: [], activeMeetings: {} });
}

async function saveState(meetings, activeMeetings) {
  await chrome.storage.local.set({ meetings, activeMeetings });
}

function collapseOverlappingSessions(meetings) {
  const sorted = [...meetings].sort((a, b) => a.startedAt - b.startedAt);
  const result = [];
  for (const meeting of sorted) {
    const prior = result.find((item) => {
      if (!item.meetingUrl || item.meetingUrl !== meeting.meetingUrl) return false;
      const gap = Math.max(item.startedAt, meeting.startedAt) - Math.min(item.endedAt, meeting.endedAt);
      return gap <= 15000;
    });
    if (prior) {
      prior.startedAt = Math.min(prior.startedAt, meeting.startedAt);
      prior.endedAt = Math.max(prior.endedAt, meeting.endedAt);
      prior.durationMs = prior.endedAt - prior.startedAt;
    } else {
      result.push({ ...meeting });
    }
  }
  return result.sort((a, b) => b.startedAt - a.startedAt);
}

async function syncMeetings(meetings) {
  if (!CONVEX_URL || CONVEX_URL.includes('YOUR_CONVEX_URL')) return { success: false, error: 'Configure the Convex URL in background.js.' };
  try {
    const response = await fetch(`${CONVEX_URL}/api/mutation`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ path: 'functions:save', args: { extensionName: EXTENSION_NAME, data: { meetings } }, format: 'json' })
    });
    if (!response.ok) throw new Error(`Convex HTTP ${response.status}: ${await response.text()}`);
    const result = await response.json();
    if (result.status === 'error' || result.errorMessage) throw new Error(result.errorMessage || 'Convex error');
    await chrome.storage.local.set({ lastSyncedAt: Date.now(), syncError: '' });
    return { success: true };
  } catch (error) {
    await chrome.storage.local.set({ syncError: error.message });
    return { success: false, error: error.message };
  }
}

async function finalize(tabId, endedAt = Date.now()) {
  const { meetings, activeMeetings } = await readState();
  const session = activeMeetings[String(tabId)];
  if (!session) return;
  const endTime = Math.max(endedAt, session.startedAt);
  const record = {
    id: session.id,
    meetingName: session.meetingName,
    meetingUrl: session.meetingUrl,
    startedAt: session.startedAt,
    endedAt: endTime,
    durationMs: endTime - session.startedAt
  };
  delete activeMeetings[String(tabId)];
  meetings.unshift(record);
  const normalizedMeetings = collapseOverlappingSessions(meetings).slice(0, MAX_MEETINGS);
  await saveState(normalizedMeetings, activeMeetings);
  await syncMeetings(normalizedMeetings);
}

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  (async () => {
    const tabId = sender.tab?.id;
    if (message.action === 'meetingState' && tabId !== undefined) {
      const { meetings, activeMeetings } = await readState();
      const key = String(tabId);
      if (message.active) {
        const existing = activeMeetings[key];
        activeMeetings[key] = existing ? {
          ...existing,
          meetingName: message.name || existing.meetingName,
          meetingUrl: message.url || existing.meetingUrl
        } : {
          id: crypto.randomUUID(),
          meetingName: message.name || 'Google Meet',
          meetingUrl: message.url || '',
          startedAt: message.observedAt || Date.now()
        };
        await saveState(meetings, activeMeetings);
      } else {
        await finalize(tabId, message.observedAt);
      }
      sendResponse({ success: true });
    } else if (message.action === 'meetingTabClosing' && tabId !== undefined) {
      await finalize(tabId, message.observedAt);
      sendResponse({ success: true });
    } else if (message.action === 'syncNow') {
      const { meetings } = await readState();
      sendResponse(await syncMeetings(meetings));
    } else if (message.action === 'restoreFromConvex') {
      try {
        const response = await fetch(`${CONVEX_URL}/api/query`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ path: 'functions:get', args: { extensionName: EXTENSION_NAME }, format: 'json' })
        });
        if (!response.ok) throw new Error(`Convex HTTP ${response.status}: ${await response.text()}`);
        const result = await response.json();
        if (result.status === 'error' || result.errorMessage) throw new Error(result.errorMessage || 'Convex error');
        const remote = result.value?.meetings;
        if (Array.isArray(remote)) {
          const { activeMeetings } = await readState();
          await saveState(remote, activeMeetings);
        }
        sendResponse({ success: true, count: Array.isArray(remote) ? remote.length : 0 });
      } catch (error) {
        sendResponse({ success: false, error: error.message });
      }
    }
  })().catch((error) => sendResponse({ success: false, error: error.message }));
  return true;
});

chrome.tabs.onRemoved.addListener((tabId) => { finalize(tabId).catch(console.error); });
