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
        <input type="text" id="channelUrl" name="channel_url" autocomplete="off" autocapitalize="off" spellcheck="false" data-bwignore="true" data-lpignore="true" data-1p-ignore="true" placeholder="Paste YouTube Channel URL (e.g. @username)" required class="flex-1 min-w-[180px] bg-slate-950 border border-slate-700 rounded-lg px-3.5 py-2 text-xs sm:text-sm text-white focus:outline-none focus:border-red-500 transition">
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
        <div class="border-t border-slate-800 pt-6">
          <label for="feedLimitSelect" class="block text-white font-medium">Videos Per Feed Page</label>
          <p class="mt-1 text-xs text-slate-500">Choose how many videos to display on your feed page.</p>
          <select id="feedLimitSelect" name="feed_limit" class="mt-3 bg-slate-950 border border-slate-700 rounded-lg px-4 py-2.5 text-sm text-white focus:outline-none focus:border-red-500 transition">
            <option value="20">20 Videos</option>
            <option value="50" selected>50 Videos</option>
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
};

function renderNav({ unreadCount = 0, showSeen = false, category = "all", subCategory = "all", folder = "" } = {}) {
  const el = document.getElementById("navbar");
  if (!el) return;

  const isShorts = category === "shorts";
  const activeFilterId = isShorts ? subCategory : category;

  const filterItems = isShorts ? [
    { id: "all", label: "All Shorts", icon: "fa-border-all" },
    { id: "unseen", label: "Unseen Shorts", icon: "fa-eye-slash" },
    { id: "seen", label: "Seen Shorts", icon: "fa-eye" },
    { id: "favorites", label: "Saved Shorts", icon: "fa-star text-amber-400" },
  ] : [
    { id: "all", label: "All Videos", icon: "fa-border-all" },
    { id: "unseen", label: "Unseen", icon: "fa-eye-slash" },
    { id: "seen", label: "Seen", icon: "fa-eye" },
    { id: "favorites", label: "Saved", icon: "fa-star text-amber-400" },
    { id: "shorts", label: "Shorts", icon: "fa-mobile-screen-button text-amber-400" },
  ];

  el.innerHTML = `
  <nav class="bg-slate-900/80 backdrop-blur-md border-b border-slate-800">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex h-16 items-center justify-between gap-2 sm:gap-4">
        <div class="flex items-center space-x-2 sm:space-x-3 flex-shrink-0 min-w-0">
          <a href="index.html" class="flex items-center space-x-2 text-red-500 font-bold text-lg sm:text-xl tracking-tight flex-shrink-0">
            <i class="fa-brands fa-youtube text-2xl sm:text-3xl"></i>
            <span class="bg-gradient-to-r from-red-500 to-amber-500 bg-clip-text text-transparent">YT Notifier</span>
            <span id="headerCardCount" class="ml-1 px-2 py-0.5 rounded-full bg-slate-800/90 border border-slate-700/60 text-[11px] font-bold text-slate-300 shadow flex items-center" title="Videos showing on current page">0</span>
          </a>
          <div id="headerFolderPills" class="relative flex items-center py-1"></div>
        </div>
        <div class="flex items-center gap-1.5 sm:gap-3 flex-shrink-0">
          <a href="index.html" class="nav-link ${PAGE === "feed" && !isShorts ? "is-active" : ""} relative inline-flex h-9 w-9 sm:h-10 sm:w-10 items-center justify-center rounded-lg text-sm font-medium transition hover:bg-slate-800 ${PAGE === "feed" && !isShorts ? "bg-slate-800 text-red-400" : "text-slate-300"}" title="Feed (${unreadCount} unseen)" aria-label="Feed (${unreadCount} unseen)">
            <i class="fa-solid fa-bell"></i>
            ${unreadCount > 0 ? `<span class="absolute -top-1.5 -right-1.5 text-[10px] sm:text-[11px] font-extrabold text-red-400 leading-none tracking-tight">${unreadCount}</span>` : ""}
          </a>
          ${PAGE === "feed" ? `
          <div class="relative inline-block text-left">
            <button id="dropdownButton" onclick="toggleDropdown()" class="inline-flex h-9 w-9 sm:h-10 sm:w-10 items-center justify-center rounded-lg bg-slate-900 border border-slate-800 text-slate-300 hover:text-white transition" title="Filter: ${esc(activeFilterId)}" aria-label="Filter: ${esc(activeFilterId)}">
              <i class="fa-solid fa-filter"></i>
            </button>
            <div id="dropdownMenu" class="hidden absolute right-0 mt-2 w-40 rounded-xl bg-slate-900/95 backdrop-blur-xl border border-slate-800 shadow-2xl shadow-black/80 z-50 py-1.5 popup-enter">
              <div class="px-3 py-1 text-[10px] font-bold uppercase tracking-wider text-slate-500 border-b border-slate-800/80 mb-1">${isShorts ? "Filter Shorts" : "Filter Feed"}</div>
              ${filterItems.map((item) => {
                const isActive = item.id === activeFilterId;
                const folderParam = folder ? `&folder=${encodeURIComponent(folder)}` : "";
                const linkHref = isShorts
                  ? `?category=shorts&subCategory=${item.id}${folderParam}`
                  : `?category=${item.id}${folderParam}`;
                return `
                <a href="${linkHref}" class="flex items-center gap-2.5 px-3 py-2 text-xs font-medium transition ${isActive ? "bg-red-500/15 text-red-400 font-semibold" : "text-slate-300 hover:bg-slate-800/70 hover:text-white"}">
                  <i class="fa-solid ${item.icon} w-3.5 text-center text-xs"></i>
                  <span>${esc(item.label)}</span>
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
          <a href="index.html?category=shorts" class="nav-link ${category === "shorts" ? "is-active" : ""} inline-flex h-9 w-9 sm:h-10 sm:w-10 items-center justify-center rounded-lg text-sm font-medium transition hover:bg-slate-800 ${category === "shorts" ? "bg-slate-800 text-amber-400" : "text-slate-300"}" title="Shorts Feed" aria-label="Shorts Feed">
            <i class="fa-solid fa-mobile-screen-button"></i>
          </a>
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
    } else if (page === "stats") {
      await renderStats({ refreshNav: false });
    } else if (page === "settings") {
      const configData = await callConvex("query", "settings:config");
      renderSettingsConfig(configData);
      initSettingsPage();
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
  const [settings, unread] = await Promise.all([
    callConvex("query", "settings:get"),
    callConvex("query", "videos:unreadCount", { folder: folder || undefined }),
  ]);
  renderNav({ unreadCount: unread, showSeen: settings, folder });
}

/* --------------------------------- feed page ------------------------------- */

function videoCard(video, categories = []) {
  const isNew = video.isNew;
  const isFavorite = Boolean(video.isFavorite);
  const currentCat = video.channelCategory || "";
  const cardTone = isNew
    ? "bg-slate-900/90 border-slate-800 hover:border-red-500/50 ring-1 ring-red-500/30 hover:shadow-red-900/20"
    : "bg-slate-900/55 border-slate-800/60 hover:border-slate-700 opacity-85";
  const imageTone = isNew
    ? "grayscale-0 opacity-100"
    : "grayscale opacity-60";
  const titleTone = isNew
    ? "text-slate-100 group-hover:text-red-400"
    : "text-slate-500 group-hover:text-slate-300";
  const channelTone = isNew
    ? "text-slate-200 group-hover:text-white"
    : "text-slate-500 group-hover:text-slate-300";

  const optionsHtml = (categories || []).map((cat) => `
    <option value="${esc(cat)}" ${cat.toLowerCase() === currentCat.toLowerCase() ? "selected" : ""}>📁 ${esc(cat)}</option>
  `).join("");

  return `
  <article class="motion-card group soft-panel ${cardTone} border rounded-none overflow-hidden transition-all duration-300 hover:-translate-y-1 hover:shadow-2xl">
    <div class="relative aspect-video bg-slate-950 overflow-hidden">
      <a href="${esc(video.link)}" target="_blank" class="absolute inset-0">
      <img src="https://img.youtube.com/vi/${esc(video.videoId)}/hqdefault.jpg" alt="${esc(video.title)}" class="${imageTone} w-full h-full object-cover group-hover:scale-105 transition duration-500" loading="lazy">
      <div class="absolute inset-0 bg-gradient-to-t from-slate-950/65 via-transparent to-transparent opacity-90 group-hover:opacity-60 transition"></div>
      </a>
      <div class="absolute right-3 top-3 z-10 flex items-center gap-2">
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
        <div class="w-9 h-9 rounded-full bg-slate-800 flex items-center justify-center overflow-hidden text-slate-500 ring-1 ring-slate-700">
          ${video.channelThumbnail ? `<img src="${esc(video.channelThumbnail)}" class="w-full h-full object-cover" alt="">` : `<i class="fa-solid fa-user text-sm"></i>`}
        </div>
        <div class="min-w-0 flex-1">
          <div class="flex items-center gap-2 min-w-0">
            <span class="truncate text-sm font-semibold ${channelTone} transition">${esc(video.channelName)}</span>
            <select onchange="changeChannelFolderFromCard(this.value, '${esc(video.channelId)}')" class="flex-shrink-0 rounded bg-red-950/80 border border-red-800/60 px-1.5 py-0.5 text-[10px] font-bold text-red-300 outline-none transition cursor-pointer hover:bg-red-900/90" title="Change folder for ${esc(video.channelName)}">
              <option value="" ${!currentCat ? "selected" : ""}>+ Folder</option>
              ${optionsHtml}
            </select>
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
  const settings = await callConvex("query", "settings:get");
  const urlCategory = urlParams.get("category") || "all";
  const urlSubCategory = urlParams.get("subCategory") || "all";
  const folder = urlParams.get("folder") || "";
  const channelId = urlParams.get("channelId") || "";

  const [videos, unread, categories, channels] = await Promise.all([
    callConvex("query", "videos:list", {
      category: urlCategory,
      subCategory: urlSubCategory || undefined,
      folder: folder || undefined,
      channelId: channelId || undefined,
    }),
    callConvex("query", "videos:unreadCount", { folder: folder || undefined, channelId: channelId || undefined }),
    callConvex("query", "channels:categories"),
    callConvex("query", "channels:list"),
  ]);

  renderNav({
    unreadCount: unread,
    showSeen: settings,
    category: urlCategory,
    subCategory: urlSubCategory,
    folder,
  });

  renderFolderPills(categories, folder, urlCategory, urlSubCategory);
  renderChannelAvatarsBar(channels, channelId, urlCategory, folder, urlSubCategory);

  const countBadge = document.getElementById("headerCardCount");
  if (countBadge) {
    countBadge.textContent = `${videos.length}`;
    countBadge.title = `${videos.length} video card${videos.length === 1 ? "" : "s"} showing on current page`;
  }

  const grid = document.getElementById("videoGrid");
  if (!grid) return;
  if (!videos.length) {
    grid.innerHTML = `
    <div class="col-span-full py-20 text-center text-slate-600">
      <i class="fa-solid fa-video-slash text-5xl mb-4 opacity-20"></i>
      <p class="text-lg">No videos found. ${urlCategory === "favorites" ? "Star videos to save them for later!" : urlCategory === "shorts" ? "No Shorts videos found in this feed." : "Add channels or adjust filters to see videos."}</p>
    </div>`;
  } else {
    grid.innerHTML = videos.map((v) => videoCard(v, categories)).join("");
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

function renderChannelAvatarsBar(channels, activeChannelId, currentCategory, currentFolder, currentSubCategory = "all") {
  let bar = document.getElementById("channelAvatarsBar");
  if (!channels || !channels.length) {
    if (bar) bar.remove();
    return;
  }
  if (!bar) {
    bar = document.createElement("div");
    bar.id = "channelAvatarsBar";
    bar.className = "mb-5 flex items-center justify-between gap-3 bg-slate-900/60 border border-slate-800/80 rounded-xl p-2.5 px-4 backdrop-blur-md";
    const main = document.querySelector("main");
    if (main) main.insertBefore(bar, main.firstChild);
  }

  const enabledChannels = channels.filter((c) => !c.disabled);

  const folderParam = currentFolder ? `&folder=${encodeURIComponent(currentFolder)}` : "";
  const subParam = currentCategory === "shorts" && currentSubCategory ? `&subCategory=${currentSubCategory}` : "";
  const baseUrl = `?category=${currentCategory}${subParam}${folderParam}`;

  const avatarsHtml = enabledChannels.map((c) => {
    const isActive = activeChannelId === c.channelId;
    const catUrl = `?category=${currentCategory}${subParam}&channelId=${encodeURIComponent(c.channelId)}${folderParam}`;
    return `
      <a href="${catUrl}" class="relative w-8 h-8 rounded-full ring-2 ${isActive ? "ring-red-500 scale-110 z-30 shadow-lg shadow-red-950/50" : "ring-slate-900 hover:ring-slate-600 hover:scale-105 z-10"} overflow-hidden bg-slate-800 transition-all duration-200 flex-shrink-0" title="${esc(c.channelName)}">
        ${c.thumbnail ? `<img src="${esc(c.thumbnail)}" class="w-full h-full object-cover" alt="${esc(c.channelName)}">` : `<div class="w-full h-full flex items-center justify-center text-[10px] font-bold text-slate-400">${esc(c.channelName.slice(0, 2))}</div>`}
      </a>`;
  }).join("");

  bar.innerHTML = `
    <div class="flex items-center gap-2 min-w-0">
      <span class="text-xs font-semibold uppercase tracking-wider text-slate-400 flex-shrink-0 mr-1"><i class="fa-solid fa-users text-red-500 mr-1.5"></i>Channels:</span>
      <div class="flex items-center -space-x-2 hover:space-x-1 overflow-x-auto no-scrollbar py-1 transition-all duration-300">
        <a href="${baseUrl}" class="relative w-8 h-8 rounded-full ring-2 ${!activeChannelId ? "ring-red-500 bg-red-600 text-white z-30 shadow" : "ring-slate-900 bg-slate-800 text-slate-300 hover:bg-slate-700 z-10"} flex items-center justify-center text-[10px] font-bold flex-shrink-0 transition-all duration-200" title="All Channels">
          ALL
        </a>
        ${avatarsHtml}
      </div>
    </div>
    ${activeChannelId ? `
      <a href="${baseUrl}" class="text-xs font-semibold text-slate-400 hover:text-red-400 transition flex-shrink-0 flex items-center gap-1">
        <i class="fa-solid fa-xmark text-xs"></i> Reset Filter
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

function channelRow(channel, categories = []) {
  const disabled = Boolean(channel.disabled);
  const filters = Array.isArray(channel.titleFilters) ? channel.titleFilters : [];
  const filterCount = filters.length;
  const filterText = filters.join("\n");
  const category = channel.category ?? "";

  const optionsHtml = categories.map((cat) => `
    <option value="${esc(cat)}" ${cat.toLowerCase() === category.toLowerCase() ? "selected" : ""}>${esc(cat)}</option>
  `).join("");

  const isCustomInput = category && !categories.some((c) => c.toLowerCase() === category.toLowerCase());

  return `
  <div class="motion-card border p-4 rounded-lg hover:-translate-y-0.5 transition ${disabled ? "bg-rose-950/30 border-rose-900/50 opacity-80 hover:border-rose-700/60" : "bg-slate-900/90 border-slate-800 hover:border-red-500/40"}">
    <div class="flex items-center justify-between gap-4">
      <div class="flex min-w-0 items-center space-x-4">
        <div class="w-10 h-10 flex-shrink-0 rounded-full bg-slate-800 flex items-center justify-center text-slate-500 overflow-hidden ${disabled ? "grayscale" : ""}">
          ${channel.thumbnail ? `<img src="${esc(channel.thumbnail)}" class="w-full h-full object-cover" alt="">` : `<i class="fa-solid fa-user"></i>`}
        </div>
        <div class="min-w-0">
          <div class="flex flex-wrap items-center gap-2">
            <span class="text-sm font-medium text-white">${esc(channel.channelName)}</span>
            ${category ? `<span class="rounded bg-red-950/80 border border-red-800/60 px-2 py-0.5 text-[10px] font-bold text-red-300 shadow"><i class="fa-solid fa-folder text-[9px] mr-1"></i>${esc(category)}</span>` : ""}
            ${disabled ? `<span class="rounded bg-slate-800 px-2 py-0.5 text-[10px] font-bold uppercase text-slate-400">Disabled</span>` : ""}
            ${inactivityBadge(channel.lastUpload)}
            ${filterCount ? `<span class="rounded bg-sky-950 px-2 py-0.5 text-[10px] font-bold uppercase text-sky-300">${filterCount} filter${filterCount === 1 ? "" : "s"}</span>` : ""}
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
        <button onclick="toggleChannelDisabled('${esc(channel.channelId)}')" class="inline-flex h-9 w-9 items-center justify-center rounded-lg transition ${disabled ? "text-slate-500 hover:bg-slate-800 hover:text-white" : "text-emerald-400 hover:bg-emerald-950/50 hover:text-emerald-300"}" title="${disabled ? "Enable channel" : "Disable channel"}" aria-label="${disabled ? "Enable channel" : "Disable channel"}">
          <i class="fa-solid ${disabled ? "fa-toggle-off" : "fa-toggle-on"} text-lg"></i>
        </button>
        <button onclick="toggleChannelFilterBox('${esc(channel.channelId)}')" class="inline-flex h-9 w-9 items-center justify-center rounded-lg transition ${filterCount ? "text-sky-300 hover:bg-sky-950/50" : "text-slate-500 hover:bg-slate-800 hover:text-white"}" title="Title filters" aria-label="Title filters">
          <i class="fa-solid fa-filter"></i>
        </button>
        <button onclick="deleteChannel('${esc(channel.channelId)}')" class="inline-flex h-9 w-9 items-center justify-center rounded-lg text-slate-500 hover:bg-slate-800 hover:text-red-400 transition" title="Delete channel">
          <i class="fa-solid fa-trash"></i>
        </button>
      </div>
    </div>
    <form id="folder-${esc(channel.channelId)}" onsubmit="saveChannelFolder(event, '${esc(channel.channelId)}')" class="mt-4 hidden border-t border-slate-800 pt-3 flex flex-col sm:flex-row items-center gap-2">
      <input id="input-folder-${esc(channel.channelId)}" type="text" value="${esc(category)}" class="flex-1 w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-xs text-slate-100 outline-none focus:border-red-500" placeholder="Folder name (e.g. Tech, Gaming)">
      <select onchange="applyFolderDropdownSelection(this, '${esc(channel.channelId)}')" class="w-full sm:w-auto rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-xs text-slate-300 outline-none focus:border-red-500">
        <option value="">Existing Folders...</option>
        ${optionsHtml}
      </select>
      <button type="submit" class="w-full sm:w-auto rounded-lg bg-red-600 px-4 py-2 text-xs font-semibold text-white transition hover:bg-red-500">Save Folder</button>
    </form>
    <form id="filters-${esc(channel.channelId)}" onsubmit="saveChannelFilters(event, '${esc(channel.channelId)}')" class="mt-4 hidden border-t border-slate-800 pt-4">
      <label class="block text-xs font-semibold uppercase tracking-wide text-slate-400">Title filters</label>
      <textarea rows="4" class="mt-2 w-full resize-y rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-slate-100 outline-none transition focus:border-sky-500" placeholder="One title match per line">${esc(filterText)}</textarea>
      <div class="mt-3 flex items-center justify-between gap-3">
        <p class="text-xs text-slate-500">If filters are set, only matching video titles are fetched and shown.</p>
        <button type="submit" class="rounded-lg bg-sky-600 px-4 py-2 text-xs font-semibold text-white transition hover:bg-sky-500">Save Filters</button>
      </div>
    </form>
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

window.changeChannelSort = async function changeChannelSort(sortMethod) {
  currentChannelSort = sortMethod;
  localStorage.setItem("channelSort", sortMethod);
  await renderChannels({ refreshNav: false });
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

async function renderChannels({ refreshNav = true } = {}) {
  const [channels, categories, settings, unread] = await Promise.all([
    callConvex("query", "channels:list"),
    callConvex("query", "channels:categories"),
    callConvex("query", "settings:get"),
    callConvex("query", "videos:unreadCount"),
  ]);
  if (refreshNav) renderNav({ unreadCount: unread, showSeen: settings });

  const list = document.getElementById("channelList");
  if (!list) return;

  const sortedChannels = sortChannelsList(channels, currentChannelSort);

  const sortSelect = document.getElementById("channelSortSelect");
  if (sortSelect) sortSelect.value = currentChannelSort;

  const countNum = document.getElementById("channelCountNumber");
  if (countNum) countNum.textContent = `${channels.length}`;

  list.innerHTML = sortedChannels.length
    ? sortedChannels.map((channel) => channelRow(channel, categories)).join("")
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
        <div class="flex items-center justify-between text-slate-400 text-xs font-semibold mb-2">
          <span><i class="fa-solid fa-database text-sky-400 mr-1.5"></i>Convex DB Storage</span>
          <span class="text-slate-300 font-bold">${convexDb.totalVideosInDb.toLocaleString()} Videos in DB</span>
        </div>
        <div class="w-full h-2 rounded-full bg-slate-800 overflow-hidden mb-2.5">
          <div class="h-full bg-sky-500 transition-all duration-500" style="width: ${Math.max(1, convexDb.percentStorageUsed)}%;"></div>
        </div>
        <div class="flex flex-wrap items-center justify-between text-[11px] text-slate-400 gap-2">
          <span>Est. Size: <strong class="text-sky-300">${convexDb.estimatedDbMb} MB</strong></span>
          <span><strong class="text-red-400">${convexDb.unseenVideosInDb} Unseen</strong> • <strong class="text-slate-300">${convexDb.seenVideosInDb} Seen</strong></span>
        </div>
      </div>
      <div class="sm:col-span-2 rounded-xl border border-slate-800 bg-slate-950/70 p-4">
        <div class="flex items-center justify-between text-slate-400 text-xs font-semibold mb-2">
          <span><i class="fa-solid fa-bolt text-amber-400 mr-1.5"></i>Convex Executions</span>
          <span class="text-slate-300 font-bold">${exec.total.toLocaleString()} Calls</span>
        </div>
        <div class="w-full h-2 rounded-full bg-slate-800 overflow-hidden mb-2.5">
          <div class="h-full bg-amber-500 transition-all duration-500" style="width: ${Math.max(1, exec.percentUsed)}%;"></div>
        </div>
        <div class="flex flex-wrap items-center justify-between text-[11px] text-slate-400 gap-2">
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
            <div class="h-9 w-9 flex-shrink-0 overflow-hidden rounded-full bg-slate-800">
              ${channel.thumbnail ? `<img src="${esc(channel.thumbnail)}" class="h-full w-full object-cover" alt="">` : ""}
            </div>
            <div class="min-w-0">
              <div class="truncate text-sm font-semibold text-slate-200">${esc(channel.name)}</div>
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
    const feedLimitVal = Number(document.getElementById("feedLimitSelect")?.value ?? 50);
    const apiKeyInput = document.getElementById("youtubeDataApiKey");
    const clearApiKey = document.getElementById("clearYoutubeDataApiKey").checked;
    const btn = form.querySelector("button[type=submit]");
    btn.disabled = true;
    try {
      await callConvex("mutation", "settings:updateConfig", {
        showSeen: checked,
        hideShorts: hideShortsChecked,
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
  const feedLimitSelect = document.getElementById("feedLimitSelect");
  const status = document.getElementById("youtubeApiKeyStatus");
  if (toggle) toggle.checked = config.showSeen;
  if (shortsToggle) shortsToggle.checked = Boolean(config.hideShorts);
  if (feedLimitSelect && config.feedLimit) feedLimitSelect.value = String(config.feedLimit);
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
});

window.addEventListener("keydown", (event) => {
  if (event.key === "Escape") closePopup();
});

window.addEventListener("resize", updateNavbarOffset);

document.addEventListener("DOMContentLoaded", () => {
  if (PAGE === "channels") initChannelsPage();
  refreshNavAndDispatch();
});
