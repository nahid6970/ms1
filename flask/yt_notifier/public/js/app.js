/* Shared frontend logic for the YT Notifier static site.
 * Talks to Convex through its HTTP API (/api/query, /api/mutation, /api/action)
 * so no SDK or build step is needed.
 */
const PAGE = document.body.dataset.page || "feed";
const CONFIGURED =
  window.CONVEX_URL &&
  !window.CONVEX_URL.includes("YOUR-DEPLOYMENT");
const API_BASE = CONFIGURED ? window.CONVEX_URL.replace(/\/+$/, "") : "";

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

function dayLabel(dateStr) {
  const d = new Date(dateStr);
  return isNaN(d.getTime())
    ? dateStr
    : d.toLocaleDateString(undefined, { weekday: "short", month: "short", day: "numeric" });
}

async function callConvex(endpoint, path, args = {}) {
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

function flash(message, type = "info") {
  const container = document.getElementById("flashMessages");
  if (!container) return;
  const styles = {
    success: "bg-emerald-950/40 border-emerald-800/50 text-emerald-300",
    danger: "bg-rose-950/40 border-rose-800/50 text-rose-300",
    info: "bg-amber-950/40 border-amber-800/50 text-amber-300",
  };
  const icons = {
    success: "fa-circle-check text-emerald-400",
    danger: "fa-triangle-exclamation text-rose-400",
    info: "fa-circle-info text-amber-400",
  };
  const el = document.createElement("div");
  el.className = `p-4 rounded-xl border mb-3 flex items-center justify-between shadow-md transition ${styles[type] || styles.info}`;
  el.innerHTML = `
    <div class="flex items-center space-x-3">
      <i class="fa-solid ${icons[type] || icons.info} text-lg"></i>
      <span class="text-sm font-medium">${esc(message)}</span>
    </div>
    <button class="text-slate-400 hover:text-slate-200" onclick="this.parentElement.remove()">
      <i class="fa-solid fa-xmark"></i>
    </button>`;
  container.appendChild(el);
}

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
    body: `
      <div class="space-y-6">
        <form id="addChannelForm" class="soft-panel bg-slate-900/85 border border-slate-800 rounded-lg p-4 flex flex-col sm:flex-row gap-3">
          <input type="text" id="channelUrl" name="url" placeholder="Paste YouTube Channel URL (e.g. @username)" required class="flex-1 bg-slate-950 border border-slate-700 rounded-lg px-4 py-3 text-sm text-white focus:outline-none focus:border-red-500 transition">
          <button type="submit" class="bg-red-600 hover:bg-red-500 text-white px-5 py-3 rounded-lg text-sm font-semibold transition">Add Channel</button>
        </form>
        <div id="channelList" class="space-y-3">
          <p class="text-slate-600 text-sm">Loading...</p>
        </div>
      </div>`,
  },
  stats: {
    title: "Upload Heatmap",
    icon: "fa-chart-pie",
    body: `
      <div class="space-y-5">
        <div class="flex bg-slate-900 rounded-lg p-1 border border-slate-800 w-max">
          <button type="button" data-period="week" onclick="renderStats({ refreshNav: false, periodOverride: 'week' })" class="px-4 py-1 text-xs rounded-md transition capitalize">week</button>
          <button type="button" data-period="month" onclick="renderStats({ refreshNav: false, periodOverride: 'month' })" class="px-4 py-1 text-xs rounded-md transition capitalize">month</button>
        </div>
        <div class="soft-panel bg-slate-900/85 border border-slate-800 rounded-lg p-5 overflow-x-auto">
          <div class="min-w-[600px]" id="heatmap">
            <p class="text-slate-600 text-sm">Loading...</p>
          </div>
        </div>
      </div>`,
  },
  settings: {
    title: "Settings",
    icon: "fa-gear",
    body: `
      <form id="settingsForm" class="soft-panel bg-slate-900/85 border border-slate-800 rounded-lg p-5 space-y-6">
        <div class="flex items-center justify-between gap-6">
          <div>
            <h2 class="text-white font-medium">Enable Category ALL/SEEN/UNSEEN</h2>
            <p class="text-slate-500 text-xs">If enabled, you can categorize videos into All/Unseen/Seen.</p>
          </div>
          <label class="relative inline-flex items-center cursor-pointer">
            <input type="checkbox" id="showSeenToggle" name="show_seen" class="sr-only peer">
            <div class="w-11 h-6 bg-slate-700 peer-focus:outline-none rounded-none peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-none after:h-5 after:w-5 after:transition-all peer-checked:bg-red-600"></div>
          </label>
        </div>
        <div class="border-t border-slate-800 pt-6">
          <label for="youtubeDataApiKey" class="block text-white font-medium">YouTube Data API v3 Key</label>
          <p id="youtubeApiKeyStatus" class="mt-1 text-xs text-slate-500">Leave blank to keep the saved key.</p>
          <div class="mt-3 flex flex-col gap-3 sm:flex-row">
            <input type="password" id="youtubeDataApiKey" autocomplete="off" placeholder="Paste API key" class="flex-1 bg-slate-950 border border-slate-700 rounded-lg px-4 py-3 text-sm text-white focus:outline-none focus:border-red-500 transition">
            <label class="inline-flex items-center gap-2 text-xs font-medium text-slate-400">
              <input type="checkbox" id="clearYoutubeDataApiKey" class="h-4 w-4 rounded border-slate-700 bg-slate-950 accent-red-600">
              Clear saved key
            </label>
          </div>
        </div>
        <button type="submit" class="bg-red-600 text-white px-6 py-2 text-sm font-semibold hover:bg-red-500 transition">Save Settings</button>
      </form>`,
  },
};

function renderNav({ unreadCount = 0, showSeen = false, category = "all" } = {}) {
  const el = document.getElementById("navbar");
  if (!el) return;
  el.innerHTML = `
  <nav class="bg-slate-900/80 backdrop-blur-md border-b border-slate-800 sticky top-0 z-50">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex flex-col gap-3 py-3 lg:min-h-16 lg:flex-row lg:items-center lg:justify-between">
        <div class="flex items-center space-x-3">
          <a href="index.html" class="flex items-center space-x-2 text-red-500 font-bold text-xl tracking-tight">
            <i class="fa-brands fa-youtube text-3xl animate-pulse"></i>
            <span class="bg-gradient-to-r from-red-500 to-amber-500 bg-clip-text text-transparent">YT Notifier</span>
          </a>
        </div>
        <div class="flex flex-wrap items-center gap-2 lg:gap-4">
          <a href="index.html" class="nav-link ${PAGE === "feed" ? "is-active" : ""} px-3 py-2 rounded-lg text-sm font-medium transition hover:bg-slate-800 ${PAGE === "feed" ? "bg-slate-800 text-red-400" : "text-slate-300"}">
            <i class="fa-solid fa-bell mr-1.5"></i> Feed
            ${unreadCount > 0 ? `<span class="ml-1.5 px-2 py-0.5 text-xs bg-red-600 text-white rounded-full font-bold animate-bounce">${unreadCount}</span>` : ""}
          </a>
          ${showSeen && PAGE === "feed" ? `
          <div class="relative inline-block text-left">
            <button id="dropdownButton" onclick="toggleDropdown()" class="flex items-center space-x-2 bg-slate-900 border border-slate-800 px-3 py-1.5 text-[10px] uppercase font-bold text-slate-300 hover:text-white transition">
              <span>${esc(category)}</span>
              <i class="fa-solid fa-chevron-down text-[8px]"></i>
            </button>
            <div id="dropdownMenu" class="hidden absolute left-0 mt-1 w-24 bg-slate-900 border border-slate-800 z-50">
              ${["all", "unseen", "seen"].map((c) => `
                <a href="?category=${c}" class="block px-3 py-1.5 text-[10px] uppercase font-bold text-slate-400 hover:bg-slate-800 hover:text-white transition ${c === category ? "text-red-400" : ""}">
                  ${c}
                </a>`).join("")}
            </div>
          </div>` : ""}
          ${NAV_LINKS.filter((l) => l.page !== "feed").map((l) => `
          <button type="button" onclick="openPopup('${l.page}')" class="nav-link px-3 py-2 rounded-lg text-sm font-medium transition hover:bg-slate-800 text-slate-300">
            <i class="fa-solid ${l.icon} mr-1.5"></i> ${l.label}
          </button>`).join("")}
          <button id="refreshButton" onclick="checkUpdates()" class="bg-gradient-to-r from-red-600 to-amber-500 hover:from-red-500 hover:to-amber-400 text-white px-4 py-2 rounded-lg text-sm font-semibold shadow-lg shadow-red-900/30 transition transform hover:-translate-y-0.5 active:scale-95 flex items-center space-x-1.5">
            <i class="fa-solid fa-rotate"></i>
            <span>Check Updates</span>
          </button>
        </div>
      </div>
    </div>
  </nav>`;
}

function ensurePopup() {
  let popup = document.getElementById("appPopup");
  if (popup) return popup;

  popup = document.createElement("div");
  popup.id = "appPopup";
  popup.className = "fixed inset-0 z-[80] hidden";
  popup.innerHTML = `
    <div class="absolute inset-0 bg-slate-950/75 backdrop-blur-sm" onclick="closePopup()"></div>
    <section class="popup-panel absolute left-1/2 top-1/2 max-h-[calc(100vh-3rem)] w-[min(940px,calc(100vw-2rem))] -translate-x-1/2 -translate-y-1/2 overflow-hidden rounded-xl border border-slate-800 bg-slate-950 shadow-2xl shadow-black/50">
      <header class="flex items-center justify-between border-b border-slate-800 px-5 py-4">
        <h2 id="popupTitle" class="text-lg font-semibold text-white"></h2>
        <button type="button" onclick="closePopup()" class="rounded-lg px-3 py-2 text-slate-400 transition hover:bg-slate-900 hover:text-white" title="Close">
          <i class="fa-solid fa-xmark"></i>
        </button>
      </header>
      <div id="popupBody" class="max-h-[calc(100vh-8rem)] overflow-y-auto p-5"></div>
    </section>`;
  document.body.appendChild(popup);
  return popup;
}

window.openPopup = async function openPopup(page) {
  const config = POPUP_PAGES[page];
  if (!config) return;
  const popup = ensurePopup();
  document.getElementById("popupTitle").innerHTML = `<i class="fa-solid ${config.icon} mr-2 text-red-400"></i>${esc(config.title)}`;
  document.getElementById("popupBody").innerHTML = config.body;
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

window.checkUpdates = async function checkUpdates() {
  const btn = document.getElementById("refreshButton");
  if (!btn) return;
  btn.disabled = true;
  btn.querySelector("span").textContent = "Updating...";
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
    if (PAGE === "feed") await renderFeed();
    else await refreshNavOnly();
  } catch (err) {
    flash(err.message, "danger");
  } finally {
    btn.disabled = false;
    btn.querySelector("span").textContent = "Check Updates";
  }
};

async function refreshNavOnly() {
  const [settings, unread] = await Promise.all([
    callConvex("query", "settings:get"),
    callConvex("query", "videos:unreadCount"),
  ]);
  renderNav({ unreadCount: unread, showSeen: settings });
}

/* --------------------------------- feed page ------------------------------- */

function videoCard(video) {
  const isNew = video.isNew;
  return `
  <article class="motion-card group soft-panel bg-slate-900/90 border border-slate-800 rounded-lg overflow-hidden hover:border-red-500/50 transition-all duration-300 hover:-translate-y-1 hover:shadow-2xl hover:shadow-red-900/20 ${isNew ? "ring-1 ring-red-500/30" : "opacity-70 grayscale-[0.35]"}">
    <a href="${esc(video.link)}" target="_blank" class="block relative aspect-video bg-slate-950 overflow-hidden">
      <img src="https://img.youtube.com/vi/${esc(video.videoId)}/hqdefault.jpg" alt="${esc(video.title)}" class="w-full h-full object-cover group-hover:scale-105 transition duration-500" loading="lazy">
      <div class="absolute inset-0 bg-gradient-to-t from-slate-950/65 via-transparent to-transparent opacity-90 group-hover:opacity-60 transition"></div>
      <div class="absolute left-3 top-3 flex items-center gap-2">
        ${isNew ? `<span class="bg-red-600/95 backdrop-blur px-2.5 py-1 rounded-md text-[10px] font-bold text-white shadow-lg shadow-red-950/30">NEW</span>` : ""}
      </div>
      ${durationBadge(video)}
    </a>
    <div class="p-5 flex min-h-48 flex-col">
      <div class="flex items-center gap-3 mb-3">
        <div class="w-9 h-9 rounded-full bg-slate-800 flex items-center justify-center overflow-hidden text-slate-500 ring-1 ring-slate-700">
          ${video.channelThumbnail ? `<img src="${esc(video.channelThumbnail)}" class="w-full h-full object-cover" alt="">` : `<i class="fa-solid fa-user text-sm"></i>`}
        </div>
        <div class="min-w-0">
          <div class="truncate text-sm font-semibold text-slate-200 group-hover:text-white transition">${esc(video.channelName)}</div>
          <div class="mt-0.5 text-xs text-slate-500" title="${esc(isoDate(video.published))}">${esc(timeLabel(video.published))}</div>
        </div>
      </div>
      <h3 class="text-lg font-semibold text-slate-100 leading-snug mb-auto line-clamp-2 group-hover:text-red-400 transition">${esc(video.title)}</h3>
      <div class="flex items-center justify-end border-t border-slate-800/80 text-slate-500 text-xs mt-5 pt-4">
        <div class="flex items-center space-x-3">
          <button onclick="toggleRead('${esc(video._id)}')" class="relative inline-flex items-center cursor-pointer" title="Toggle read status">
            <input type="checkbox" class="sr-only peer" ${isNew ? "" : "checked"}>
            <div class="w-9 h-5 bg-slate-700 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-red-600"></div>
          </button>
          <a href="${esc(video.link)}" target="_blank" class="text-slate-400 hover:text-white transition">
            <i class="fa-solid fa-external-link"></i>
          </a>
        </div>
      </div>
    </div>
  </article>`;
}

window.toggleRead = async function toggleRead(id) {
  try {
    await callConvex("mutation", "videos:toggleRead", { id });
    await renderFeed();
  } catch (err) {
    flash(err.message, "danger");
  }
};

async function renderFeed() {
  const urlParams = new URLSearchParams(location.search);
  const settings = await callConvex("query", "settings:get");
  const urlCategory = urlParams.get("category") || "all";
  const category = settings ? urlCategory : "unseen";

  const [videos, unread] = await Promise.all([
    callConvex("query", "videos:list", { category }),
    callConvex("query", "videos:unreadCount"),
  ]);
  renderNav({ unreadCount: unread, showSeen: settings, category });

  const grid = document.getElementById("videoGrid");
  if (!grid) return;
  if (!videos.length) {
    grid.innerHTML = `
    <div class="col-span-full py-20 text-center text-slate-600">
      <i class="fa-solid fa-video-slash text-5xl mb-4 opacity-20"></i>
      <p class="text-lg">No videos found. Add some channels to get started!</p>
    </div>`;
  } else {
    grid.innerHTML = videos.map(videoCard).join("");
  }
}

/* ------------------------------- channels page ----------------------------- */

function channelRow(channel) {
  return `
  <div class="motion-card flex items-center justify-between bg-slate-900/90 border border-slate-800 p-4 rounded-lg hover:border-red-500/40 hover:-translate-y-0.5 transition">
    <div class="flex items-center space-x-4">
      <div class="w-10 h-10 rounded-full bg-slate-800 flex items-center justify-center text-slate-500 overflow-hidden">
        ${channel.thumbnail ? `<img src="${esc(channel.thumbnail)}" class="w-full h-full object-cover" alt="">` : `<i class="fa-solid fa-user"></i>`}
      </div>
      <div>
        <div class="text-sm font-medium text-white">${esc(channel.channelName)}</div>
        <div class="text-[10px] text-slate-500 truncate max-w-[200px]">${esc(channel.url)}</div>
      </div>
    </div>
    <button onclick="deleteChannel('${esc(channel.channelId)}')" class="text-slate-500 hover:text-red-400 transition p-2" title="Delete channel">
      <i class="fa-solid fa-trash"></i>
    </button>
  </div>`;
}

window.deleteChannel = async function deleteChannel(channelId) {
  if (!confirm("Remove this channel and all its videos?")) return;
  try {
    await callConvex("mutation", "channels:remove", { channelId });
    await renderChannels({ refreshNav: !document.getElementById("appPopup") || document.getElementById("appPopup").classList.contains("hidden") });
  } catch (err) {
    flash(err.message, "danger");
  }
};

async function renderChannels({ refreshNav = true } = {}) {
  const [channels, settings, unread] = await Promise.all([
    callConvex("query", "channels:list"),
    callConvex("query", "settings:get"),
    callConvex("query", "videos:unreadCount"),
  ]);
  if (refreshNav) renderNav({ unreadCount: unread, showSeen: settings });

  const list = document.getElementById("channelList");
  if (!list) return;
  list.innerHTML = channels.length
    ? channels.map(channelRow).join("")
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
      await renderChannels({ refreshNav: !document.getElementById("appPopup") || document.getElementById("appPopup").classList.contains("hidden") });
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
    container.innerHTML = '<p class="text-slate-600 text-sm">No uploads in this period yet.</p>';
    return;
  }
  container.innerHTML = data.map((stat) => {
    const cells = stat.dailyCounts
      .map((count, i) => {
        const cls = count === 0 ? "bg-slate-800" : count === 1 ? "bg-red-900" : count === 2 ? "bg-red-700" : "bg-red-500";
        return `<div class="w-3 h-3 flex-shrink-0 rounded-none ${cls}" title="${dayLabel(days[i])}: ${count} uploads"></div>`;
      })
      .join("");
    return `
    <div class="mb-6">
      <div class="mb-3">
        <span class="text-slate-300 font-medium text-sm">${esc(stat.name)}</span>
        <span class="text-red-500 font-bold text-xs ml-2">(${stat.total})</span>
      </div>
      <div class="flex gap-1 overflow-x-auto pb-2">
        ${cells}
      </div>
    </div>`;
  }).join("");
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
  renderHeatmap(data.channels, data.days);
}

/* -------------------------------- settings page ---------------------------- */

function initSettingsPage() {
  const form = document.getElementById("settingsForm");
  if (!form) return;
  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const checked = document.getElementById("showSeenToggle").checked;
    const apiKeyInput = document.getElementById("youtubeDataApiKey");
    const clearApiKey = document.getElementById("clearYoutubeDataApiKey").checked;
    const btn = form.querySelector("button[type=submit]");
    btn.disabled = true;
    try {
      await callConvex("mutation", "settings:updateConfig", {
        showSeen: checked,
        youtubeDataApiKey: apiKeyInput.value,
        clearYoutubeDataApiKey: clearApiKey,
      });
      apiKeyInput.value = "";
      document.getElementById("clearYoutubeDataApiKey").checked = false;
      const config = await callConvex("query", "settings:config");
      renderSettingsConfig(config);
      flash("Settings updated!", "success");
    } catch (err) {
      flash(err.message, "danger");
    } finally {
      btn.disabled = false;
    }
  });
}

function renderSettingsConfig(config) {
  const toggle = document.getElementById("showSeenToggle");
  const status = document.getElementById("youtubeApiKeyStatus");
  if (toggle) toggle.checked = config.showSeen;
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

// Close dropdown when clicking outside.
window.addEventListener("click", (event) => {
  if (!event.target.closest("#dropdownButton")) {
    const menu = document.getElementById("dropdownMenu");
    if (menu && !menu.classList.contains("hidden")) menu.classList.add("hidden");
  }
});

window.addEventListener("keydown", (event) => {
  if (event.key === "Escape") closePopup();
});

document.addEventListener("DOMContentLoaded", () => {
  if (PAGE === "channels") initChannelsPage();
  refreshNavAndDispatch();
});
