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

function renderNav({ unreadCount = 0, showSeen = false, category = "all" } = {}) {
  const el = document.getElementById("navbar");
  if (!el) return;
  el.innerHTML = `
  <nav class="bg-slate-900/80 backdrop-blur-md border-b border-slate-800 sticky top-0 z-50">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex justify-between h-16">
        <div class="flex items-center space-x-3">
          <a href="index.html" class="flex items-center space-x-2 text-red-500 font-bold text-xl tracking-tight">
            <i class="fa-brands fa-youtube text-3xl animate-pulse"></i>
            <span class="bg-gradient-to-r from-red-500 to-amber-500 bg-clip-text text-transparent">YT Notifier</span>
          </a>
        </div>
        <div class="flex items-center space-x-4">
          <a href="index.html" class="px-3 py-2 rounded-lg text-sm font-medium transition hover:bg-slate-800 ${PAGE === "feed" ? "bg-slate-800 text-red-400" : "text-slate-300"}">
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
          <a href="${l.href}" class="px-3 py-2 rounded-none text-sm font-medium transition hover:bg-slate-800 ${PAGE === l.page ? "bg-slate-800 text-red-400" : "text-slate-300"}">
            <i class="fa-solid ${l.icon} mr-1.5"></i> ${l.label}
          </a>`).join("")}
          <button id="refreshButton" onclick="checkUpdates()" class="bg-gradient-to-r from-red-600 to-rose-600 hover:from-red-500 hover:to-rose-500 text-white px-4 py-2 rounded-none text-sm font-semibold shadow-lg shadow-red-900/30 transition transform active:scale-95 flex items-center space-x-1.5">
            <i class="fa-solid fa-rotate"></i>
            <span>Check Updates</span>
          </button>
        </div>
      </div>
    </div>
  </nav>`;
}

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
    const res = await callConvex("action", "refresh:refreshAll");
    flash(`Refreshed all channels! Found ${res.totalNew} new video(s).`, "success");
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
  <div class="group bg-slate-900 border border-slate-800 rounded-none overflow-hidden hover:border-red-500/50 transition-all duration-300 hover:shadow-2xl hover:shadow-red-900/10 ${isNew ? "ring-1 ring-red-500/30" : "opacity-60 grayscale-[0.5]"}">
    <a href="${esc(video.link)}" target="_blank" class="block relative aspect-video bg-slate-950 overflow-hidden">
      <img src="https://img.youtube.com/vi/${esc(video.videoId)}/mqdefault.jpg" alt="${esc(video.title)}" class="w-full h-full object-cover group-hover:scale-105 transition duration-500" loading="lazy">
      <div class="absolute inset-0 bg-black/20 group-hover:bg-transparent transition"></div>
      ${isNew ? `<div class="absolute bottom-2 right-2 bg-red-600 backdrop-blur px-2 py-1 rounded text-[10px] font-bold text-white">NEW</div>` : ""}
    </a>
    <div class="p-5 flex flex-col flex-grow">
      <div class="flex items-center space-x-2 mb-2">
        ${video.channelThumbnail ? `<img src="${esc(video.channelThumbnail)}" class="w-6 h-6 rounded-full" alt="">` : ""}
        <div class="text-[10px] uppercase tracking-wider text-red-500 font-bold">${esc(video.channelName)}</div>
      </div>
      <h3 class="text-base font-semibold text-slate-100 leading-snug mb-auto line-clamp-2 group-hover:text-red-400 transition h-12">${esc(video.title)}</h3>
      <div class="flex items-center justify-between text-slate-500 text-xs mt-4">
        <span>${isoDate(video.published)}</span>
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
  </div>`;
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
  <div class="flex items-center justify-between bg-slate-900 border border-slate-800 p-4 rounded-none hover:border-slate-700 transition">
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
    await renderChannels();
  } catch (err) {
    flash(err.message, "danger");
  }
};

async function renderChannels() {
  const [channels, settings, unread] = await Promise.all([
    callConvex("query", "channels:list"),
    callConvex("query", "settings:get"),
    callConvex("query", "videos:unreadCount"),
  ]);
  renderNav({ unreadCount: unread, showSeen: settings });

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
      await renderChannels();
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

async function renderStats() {
  const urlParams = new URLSearchParams(location.search);
  const period = urlParams.get("period") === "week" ? "week" : "month";

  // Highlight the active period toggle
  document.querySelectorAll('a[href^="?period="]').forEach((a) => {
    const active = a.getAttribute("href").includes(`period=${period}`);
    a.className = `px-4 py-1 text-xs rounded-md transition capitalize ${active ? "bg-red-600 text-white" : "text-slate-400 hover:text-white"}`;
  });

  const [data, settings, unread] = await Promise.all([
    callConvex("query", "stats:heatmap", { period }),
    callConvex("query", "settings:get"),
    callConvex("query", "videos:unreadCount"),
  ]);
  renderNav({ unreadCount: unread, showSeen: settings });
  renderHeatmap(data.channels, data.days);
}

/* -------------------------------- settings page ---------------------------- */

function initSettingsPage() {
  const form = document.getElementById("settingsForm");
  if (!form) return;
  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const checked = document.getElementById("showSeenToggle").checked;
    const btn = form.querySelector("button[type=submit]");
    btn.disabled = true;
    try {
      await callConvex("mutation", "settings:updateShowSeen", { showSeen: checked });
      flash("Settings updated!", "success");
    } catch (err) {
      flash(err.message, "danger");
    } finally {
      btn.disabled = false;
    }
  });
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
      const [settings, unread] = await Promise.all([
        callConvex("query", "settings:get"),
        callConvex("query", "videos:unreadCount"),
      ]);
      renderNav({ unreadCount: unread, showSeen: settings });
      document.getElementById("showSeenToggle").checked = settings;
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

document.addEventListener("DOMContentLoaded", () => {
  if (PAGE === "channels") initChannelsPage();
  refreshNavAndDispatch();
});
