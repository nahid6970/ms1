const meetingList = document.getElementById('meeting-list');
const emptyState = document.getElementById('empty-state');

function formatDuration(ms) {
  const totalMinutes = Math.max(0, Math.floor(ms / 60000));
  const hours = Math.floor(totalMinutes / 60);
  const minutes = totalMinutes % 60;
  return hours ? `${hours}h ${minutes}m` : `${minutes}m`;
}

function formatDate(timestamp) {
  return new Intl.DateTimeFormat(undefined, { month: 'short', day: 'numeric', hour: 'numeric', minute: '2-digit' }).format(timestamp);
}

function collapseDuplicateRows(meetings) {
  const sorted = [...meetings].sort((a, b) => a.startedAt - b.startedAt);
  const rows = [];
  for (const meeting of sorted) {
    const duplicate = rows.find((row) => {
      if (!row.meetingUrl || row.meetingUrl !== meeting.meetingUrl) return false;
      return Math.max(row.startedAt, meeting.startedAt) - Math.min(row.endedAt, meeting.endedAt) <= 15000;
    });
    if (duplicate) {
      duplicate.startedAt = Math.min(duplicate.startedAt, meeting.startedAt);
      duplicate.endedAt = Math.max(duplicate.endedAt, meeting.endedAt);
      duplicate.durationMs = duplicate.endedAt - duplicate.startedAt;
    } else {
      rows.push({ ...meeting });
    }
  }
  return rows.sort((a, b) => b.startedAt - a.startedAt);
}

function render(state) {
  const meetings = state.meetings || [];
  const activeMeetings = Object.values(state.activeMeetings || {});
  document.getElementById('meeting-count').textContent = String(meetings.length);
  const dot = document.getElementById('active-status-dot');
  const status = document.getElementById('active-status');
  const detail = document.getElementById('active-detail');
  if (activeMeetings.length) {
    dot.classList.add('is-active');
    status.textContent = activeMeetings[0].meetingName || 'Meeting in progress';
    detail.textContent = `Started ${formatDate(activeMeetings[0].startedAt)}`;
  } else {
    dot.classList.remove('is-active');
    status.textContent = 'No active meeting';
    detail.textContent = 'Meetings are tracked automatically.';
  }
  meetingList.replaceChildren();
  emptyState.hidden = meetings.length > 0;
  for (const meeting of meetings.slice(0, 30)) {
    const card = document.createElement('article');
    card.className = 'meeting-card';
    card.setAttribute('role', 'listitem');
    card.dataset.testid = 'meeting-record';
    const name = document.createElement('div');
    name.className = 'meeting-name';
    name.textContent = meeting.meetingName || 'Google Meet';
    const meta = document.createElement('div');
    meta.className = 'meeting-meta';
    const date = document.createElement('span');
    date.textContent = formatDate(meeting.startedAt);
    const duration = document.createElement('span');
    duration.className = 'meeting-duration';
    duration.textContent = formatDuration(meeting.durationMs);
    meta.append(date, duration);
    card.append(name, meta);
    meetingList.append(card);
  }
  const syncStatus = document.getElementById('sync-status');
  syncStatus.textContent = state.syncError ? `Sync issue: ${state.syncError}` : state.lastSyncedAt ? `Synced ${formatDate(state.lastSyncedAt)}` : 'Local records';
}

function refresh() {
  chrome.storage.local.get({ meetings: [], activeMeetings: {}, lastSyncedAt: null, syncError: '' }, (state) => {
    const meetings = collapseDuplicateRows(state.meetings || []);
    if (meetings.length !== (state.meetings || []).length) {
      chrome.storage.local.set({ meetings }, () => {
        chrome.runtime.sendMessage({ action: 'syncNow' });
        render({ ...state, meetings });
      });
      return;
    }
    render({ ...state, meetings });
  });
}

document.getElementById('refresh-meetings').addEventListener('click', refresh);
document.getElementById('clear-meetings').addEventListener('click', () => {
  if (!window.confirm('Clear all recorded meetings from this device and Convex?')) return;
  const button = document.getElementById('clear-meetings');
  button.disabled = true;
  chrome.storage.local.set({ meetings: [] }, () => {
    chrome.runtime.sendMessage({ action: 'syncNow' }, (response) => {
      button.disabled = false;
      button.textContent = response?.success ? 'Cleared' : 'Local cleared';
      refresh();
      setTimeout(() => { button.textContent = 'Clear'; }, 1600);
    });
  });
});
document.getElementById('sync-to-convex').addEventListener('click', () => {
  const button = document.getElementById('sync-to-convex');
  button.disabled = true;
  button.textContent = 'Syncing…';
  chrome.runtime.sendMessage({ action: 'syncNow' }, (response) => {
    button.disabled = false;
    button.textContent = response?.success ? 'Synced' : 'Retry sync';
    refresh();
    setTimeout(() => { button.textContent = 'Sync now'; }, 1600);
  });
});
document.getElementById('restore-from-convex').addEventListener('click', () => {
  const button = document.getElementById('restore-from-convex');
  button.disabled = true;
  chrome.runtime.sendMessage({ action: 'restoreFromConvex' }, (response) => {
    button.disabled = false;
    button.textContent = response?.success ? 'Restored' : 'Failed';
    refresh();
    setTimeout(() => { button.textContent = 'Restore'; }, 1600);
  });
});

chrome.storage.onChanged.addListener(refresh);
refresh();
