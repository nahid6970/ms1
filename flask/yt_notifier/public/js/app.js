/* Shared frontend logic for the YT Notifier static site.
 * Talks to Convex through its HTTP API (/api/query, /api/mutation, /api/action)
 * so no SDK or build step is needed.
 */
const PAGE = document.body.dataset.page || "feed";
const CONFIGURED =
  window.CONVEX_URL &&
  !window.CONVEX_URL.includes("YOUR-DEPLOYMENT");
const API_BASE = CONFIGURED ? window.CONVEX_URL.replace(/\/+$/, "") : "";
let isCheckingUpdates = false;

/* ---------------------------------- utils --------------------------------- */

function esc(value) {
  return String(value ?? "").replace(/[&<>"']/g, (c) => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#39;",
  }[c]));
}

function isoDate(dateStr) {
  const d = new Date(dateStr);
  return isNaN(d.getTime()) ? String(dateStr).slice(0, 10) : d.toISOString().slice(0, 10);
}

function timeLabel(dateStr) {
  const d = new Date(dateStr);
  if (isNaN(d.getTime())) return String(dateStr || "Unknown date");
  const diffMs = Date.now() - d.getTime();
  const minute = 60 * 1000;
  const hour = 60 * minute;
  const day = 24 * hour;
  if (diffMs < minute) return "Just now";
  if (diffMs < hour) return `${Math.floor(diffMs / minute)}m ago`;
  if (diffMs < day) return `${Math.floor(diffMs / hour)}h ago`;
  if (diffMs < day * 7) return `${Math.floor(diffMs / day)}d ago`;
  return d.toLocaleDateString(undefined, { month: "short", day: "numeric", year: "numeric" });
}

function durationBadge(video) {
  if (video.duration) {
    return `<span class="absolute bottom-3 right-3 rounded-md bg-black/85 px-2 py-1 text-xs font-semibold text-white shadow-lg">${esc(video.duration)}</span>`;
  }
  return `<span class="absolute bottom-3 right-3 rounded-md bg-black/70 px-2 py-1 text-[10px] font-semibold uppercase tracking-wide text-slate-300 shadow-lg" title="Run Check Updates after deploying the latest Convex functions to backfill this video duration">Duration pending</span>`;
}

function eyeIcon(isNew) {
  return isNew
    ? `<svg viewBox="0 0 24 24" class="h-4 w-4" fill="none" aria-hidden="true">
        <path d="M2.5 12s3.5-6 9.5-6 9.5 6 9.5 6-3.5 6-9.5 6-9.5-6-9.5-6Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        <path d="M12 15a3 3 0 1 0 0-6 3 3 0 0 0 0 6Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
      </svg>`
    : `<svg viewBox="0 0 24 24" class="h-4 w-4" fill="none" aria-hidden="true">
        <path d="m3 3 18 18" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
        <path d="M10.7 5.2A10.5 10.5 0 0 1 12 5c6 0 9.5 7 9.5 7a17.7 17.7 0 0 1-2.3 3.3M6.1 6.7C3.8 8.2 2.5 12 2.5 12s3.5 7 9.5 7c1.7 0 3.2-.5 4.4-1.2" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        <path d="M9.9 9.9A3 3 0 0 0 14.1 14.1" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
      </svg>`;
}

function externalIcon() {
  return `<svg viewBox="0 0 24 24" class="h-4 w-4" fill="none" aria-hidden="true">
    <path d="M14 4h6v6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
    <path d="M10 14 20 4" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
    <path d="M20 14v4a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h4" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
  </svg>`;
}

function dayLabel(dateStr) {
  const d = new Date(dateStr);
  return isNaN(d.getTime())
    ? dateStr
    : d.toLocaleDateString(undefined, { weekday: "short", month: "short", day: "numeric" });
}

function trackConvexExecution(endpoint) {
  try {
    const raw = localStorage.getItem("convexExecutions") || '{"queries":0,"mutations":0,"actions":0}';
    const data = JSON.parse(raw);
    if (endpoint === "query") data.queries = (data.queries || 0) + 1;
    else if (endpoint === "mutation") data.mutations = (data.mutations || 0) + 1;
    else if (endpoint === "action") data.actions = (data.actions || 0) + 1;
    localStorage.setItem("convexExecutions", JSON.stringify(data));
  } catch (err) {
    console.error("Exec track error:", err);
  }
}

function getConvexExecutions() {
  try {
    const raw = localStorage.getItem("convexExecutions") || '{"queries":0,"mutations":0,"actions":0}';
    const data = JSON.parse(raw);
    const total = (data.queries || 0) + (data.mutations || 0) + (data.actions || 0);
    return {
      queries: data.queries || 0,
      mutations: data.mutations || 0,
      actions: data.actions || 0,
      total,
      limit: 1000000,
      percentUsed: Math.min(100, Math.round((total / 1000000) * 10000) / 100),
    };
  } catch {
    return { queries: 0, mutations: 0, actions: 0, total: 0, limit: 1000000, percentUsed: 0 };
  }
}

window.resetConvexExecutions = function resetConvexExecutions() {
  if (confirm("Reset Convex function execution counters?")) {
    localStorage.removeItem("convexExecutions");
    if (PAGE === "stats" || isPopupOpen()) renderStats({ refreshNav: false });
  }
};

async function callConvex(endpoint, path, args = {}) {
  trackConvexExecution(endpoint);
  const res = await fetch(`${API_BASE}/api/${endpoint}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ path, args, format: "json" }),
  });
  let data;
  try {
    data = await res.json();
  } catch {
    throw new Error(`Convex returned an invalid response (HTTP ${res.status}). Check CONVEX_URL in js/config.js`);
  }
  if (!res.ok || data.status !== "success") {
    throw new Error(data.errorMessage || `Convex error (HTTP ${res.status})`);
  }
  return data.value;
}

function flash(message, type = "info", duration = 3000) {
  const container = document.getElementById("flashMessages");
  if (!container) return;
  const styles = {
    success: "bg-slate-900/95 border-emerald-500/40 text-emerald-300 shadow-emerald-950/30",
    danger: "bg-slate-900/95 border-rose-500/40 text-rose-300 shadow-rose-950/30",
    info: "bg-slate-900/95 border-amber-500/40 text-amber-300 shadow-amber-950/30",
  };
  const icons = {
    success: "fa-circle-check text-emerald-400",
    danger: "fa-triangle-exclamation text-rose-400",
    info: "fa-circle-info text-amber-400",
  };
  const el = document.createElement("div");
  el.className = `toast-enter p-3.5 px-4 rounded-xl border backdrop-blur-md flex items-center justify-between gap-3 shadow-2xl transition ${styles[type] || styles.info}`;
  el.innerHTML = `
    <div class="flex items-center space-x-3 min-w-0">
      <i class="fa-solid ${icons[type] || icons.info} text-base flex-shrink-0"></i>
      <span class="text-xs font-medium leading-relaxed text-slate-200">${esc(message)}</span>
    </div>
    <button type="button" class="text-slate-400 hover:text-white flex-shrink-0 ml-2 transition" onclick="dismissToast(this.parentElement)">
      <i class="fa-solid fa-xmark text-sm"></i>
    </button>`;
  container.appendChild(el);

  if (duration > 0) {
    setTimeout(() => {
      dismissToast(el);
    }, duration);
  }
}

window.dismissToast = function dismissToast(el) {
  if (!el || el.classList.contains("toast-exit")) return;
  el.classList.remove("toast-enter");
  el.classList.add("toast-exit");
  el.addEventListener("animationend", () => el.remove(), { once: true });
  setTimeout(() => {
    if (el.parentNode) el.remove();
  }, 350);
};

function configBanner() {
  const container = document.getElementById("flashMessages");
  if (!container) return;
  flash(
    "Convex URL is not configured yet. Paste your deployment URL into public/js/config.js (see README).",
    "danger",
  );
}

/* ---------------------------------- navbar --------------------------------- */

const NAV_LINKS = [
  { page: "feed", href: "index.html", label: "Feed", icon: "fa-bell" },
  { page: "channels", href: "channels.html", label: "Channels", icon: "fa-tv" },
  { page: "stats", href: "stats.html", label: "Stats", icon: "fa-chart-pie" },
  { page: "settings", href: "settings.html", label: "Settings", icon: "fa-gear" },
];

const POPUP_PAGES = {
  channels: {
    title: "Manage Channels",
    icon: "fa-tv",
    header: `
      <form id="addChannelForm" class="soft-panel bg-slate-900 border border-slate-800 rounded-lg p-2.5 sm:p-3 flex flex-wrap items-center gap-2 sm:gap-3">
        <div class="flex-shrink-0 px-2.5 py-1.5 rounded-lg bg-slate-950 border border-slate-800 text-xs font-bold text-slate-300 shadow flex items-center gap-1.5" title="Subscribed Channels">
          <i class="fa-solid fa-tv text-red-500 text-xs"></i>
          <span id="channelCountNumber">0</span>
        </div>
        <input type="text" id="channelUrl" name="channel_url" oninput="handleChannelSearchInput(this.value)" autocomplete="off" autocapitalize="off" spellcheck="false" data-bwignore="true" data-lpignore="true" data-1p-ignore="true" placeholder="Search channels or paste YouTube URL to add..." required class="flex-1 min-w-[180px] bg-slate-950 border border-slate-700 rounded-lg px-3.5 py-2 text-xs sm:text-sm text-white focus:outline-none focus:border-red-500 transition">
        <button type="submit" class="bg-red-600 hover:bg-red-500 text-white px-4 py-2 rounded-lg text-xs font-semibold transition flex-shrink-0">Add Channel</button>
        <select id="channelSortSelect" onchange="changeChannelSort(this.value)" class="rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-xs text-slate-200 outline-none focus:border-red-500 transition flex-shrink-0" title="Sort channels">
          <option value="recent">Sort: Recent</option>
          <option value="name">Sort: Name (A-Z)</option>
          <option value="category">Sort: Folder</option>
          <option value="inactive">Sort: Inactive</option>
        </select>
      </form>`,
    body: `
      <div id="channelList" class="space-y-3">
        <p class="text-slate-600 text-sm">Loading...</p>
      </div>`,
  },
  stats: {
    title: "Stats",
    icon: "fa-chart-pie",
    header: `
      <div class="flex items-center justify-between gap-4">
        <h2 class="text-lg font-bold text-white"><i class="fa-solid fa-chart-pie text-red-400 mr-2"></i>Stats</h2>
        <div class="flex bg-slate-900 rounded-lg p-1 border border-slate-800">
          <button type="button" data-period="week" onclick="renderStats({ refreshNav: false, periodOverride: 'week' })" class="px-4 py-1 text-xs rounded-md transition capitalize">week</button>
          <button type="button" data-period="month" onclick="renderStats({ refreshNav: false, periodOverride: 'month' })" class="px-4 py-1 text-xs rounded-md transition capitalize">month</button>
        </div>
      </div>`,
    body: `
      <div class="soft-panel bg-slate-900/85 border border-slate-800 rounded-lg p-5 overflow-x-auto">
        <div id="statsSummary" class="mb-5"></div>
        <div id="channelStats" class="mb-6"></div>
        <div class="min-w-[600px]" id="heatmap">
          <p class="text-slate-600 text-sm">Loading...</p>
        </div>
      </div>`,
  },
  settings: {
    title: "Settings",
    icon: "fa-gear",
    header: `
      <h2 class="text-lg font-bold text-white"><i class="fa-solid fa-gear text-red-400 mr-2"></i>Settings</h2>`,
    body: `
      <form id="settingsForm" class="soft-panel bg-slate-900/85 border border-slate-800 rounded-lg p-5 space-y-6">
        <div class="flex items-center justify-between gap-6">
          <div>
            <h2 class="text-white font-medium">Enable Category ALL/SEEN/UNSEEN</h2>
            <p class="text-slate-500 text-xs">If enabled, you can categorize videos into All/Unseen/Seen.</p>
          </div>
          <label class="relative inline-flex items-center cursor-pointer">
            <input type="checkbox" id="showSeenToggle" name="show_seen" class="sr-only peer">
            <div class="relative h-7 w-12 rounded-full bg-slate-700 transition peer-checked:bg-red-600 peer-focus-visible:ring-2 peer-focus-visible:ring-red-400 after:absolute after:left-1 after:top-1 after:h-5 after:w-5 after:rounded-full after:bg-white after:shadow after:transition peer-checked:after:translate-x-5"></div>
          </label>
        </div>
        <div class="flex items-center justify-between gap-6 border-t border-slate-800 pt-6">
          <div>
            <h2 class="text-white font-medium">Hide YouTube Shorts</h2>
            <p class="text-slate-500 text-xs">Automatically hide Shorts (videos under 60 seconds or with #shorts in title) from your feed.</p>
          </div>
          <label class="relative inline-flex items-center cursor-pointer">
            <input type="checkbox" id="hideShortsToggle" name="hide_shorts" class="sr-only peer">
            <div class="relative h-7 w-12 rounded-full bg-slate-700 transition peer-checked:bg-red-600 peer-focus-visible:ring-2 peer-focus-visible:ring-red-400 after:absolute after:left-1 after:top-1 after:h-5 after:w-5 after:rounded-full after:bg-white after:shadow after:transition peer-checked:after:translate-x-5"></div>
          </label>
        </div>
        <div class="flex items-center justify-between gap-6 border-t border-slate-800 pt-6">
          <div>
            <h2 class="text-white font-medium">Show Unseen Videos First</h2>
            <p class="text-slate-500 text-xs">Automatically display unseen videos at the top of your main feed and Shorts feed before seen videos.</p>
          </div>
          <label class="relative inline-flex items-center cursor-pointer">
            <input type="checkbox" id="unseenFirstToggle" name="unseen_first" class="sr-only peer">
            <div class="relative h-7 w-12 rounded-full bg-slate-700 transition peer-checked:bg-red-600 peer-focus-visible:ring-2 peer-focus-visible:ring-red-400 after:absolute after:left-1 after:top-1 after:h-5 after:w-5 after:rounded-full after:bg-white after:shadow after:transition peer-checked:after:translate-x-5"></div>
          </label>
        </div>
        <div class="border-t border-slate-800 pt-6">
          <label for="defaultFeedFilterSelect" class="block text-white font-medium">Default Landing Feed View</label>
          <p class="mt-1 text-xs text-slate-500">Select which feed filter is shown by default when opening the homepage.</p>
          <select id="defaultFeedFilterSelect" name="default_feed_filter" class="mt-3 bg-slate-950 border border-slate-700 rounded-lg px-4 py-2.5 text-sm text-white focus:outline-none focus:border-red-500 transition">
            <option value="all">All Videos</option>
            <option value="unseen">Unseen Videos</option>
            <option value="seen">Seen Videos</option>
            <option value="favorites">Saved Videos</option>
            <option value="watchlater">Watch Later Videos</option>
            <option value="long">Long Videos</option>
            <option value="blocked">Blocked Items Feed</option>
            <option value="shorts">Shorts Feed</option>
          </select>
        </div>
        <div class="border-t border-slate-800 pt-6">
          <label for="defaultShortsFilterSelect" class="block text-white font-medium">Default Shorts Feed View</label>
          <p class="mt-1 text-xs text-slate-500">Select which filter view is shown by default when opening the Shorts feed.</p>
          <select id="defaultShortsFilterSelect" name="default_shorts_filter" class="mt-3 bg-slate-950 border border-slate-700 rounded-lg px-4 py-2.5 text-sm text-white focus:outline-none focus:border-red-500 transition">
            <option value="all">All Shorts</option>
            <option value="unseen">Unseen Shorts</option>
            <option value="seen">Seen Shorts</option>
            <option value="favorites">Saved Shorts</option>
            <option value="watchlater">Watch Later Shorts</option>
          </select>
        </div>


        <div class="border-t border-slate-800 pt-6">
          <label for="feedLimitSelect" class="block text-white font-medium">Videos Per Feed Page</label>
          <p class="mt-1 text-xs text-slate-500">Choose how many videos to display on your feed page.</p>
          <select id="feedLimitSelect" name="feed_limit" class="mt-3 bg-slate-950 border border-slate-700 rounded-lg px-4 py-2.5 text-sm text-white focus:outline-none focus:border-red-500 transition">
            <option value="20">20 Videos</option>
            <option value="50">50 Videos</option>
            <option value="100">100 Videos</option>
            <option value="200">200 Videos</option>
            <option value="500">500 Videos</option>
            <option value="1000">1000 Videos</option>
            <option value="0">All Videos</option>
          </select>
        </div>
        <div class="border-t border-slate-800 pt-6 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h2 class="text-white font-medium">Mark All Unseen Videos as Seen</h2>
            <p class="text-slate-500 text-xs">Clear all unseen notification badges by marking current videos as seen.</p>
          </div>
          <button type="button" onclick="markAllSeen()" class="bg-slate-800 border border-slate-700 hover:bg-slate-700 text-slate-200 px-4 py-2 rounded-lg text-xs font-semibold transition flex-shrink-0">
            <i class="fa-solid fa-check-double mr-1.5 text-emerald-400"></i>Mark All Seen
          </button>
        </div>
        <div class="border-t border-slate-800 pt-6">
          <label for="youtubeDataApiKey" class="block text-white font-medium">YouTube Data API v3 Key</label>
          <p id="youtubeApiKeyStatus" class="mt-1 text-xs text-slate-500">Leave blank to keep the saved key.</p>
          <div class="mt-3 flex flex-col gap-3 sm:flex-row">
            <input type="text" id="youtubeDataApiKey" name="youtube_data_api_key" autocomplete="off" autocapitalize="off" spellcheck="false" data-bwignore="true" data-lpignore="true" data-1p-ignore="true" placeholder="Paste API key" class="flex-1 bg-slate-950 border border-slate-700 rounded-lg px-4 py-3 text-sm text-white focus:outline-none focus:border-red-500 transition">
            <label class="inline-flex items-center gap-2 rounded-lg border border-slate-800 bg-slate-950/70 px-3 py-2 text-xs font-medium text-slate-400 transition hover:border-slate-700 hover:text-slate-200">
              <input type="checkbox" id="clearYoutubeDataApiKey" class="h-4 w-4 rounded border-slate-700 bg-slate-950 accent-red-600">
              Clear saved key
            </label>
          </div>
        </div>
        <button type="submit" class="bg-red-600 text-white px-6 py-2 text-sm font-semibold hover:bg-red-500 transition">Save Settings</button>
      </form>`,
  },
  playlists: {
    title: "Playlists",
    icon: "fa-list",
    header: `<h2 class="text-lg font-bold text-white"><i class="fa-solid fa-list text-sky-400 mr-2"></i>Playlists</h2>`,
    body: `<div id="playlistsPanel" class="space-y-3"><p class="text-slate-600 text-sm">Loading...</p></div>`,
  },
};

function renderNav({ counts = { main: 0, shorts: 0, watchLater: 0, longVideos: 0, blocked: 0 }, currentCount = null, showSeen = false, feedLimit = 50, category = "all", subCategory = "all", folder = "", playlistId = "", sortBy = "date-desc" } = {}) {
  const el = document.getElementById("navbar");
  if (!el) return;

  const isShorts = category === "shorts";
  const isPlaylistActive = Boolean(playlistId);
  const isMainActive = PAGE === "feed" && !isPlaylistActive && category !== "shorts" && category !== "watchlater" && category !== "long" && category !== "blocked";
  const activeFilterId = isShorts ? subCategory : category;

  const filterItems = isShorts ? [
    { id: "all", label: "All Shorts", icon: "fa-border-all" },
    { id: "unseen", label: "Unseen Shorts", icon: "fa-eye-slash" },
    { id: "seen", label: "Seen Shorts", icon: "fa-eye" },
    { id: "favorites", label: "Saved Shorts", icon: "fa-star text-amber-400" },
    { id: "watchlater", label: "Watch Later Shorts", icon: "fa-clock text-sky-400" },
    { id: "blocked", label: "Blocked Shorts", icon: "fa-ban text-rose-400" },
  ] : [
    { id: "all", label: "All Videos", icon: "fa-border-all" },
    { id: "unseen", label: "Unseen", icon: "fa-eye-slash" },
    { id: "seen", label: "Seen", icon: "fa-eye" },
    { id: "favorites", label: "Saved", icon: "fa-star text-amber-400" },
    { id: "watchlater", label: "Watch Later", icon: "fa-clock text-sky-400" },
    { id: "long", label: "Long Videos", icon: "fa-hourglass text-violet-400" },
    { id: "blocked", label: "Blocked Items", icon: "fa-ban text-rose-400" },
  ];

  const mainCount = typeof counts === "object" ? counts.main ?? 0 : counts ?? 0;
  const shortsCount = typeof counts === "object" ? counts.shorts ?? 0 : 0;
  const watchLaterCount = typeof counts === "object" ? counts.watchLater ?? 0 : 0;
  const longVideosCount = typeof counts === "object" ? counts.longVideos ?? 0 : 0;
  const blockedCount = typeof counts === "object" ? counts.blocked ?? 0 : 0;
  const hasCurrentCount = Number.isFinite(currentCount);
  const displayMainCount = hasCurrentCount && isMainActive ? currentCount : mainCount;
  const displayShortsCount = hasCurrentCount && isShorts ? currentCount : shortsCount;
  const displayWatchLaterCount = hasCurrentCount && category === "watchlater" ? currentCount : watchLaterCount;
  const displayLongVideosCount = hasCurrentCount && category === "long" ? currentCount : longVideosCount;
  const displayBlockedCount = hasCurrentCount && category === "blocked" ? currentCount : blockedCount;
  const limitVal = feedLimit != null ? String(feedLimit) : "50";
  const folderSuffix = folder ? `&folder=${encodeURIComponent(folder)}` : "";
  const folderQuery = folder ? `?folder=${encodeURIComponent(folder)}` : "";

  el.innerHTML = `
  <nav class="bg-slate-900/80 backdrop-blur-md border-b border-slate-800">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex min-h-[4rem] flex-col items-stretch justify-center gap-2 py-2 sm:h-16 sm:flex-row sm:items-center sm:justify-between sm:gap-4 sm:py-0">
        <div class="flex w-full items-center justify-center space-x-2 flex-shrink-0 min-w-0 sm:w-auto sm:justify-start sm:space-x-3">
          <div class="flex items-center gap-1.5 flex-shrink-0">
            <select id="headerFeedLimitSelect" onchange="changeFeedLimitFromHeader(this.value)" class="rounded-lg border border-slate-700/80 bg-slate-950/90 px-2.5 py-1 text-xs font-semibold text-slate-200 outline-none focus:border-red-500 transition cursor-pointer shadow" title="Videos Per Feed Page">
              <option value="20" ${limitVal === "20" ? "selected" : ""}>20 Limit</option>
              <option value="50" ${limitVal === "50" ? "selected" : ""}>50 Limit</option>
              <option value="100" ${limitVal === "100" ? "selected" : ""}>100 Limit</option>
              <option value="200" ${limitVal === "200" ? "selected" : ""}>200 Limit</option>
              <option value="500" ${limitVal === "500" ? "selected" : ""}>500 Limit</option>
              <option value="1000" ${limitVal === "1000" ? "selected" : ""}>1000 Limit</option>
              <option value="0" ${limitVal === "0" ? "selected" : ""}>All Limit</option>
            </select>
            <span id="headerCardCount" class="inline-flex items-center px-2.5 py-1 rounded-full bg-white text-xs font-bold text-black shadow-md shadow-black/30 tracking-wide" title="Videos showing on current page">0</span>
          </div>
          <div id="headerFolderPills" class="relative flex items-center py-1"></div>
        </div>
        <div class="flex w-full min-w-0 flex-wrap items-center justify-center gap-1.5 pb-0.5 sm:w-auto sm:flex-nowrap sm:justify-end sm:gap-3 sm:pb-0">
          <a href="index.html${folderQuery}" class="nav-link ${isMainActive ? "is-active" : ""} relative inline-flex h-9 w-9 sm:h-10 sm:w-10 items-center justify-center rounded-lg text-sm font-medium transition hover:bg-slate-800 ${isMainActive ? "bg-slate-800 text-red-500" : "text-slate-300"}" title="Main Feed (${displayMainCount} ${hasCurrentCount && isMainActive ? "available" : "unseen"})" aria-label="Main Feed (${displayMainCount} ${hasCurrentCount && isMainActive ? "available" : "unseen"})">
            <i class="fa-brands fa-youtube text-lg"></i>
            ${displayMainCount > 0 ? `<span class="absolute -top-1.5 -right-1.5 text-[10px] sm:text-[11px] font-extrabold text-red-400 leading-none tracking-tight">${displayMainCount}</span>` : ""}
          </a>
          <a href="index.html?category=shorts${folderSuffix}" class="nav-link ${category === "shorts" ? "is-active" : ""} relative inline-flex h-9 w-9 sm:h-10 sm:w-10 items-center justify-center rounded-lg text-sm font-medium transition hover:bg-slate-800 ${category === "shorts" ? "bg-slate-800 text-amber-400" : "text-slate-300"}" title="Shorts Feed (${displayShortsCount} ${hasCurrentCount && isShorts ? "available" : "unseen"})" aria-label="Shorts Feed (${displayShortsCount} ${hasCurrentCount && isShorts ? "available" : "unseen"})">
            <i class="fa-solid fa-mobile-screen-button"></i>
            ${displayShortsCount > 0 ? `<span class="absolute -top-1.5 -right-1.5 text-[10px] sm:text-[11px] font-extrabold text-amber-400 leading-none tracking-tight">${displayShortsCount}</span>` : ""}
          </a>
          <a href="index.html?category=watchlater${folderSuffix}" class="nav-link ${category === "watchlater" ? "is-active" : ""} relative inline-flex h-9 w-9 sm:h-10 sm:w-10 items-center justify-center rounded-lg text-sm font-medium transition hover:bg-slate-800 ${category === "watchlater" ? "bg-slate-800 text-sky-400" : "text-slate-300"}" title="Watch Later Feed (${displayWatchLaterCount} ${hasCurrentCount && category === "watchlater" ? "available" : "saved"})" aria-label="Watch Later Feed (${displayWatchLaterCount} ${hasCurrentCount && category === "watchlater" ? "available" : "saved"})">
            <i class="fa-solid fa-clock"></i>
            ${displayWatchLaterCount > 0 ? `<span class="absolute -top-1.5 -right-1.5 text-[10px] sm:text-[11px] font-extrabold text-sky-400 leading-none tracking-tight">${displayWatchLaterCount}</span>` : ""}
          </a>
          <a href="index.html?category=long${folderSuffix}" class="nav-link ${category === "long" ? "is-active" : ""} relative inline-flex h-9 w-9 sm:h-10 sm:w-10 items-center justify-center rounded-lg text-sm font-medium transition hover:bg-slate-800 ${category === "long" ? "bg-slate-800 text-violet-400" : "text-slate-300"}" title="Long Videos Feed (${displayLongVideosCount} ${hasCurrentCount && category === "long" ? "available" : "saved"})" aria-label="Long Videos Feed (${displayLongVideosCount} ${hasCurrentCount && category === "long" ? "available" : "saved"})">
            <i class="fa-solid fa-hourglass"></i>
            ${displayLongVideosCount > 0 ? `<span class="absolute -top-1.5 -right-1.5 text-[10px] sm:text-[11px] font-extrabold text-violet-400 leading-none tracking-tight">${displayLongVideosCount}</span>` : ""}
          </a>
          <button type="button" onclick="openPopup('playlists')" class="nav-link relative inline-flex h-9 w-9 sm:h-10 sm:w-10 items-center justify-center rounded-lg text-sm font-medium transition hover:bg-slate-800 ${isPlaylistActive ? "bg-slate-800 text-sky-400 is-active" : "text-slate-300"}" title="Playlists" aria-label="Playlists">
            <i class="fa-solid fa-list"></i>
            ${isPlaylistActive ? `<span class="absolute -top-1 -right-1 w-2 h-2 rounded-full bg-sky-400"></span>` : ""}
          </button>
          <a href="index.html?category=blocked${folderSuffix}" class="nav-link ${category === "blocked" ? "is-active" : ""} relative inline-flex h-9 w-9 sm:h-10 sm:w-10 items-center justify-center rounded-lg text-sm font-medium transition hover:bg-slate-800 ${category === "blocked" ? "bg-slate-800 text-rose-400" : "text-slate-300"}" title="Blocked Items (${displayBlockedCount} blocked${hasCurrentCount && category === "blocked" ? " available" : ""})" aria-label="Blocked Items (${displayBlockedCount} blocked${hasCurrentCount && category === "blocked" ? " available" : ""})">
            <i class="fa-solid fa-ban text-rose-400"></i>
            ${displayBlockedCount > 0 ? `<span class="absolute -top-1.5 -right-1.5 text-[10px] sm:text-[11px] font-extrabold text-rose-400 leading-none tracking-tight">${displayBlockedCount}</span>` : ""}
          </a>
          ${PAGE === "feed" ? `
          <div class="relative inline-block text-left">
            <button id="dropdownButton" onclick="toggleDropdown()" class="inline-flex h-9 w-9 sm:h-10 sm:w-10 items-center justify-center rounded-lg bg-slate-900 border border-slate-800 text-slate-300 hover:text-white transition" title="Filter: ${esc(activeFilterId)}" aria-label="Filter: ${esc(activeFilterId)}">
              <i class="fa-solid fa-filter"></i>
            </button>
            <div id="dropdownMenu" class="hidden absolute right-0 mt-2 w-44 rounded-xl bg-slate-900/95 backdrop-blur-xl border border-slate-800 shadow-2xl shadow-black/80 z-50 py-1.5 popup-enter">
              <div class="px-3 py-1 text-[10px] font-bold uppercase tracking-wider text-slate-500 border-b border-slate-800/80 mb-1">${isShorts ? "Filter Shorts" : "Filter Feed"}</div>
              ${filterItems.map((item) => {
                const isActive = item.id === activeFilterId;
                const folderParam = folder ? `&folder=${encodeURIComponent(folder)}` : "";
                const sortParam = sortBy !== "date-desc" ? `&sortBy=${sortBy}` : "";
                const linkHref = isShorts
                  ? `?category=shorts&subCategory=${item.id}${folderParam}${sortParam}`
                  : `?category=${item.id}${folderParam}${sortParam}`;
                return `
                <a href="${linkHref}" class="flex items-center gap-2.5 px-3 py-2 text-xs font-medium transition ${isActive ? "bg-red-500/15 text-red-400 font-semibold" : "text-slate-300 hover:bg-slate-800/70 hover:text-white"}">
                  <i class="fa-solid ${item.icon} w-3.5 text-center text-xs"></i>
                  <span>${esc(item.label)}</span>
                </a>`;
              }).join("")}
              <div class="px-3 py-1 mt-1 text-[10px] font-bold uppercase tracking-wider text-slate-500 border-t border-slate-800/80 border-b border-slate-800/80 mb-1">Sort By</div>
              ${[
                { id: "date-desc", label: "Newest First",   icon: "fa-arrow-down-wide-short" },
                { id: "date-asc",  label: "Oldest First",   icon: "fa-arrow-up-wide-short" },
                { id: "title-asc", label: "Title A → Z",    icon: "fa-arrow-down-a-z" },
                { id: "title-desc",label: "Title Z → A",    icon: "fa-arrow-up-a-z" },
              ].map((s) => {
                const isActiveSortItem = s.id === sortBy;
                const folderParam = folder ? `&folder=${encodeURIComponent(folder)}` : "";
                const catParam = isShorts ? `category=shorts&subCategory=${activeFilterId}` : `category=${activeFilterId}`;
                const plParam = playlistId ? `&playlistId=${encodeURIComponent(playlistId)}` : "";
                const sortHref = `?${catParam}${folderParam}${plParam}&sortBy=${s.id}`;
                return `
                <a href="${sortHref}" class="flex items-center gap-2.5 px-3 py-2 text-xs font-medium transition ${isActiveSortItem ? "bg-indigo-500/15 text-indigo-400 font-semibold" : "text-slate-300 hover:bg-slate-800/70 hover:text-white"}">
                  <i class="fa-solid ${s.icon} w-3.5 text-center text-xs"></i>
                  <span>${s.label}</span>
                </a>`;
              }).join("")}
            </div>
          </div>` : ""}
          <button type="button" onclick="openPopup('channels')" class="nav-link inline-flex h-9 w-9 sm:h-10 sm:w-10 items-center justify-center rounded-lg text-sm font-medium transition hover:bg-slate-800 text-slate-300" title="Channels" aria-label="Channels">
            <i class="fa-solid fa-tv"></i>
          </button>
          <button type="button" onclick="openPopup('stats')" class="nav-link inline-flex h-9 w-9 sm:h-10 sm:w-10 items-center justify-center rounded-lg text-sm font-medium transition hover:bg-slate-800 text-slate-300" title="Stats" aria-label="Stats">
            <i class="fa-solid fa-chart-pie"></i>
          </button>
          <button type="button" onclick="openPopup('settings')" class="nav-link inline-flex h-9 w-9 sm:h-10 sm:w-10 items-center justify-center rounded-lg text-sm font-medium transition hover:bg-slate-800 text-slate-300" title="Settings" aria-label="Settings">
            <i class="fa-solid fa-gear"></i>
          </button>
          <button id="refreshButton" onclick="checkUpdates()" ${isCheckingUpdates ? "disabled" : ""} class="inline-flex h-9 w-9 sm:h-10 sm:w-10 items-center justify-center rounded-lg bg-gradient-to-r from-red-600 to-amber-500 text-sm font-semibold text-white shadow-lg shadow-red-900/30 transition transform hover:-translate-y-0.5 hover:from-red-500 hover:to-amber-400 active:scale-95 disabled:opacity-75 disabled:cursor-not-allowed ${isCheckingUpdates ? "is-syncing" : ""}" title="${isCheckingUpdates ? "Updating..." : "Check updates"}" aria-label="${isCheckingUpdates ? "Updating..." : "Check updates"}">
            <i class="fa-solid fa-rotate"></i>
            <span class="sr-only">Check Updates</span>
          </button>
        </div>
      </div>
    </div>
  </nav>`;
  updateNavbarOffset();
}

function updateNavbarOffset() {
  const navbar = document.getElementById("navbar");
  if (!navbar) return;
  requestAnimationFrame(() => {
    document.documentElement.style.setProperty(
      "--navbar-height",
      `${navbar.offsetHeight}px`,
    );
  });
}

function ensurePopup() {
  let popup = document.getElementById("appPopup");
  if (popup) return popup;

  popup = document.createElement("div");
  popup.id = "appPopup";
  popup.className = "fixed inset-0 z-[80] hidden";
  popup.innerHTML = `
    <div class="absolute inset-0 bg-slate-950/75 backdrop-blur-sm" onclick="closePopup()"></div>
    <section class="popup-panel absolute left-1/2 top-1/2 max-h-[calc(100vh-3rem)] w-[min(940px,calc(100vw-2rem))] -translate-x-1/2 -translate-y-1/2 flex flex-col overflow-hidden rounded-xl border border-slate-800 bg-slate-950 shadow-2xl shadow-black/80">
      <header id="popupHeader" class="flex-shrink-0 flex items-center justify-between border-b border-slate-800/80 bg-slate-950 px-5 py-4 z-20">
        <div id="popupHeaderContent" class="flex-1 min-w-0 mr-3"></div>
        <button type="button" onclick="closePopup()" class="rounded-lg p-2 text-slate-400 transition hover:bg-slate-900 hover:text-white flex-shrink-0" title="Close">
          <i class="fa-solid fa-xmark text-lg"></i>
        </button>
      </header>
      <div id="popupBody" class="flex-1 overflow-y-auto p-5"></div>
    </section>`;
  document.body.appendChild(popup);
  return popup;
}

window.openPopup = async function openPopup(page) {
  const config = POPUP_PAGES[page];
  if (!config) return;
  const popup = ensurePopup();
  document.getElementById("popupHeaderContent").innerHTML = config.header || "";
  document.getElementById("popupBody").innerHTML = config.body || "";
  popup.classList.remove("hidden");
  document.body.classList.add("overflow-hidden");

  if (!CONFIGURED) {
    configBanner();
    return;
  }
  try {
    if (page === "channels") {
      initChannelsPage();
      await renderChannels({ refreshNav: false });
      // Auto-focus the search/add input once the popup is visible
      requestAnimationFrame(() => {
        const input = document.getElementById("channelUrl");
        if (input) input.focus();
      });
    } else if (page === "stats") {
      await renderStats({ refreshNav: false });
    } else if (page === "settings") {
      const configData = await callConvex("query", "settings:config");
      renderSettingsConfig(configData);
      initSettingsPage();
    } else if (page === "playlists") {
      await renderPlaylistsPanel();
    }
  } catch (err) {
    flash(err.message, "danger");
  }
};

window.closePopup = function closePopup() {
  const popup = document.getElementById("appPopup");
  if (!popup) return;
  popup.classList.add("hidden");
  document.body.classList.remove("overflow-hidden");
};

async function renderPlaylistsPanel() {
  const container = document.getElementById("playlistsPanel");
  if (!container) return;

  const urlParams = new URLSearchParams(location.search);
  const activePlaylistId = urlParams.get("playlistId") || "";

  let data;
  try {
    data = await callConvex("query", "videos:listPlaylists");
  } catch (err) {
    container.innerHTML = `<p class="text-rose-400 text-sm"><i class="fa-solid fa-triangle-exclamation mr-1.5"></i>${esc(err.message)}</p>`;
    return;
  }

  if (!data || !data.length) {
    container.innerHTML = `
      <div class="py-10 text-center text-slate-500">
        <i class="fa-solid fa-list text-4xl mb-3 opacity-20"></i>
        <p class="text-sm">No playlists yet.</p>
        <p class="text-xs mt-1 text-slate-600">Open a channel's playlist panel and click Load on a playlist to add it.</p>
      </div>`;
    return;
  }

  // Auto-sync titles for any playlist still showing a raw ID
  const channelsNeedingTitles = data.filter((ch) =>
    ch.playlists.some((pl) => pl.title === pl.playlistId)
  );
  if (channelsNeedingTitles.length > 0) {
    // Fetch titles in background and re-render when done
    Promise.all(channelsNeedingTitles.map(async (ch) => {
      try {
        const playlists = await callConvex("action", "youtube:listChannelPlaylists", { channelId: ch.channelId });
        if (!playlists || !playlists.length) return;
        const meta = playlists.map((pl) => ({ id: pl.id, title: pl.title }));
        await callConvex("mutation", "channels:savePlaylistMeta", { channelId: ch.channelId, playlists: meta });
      } catch (e) { /* silently skip if API key missing */ }
    })).then(() => {
      // Re-render panel with updated titles
      if (document.getElementById("playlistsPanel")) renderPlaylistsPanel();
    });
  }

  renderPlaylistsPanelHtml(data, activePlaylistId);
}

function renderPlaylistsPanelHtml(data, activePlaylistId) {
  const container = document.getElementById("playlistsPanel");
  if (!container) return;
  container.innerHTML = data.map((channel) => `
    <div class="rounded-xl border border-slate-800 bg-slate-900/70 overflow-hidden">
      <div class="flex items-center gap-3 px-4 py-3 border-b border-slate-800/60">
        <div class="w-8 h-8 rounded-full bg-slate-800 flex-shrink-0 overflow-hidden ring-1 ring-slate-700">
          ${channel.thumbnail
            ? `<img src="${esc(channel.thumbnail)}" class="w-full h-full object-cover" alt="${esc(channel.channelName)}">`
            : `<div class="w-full h-full flex items-center justify-center text-[10px] font-bold text-slate-400">${esc(channel.channelName.slice(0,2))}</div>`}
        </div>
        <span class="text-sm font-bold text-white truncate flex-1">${esc(channel.channelName)}</span>
        ${channel.totalUnseen > 0
          ? `<span class="flex-shrink-0 text-[11px] font-extrabold text-red-400">${channel.totalUnseen} unseen</span>`
          : ""}
      </div>
      <div class="divide-y divide-slate-800/50">
        ${channel.playlists.map((pl) => {
          const isActive = pl.playlistId === activePlaylistId;
          const href = isActive
            ? "?"
            : `?playlistId=${encodeURIComponent(pl.playlistId)}&playlistTitle=${encodeURIComponent(pl.title)}&category=all`;
          return `
          <div class="flex items-center gap-3 px-4 py-3 transition hover:bg-slate-800/50 ${isActive ? "bg-sky-950/40 border-l-2 border-sky-500" : ""} group">
            <a href="${href}" onclick="closePopup()" class="flex items-center gap-3 flex-1 min-w-0">
              <i class="fa-solid fa-list-ul text-xs ${isActive ? "text-sky-400" : "text-slate-500"} flex-shrink-0"></i>
              <span class="flex-1 text-sm ${isActive ? "text-sky-300 font-semibold" : "text-slate-200"} truncate">${esc(pl.title)}</span>
            </a>
            <span class="flex-shrink-0 text-[10px] text-slate-500">${pl.total} video${pl.total === 1 ? "" : "s"}</span>
            ${pl.unseen > 0
              ? `<span class="flex-shrink-0 text-[11px] font-extrabold text-red-400 min-w-[1.5rem] text-right">${pl.unseen}</span>`
              : `<span class="flex-shrink-0 min-w-[1.5rem]"></span>`}
            <button onclick="removePlaylistRule('${esc(channel.channelId)}', '${esc(pl.playlistId)}')" class="flex-shrink-0 opacity-0 group-hover:opacity-100 transition text-slate-600 hover:text-rose-400 ml-1" title="Remove playlist from rules">
              <i class="fa-solid fa-xmark text-xs"></i>
            </button>
          </div>`;
        }).join("")}
      </div>
    </div>
  `).join("");
}


window.toggleDropdown = function toggleDropdown() {
  const menu = document.getElementById("dropdownMenu");
  if (menu) menu.classList.toggle("hidden");
};

function updateSyncBtnUI(syncing) {
  const btn = document.getElementById("refreshButton");
  if (!btn) return;
  btn.disabled = syncing;
  btn.title = syncing ? "Updating..." : "Check updates";
  btn.setAttribute("aria-label", syncing ? "Updating..." : "Check updates");
  if (syncing) {
    btn.classList.add("is-syncing");
  } else {
    btn.classList.remove("is-syncing");
  }
}

window.checkUpdates = async function checkUpdates() {
  if (isCheckingUpdates) return;
  isCheckingUpdates = true;
  updateSyncBtnUI(true);

  try {
    const [res, backfill] = await Promise.all([
      callConvex("action", "refresh:refreshAll"),
      callConvex("action", "refresh:backfillDurations", { limit: 50 }),
    ]);
    const durationsUpdated = (res.durationsUpdated ?? 0) + (backfill.updated ?? 0);
    const backfillNote = backfill.reason ? ` ${backfill.reason}` : "";
    flash(
      `Refreshed all channels! Found ${res.totalNew} new video(s), updated ${durationsUpdated} duration(s).${backfillNote}`,
      "success",
    );
  } catch (err) {
    flash(err.message, "danger");
  } finally {
    isCheckingUpdates = false;
    updateSyncBtnUI(false);
  }

  try {
    if (PAGE === "feed") await renderFeed();
    else await refreshNavOnly();
  } catch (err) {
    flash(err.message, "danger");
  }
};

async function refreshNavOnly() {
  const urlParams = new URLSearchParams(location.search);
  const folder = urlParams.get("folder") || "";
  const channelId = urlParams.get("channelId") || "";
  const playlistId = urlParams.get("playlistId") || "";
  const [config, counts] = await Promise.all([
    callConvex("query", "settings:config"),
    callConvex("query", "videos:counts", {
      folder: folder || undefined,
      channelId: channelId || undefined,
    }),
  ]);
  const urlCategory = urlParams.get("category") || config.defaultFeedFilter || "all";
  const urlSubCategory = urlParams.get("subCategory") || (urlCategory === "shorts" ? (config.defaultShortsFilter || "all") : "all");
  renderNav({ counts, showSeen: config.showSeen, feedLimit: config.feedLimit, category: urlCategory, subCategory: urlSubCategory, folder });
}

/* --------------------------------- feed page ------------------------------- */

function videoCard(video, categories = []) {
  const isNew = video.isNew;
  const isFavorite = Boolean(video.isFavorite);
  const isWatchLater = Boolean(video.isWatchLater);
  const isLong = Boolean(video.isLong);
  const isPlaylist = Boolean(video.isPlaylist);
  const currentCat = video.channelCategory || "";
  const folderTagWidth = Math.max(58, 38 + (currentCat || "+ Folder").length * 6);
  const cardTone = isNew
    ? isPlaylist
      ? "bg-slate-900/90 border-slate-800 ring-1 ring-amber-500/30"
      : "bg-slate-900/90 border-slate-800 ring-1 ring-red-500/20"
    : "bg-slate-900/55 border-slate-800/60 opacity-85";
  const imageTone = isNew
    ? "grayscale-0 opacity-100"
    : "grayscale opacity-60";
  const titleTone = isNew
    ? isPlaylist
      ? "text-slate-100 group-hover:text-amber-400"
      : "text-slate-100 group-hover:text-red-400"
    : "text-slate-500 group-hover:text-slate-300";
  const channelTone = isNew
    ? "text-slate-200 group-hover:text-white"
    : "text-slate-500 group-hover:text-slate-300";

  const folderOptionsHtml = (categories || []).map((cat) => {
    const encodedCategory = encodeURIComponent(cat);
    const active = cat.toLowerCase() === currentCat.toLowerCase();
    return `<button type="button" onclick="selectVideoFolder(event, '${encodedCategory}', '${esc(video.channelId)}', '${esc(video._id)}')" class="flex w-full items-center gap-2 whitespace-nowrap px-3 py-1.5 text-left text-[11px] font-semibold transition ${active ? "bg-red-600 text-white" : "text-slate-200 hover:bg-slate-700"}">
      <i class="fa-solid fa-folder text-[10px] ${active ? "text-amber-300" : "text-amber-400"}"></i>${esc(cat)}
    </button>`;
  }).join("");

  return `
  <article class="motion-card group relative z-0 soft-panel ${cardTone} border rounded-none overflow-visible transition-all duration-300 hover:z-50 hover:-translate-y-1">
    <div class="relative aspect-video bg-slate-950 overflow-hidden">
      <a href="${esc(video.link)}" target="_blank" class="absolute inset-0">
      <img src="https://img.youtube.com/vi/${esc(video.videoId)}/hqdefault.jpg" alt="${esc(video.title)}" class="${imageTone} w-full h-full object-cover group-hover:scale-105 transition duration-500" loading="lazy">
      <div class="absolute inset-0 bg-gradient-to-t from-slate-950/65 via-transparent to-transparent opacity-90 group-hover:opacity-60 transition"></div>
      </a>
      <div class="absolute right-3 top-3 z-10 flex items-center gap-2">
        <button onclick="toggleWatchLater('${esc(video._id)}')" class="${isWatchLater ? "inline-flex opacity-100 text-sky-400 border border-sky-500/50 bg-sky-950/80" : "hidden group-hover:inline-flex opacity-0 group-hover:opacity-100 text-slate-300 hover:text-sky-400 bg-slate-950/80"} h-9 w-9 items-center justify-center rounded-lg shadow-lg backdrop-blur transition-all duration-200 hover:bg-slate-900" title="${isWatchLater ? "Remove from Watch Later" : "Add to Watch Later"}">
          <i class="${isWatchLater ? "fa-solid" : "fa-regular"} fa-clock text-sm"></i>
        </button>
        <button onclick="toggleLong('${esc(video._id)}')" class="${isLong ? "inline-flex opacity-100 text-violet-400 border border-violet-500/50 bg-violet-950/80" : "hidden group-hover:inline-flex opacity-0 group-hover:opacity-100 text-slate-300 hover:text-violet-400 bg-slate-950/80"} h-9 w-9 items-center justify-center rounded-lg shadow-lg backdrop-blur transition-all duration-200 hover:bg-slate-900" title="${isLong ? "Remove from Long Videos" : "Add to Long Videos"}">
          <i class="fa-solid fa-hourglass text-sm"></i>
        </button>
        <button onclick="toggleFavorite('${esc(video._id)}')" class="${isFavorite ? "inline-flex opacity-100 text-amber-400 border border-amber-500/50 bg-amber-950/80" : "hidden group-hover:inline-flex opacity-0 group-hover:opacity-100 text-slate-300 hover:text-amber-400 bg-slate-950/80"} h-9 w-9 items-center justify-center rounded-lg shadow-lg backdrop-blur transition-all duration-200 hover:bg-slate-900" title="${isFavorite ? "Remove from Saved" : "Save for Later"}">
          <i class="${isFavorite ? "fa-solid" : "fa-regular"} fa-star text-sm"></i>
        </button>
        <button onclick="toggleRead('${esc(video._id)}')" class="hidden group-hover:inline-flex opacity-0 group-hover:opacity-100 h-9 w-9 items-center justify-center rounded-lg bg-slate-950/80 text-slate-200 shadow-lg backdrop-blur transition-all duration-200 hover:bg-red-600 hover:text-white" title="${isNew ? "Mark as seen" : "Mark as unseen"}" aria-label="${isNew ? "Mark as seen" : "Mark as unseen"}">
          ${eyeIcon(isNew)}
        </button>
        <button onclick="toggleShort('${esc(video._id)}')" class="${video.isShort ? "inline-flex opacity-100 text-amber-300 border border-amber-500/50 bg-amber-950/80" : "hidden group-hover:inline-flex opacity-0 group-hover:opacity-100 text-slate-300 hover:text-amber-300 bg-slate-950/80"} h-9 w-9 items-center justify-center rounded-lg shadow-lg backdrop-blur transition-all duration-200 hover:bg-slate-900" title="${video.isShort ? "Marked as Short (click to unmark)" : "Click to mark as Short"}">
          <i class="fa-solid fa-mobile-screen-button text-sm"></i>
        </button>
        <a href="${esc(video.link)}" target="_blank" class="hidden group-hover:inline-flex opacity-0 group-hover:opacity-100 h-9 w-9 items-center justify-center rounded-lg bg-slate-950/80 text-slate-200 shadow-lg backdrop-blur transition-all duration-200 hover:bg-slate-800 hover:text-white" title="Open video" aria-label="Open video">
          ${externalIcon()}
        </a>
      </div>
      ${durationBadge(video)}
    </div>
    <div class="p-5 flex flex-col">
      <div class="flex items-center gap-3 mb-3">
        <a href="https://www.youtube.com/channel/${esc(video.channelId)}" target="_blank" class="w-9 h-9 rounded-full bg-slate-800 flex items-center justify-center overflow-hidden text-slate-500 ring-1 ring-slate-700 transition hover:opacity-80 hover:scale-105 flex-shrink-0" title="Open ${esc(video.channelName)} on YouTube">
          ${video.channelThumbnail ? `<img src="${esc(video.channelThumbnail)}" class="w-full h-full object-cover" alt="${esc(video.channelName)}">` : `<i class="fa-solid fa-user text-sm"></i>`}
        </a>
        <div class="min-w-0 flex-1">
          <div class="flex items-center gap-2 min-w-0">
            <span class="truncate text-sm font-semibold ${channelTone} transition">${esc(video.channelName)}</span>
            <div class="video-folder-picker relative flex-shrink-0">
              <button type="button" onclick="toggleVideoFolderMenu(event, '${esc(video._id)}')" style="width: ${folderTagWidth}px" class="inline-flex items-center gap-1 rounded bg-red-950/80 border border-red-800/60 px-1.5 py-0.5 text-[10px] font-bold text-red-300 outline-none transition hover:bg-red-900/90" title="Change folder for ${esc(video.channelName)}">
                <i class="fa-solid fa-folder text-[9px] text-amber-300"></i>
                <span class="truncate">${esc(currentCat || "+ Folder")}</span>
                <i class="fa-solid fa-chevron-down ml-auto text-[8px] text-red-200"></i>
              </button>
              <div id="video-folder-menu-${esc(video._id)}" class="video-folder-menu hidden absolute left-0 top-full z-50 mt-1 w-max min-w-full overflow-hidden rounded border border-red-800/80 bg-red-950/95 py-1 shadow-xl shadow-black/50">
                <button type="button" onclick="selectVideoFolder(event, '', '${esc(video.channelId)}', '${esc(video._id)}')" class="flex w-full items-center gap-2 whitespace-nowrap px-3 py-1.5 text-left text-[11px] font-semibold transition ${!currentCat ? "bg-red-600 text-white" : "text-slate-200 hover:bg-slate-700"}">
                  <i class="fa-solid fa-folder-plus text-[10px] text-amber-300"></i>+ Folder
                </button>
                ${folderOptionsHtml}
              </div>
            </div>
          </div>
          <div class="mt-0.5 text-xs text-slate-500" title="${esc(isoDate(video.published))}">${esc(timeLabel(video.published))}</div>
        </div>
      </div>
      <h3 class="text-lg font-semibold ${titleTone} leading-snug line-clamp-2 transition">${esc(video.title)}</h3>
    </div>
  </article>`;
}

window.changeChannelFolderFromCard = async function changeChannelFolderFromCard(newCategory, channelId) {
  try {
    await callConvex("mutation", "channels:updateCategory", {
      channelId,
      category: newCategory,
    });
    flash("Channel folder updated!", "success");
    if (PAGE === "feed") await renderFeed();
  } catch (err) {
    flash(err.message, "danger");
  }
};

window.toggleFavorite = async function toggleFavorite(id) {
  try {
    await callConvex("mutation", "videos:toggleFavorite", { id });
    await renderFeed();
  } catch (err) {
    flash(err.message, "danger");
  }
};

window.toggleWatchLater = async function toggleWatchLater(id) {
  try {
    await callConvex("mutation", "videos:toggleWatchLater", { id });
    await renderFeed();
  } catch (err) {
    flash(err.message, "danger");
  }
};

window.toggleVideoFolderMenu = function toggleVideoFolderMenu(event, videoId) {
  event.stopPropagation();
  const menu = document.getElementById(`video-folder-menu-${videoId}`);
  if (!menu) return;
  document.querySelectorAll(".video-folder-menu").forEach((item) => {
    if (item !== menu) item.classList.add("hidden");
  });
  menu.classList.toggle("hidden");
};

window.selectVideoFolder = async function selectVideoFolder(event, encodedCategory, channelId, videoId) {
  event.stopPropagation();
  const menu = document.getElementById(`video-folder-menu-${videoId}`);
  if (menu) menu.classList.add("hidden");
  await changeChannelFolderFromCard(decodeURIComponent(encodedCategory), channelId);
};

window.toggleLong = async function toggleLong(id) {
  try {
    await callConvex("mutation", "videos:toggleLong", { id });
    await renderFeed();
  } catch (err) {
    flash(err.message, "danger");
  }
};


window.toggleRead = async function toggleRead(id) {
  try {
    await callConvex("mutation", "videos:toggleRead", { id });
    await renderFeed();
  } catch (err) {
    flash(err.message, "danger");
  }
};

window.toggleShort = async function toggleShort(id) {
  try {
    await callConvex("mutation", "videos:toggleShort", { id });
    await renderFeed();
  } catch (err) {
    flash(err.message, "danger");
  }
};


window.markAllSeen = async function markAllSeen() {
  const urlParams = new URLSearchParams(location.search);
  const folder = urlParams.get("folder") || "";
  try {
    const res = await callConvex("mutation", "videos:markAllSeen", { folder: folder || undefined });
    flash(`Marked ${res.marked} video(s) as seen!`, "success");
    if (PAGE === "feed") await renderFeed();
    else await refreshNavOnly();
  } catch (err) {
    flash(err.message, "danger");
  }
};


async function renderFeed() {
  const urlParams = new URLSearchParams(location.search);
  const config = await callConvex("query", "settings:config");
  const urlCategory = urlParams.get("category") || config.defaultFeedFilter || "all";
  const urlSubCategory = urlParams.get("subCategory") || (urlCategory === "shorts" ? (config.defaultShortsFilter || "all") : "all");
  const folder = urlParams.get("folder") || "";
  const channelId = urlParams.get("channelId") || "";
  const playlistId = urlParams.get("playlistId") || "";
  const playlistTitleFromUrl = urlParams.get("playlistTitle") || "";
  const sortBy = urlParams.get("sortBy") || "date-desc";

  const [allVideos, counts, categories, channels] = await Promise.all([
    callConvex("query", "videos:list", {
      category: urlCategory,
      subCategory: urlSubCategory || undefined,
      folder: folder || undefined,
      channelId: channelId || undefined,
      playlistId: playlistId || undefined,
    }),
    callConvex("query", "videos:counts", {
      folder: folder || undefined,
      channelId: channelId || undefined,
      category: urlCategory,
      subCategory: urlSubCategory || undefined,
    }),
    callConvex("query", "channels:categories"),
    callConvex("query", "channels:list"),
  ]);

  const videos = channelId ? allVideos.filter((v) => v.channelId === channelId) : allVideos;

  const feedTotal = counts.feedTotal ?? videos.length;

  renderNav({
    counts,
    currentCount: feedTotal,
    showSeen: config.showSeen,
    feedLimit: config.feedLimit,
    category: urlCategory,
    subCategory: urlSubCategory,
    folder,
    playlistId,
    sortBy,
  });

  renderFolderPills(categories, folder, urlCategory, urlSubCategory);
  renderChannelAvatarsBar(channels, allVideos, channelId, urlCategory, folder, urlSubCategory, playlistId, playlistTitleFromUrl);

  // Playlist header banner
  const existingBanner = document.getElementById("playlistBanner");
  if (existingBanner) existingBanner.remove();
  if (playlistId && videos.length > 0) {
    // Resolve title: URL param (set by panel) → stamped on video → playlistMeta cache → generic
    let plTitle = playlistTitleFromUrl || videos[0]?.sourcePlaylistTitle || "";
    if (!plTitle) {
      for (const ch of channels) {
        const meta = (ch.playlistMeta || []).find((m) => m.id === playlistId);
        if (meta) { plTitle = meta.title; break; }
      }
    }
    // If title looks like a raw playlist ID or is missing, show a generic label
    if (!plTitle || /^PL[A-Za-z0-9_-]{10,}$/.test(plTitle)) plTitle = "Playlist";
    const plChannel = videos[0]?.channelName || "";
    const banner = document.createElement("div");
    banner.id = "playlistBanner";
    banner.className = "mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 mb-3";
    banner.innerHTML = `
      <div class="flex items-center gap-2 bg-gradient-to-r from-sky-600/15 via-indigo-600/8 to-transparent border border-sky-500/25 rounded-lg px-3 py-1.5 shadow shadow-sky-900/20 min-w-0">
        <i class="fa-solid fa-list text-sky-400 text-xs flex-shrink-0"></i>
        <span class="text-[11px] text-sky-400/70 flex-shrink-0 font-medium">${esc(plChannel)}</span>
        <span class="text-slate-500 text-[11px] flex-shrink-0">/</span>
        <span class="text-xs font-bold text-white truncate">${esc(plTitle)}</span>
        <span class="text-[11px] text-slate-400 flex-shrink-0 font-medium">&middot; <span class="text-sky-400 font-bold">${videos.length}</span> video${videos.length === 1 ? "" : "s"}</span>
        <a href="https://www.youtube.com/playlist?list=${encodeURIComponent(playlistId)}" target="_blank" rel="noopener" class="flex-shrink-0 text-red-400 hover:text-red-300 transition ml-1" title="Open on YouTube"><i class="fa-solid fa-arrow-up-right-from-square text-[10px]"></i></a>
      </div>`;
    const main = document.querySelector("main");
    const grid = document.getElementById("videoGrid");
    if (main && grid) main.insertBefore(banner, grid);
  }

  const countBadge = document.getElementById("headerCardCount");
  if (countBadge) {
    countBadge.textContent = `${feedTotal}`;
    countBadge.title = `${feedTotal} matching video${feedTotal === 1 ? "" : "s"} in this feed${videos.length !== feedTotal ? ` (${videos.length} currently shown)` : ""}`;
  }

  // Client-side sort (backend already returns date-desc; other sorts applied here)
  const sortedVideos = [...videos];
  if (sortBy === "date-asc") {
    sortedVideos.sort((a, b) => a.published.localeCompare(b.published));
  } else if (sortBy === "title-asc") {
    sortedVideos.sort((a, b) => a.title.localeCompare(b.title));
  } else if (sortBy === "title-desc") {
    sortedVideos.sort((a, b) => b.title.localeCompare(a.title));
  }
  // date-desc: already sorted by backend

  const grid = document.getElementById("videoGrid");
  if (!grid) return;
  if (!videos.length) {
    grid.innerHTML = `
    <div class="col-span-full py-20 text-center text-slate-600">
      <i class="fa-solid fa-video-slash text-5xl mb-4 opacity-20"></i>
      <p class="text-lg">No videos found. ${playlistId ? "No videos loaded for this playlist yet — open Channels and use Load to fetch them." : urlCategory === "favorites" ? "Star videos to save them for later!" : urlCategory === "watchlater" ? "Click the clock icon on any video card to add it to Watch Later!" : urlCategory === "long" ? "Hover a video and click the hourglass icon to add it here." : urlCategory === "blocked" ? "No blocked videos in your database matching your Block-Rules." : urlCategory === "shorts" ? "No Shorts videos found in this feed." : "Add channels or adjust filters to see videos."}</p>
    </div>`;
  } else {
    grid.innerHTML = sortedVideos.map((v) => videoCard(v, categories)).join("");
  }
}

function renderFolderPills(categories, currentFolder, currentCategory, currentSubCategory = "all") {
  const oldBar = document.getElementById("folderPillsBar");
  if (oldBar) oldBar.remove();

  const container = document.getElementById("headerFolderPills");
  if (!container) return;

  const subParam = currentCategory === "shorts" && currentSubCategory ? `&subCategory=${currentSubCategory}` : "";

  const allUrl = `?category=${currentCategory}${subParam}`;
  const naActive = currentFolder.toUpperCase() === "N/A" || currentFolder.toLowerCase() === "uncategorized";
  const naUrl = `?category=${currentCategory}${subParam}&folder=N%2FA`;

  const displayLabel = currentFolder ? (naActive ? "N/A" : currentFolder) : "All";

  const categoryOptionsHtml = (categories || []).map((cat) => {
    const active = currentFolder.toLowerCase() === cat.toLowerCase();
    const catUrl = `?category=${currentCategory}${subParam}&folder=${encodeURIComponent(cat)}`;
    return `<a href="${catUrl}" class="flex items-center gap-2.5 px-3 py-2 text-xs font-medium transition ${active ? "bg-red-500/15 text-red-400 font-semibold" : "text-slate-300 hover:bg-slate-800/70 hover:text-white"}">
      <i class="fa-solid fa-folder text-xs ${active ? "text-red-400" : "text-slate-400"}"></i>
      <span>${esc(cat)}</span>
    </a>`;
  }).join("");

  container.innerHTML = `
    <div class="relative inline-block text-left">
      <button id="folderDropdownBtn" onclick="toggleFolderDropdown()" class="flex items-center gap-1.5 rounded-full bg-slate-800/90 border border-slate-700/60 px-3 py-1 text-xs font-semibold text-slate-200 transition hover:bg-slate-700 hover:text-white shadow" title="Active Folder: ${esc(displayLabel)}">
        <i class="fa-solid fa-folder-open text-red-400 text-[11px]"></i>
        <span class="whitespace-nowrap">${esc(displayLabel)}</span>
        <i class="fa-solid fa-chevron-down text-[9px] text-slate-400 ml-0.5"></i>
      </button>
      <div id="folderDropdownMenu" class="hidden absolute left-0 top-full mt-1.5 w-32 rounded-xl bg-slate-900/95 backdrop-blur-xl border border-slate-800 shadow-2xl shadow-black/80 z-50 py-1.5 popup-enter">
        <a href="${allUrl}" class="flex items-center gap-2.5 px-3 py-2 text-xs font-medium transition ${!currentFolder ? "bg-red-500/15 text-red-400 font-semibold" : "text-slate-300 hover:bg-slate-800/70 hover:text-white"}">
          <i class="fa-solid fa-folder text-xs ${!currentFolder ? "text-red-400" : "text-slate-400"}"></i>
          <span>All</span>
        </a>
        ${categoryOptionsHtml}
        <a href="${naUrl}" class="flex items-center gap-2.5 px-3 py-2 text-xs font-medium transition ${naActive ? "bg-red-500/15 text-red-400 font-semibold" : "text-slate-300 hover:bg-slate-800/70 hover:text-white"}" title="N/A">
          <i class="fa-solid fa-folder text-xs ${naActive ? "text-red-400" : "text-slate-400"}"></i>
          <span>N/A</span>
        </a>
      </div>
    </div>`;
}

function renderChannelAvatarsBar(channels, videos, activeChannelId, currentCategory, currentFolder, currentSubCategory = "all", activePlaylistId = "", activePlaylistTitle = "") {
  let bar = document.getElementById("channelAvatarsBar");
  if (!channels || !channels.length) {
    if (bar) bar.remove();
    return;
  }
  if (!bar) {
    bar = document.createElement("div");
    bar.id = "channelAvatarsBar";
    const main = document.querySelector("main");
    if (main) main.insertBefore(bar, main.firstChild);
  }
  bar.className = "sticky top-[var(--navbar-height,0px)] z-30 mb-4 flex items-center justify-between gap-3 bg-slate-900 border-b border-slate-800/80 px-4 backdrop-blur-md shadow-xl shadow-black/40 transition-all duration-200";

  const enabledChannels = (channels || []).filter((c) => !c.disabled);
  const channelIdsWithVideos = new Set((videos || []).map((v) => v.channelId));
  if (activeChannelId) channelIdsWithVideos.add(activeChannelId);

  const activeChannels = enabledChannels.filter((c) => channelIdsWithVideos.has(c.channelId));

  if (!activeChannels.length) {
    bar.style.display = "none";
    return;
  } else {
    bar.style.display = "flex";
  }

  const folderParam = currentFolder ? `&folder=${encodeURIComponent(currentFolder)}` : "";
  const subParam = currentCategory === "shorts" && currentSubCategory ? `&subCategory=${currentSubCategory}` : "";
  const baseUrl = `?category=${currentCategory}${subParam}${folderParam}`;
  const playlistParam = activePlaylistId ? `&playlistId=${encodeURIComponent(activePlaylistId)}${activePlaylistTitle ? `&playlistTitle=${encodeURIComponent(activePlaylistTitle)}` : ""}` : "";

  const avatarsHtml = activeChannels.map((c) => {
    const isActive = activeChannelId === c.channelId;
    const targetUrl = isActive ? baseUrl : `?category=${currentCategory}${subParam}&channelId=${encodeURIComponent(c.channelId)}${folderParam}${playlistParam}`;
    return `
      <a href="${targetUrl}" class="avatar-item rounded-full overflow-hidden bg-slate-800 ${isActive ? "ring-2 ring-red-500 ring-offset-2 ring-offset-slate-900 scale-105 z-30" : "ring-1 ring-slate-800/80 hover:ring-2 hover:ring-red-500/50"} transition-all duration-200" title="${esc(c.channelName)}${isActive ? " (Click to unselect)" : ""}">
        ${c.thumbnail ? `<img src="${esc(c.thumbnail)}" class="w-full h-full object-cover rounded-full" alt="${esc(c.channelName)}">` : `<div class="w-full h-full flex items-center justify-center text-[10px] font-bold text-slate-400 rounded-full">${esc(c.channelName.slice(0, 2))}</div>`}
      </a>`;
  }).join("");

  bar.innerHTML = `
    <div class="avatar-stack min-w-0 flex-1 overflow-x-auto scrollbar-none">
      ${avatarsHtml}
    </div>
    ${activeChannelId ? `
      <a href="${baseUrl}${playlistParam}" class="flex-shrink-0 inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-slate-800/90 border border-slate-700/80 text-xs font-semibold text-slate-300 hover:text-white hover:bg-slate-700 transition shadow-md ml-2" title="Show all channels">
        <i class="fa-solid fa-xmark text-xs text-red-400"></i>
        <span>All</span>
      </a>` : ""}
    ${activePlaylistId ? `
      <a href="${baseUrl}${activeChannelId ? `&channelId=${encodeURIComponent(activeChannelId)}` : ""}" class="flex-shrink-0 inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-sky-900/60 border border-sky-700/60 text-xs font-semibold text-sky-300 hover:text-white hover:bg-sky-800/60 transition shadow-md ml-1" title="Clear playlist filter">
        <i class="fa-solid fa-xmark text-xs text-sky-400"></i>
        <span>Playlist</span>
      </a>` : ""}
  `;
}


window.toggleFolderDropdown = function toggleFolderDropdown() {
  const menu = document.getElementById("folderDropdownMenu");
  if (menu) menu.classList.toggle("hidden");
};

/* ------------------------------- channels page ----------------------------- */

function inactivityBadge(lastUpload) {
  if (!lastUpload) return `<span class="rounded bg-slate-800/80 px-2 py-0.5 text-[10px] font-bold text-slate-400" title="No uploads fetched yet">No Uploads</span>`;
  const date = new Date(lastUpload);
  if (isNaN(date.getTime())) return "";
  const diffMs = Date.now() - date.getTime();
  if (diffMs < 0) return "";
  const daysAgo = Math.floor(diffMs / (1000 * 60 * 60 * 24));
  if (daysAgo >= 365) {
    return `<span class="rounded bg-rose-950/90 border border-rose-800/60 px-2 py-0.5 text-[10px] font-bold text-rose-300 shadow" title="Last upload was ${daysAgo} days ago (${isoDate(lastUpload)})"><i class="fa-solid fa-triangle-exclamation mr-1"></i>Inactive (> 1 yr)</span>`;
  }
  if (daysAgo >= 180) {
    return `<span class="rounded bg-amber-950/90 border border-amber-800/60 px-2 py-0.5 text-[10px] font-bold text-amber-300 shadow" title="Last upload was ${daysAgo} days ago (${isoDate(lastUpload)})"><i class="fa-solid fa-clock-rotate-left mr-1"></i>Inactive (> 6 mo)</span>`;
  }
  return "";
}

const DEFAULT_RULES_TEMPLATE = `:Allow-Rules:\n\n:Block-Rules:\n\n:Playlists:`;

function parseRulesCount(rulesText, titleFilters = []) {
  if (!rulesText && titleFilters.length > 0) return titleFilters.length;
  if (!rulesText) return 0;
  const lines = rulesText.split(/\r?\n/).map((l) => l.trim()).filter(Boolean);
  // Count all non-header lines (section headers start with ":")
  const activeLines = lines.filter((l) => !l.startsWith(":"));
  return activeLines.length;
}

function channelRow(channel, categories = []) {
  const disabled = Boolean(channel.disabled);
  const filters = Array.isArray(channel.titleFilters) ? channel.titleFilters : [];
  const rulesText = channel.rulesText ?? "";
  const ruleCount = parseRulesCount(rulesText, filters);
  const initialRulesText = rulesText || (filters.length ? `:Allow-Rules:\n${filters.join("\n")}\n\n:Block-Rules:\n\n:Playlists:` : DEFAULT_RULES_TEMPLATE);
  const category = channel.category ?? "";
  const folderOnly = Boolean(channel.folderOnly);
  const shortsThreshold = Number(channel.shortsThresholdSeconds ?? 60);

  const optionsHtml = categories.map((cat) => `
    <option value="${esc(cat)}" ${cat.toLowerCase() === category.toLowerCase() ? "selected" : ""}>${esc(cat)}</option>
  `).join("");

  return `
  <div class="motion-card border p-4 rounded-lg hover:-translate-y-0.5 transition ${disabled ? "bg-rose-950/30 border-rose-900/50 opacity-80 hover:border-rose-700/60" : "bg-slate-900/90 border-slate-800 hover:border-red-500/40"}">
    <div class="flex items-center justify-between gap-4">
      <div class="flex min-w-0 items-center space-x-4">
        <a href="${esc(channel.url)}" target="_blank" class="w-10 h-10 flex-shrink-0 rounded-full bg-slate-800 flex items-center justify-center text-slate-500 overflow-hidden transition hover:opacity-80 hover:scale-105 ring-1 ring-slate-700/60 ${disabled ? "grayscale" : ""}" title="Open ${esc(channel.channelName)} on YouTube">
          ${channel.thumbnail ? `<img src="${esc(channel.thumbnail)}" class="w-full h-full object-cover" alt="${esc(channel.channelName)}">` : `<i class="fa-solid fa-user"></i>`}
        </a>
        <div class="min-w-0">
          <div class="flex flex-wrap items-center gap-2">
            <a href="${esc(channel.url)}" target="_blank" class="text-sm font-medium text-white hover:text-red-400 transition flex items-center gap-1.5" title="Open ${esc(channel.channelName)} on YouTube">
              <span>${esc(channel.channelName)}</span>
              <i class="fa-solid fa-arrow-up-right-from-square text-[10px] text-slate-500"></i>
            </a>
            ${category ? `<span class="rounded bg-red-950/80 border border-red-800/60 px-2 py-0.5 text-[10px] font-bold text-red-300 shadow"><i class="fa-solid fa-folder text-[9px] mr-1"></i>${esc(category)}</span>` : ""}
            ${folderOnly ? `<span class="inline-flex h-5 w-6 items-center justify-center rounded bg-amber-950/80 border border-amber-800/60 text-[10px] font-bold text-amber-300 shadow" title="Folder Only"><i class="fa-solid fa-folder-tree text-[9px]"></i></span>` : ""}
            ${shortsThreshold !== 60 ? `<span class="inline-flex items-center gap-1 rounded bg-purple-950/80 border border-purple-800/60 px-2 py-0.5 text-[10px] font-bold text-purple-300 shadow" title="Automatic Shorts cutoff: ${shortsThreshold} seconds"><i class="fa-solid fa-stopwatch text-[9px]"></i>≤ ${shortsThreshold}s</span>` : ""}
            ${disabled ? `<span class="rounded bg-slate-800 px-2 py-0.5 text-[10px] font-bold uppercase text-slate-400">Disabled</span>` : ""}
            ${inactivityBadge(channel.lastUpload)}
            ${ruleCount ? `<span class="rounded bg-sky-950 px-2 py-0.5 text-[10px] font-bold uppercase text-sky-300">${ruleCount} Rule${ruleCount === 1 ? "" : "s"}</span>` : ""}
          </div>
          <div class="text-[10px] text-slate-500 truncate max-w-[260px]">${esc(channel.url)}</div>
        </div>
      </div>
      <div class="flex flex-shrink-0 items-center gap-2">
        <button onclick="fetchMoreChannelVideos('${esc(channel.channelId)}', this)" class="inline-flex h-9 w-9 items-center justify-center rounded-lg text-slate-400 hover:bg-slate-800 hover:text-white transition" title="Fetch 10 older past videos from YouTube" aria-label="Fetch older videos">
          <i class="fa-solid fa-cloud-arrow-down"></i>
        </button>
        <button onclick="toggleChannelFolderBox('${esc(channel.channelId)}')" class="inline-flex h-9 w-9 items-center justify-center rounded-lg transition ${category ? "text-red-400 hover:bg-red-950/40" : "text-slate-500 hover:bg-slate-800 hover:text-white"}" title="${category ? "Folder: " + esc(category) : "Assign Folder/Category"}" aria-label="Assign Folder">
          <i class="fa-solid fa-folder-plus"></i>
        </button>
        <button onclick="toggleChannelShortsBox('${esc(channel.channelId)}')" class="inline-flex h-9 w-9 items-center justify-center rounded-lg transition ${shortsThreshold !== 60 ? "text-purple-400 hover:bg-purple-950/50" : "text-slate-500 hover:bg-slate-800 hover:text-purple-300"}" title="Configure Shorts cutoff" aria-label="Configure Shorts cutoff">
          <i class="fa-solid fa-gear"></i>
        </button>
        <button onclick="toggleChannelFolderOnly('${esc(channel.channelId)}')" ${!category ? "disabled" : ""} class="inline-flex h-9 w-9 items-center justify-center rounded-lg transition ${!category ? "text-slate-700 cursor-not-allowed" : folderOnly ? "text-amber-400 hover:bg-amber-950/50" : "text-slate-500 hover:bg-slate-800 hover:text-amber-300"}" title="${folderOnly ? "Show this channel in all feeds" : category ? "Only show videos in the " + esc(category) + " folder" : "Assign a folder first"}" aria-label="${folderOnly ? "Disable Folder Only" : "Enable Folder Only"}">
          <i class="fa-solid ${folderOnly ? "fa-toggle-on" : "fa-toggle-off"} text-lg"></i>
        </button>
        <button onclick="toggleChannelDisabled('${esc(channel.channelId)}')" class="inline-flex h-9 w-9 items-center justify-center rounded-lg transition ${disabled ? "text-slate-500 hover:bg-slate-800 hover:text-white" : "text-emerald-400 hover:bg-emerald-950/50 hover:text-emerald-300"}" title="${disabled ? "Enable channel" : "Disable channel"}" aria-label="${disabled ? "Enable channel" : "Disable channel"}">
          <i class="fa-solid ${disabled ? "fa-toggle-off" : "fa-toggle-on"} text-lg"></i>
        </button>
        <button onclick="toggleChannelPlaylistsBox('${esc(channel.channelId)}')" class="inline-flex h-9 w-9 items-center justify-center rounded-lg text-slate-400 hover:bg-slate-800 hover:text-amber-400 transition" title="Load Channel Playlists" aria-label="Load Playlists">
          <i class="fa-solid fa-bars-staggered"></i>
        </button>
        <button onclick="toggleChannelRuleBox('${esc(channel.channelId)}')" class="inline-flex h-9 w-9 items-center justify-center rounded-lg transition ${ruleCount ? "text-sky-300 hover:bg-sky-950/50" : "text-slate-500 hover:bg-slate-800 hover:text-white"}" title="Channel Rules" aria-label="Channel Rules">
          <i class="fa-solid fa-scale-balanced"></i>
        </button>
        <button onclick="deleteChannel('${esc(channel.channelId)}')" class="inline-flex h-9 w-9 items-center justify-center rounded-lg text-slate-500 hover:bg-slate-800 hover:text-red-400 transition" title="Delete channel">
          <i class="fa-solid fa-trash"></i>
        </button>
      </div>
    </div>
    <form id="folder-${esc(channel.channelId)}" onsubmit="saveChannelFolder(event, '${esc(channel.channelId)}')" class="mt-4 hidden border-t border-slate-800 pt-3 flex flex-col sm:flex-row sm:items-end gap-2">
      <input id="input-folder-${esc(channel.channelId)}" type="text" value="${esc(category)}" class="flex-1 w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-xs text-slate-100 outline-none focus:border-red-500" placeholder="Folder name (e.g. Tech, Gaming)">
      <select onchange="applyFolderDropdownSelection(this, '${esc(channel.channelId)}')" class="w-full sm:w-auto rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-xs text-slate-300 outline-none focus:border-red-500">
        <option value="">Existing Folders...</option>
        ${optionsHtml}
      </select>
      <button type="submit" class="w-full sm:w-auto rounded-lg bg-red-600 px-4 py-2 text-xs font-semibold text-white transition hover:bg-red-500">Save Folder</button>
    </form>
    <form id="shorts-${esc(channel.channelId)}" onsubmit="saveChannelShortsSettings(event, '${esc(channel.channelId)}')" class="mt-4 hidden border-t border-slate-800 pt-3 flex flex-col sm:flex-row sm:items-end gap-2">
      <label class="w-full sm:w-48">
        <span class="mb-1 block text-[10px] font-semibold uppercase tracking-wide text-slate-500" title="Videos at or below this duration are automatically classified as Shorts">Shorts cutoff (seconds)</span>
        <input id="input-shorts-threshold-${esc(channel.channelId)}" type="number" min="1" max="3600" step="1" value="${shortsThreshold}" class="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-xs text-slate-100 outline-none focus:border-purple-500" title="Automatic Shorts cutoff in seconds">
      </label>
      <button type="submit" class="w-full sm:w-auto rounded-lg bg-purple-600 px-4 py-2 text-xs font-semibold text-white transition hover:bg-purple-500">Save Shorts Setting</button>
    </form>
    <form id="rules-${esc(channel.channelId)}" onsubmit="saveChannelRules(event, '${esc(channel.channelId)}')" class="mt-4 hidden border-t border-slate-800 pt-4">
      <label class="block text-xs font-semibold uppercase tracking-wide text-slate-400"><i class="fa-solid fa-scale-balanced text-sky-400 mr-1.5"></i>Channel Rules (Allow & Block)</label>
      <textarea rows="8" class="mt-2 w-full resize-y rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-slate-100 font-mono text-xs leading-relaxed outline-none transition focus:border-sky-500" placeholder="${esc(DEFAULT_RULES_TEMPLATE)}">${esc(initialRulesText)}</textarea>
      <div class="mt-3 flex items-center justify-between gap-3">
        <p class="text-xs text-slate-500">Type whitelisted words under :Allow-Rules:, blacklisted words under :Block-Rules:, and playlist names under :Playlists: to show them first.</p>
        <button type="submit" class="rounded-lg bg-sky-600 px-4 py-2 text-xs font-semibold text-white transition hover:bg-sky-500">Save Rules</button>
      </div>
    </form>
    <div id="playlists-${esc(channel.channelId)}" class="mt-4 hidden border-t border-slate-800 pt-3">
      <div class="flex items-center justify-between mb-2">
        <span class="text-xs font-semibold uppercase tracking-wide text-slate-400"><i class="fa-solid fa-bars-staggered text-amber-400 mr-1.5"></i>Channel Playlists</span>
        <button onclick="loadChannelPlaylists('${esc(channel.channelId)}')" class="text-xs text-amber-400 hover:underline"><i class="fa-solid fa-rotate text-[10px] mr-1"></i>Fetch Playlists</button>
      </div>
      <div id="playlists-list-${esc(channel.channelId)}" class="space-y-1.5 text-xs text-slate-400">
        <p class="italic text-slate-500">Click Fetch Playlists to load available playlists...</p>
      </div>
    </div>

  </div>`;
}

window.applyFolderDropdownSelection = function applyFolderDropdownSelection(selectEl, channelId) {
  const input = document.getElementById(`input-folder-${channelId}`);
  if (input && selectEl.value) {
    input.value = selectEl.value;
  }
};

window.toggleChannelFolderBox = function toggleChannelFolderBox(channelId) {
  const form = document.getElementById(`folder-${channelId}`);
  if (form) form.classList.toggle("hidden");
};

window.toggleChannelShortsBox = function toggleChannelShortsBox(channelId) {
  const form = document.getElementById(`shorts-${channelId}`);
  if (form) form.classList.toggle("hidden");
};

window.toggleChannelFolderOnly = async function toggleChannelFolderOnly(channelId) {
  try {
    const result = await callConvex("mutation", "channels:toggleFolderOnly", { channelId });
    flash(result?.folderOnly ? "Channel is now limited to its assigned folder." : "Channel is visible in all feeds again.", "success");
    await renderChannels({ refreshNav: !isPopupOpen() });
    if (PAGE === "feed") await renderFeed();
  } catch (err) {
    flash(err.message, "danger");
  }
};

window.saveChannelShortsSettings = async function saveChannelShortsSettings(event, channelId) {
  event.preventDefault();
  const input = document.getElementById(`input-shorts-threshold-${channelId}`);
  const seconds = input ? Number(input.value) : 60;
  if (!Number.isFinite(seconds) || seconds < 1 || seconds > 3600) {
    flash("Shorts cutoff must be between 1 and 3600 seconds.", "danger");
    return;
  }
  try {
    await callConvex("mutation", "channels:updateShortsThreshold", { channelId, seconds });
    await renderChannels({ refreshNav: !isPopupOpen() });
    if (PAGE === "feed") await renderFeed();
    flash("Shorts setting updated.", "success");
  } catch (err) {
    flash(err.message, "danger");
  }
};

window.toggleChannelRuleBox = function toggleChannelRuleBox(channelId) {
  const form = document.getElementById(`rules-${channelId}`);
  if (form) form.classList.toggle("hidden");
};

window.toggleChannelPlaylistsBox = function toggleChannelPlaylistsBox(channelId) {
  const box = document.getElementById(`playlists-${channelId}`);
  if (!box) return;
  const isHidden = box.classList.contains("hidden");
  box.classList.toggle("hidden");
  if (isHidden) {
    loadChannelPlaylists(channelId);
  }
};

window.loadChannelPlaylists = async function loadChannelPlaylists(channelId) {
  const listContainer = document.getElementById(`playlists-list-${channelId}`);
  if (!listContainer) return;
  listContainer.innerHTML = '<p class="text-xs text-slate-400"><i class="fa-solid fa-circle-notch fa-spin mr-1.5 text-amber-400"></i>Loading playlists...</p>';
  try {
    const playlists = await callConvex("action", "youtube:listChannelPlaylists", { channelId });
    if (!playlists || !playlists.length) {
      listContainer.innerHTML = '<p class="text-xs text-slate-500">No public playlists found for this channel.</p>';
      return;
    }
    listContainer.innerHTML = playlists.map((pl) => `
      <div class="flex items-center justify-between gap-3 p-2 rounded-lg bg-slate-950 border border-slate-800 hover:border-slate-700 transition">
        <div class="min-w-0 flex-1">
          <a href="${esc(pl.url)}" target="_blank" class="font-medium text-slate-200 hover:text-amber-400 transition truncate block">${esc(pl.title)}</a>
          <span class="text-[10px] text-slate-500">${pl.count} video${pl.count === 1 ? "" : "s"}</span>
        </div>
        <div class="flex items-center gap-1.5 flex-shrink-0">
          <button onclick="openLoadPlaylistModal('${esc(channelId)}', '${esc(pl.url)}', '${esc(pl.title)}', ${pl.count})" class="px-2.5 py-1 rounded bg-sky-600/20 border border-sky-500/40 text-sky-300 hover:bg-sky-600 hover:text-white text-[11px] font-semibold transition" title="Load videos into feed">
            <i class="fa-solid fa-download text-[10px] mr-1"></i>Load
          </button>
          <button onclick="addPlaylistToChannelRules('${esc(channelId)}', '${esc(pl.url)}', '${esc(pl.title)}', ${pl.count})" class="px-2.5 py-1 rounded bg-amber-600/20 border border-amber-500/40 text-amber-300 hover:bg-amber-600 hover:text-white text-[11px] font-semibold transition" title="Add playlist URL to channel rules and load videos">
            + Rule
          </button>
        </div>
      </div>
    `).join("");
  } catch (err) {
    listContainer.innerHTML = `<p class="text-xs text-rose-400"><i class="fa-solid fa-triangle-exclamation mr-1"></i>${esc(err.message)}</p>`;
  }
};

window.addPlaylistToChannelRules = async function addPlaylistToChannelRules(channelId, plUrl, plTitle, plCount = 0) {
  try {
    const channels = await callConvex("query", "channels:list");
    const channel = (channels || []).find((c) => c.channelId === channelId);
    let rawText = channel?.rulesText ?? "";
    if (!rawText) {
      rawText = `:Allow-Rules:\n\n:Block-Rules:\n\n:Playlists:\n${plUrl}`;
    } else if (rawText.includes(":Playlists:")) {
      rawText = rawText.trim() + `\n${plUrl}`;
    } else {
      rawText = rawText.trim() + `\n\n:Playlists:\n${plUrl}`;
    }

    await callConvex("mutation", "channels:updateRules", { channelId, rulesText: rawText });
    flash(`Added "${plTitle}" to channel rules!`, "success");
    await renderChannels({ refreshNav: !isPopupOpen() });
    // Re-open the playlists and rules boxes so user doesn't lose their place
    const playlistsBox = document.getElementById(`playlists-${channelId}`);
    if (playlistsBox) {
      playlistsBox.classList.remove("hidden");
      loadChannelPlaylists(channelId); // repopulate the list (re-render wiped it)
    }
    const rulesBox = document.getElementById(`rules-${channelId}`);
    if (rulesBox) rulesBox.classList.remove("hidden");
    // Immediately open the Load modal so user can load videos without extra steps
    openLoadPlaylistModal(channelId, plUrl, plTitle, plCount);
    if (PAGE === "feed") await renderFeed();
  } catch (err) {
    flash(err.message, "danger");
  }
};

window.removePlaylistRule = async function removePlaylistRule(channelId, playlistId) {
  try {
    await callConvex("mutation", "channels:removePlaylistRule", { channelId, playlistId });
    flash("Playlist removed from rules.", "success");
    // If currently viewing this playlist, navigate away
    const urlParams = new URLSearchParams(location.search);
    if (urlParams.get("playlistId") === playlistId) {
      history.replaceState(null, "", "?");
    }
    await renderPlaylistsPanel();
    if (PAGE === "feed") await renderFeed();
  } catch (err) {
    flash(err.message, "danger");
  }
};

window.openLoadPlaylistModal = function openLoadPlaylistModal(channelId, plUrl, plTitle, totalCount) {
  // Remove any existing modal
  const existing = document.getElementById("loadPlaylistModal");
  if (existing) existing.remove();

  const modal = document.createElement("div");
  modal.id = "loadPlaylistModal";
  modal.className = "fixed inset-0 z-[100] flex items-center justify-center";
  modal.innerHTML = `
    <div class="absolute inset-0 bg-slate-950/80 backdrop-blur-sm" onclick="closeLoadPlaylistModal()"></div>
    <div class="relative z-10 w-[min(420px,calc(100vw-2rem))] rounded-xl border border-slate-700 bg-slate-900 shadow-2xl shadow-black/80 p-5">
      <div class="flex items-start justify-between mb-4">
        <div class="min-w-0">
          <h3 class="text-sm font-bold text-white"><i class="fa-solid fa-download text-sky-400 mr-1.5"></i>Load Playlist Videos</h3>
          <p class="mt-0.5 text-xs text-slate-400 truncate max-w-[300px]">${esc(plTitle)}</p>
          <p class="text-[10px] text-slate-500 mt-0.5">${totalCount > 0 ? `${totalCount} videos in playlist` : ""}</p>
        </div>
        <button onclick="closeLoadPlaylistModal()" class="flex-shrink-0 text-slate-500 hover:text-white transition ml-3"><i class="fa-solid fa-xmark"></i></button>
      </div>

      <div class="space-y-4">
        <div>
          <label class="block text-xs font-semibold text-slate-400 mb-1.5">How many videos to load</label>
          <div class="grid grid-cols-3 gap-1.5" id="plLimitBtns">
            ${[["10","10"],["25","25"],["50","50"],["100","100"],["250","250"],["0","All"]].map(([val, label]) =>
              `<button type="button" data-val="${val}" onclick="selectPlLimit(this)"
                class="pl-limit-btn rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-xs font-semibold text-slate-300 hover:border-sky-500 hover:text-sky-300 transition ${val === "0" ? "border-sky-500 text-sky-300 bg-sky-950/30" : ""}"
              >${label}</button>`
            ).join("")}
          </div>
          <input type="hidden" id="plLimitValue" value="0">
        </div>

        <div class="flex gap-2 pt-1">
          <button type="button" onclick="closeLoadPlaylistModal()" class="flex-1 rounded-lg border border-slate-700 bg-slate-950 px-4 py-2 text-xs font-semibold text-slate-300 hover:bg-slate-800 transition">Cancel</button>
          <button type="button" id="plLoadConfirmBtn" onclick="confirmLoadPlaylist('${esc(channelId)}', '${esc(plUrl)}', '${esc(plTitle)}')"
            class="flex-1 rounded-lg bg-sky-600 hover:bg-sky-500 px-4 py-2 text-xs font-semibold text-white transition">
            <i class="fa-solid fa-download mr-1.5"></i>Load
          </button>
        </div>
      </div>
    </div>`;
  document.body.appendChild(modal);
};

window.closeLoadPlaylistModal = function closeLoadPlaylistModal() {
  const modal = document.getElementById("loadPlaylistModal");
  if (modal) modal.remove();
};

window.selectPlLimit = function selectPlLimit(btn) {
  document.querySelectorAll(".pl-limit-btn").forEach((b) => {
    b.className = b.className
      .replace("border-sky-500 text-sky-300 bg-sky-950/30", "")
      .trim() + " border-slate-700 text-slate-300";
  });
  btn.className = btn.className
    .replace("border-slate-700 text-slate-300", "")
    .trim() + " border-sky-500 text-sky-300 bg-sky-950/30";
  const input = document.getElementById("plLimitValue");
  if (input) input.value = btn.dataset.val;
};

window.confirmLoadPlaylist = async function confirmLoadPlaylist(channelId, plUrl, plTitle) {
  const maxItems = parseInt(document.getElementById("plLimitValue")?.value ?? "0", 10);

  const btn = document.getElementById("plLoadConfirmBtn");
  if (btn) { btn.disabled = true; btn.innerHTML = '<i class="fa-solid fa-circle-notch fa-spin mr-1.5"></i>Loading...'; }

  try {
    // 1. Add the playlist URL to the channel rules if not already there
    const channels = await callConvex("query", "channels:list");
    const channel = (channels || []).find((c) => c.channelId === channelId);
    let rawText = channel?.rulesText ?? "";
    const alreadyAdded = rawText.includes(plUrl);
    if (!alreadyAdded) {
      if (!rawText) {
        rawText = `:Allow-Rules:\n\n:Block-Rules:\n\n:Playlists:\n${plUrl}`;
      } else if (rawText.includes(":Playlists:")) {
        rawText = rawText.trim() + `\n${plUrl}`;
      } else {
        rawText = rawText.trim() + `\n\n:Playlists:\n${plUrl}`;
      }
      await callConvex("mutation", "channels:updateRules", { channelId, rulesText: rawText });
    }

    // 2. Extract playlist ID
    const playlistIdMatch = plUrl.match(/[?&]list=(PL[A-Za-z0-9_-]+)/i);
    const playlistId = playlistIdMatch ? playlistIdMatch[1] : null;
    if (!playlistId) throw new Error("Could not extract playlist ID from URL.");

    const res = await callConvex("action", "refresh:loadPlaylistVideos", {
      channelId,
      playlistId,
      maxItems,
    });

    const limitLabel = maxItems === 0 ? "all" : maxItems;
    flash(
      `Loaded "${plTitle}" — ${res.newVideos} new video${res.newVideos === 1 ? "" : "s"} added (${limitLabel})`,
      "success",
    );
    closeLoadPlaylistModal();
    await renderChannels({ refreshNav: !isPopupOpen() });
    if (PAGE === "feed") await renderFeed();
  } catch (err) {
    flash(err.message, "danger");
    if (btn) { btn.disabled = false; btn.innerHTML = '<i class="fa-solid fa-download mr-1.5"></i>Load'; }
  }
};

window.loadPlaylistVideos = async function loadPlaylistVideos(channelId, plUrl, plTitle, btn) {
  // Legacy direct-call path (kept for compatibility) — now just opens the modal
  openLoadPlaylistModal(channelId, plUrl, plTitle, 0);
};


window.saveChannelRules = async function saveChannelRules(event, channelId) {
  event.preventDefault();
  const form = event.currentTarget;
  const textarea = form.querySelector("textarea");
  const rulesText = textarea.value.trim();
  try {
    await callConvex("mutation", "channels:updateRules", {
      channelId,
      rulesText,
    });
    await renderChannels({ refreshNav: !isPopupOpen() });
    if (PAGE === "feed") await renderFeed();
    flash("Channel rules updated.", "success");
  } catch (err) {
    flash(err.message, "danger");
  }
};


window.fetchMoreChannelVideos = async function fetchMoreChannelVideos(channelId, btn) {
  if (btn) {
    btn.disabled = true;
    btn.innerHTML = '<i class="fa-solid fa-circle-notch fa-spin text-xs text-red-400"></i>';
  }
  try {
    const res = await callConvex("action", "refresh:fetchMoreChannelVideos", { channelId });
    flash(`Fetched older videos for ${res.channelName || "channel"}! Found ${res.newVideos} new video(s).`, "success");
    await renderChannels({ refreshNav: !isPopupOpen() });
    if (PAGE === "feed") await renderFeed();
  } catch (err) {
    flash(err.message, "danger");
  } finally {
    if (btn) {
      btn.disabled = false;
      btn.innerHTML = '<i class="fa-solid fa-cloud-arrow-down"></i>';
    }
  }
};


window.saveChannelFolder = async function saveChannelFolder(event, channelId) {
  event.preventDefault();
  const input = document.getElementById(`input-folder-${channelId}`);
  const categoryValue = input ? input.value.trim() : "";

  try {
    await callConvex("mutation", "channels:updateCategory", {
      channelId,
      category: categoryValue,
    });
    await renderChannels({ refreshNav: !isPopupOpen() });
    if (PAGE === "feed") await renderFeed();
    flash("Channel folder updated.", "success");
  } catch (err) {
    flash(err.message, "danger");
  }
};

window.toggleChannelFilterBox = function toggleChannelFilterBox(channelId) {
  const form = document.getElementById(`filters-${channelId}`);
  if (form) form.classList.toggle("hidden");
};

window.saveChannelFilters = async function saveChannelFilters(event, channelId) {
  event.preventDefault();
  const form = event.currentTarget;
  const textarea = form.querySelector("textarea");
  const filters = textarea.value
    .split(/\r?\n/)
    .map((line) => line.trim())
    .filter(Boolean);
  try {
    await callConvex("mutation", "channels:updateTitleFilters", {
      channelId,
      filters,
    });
    await renderChannels({ refreshNav: !isPopupOpen() });
    if (PAGE === "feed") await renderFeed();
    flash("Channel filters updated.", "success");
  } catch (err) {
    flash(err.message, "danger");
  }
};

window.toggleChannelDisabled = async function toggleChannelDisabled(channelId) {
  try {
    await callConvex("mutation", "channels:toggleDisabled", { channelId });
    await renderChannels({ refreshNav: !isPopupOpen() });
    if (PAGE === "feed") await renderFeed();
  } catch (err) {
    flash(err.message, "danger");
  }
};

function isPopupOpen() {
  const popup = document.getElementById("appPopup");
  return Boolean(popup && !popup.classList.contains("hidden"));
}

window.deleteChannel = async function deleteChannel(channelId) {
  if (!confirm("Remove this channel and all its videos?")) return;
  try {
    await callConvex("mutation", "channels:remove", { channelId });
    await renderChannels({ refreshNav: !isPopupOpen() });
    if (PAGE === "feed") await renderFeed();
  } catch (err) {
    flash(err.message, "danger");
  }
};

let currentChannelSort = localStorage.getItem("channelSort") || "recent";
let channelSearchQuery = "";

window.handleChannelSearchInput = function handleChannelSearchInput(value) {
  channelSearchQuery = value.trim().toLowerCase();
  renderChannels({ refreshNav: false, keepQuery: true });
};

window.changeChannelSort = async function changeChannelSort(sortMethod) {
  currentChannelSort = sortMethod;
  localStorage.setItem("channelSort", sortMethod);
  await renderChannels({ refreshNav: false });
};

window.changeFeedLimitFromHeader = async function changeFeedLimitFromHeader(newLimit) {
  try {
    const limitNum = Number(newLimit);
    const config = await callConvex("query", "settings:config");
    await callConvex("mutation", "settings:updateConfig", {
      showSeen: config.showSeen,
      hideShorts: config.hideShorts,
      hidePrivate: config.hidePrivate,
      unseenFirst: config.unseenFirst,
      defaultFeedFilter: config.defaultFeedFilter,
      defaultShortsFilter: config.defaultShortsFilter,
      feedLimit: limitNum,
    });
    flash(`Feed limit updated to ${limitNum === 0 ? "All" : limitNum} videos!`, "success");
    if (PAGE === "feed") await renderFeed();
  } catch (err) {
    flash(err.message, "danger");
  }
};


function sortChannelsList(channels, sortMethod) {
  const list = [...channels];
  if (sortMethod === "name") {
    list.sort((a, b) => a.channelName.localeCompare(b.channelName));
  } else if (sortMethod === "category") {
    list.sort((a, b) => (a.category || "zzz").localeCompare(b.category || "zzz") || a.channelName.localeCompare(b.channelName));
  } else if (sortMethod === "inactive") {
    list.sort((a, b) => {
      if (!a.lastUpload) return -1;
      if (!b.lastUpload) return 1;
      return a.lastUpload.localeCompare(b.lastUpload);
    });
  } else {
    // "recent" (default)
    list.sort((a, b) => {
      if (!a.lastUpload) return 1;
      if (!b.lastUpload) return -1;
      return b.lastUpload.localeCompare(a.lastUpload);
    });
  }
  return list;
}

async function renderChannels({ refreshNav = true, keepQuery = false } = {}) {
  const [channels, categories, settings, unread] = await Promise.all([
    callConvex("query", "channels:list"),
    callConvex("query", "channels:categories"),
    callConvex("query", "settings:get"),
    callConvex("query", "videos:unreadCount"),
  ]);
  if (refreshNav) renderNav({ unreadCount: unread, showSeen: settings });

  const list = document.getElementById("channelList");
  if (!list) return;

  if (!keepQuery) {
    const input = document.getElementById("channelUrl");
    if (input) channelSearchQuery = input.value.trim().toLowerCase();
  }

  const sortedChannels = sortChannelsList(channels, currentChannelSort);
  const filteredChannels = sortedChannels.filter((channel) => {
    if (!channelSearchQuery) return true;
    const nameMatch = (channel.channelName || "").toLowerCase().includes(channelSearchQuery);
    const urlMatch = (channel.url || "").toLowerCase().includes(channelSearchQuery);
    const categoryMatch = (channel.category || "").toLowerCase().includes(channelSearchQuery);
    const rulesMatch = (channel.rulesText || "").toLowerCase().includes(channelSearchQuery);
    return nameMatch || urlMatch || categoryMatch || rulesMatch;
  });

  const sortSelect = document.getElementById("channelSortSelect");
  if (sortSelect) sortSelect.value = currentChannelSort;

  const countNum = document.getElementById("channelCountNumber");
  if (countNum) countNum.textContent = `${channels.length}`;

  list.innerHTML = filteredChannels.length
    ? filteredChannels.map((channel) => channelRow(channel, categories)).join("")
    : sortedChannels.length
      ? '<p class="text-slate-600 text-sm">No matching channels found for your search.</p>'
      : '<p class="text-slate-600 text-sm">No channels yet. Add your first one above!</p>';
}

function initChannelsPage() {
  const form = document.getElementById("addChannelForm");
  if (!form) return;
  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const input = document.getElementById("channelUrl");
    const btn = form.querySelector("button[type=submit]");
    btn.disabled = true;
    btn.textContent = "Adding...";
    try {
      const res = await callConvex("action", "channels:add", { url: input.value });
      flash(`Channel added and synced successfully! Found ${res.newVideos} new video(s).`, "success");
      input.value = "";
      await renderChannels({ refreshNav: !isPopupOpen() });
      if (PAGE === "feed") await renderFeed();
    } catch (err) {
      flash(err.message, "danger");
    } finally {
      btn.disabled = false;
      btn.textContent = "Add Channel";
    }
  });
}

/* --------------------------------- stats page ------------------------------ */

function renderHeatmap(data, days) {
  const container = document.getElementById("heatmap");
  if (!container) return;
  if (!data.length) {
    container.innerHTML = '<section class="border-t border-slate-800 pt-6"><p class="text-slate-600 text-sm">No uploads in this period yet.</p></section>';
    return;
  }
  const monthLabels = days.map((day) => {
    const d = new Date(day);
    return isNaN(d.getTime()) ? "" : d.toLocaleDateString(undefined, { month: "short", day: "numeric" });
  });
  const rows = data.map((stat) => {
    const cells = stat.dailyCounts
      .map((count, i) => {
        const cls = count === 0
          ? "bg-slate-900/60 border border-slate-800/80 text-slate-600"
          : count === 1
            ? "bg-slate-800 border border-slate-700 text-red-400 font-bold"
            : count === 2
              ? "bg-red-950/80 border border-red-800/90 text-red-300 font-bold"
              : "bg-red-900/90 border border-red-700 text-red-200 font-extrabold";
        return `<div class="aspect-square h-6.5 w-full rounded flex items-center justify-center text-[10px] box-border ${cls}" title="${dayLabel(days[i])}: ${count} uploads">${count > 0 ? count : "-"}</div>`;
      })
      .join("");
    return `
    <div class="grid grid-cols-[140px_1fr] items-center gap-4 border-b border-slate-800/70 py-3 last:border-b-0">
      <div class="min-w-0">
        <div class="truncate text-sm font-semibold text-slate-300">${esc(stat.name)}</div>
        <div class="text-xs text-red-400">${esc(stat.total)} uploads</div>
      </div>
      <div class="grid gap-1.5" style="grid-template-columns: repeat(${days.length}, minmax(0, 1fr));">
        ${cells}
      </div>
    </div>`;
  }).join("");
  container.innerHTML = `
    <section class="border-t border-slate-800 pt-6">
      <div class="mb-4 flex flex-wrap items-center justify-between gap-3">
        <div>
          <h3 class="text-sm font-semibold text-white">Daily Upload Activity</h3>
          <p class="text-xs text-slate-500">${esc(monthLabels[0])} to ${esc(monthLabels[monthLabels.length - 1])}</p>
        </div>
        <div class="text-xs text-slate-400 font-medium">
          <span>Numbers show daily upload count per day</span>
        </div>
      </div>
      <div class="rounded-lg border border-slate-800 bg-slate-950/45 px-4 py-2">
        ${rows}
      </div>
    </section>`;
}

function renderStatsSummary(data) {
  const container = document.getElementById("statsSummary");
  if (!container) return;
  const summary = data.summary || {};
  const quota = data.quota || { todayUnits: 0, limit: 10000, todayPercent: 0, remainingToday: 10000, totalUnits: 0, totalRequests: 0 };
  const convexDb = data.convexDb || { totalVideosInDb: 0, unseenVideosInDb: 0, seenVideosInDb: 0, favoriteVideosInDb: 0, estimatedDbMb: 0, percentStorageUsed: 0 };
  const exec = getConvexExecutions();
  const cards = [
    ["Uploads", summary.uploadsInPeriod ?? 0, "fa-video"],
    ["Unseen", summary.unseenVisible ?? 0, "fa-bell"],
    ["Active", summary.activeChannels ?? 0, "fa-signal"],
    ["Filtered", summary.filteredVideos ?? summary.hiddenByFilters ?? 0, "fa-filter"],
  ];
  container.innerHTML = `
    <div class="grid grid-cols-2 gap-3 md:grid-cols-4">
      ${cards.map(([label, value, icon]) => `
        <div class="rounded-lg border border-slate-800 bg-slate-950/70 p-4">
          <div class="flex items-center justify-between text-slate-500">
            <span class="text-xs font-semibold uppercase tracking-wide">${esc(label)}</span>
            <i class="fa-solid ${icon}"></i>
          </div>
          <div class="mt-2 text-2xl font-bold text-white">${esc(value)}</div>
        </div>`).join("")}
    </div>
    <div class="mt-3 flex flex-wrap gap-2 text-xs text-slate-500">
      <span>${esc(summary.enabledChannels ?? 0)} enabled channels</span>
      <span>&bull;</span>
      <span>${esc(summary.disabledChannels ?? 0)} disabled channels</span>
      <span>&bull;</span>
      <span>${esc(summary.filteredChannels ?? 0)} channels with filters</span>
    </div>
    <div class="mt-4 grid grid-cols-1 sm:grid-cols-2 gap-3">
      <div class="rounded-xl border border-slate-800 bg-slate-950/70 p-4">
        <div class="flex items-center justify-between text-slate-400 text-xs font-semibold mb-2">
          <span><i class="fa-brands fa-youtube text-red-500 mr-1.5"></i>YouTube Data API v3 Quota</span>
          <span class="text-slate-300 font-bold">${quota.todayUnits.toLocaleString()} / ${quota.limit.toLocaleString()} Today</span>
        </div>
        <div class="w-full h-2 rounded-full bg-slate-800 overflow-hidden mb-2.5">
          <div class="h-full bg-gradient-to-r from-emerald-500 to-amber-500 transition-all duration-500" style="width: ${Math.max(1, quota.todayPercent)}%;"></div>
        </div>
        <div class="flex flex-wrap items-center justify-between text-[11px] text-slate-400 gap-2">
          <span>Remaining Today: <strong class="text-emerald-400">${quota.remainingToday.toLocaleString()} Units</strong></span>
          <span>All-Time: <strong class="text-white">${quota.totalUnits.toLocaleString()} Units</strong></span>
        </div>
      </div>
      <div class="rounded-xl border border-slate-800 bg-slate-950/70 p-4">
        <div class="flex items-center justify-between text-slate-400 text-xs font-semibold mb-3">
          <span><i class="fa-solid fa-database text-sky-400 mr-1.5"></i>Convex DB Storage</span>
          <span class="text-slate-300 font-bold">${convexDb.totalVideosInDb.toLocaleString()} Videos in DB</span>
        </div>
        <div class="flex flex-wrap items-center justify-between text-xs text-slate-400 gap-2 mt-2">
          <span>Est. Size: <strong class="text-sky-300">${convexDb.estimatedDbMb} MB</strong></span>
          <span><strong class="text-red-400">${convexDb.unseenVideosInDb} Unseen</strong> • <strong class="text-slate-300">${convexDb.seenVideosInDb} Seen</strong></span>
        </div>
      </div>
      <div class="sm:col-span-2 rounded-xl border border-slate-800 bg-slate-950/70 p-4">
        <div class="flex items-center justify-between text-slate-400 text-xs font-semibold mb-3">
          <span><i class="fa-solid fa-bolt text-amber-400 mr-1.5"></i>Convex Executions</span>
          <span class="text-slate-300 font-bold">${exec.total.toLocaleString()} Calls</span>
        </div>
        <div class="flex flex-wrap items-center justify-between text-xs text-slate-400 gap-2 mt-2">
          <span>Calls Breakdown: <strong class="text-sky-400">${exec.queries} Queries</strong> • <strong class="text-emerald-400">${exec.mutations} Mutations</strong> • <strong class="text-amber-400">${exec.actions} Actions</strong></span>
          <button type="button" onclick="resetConvexExecutions()" class="text-[10px] text-slate-500 hover:text-red-400 underline">Reset Counter</button>
        </div>
      </div>
    </div>`;
}

function renderChannelStats(channels) {
  const container = document.getElementById("channelStats");
  if (!container) return;
  if (!channels.length) {
    container.innerHTML = '<p class="text-slate-600 text-sm">No channel activity to show.</p>';
    return;
  }
  container.innerHTML = `
    <div class="overflow-hidden rounded-lg border border-slate-800">
      ${channels.map((channel) => `
        <div class="grid grid-cols-[1fr_auto_auto_auto] items-center gap-4 border-b border-slate-800 bg-slate-950/45 p-3 last:border-b-0">
          <div class="flex min-w-0 items-center gap-3">
            <a href="https://www.youtube.com/channel/${esc(channel.channelId)}" target="_blank" class="h-9 w-9 flex-shrink-0 overflow-hidden rounded-full bg-slate-800 transition hover:opacity-80 hover:scale-105" title="Open ${esc(channel.name)} on YouTube">
              ${channel.thumbnail ? `<img src="${esc(channel.thumbnail)}" class="h-full w-full object-cover" alt="${esc(channel.name)}">` : ""}
            </a>
            <div class="min-w-0">
              <a href="https://www.youtube.com/channel/${esc(channel.channelId)}" target="_blank" class="truncate text-sm font-semibold text-slate-200 hover:text-red-400 transition block">${esc(channel.name)}</a>
              <div class="text-xs text-slate-500">${channel.lastUpload ? esc(timeLabel(channel.lastUpload)) : "No uploads"}</div>
            </div>
          </div>
          <div class="text-right">
            <div class="text-sm font-bold text-white">${esc(channel.periodCount)}</div>
            <div class="text-[10px] uppercase text-slate-500">uploads</div>
          </div>
          <div class="text-right">
            <div class="text-sm font-bold text-red-300">${esc(channel.unseenCount)}</div>
            <div class="text-[10px] uppercase text-slate-500">unseen</div>
          </div>
          <div class="text-right">
            <div class="text-sm font-bold ${channel.filterCount ? "text-sky-300" : "text-slate-500"}">${esc(channel.filterCount)}</div>
            <div class="text-[10px] uppercase text-slate-500">rules</div>
          </div>
        </div>`).join("")}
    </div>`;
}

async function renderStats({ refreshNav = true, periodOverride = null } = {}) {
  const urlParams = new URLSearchParams(location.search);
  const period = periodOverride || (urlParams.get("period") === "week" ? "week" : "month");

  // Highlight the active period toggle
  document.querySelectorAll('a[href^="?period="]').forEach((a) => {
    const active = a.getAttribute("href").includes(`period=${period}`);
    a.className = `px-4 py-1 text-xs rounded-md transition capitalize ${active ? "bg-red-600 text-white" : "text-slate-400 hover:text-white"}`;
  });
  document.querySelectorAll("[data-period]").forEach((button) => {
    const active = button.dataset.period === period;
    button.className = `px-4 py-1 text-xs rounded-md transition capitalize ${active ? "bg-red-600 text-white" : "text-slate-400 hover:text-white"}`;
  });

  const [data, settings, unread] = await Promise.all([
    callConvex("query", "stats:heatmap", { period }),
    callConvex("query", "settings:get"),
    callConvex("query", "videos:unreadCount"),
  ]);
  if (refreshNav) renderNav({ unreadCount: unread, showSeen: settings });
  renderStatsSummary(data);
  renderChannelStats(data.channelSummaries || []);
  renderHeatmap(data.channels, data.days);
}

/* -------------------------------- settings page ---------------------------- */

function initSettingsPage() {
  const form = document.getElementById("settingsForm");
  if (!form) return;
  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const checked = document.getElementById("showSeenToggle")?.checked ?? false;
    const hideShortsChecked = document.getElementById("hideShortsToggle")?.checked ?? false;
    const hidePrivateChecked = document.getElementById("hidePrivateToggle")?.checked ?? false;
    const unseenFirstChecked = document.getElementById("unseenFirstToggle")?.checked ?? false;
    const defaultFeedFilterVal = document.getElementById("defaultFeedFilterSelect")?.value ?? "all";
    const defaultShortsFilterVal = document.getElementById("defaultShortsFilterSelect")?.value ?? "all";
    const feedLimitVal = Number(document.getElementById("feedLimitSelect")?.value ?? 50);
    const apiKeyInput = document.getElementById("youtubeDataApiKey");
    const clearApiKey = document.getElementById("clearYoutubeDataApiKey").checked;
    const btn = form.querySelector("button[type=submit]");
    btn.disabled = true;
    try {
      await callConvex("mutation", "settings:updateConfig", {
        showSeen: checked,
        hideShorts: hideShortsChecked,
        hidePrivate: hidePrivateChecked,
        unseenFirst: unseenFirstChecked,
        defaultFeedFilter: defaultFeedFilterVal,
        defaultShortsFilter: defaultShortsFilterVal,
        feedLimit: feedLimitVal,
        youtubeDataApiKey: apiKeyInput.value,
        clearYoutubeDataApiKey: clearApiKey,
      });
      apiKeyInput.value = "";
      document.getElementById("clearYoutubeDataApiKey").checked = false;
      const config = await callConvex("query", "settings:config");
      renderSettingsConfig(config);
      flash("Settings updated!", "success");
      if (PAGE === "feed") await renderFeed();
    } catch (err) {
      flash(err.message, "danger");
    } finally {
      btn.disabled = false;
    }
  });
}

function renderSettingsConfig(config) {
  const toggle = document.getElementById("showSeenToggle");
  const shortsToggle = document.getElementById("hideShortsToggle");
  const privateToggle = document.getElementById("hidePrivateToggle");
  const unseenFirstToggle = document.getElementById("unseenFirstToggle");
  const defaultFilterSelect = document.getElementById("defaultFeedFilterSelect");
  const defaultShortsFilterSelect = document.getElementById("defaultShortsFilterSelect");
  const feedLimitSelect = document.getElementById("feedLimitSelect");
  const status = document.getElementById("youtubeApiKeyStatus");
  if (toggle) toggle.checked = config.showSeen;
  if (shortsToggle) shortsToggle.checked = Boolean(config.hideShorts);
  if (privateToggle) privateToggle.checked = Boolean(config.hidePrivate);
  if (unseenFirstToggle) unseenFirstToggle.checked = Boolean(config.unseenFirst);
  if (defaultFilterSelect && config.defaultFeedFilter) defaultFilterSelect.value = config.defaultFeedFilter;
  if (defaultShortsFilterSelect && config.defaultShortsFilter) defaultShortsFilterSelect.value = config.defaultShortsFilter;
  if (feedLimitSelect && config.feedLimit != null) feedLimitSelect.value = String(config.feedLimit);
  if (status) {
    status.textContent = config.hasYoutubeDataApiKey
      ? "A key is saved. Leave blank to keep it, paste a new key to replace it, or check Clear saved key."
      : "No key saved. Paste a YouTube Data API v3 key to fetch video durations.";
  }
}

/* ----------------------------------- init ---------------------------------- */

async function refreshNavAndDispatch() {
  if (!CONFIGURED) {
    configBanner();
    renderNav({});
    return;
  }
  try {
    if (PAGE === "feed") await renderFeed();
    else if (PAGE === "channels") await renderChannels();
    else if (PAGE === "stats") await renderStats();
    else if (PAGE === "settings") {
      const [config, unread] = await Promise.all([
        callConvex("query", "settings:config"),
        callConvex("query", "videos:unreadCount"),
      ]);
      renderNav({ unreadCount: unread, showSeen: config.showSeen });
      renderSettingsConfig(config);
      initSettingsPage();
    }
  } catch (err) {
    flash(err.message, "danger");
  }
}

// Close dropdowns when clicking outside.
window.addEventListener("click", (event) => {
  if (!event.target.closest("#dropdownButton")) {
    const menu = document.getElementById("dropdownMenu");
    if (menu && !menu.classList.contains("hidden")) menu.classList.add("hidden");
  }
  if (!event.target.closest("#folderDropdownBtn")) {
    const folderMenu = document.getElementById("folderDropdownMenu");
    if (folderMenu && !folderMenu.classList.contains("hidden")) folderMenu.classList.add("hidden");
  }
  if (!event.target.closest(".video-folder-picker")) {
    document.querySelectorAll(".video-folder-menu").forEach((menu) => menu.classList.add("hidden"));
  }
});

window.addEventListener("keydown", (event) => {
  if (event.key === "Escape") closePopup();
});

window.addEventListener("resize", updateNavbarOffset);

document.addEventListener("DOMContentLoaded", () => {
  if (PAGE === "channels") initChannelsPage();
  refreshNavAndDispatch();
});
