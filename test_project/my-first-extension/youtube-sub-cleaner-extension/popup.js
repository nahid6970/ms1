// Stores all resolved channel data so we can re-sort without re-fetching
let allChannels = [];
let currentSort = 'oldest';

document.addEventListener('DOMContentLoaded', () => {
  // ── Restore saved state on open ──
  chrome.storage.local.get(['yt_api_key', 'yt_scan_results', 'yt_scan_sort'], (result) => {
    if (result.yt_api_key) {
      document.getElementById('api-key').value = result.yt_api_key;
    }

    if (result.yt_scan_results && result.yt_scan_results.length > 0) {
      allChannels = result.yt_scan_results;
      currentSort = result.yt_scan_sort || 'oldest';

      // Restore active sort button
      document.querySelectorAll('.sort-btn').forEach(b => b.classList.remove('active'));
      const activeBtn = document.querySelector(`[data-sort="${currentSort}"]`);
      if (activeBtn) activeBtn.classList.add('active');

      renderList();
      document.getElementById('sort-bar').style.display = 'flex';
      renderStats(allChannels.length);
    }
  });

  // ── Scan button ──
  document.getElementById('scan-btn').addEventListener('click', async () => {
    const apiKey = document.getElementById('api-key').value.trim();
    if (!apiKey) { alert('Please enter your API Key'); return; }

    chrome.storage.local.set({ yt_api_key: apiKey });

    allChannels = [];
    currentSort = 'oldest';

    const list     = document.getElementById('channels-list');
    const sortBar  = document.getElementById('sort-bar');
    const statsBar = document.getElementById('stats-bar');

    list.innerHTML = '<div class="status-msg">Scrolling page to load all channels…</div>';
    sortBar.style.display  = 'none';
    statsBar.style.display = 'none';

    // Reset active sort button
    document.querySelectorAll('.sort-btn').forEach(b => b.classList.remove('active'));
    document.querySelector('[data-sort="oldest"]').classList.add('active');

    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    if (!tab) { list.innerHTML = '<div class="status-msg error">No active tab found.</div>'; return; }

    chrome.tabs.sendMessage(tab.id, { action: 'scan' }, async (response) => {
      if (chrome.runtime.lastError) {
        list.innerHTML = `<div class="status-msg error">${chrome.runtime.lastError.message}</div>`;
        return;
      }
      if (!response || !response.channels || response.channels.length === 0) {
        list.innerHTML = '<div class="status-msg">No channels found. Go to <b>youtube.com/feed/channels</b></div>';
        return;
      }

      list.innerHTML = '';
      const total = response.channels.length;

      for (const ch of response.channels) {
        const div = document.createElement('div');
        div.className = 'ch-row';
        div.innerHTML = `<span class="ch-name">${ch.name}</span><em class="ch-status">Loading...</em>`;
        list.appendChild(div);
        list.scrollTop = list.scrollHeight;

        try {
          const channelId = await resolveChannelId(ch.url, apiKey);
          if (!channelId) {
            div.querySelector('.ch-status').textContent = 'Unresolved';
            allChannels.push({ name: ch.name, url: ch.url, days: 999999, text: '?', color: '#555' });
            continue;
          }

          const res1  = await fetch(`https://www.googleapis.com/youtube/v3/channels?part=contentDetails&id=${channelId}&key=${apiKey}`);
          const data1 = await res1.json();

          if (data1.error || !data1.items || data1.items.length === 0) {
            div.querySelector('.ch-status').textContent = data1.error ? 'API Error' : 'Not found';
            allChannels.push({ name: ch.name, url: ch.url, days: 999999, text: '?', color: '#555' });
            continue;
          }

          const uploadsId = data1.items[0].contentDetails.relatedPlaylists.uploads;
          const res2      = await fetch(`https://www.googleapis.com/youtube/v3/playlistItems?part=snippet&playlistId=${uploadsId}&maxResults=1&key=${apiKey}`);
          const data2     = await res2.json();

          if (data2.items && data2.items.length > 0) {
            const publishedAt = new Date(data2.items[0].snippet.publishedAt);
            const days        = Math.floor((Date.now() - publishedAt.getTime()) / 86400000);
            const { text, color } = timeAgoColored(days);

            allChannels.push({ name: ch.name, url: ch.url, days, text, color });

            div.querySelector('.ch-name').style.color  = color;
            div.querySelector('.ch-name').style.cursor = 'pointer';
            div.querySelector('.ch-name').title        = 'Open channel';
            div.querySelector('.ch-name').addEventListener('click', () => chrome.tabs.create({ url: ch.url }));

            const badge       = div.querySelector('.ch-status');
            badge.textContent = text;
            badge.style.color = color;
            badge.className   = 'ch-badge';
          } else {
            div.querySelector('.ch-status').textContent = 'No videos';
            allChannels.push({ name: ch.name, url: ch.url, days: 999999, text: 'No videos', color: '#555' });
          }
        } catch (e) {
          div.querySelector('.ch-status').textContent = 'Error';
          allChannels.push({ name: ch.name, url: ch.url, days: 999999, text: 'Error', color: '#555' });
        }

        list.scrollTop = list.scrollHeight;

        // Save incrementally so partial results survive if popup is closed mid-scan
        chrome.storage.local.set({ yt_scan_results: allChannels, yt_scan_sort: currentSort });
      }

      // All done — show sort bar, render stats, save final results
      sortBar.style.display = 'flex';
      renderStats(total);
      chrome.storage.local.set({ yt_scan_results: allChannels, yt_scan_sort: currentSort });
    });
  });

  // ── Sort buttons ──
  document.getElementById('sort-bar').addEventListener('click', (e) => {
    const btn = e.target.closest('.sort-btn');
    if (!btn) return;
    document.querySelectorAll('.sort-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    currentSort = btn.dataset.sort;
    chrome.storage.local.set({ yt_scan_sort: currentSort });
    renderList();
  });
});

// ── Render helpers ──

function renderList() {
  const list = document.getElementById('channels-list');
  const safeDays = d => (d === null || d === undefined || isNaN(d)) ? 999999 : d;
  const sorted = [...allChannels].sort((a, b) => {
    if (currentSort === 'oldest') return safeDays(b.days) - safeDays(a.days);
    if (currentSort === 'newest') return safeDays(a.days) - safeDays(b.days);
    if (currentSort === 'az')     return a.name.localeCompare(b.name);
    return 0;
  });

  list.innerHTML = '';
  for (const ch of sorted) {
    const div = document.createElement('div');
    div.className = 'ch-row';

    const nameEl       = document.createElement('span');
    nameEl.className   = 'ch-name';
    nameEl.textContent = ch.name;
    nameEl.style.color = ch.color;

    if (ch.url && ch.days !== 999999) {
      nameEl.style.cursor = 'pointer';
      nameEl.title        = 'Open channel';
      nameEl.addEventListener('click', () => chrome.tabs.create({ url: ch.url }));
    }

    const badge       = document.createElement('span');
    badge.className   = 'ch-badge';
    badge.textContent = ch.text;
    badge.style.color = ch.color;

    div.appendChild(nameEl);
    div.appendChild(badge);
    list.appendChild(div);
  }
}

function renderStats(total) {
  const deadCount = allChannels.filter(c => c.days >= 365).length;
  const statsBar  = document.getElementById('stats-bar');
  statsBar.style.display = 'flex';
  statsBar.innerHTML = `
    <span>📺 <b>${total}</b> subscriptions</span>
    <span class="stat-dead">🔴 <b>${deadCount}</b> inactive &gt;1y</span>
  `;
}

// ── URL → Channel ID resolution ──

async function resolveChannelId(url, apiKey) {
  if (!url) return null;
  if (url.includes('/channel/')) return url.split('/channel/')[1].split('/')[0];
  if (url.includes('/@')) {
    const handle = url.split('/@')[1].split('/')[0];
    return fetchChannelIdByHandle(handle, apiKey);
  }
  if (url.includes('/user/')) {
    const username = url.split('/user/')[1].split('/')[0];
    return fetchChannelIdByUsername(username, apiKey);
  }
  if (url.includes('/c/')) {
    const name = url.split('/c/')[1].split('/')[0];
    return fetchChannelIdByHandle(name, apiKey);
  }
  return null;
}

async function fetchChannelIdByHandle(handle, apiKey) {
  const res  = await fetch(`https://www.googleapis.com/youtube/v3/channels?part=id&forHandle=${encodeURIComponent(handle)}&key=${apiKey}`);
  const data = await res.json();
  return data.items?.[0]?.id ?? null;
}

async function fetchChannelIdByUsername(username, apiKey) {
  const res  = await fetch(`https://www.googleapis.com/youtube/v3/channels?part=id&forUsername=${encodeURIComponent(username)}&key=${apiKey}`);
  const data = await res.json();
  return data.items?.[0]?.id ?? null;
}

// ── Time helpers ──

function timeAgoColored(days) {
  let text;
  if (days < 1)        text = 'today';
  else if (days < 7)   text = `${days}d`;
  else if (days < 30)  text = `${Math.floor(days / 7)}w`;
  else if (days < 365) text = `${Math.floor(days / 30)}mo`;
  else                 text = `${Math.floor(days / 365)}y`;

  let color;
  if (days < 7)        color = '#2ecc71';
  else if (days < 30)  color = '#27ae60';
  else if (days < 180) color = '#f39c12';
  else if (days < 365) color = '#e67e22';
  else                 color = '#e74c3c';

  return { text, color };
}
