import { v } from "convex/values";
import { internalMutation, internalQuery, mutation, query } from "./_generated/server";

export const list = query({
  args: {
    category: v.union(v.literal("all"), v.literal("unseen"), v.literal("seen"), v.literal("favorites"), v.literal("shorts"), v.literal("watchlater"), v.literal("blocked")),
    subCategory: v.optional(v.union(v.literal("all"), v.literal("unseen"), v.literal("seen"), v.literal("favorites"), v.literal("watchlater"), v.literal("blocked"))),
    folder: v.optional(v.string()),
    channelId: v.optional(v.string()),
    playlistId: v.optional(v.string()),
  },
  handler: async (ctx, { category, subCategory, folder, channelId, playlistId }) => {
    const hideShortsSetting = await ctx.db
      .query("settings")
      .withIndex("by_key", (q) => q.eq("key", "hide_shorts"))
      .first();
    const hideShorts = Boolean(hideShortsSetting?.value);

    const hidePrivateSetting = await ctx.db
      .query("settings")
      .withIndex("by_key", (q) => q.eq("key", "hide_private"))
      .first();
    const hidePrivate = Boolean(hidePrivateSetting?.value);

    const unseenFirstSetting = await ctx.db
      .query("settings")
      .withIndex("by_key", (q) => q.eq("key", "unseen_first"))
      .first();
    const unseenFirst = Boolean(unseenFirstSetting?.value);

    const feedLimitSetting = await ctx.db
      .query("settings")
      .withIndex("by_key", (q) => q.eq("key", "feed_limit"))
      .first();
    const feedLimit = feedLimitSetting ? Number(feedLimitSetting.value) : 50;

    const channels = await ctx.db.query("channels").collect();
    const enabledChannels = channels.filter((channel) => !channel.disabled);
    
    const targetFolder = folder?.trim();
    const isUncategorized = targetFolder?.toLowerCase() === "n/a" || targetFolder?.toLowerCase() === "uncategorized";

    let filteredChannels = targetFolder
      ? isUncategorized
        ? enabledChannels.filter((c) => !c.category || c.category.trim() === "")
        : enabledChannels.filter((c) => (c.category ?? "").trim().toLowerCase() === targetFolder.toLowerCase())
      : enabledChannels;

    if (channelId) {
      filteredChannels = filteredChannels.filter((c) => c.channelId === channelId);
    }

    const enabledChannelIds = new Set(
      filteredChannels.map((channel) => channel.channelId),
    );
    const nameById = new Map(
      enabledChannels.map((c) => [c.channelId, c.channelName]),
    );
    const thumbById = new Map(
      enabledChannels.map((c) => [c.channelId, c.thumbnail ?? null]),
    );
    const filtersById = new Map(
      enabledChannels.map((c) => [c.channelId, c.titleFilters ?? []]),
    );
    const rulesById = new Map(
      enabledChannels.map((c) => [c.channelId, c.rulesText ?? ""]),
    );
    const channelCategoryMap = new Map(
      enabledChannels.map((c) => [c.channelId, c.category ?? ""]),
    );

    let q = ctx.db.query("videos").withIndex("by_published").order("desc");

    const effectiveCategory = category === "shorts" ? (subCategory || "all") : category;

    if (effectiveCategory === "unseen") {
      q = q.filter((f) => f.eq(f.field("isNew"), true));
    } else if (effectiveCategory === "seen") {
      q = q.filter((f) => f.eq(f.field("isNew"), false));
    } else if (effectiveCategory === "favorites") {
      q = q.filter((f) => f.eq(f.field("isFavorite"), true));
    } else if (effectiveCategory === "watchlater") {
      q = q.filter((f) => f.eq(f.field("isWatchLater"), true));
    }

    const isShortsView = category === "shorts";
    const isBlockedView = effectiveCategory === "blocked";
    const isWatchLaterView = effectiveCategory === "watchlater";

    // When filtering by playlist, fetch all videos so none are missed regardless of date.
    // For blocked/watchlater, also fetch all so count matches what's shown.
    const takeAmount = (playlistId || isBlockedView || isWatchLaterView) ? 10000 : (isShortsView || feedLimit === 0 ? 2000 : Math.max(500, feedLimit * 4));
    const videos = await q.take(takeAmount);

    const filtered = videos
      .filter((video) => enabledChannelIds.has(video.channelId))
      .filter((video) => {
        const rulesText = rulesById.get(video.channelId);
        const fallbackFilters = filtersById.get(video.channelId) ?? [];
        if (isBlockedView) {
          return isTitleBlocked(video.title, video, rulesText, fallbackFilters);
        }
        if (isWatchLaterView) {
          return Boolean(video.isWatchLater);
        }
        // A video passes if it comes from an allowed playlist OR its title matches allow-rules.
        // The two systems are independent OR conditions — having both means either is enough.
        const fromAllowedPlaylist = passesPlaylistFilter(video, rulesText, fallbackFilters);
        const titleAllowed = titleMatchesRules(video.title, rulesText, fallbackFilters);
        return !video.isWatchLater && (fromAllowedPlaylist || titleAllowed);
      })
      .filter((video) => {
        // Shorts view: show only shorts.
        // hideShorts only applies to main feeds (all/unseen/seen/favorites) — NOT blocked/watchlater/shorts.
        if (isShortsView) return isShortVideo(video);
        if (isBlockedView || isWatchLaterView) return true;
        return !hideShorts || !isShortVideo(video);
      })
      .filter((video) => !hidePrivate || !isPrivateVideo(video));

    filtered.sort((a, b) => {
      const aPlaylist = matchesPlaylistRule(a.title, rulesById.get(a.channelId)) ? 1 : 0;
      const bPlaylist = matchesPlaylistRule(b.title, rulesById.get(b.channelId)) ? 1 : 0;
      if (aPlaylist !== bPlaylist) return bPlaylist - aPlaylist;

      if (unseenFirst) {
        const aNew = a.isNew ? 1 : 0;
        const bNew = b.isNew ? 1 : 0;
        if (aNew !== bNew) return bNew - aNew;
      }

      return b.published.localeCompare(a.published);
    });

    const finalVideos = (feedLimit === 0 || isBlockedView || isWatchLaterView) ? filtered : filtered.slice(0, feedLimit);

    // Apply playlistId filter after feed limit (playlist view shows all matching videos)
    const outputVideos = playlistId
      ? filtered.filter((v) => v.sourcePlaylistId === playlistId)
      : finalVideos;

    return outputVideos.map((video) => ({
      _id: video._id,
      videoId: video.videoId,
      title: video.title,
      link: video.link,
      duration: video.duration,
      published: video.published,
      isNew: video.isNew,
      isFavorite: video.isFavorite ?? false,
      isWatchLater: video.isWatchLater ?? false,
      isShort: isShortVideo(video),
      isPlaylist: matchesPlaylistRule(video.title, rulesById.get(video.channelId)),
      channelId: video.channelId,
      channelName: nameById.get(video.channelId) ?? "Unknown Channel",
      channelThumbnail: thumbById.get(video.channelId) ?? null,
      channelCategory: channelCategoryMap.get(video.channelId) ?? "",
      sourcePlaylistId: video.sourcePlaylistId ?? null,
      sourcePlaylistTitle: video.sourcePlaylistTitle ?? null,
    }));
  },
});

export const toggleFavorite = mutation({
  args: { id: v.id("videos") },
  handler: async (ctx, { id }) => {
    const video = await ctx.db.get(id);
    if (!video) return;
    await ctx.db.patch(id, { isFavorite: !(video.isFavorite ?? false) });
  },
});

export const toggleWatchLater = mutation({
  args: { id: v.id("videos") },
  handler: async (ctx, { id }) => {
    const video = await ctx.db.get(id);
    if (!video) return;
    await ctx.db.patch(id, { isWatchLater: !(video.isWatchLater ?? false) });
  },
});


export const toggleShort = mutation({
  args: { id: v.id("videos") },
  handler: async (ctx, { id }) => {
    const video = await ctx.db.get(id);
    if (!video) return;
    const currentIsShort = video.isShort ?? isShortVideo(video);
    await ctx.db.patch(id, { isShort: !currentIsShort });
  },
});

export const unreadCount = query({
  args: {
    folder: v.optional(v.string()),
    channelId: v.optional(v.string()),
  },
  handler: async (ctx, { folder, channelId }) => {
    const hideShortsSetting = await ctx.db
      .query("settings")
      .withIndex("by_key", (q) => q.eq("key", "hide_shorts"))
      .first();
    const hideShorts = Boolean(hideShortsSetting?.value);

    const channels = await ctx.db.query("channels").collect();
    const enabledChannels = channels.filter((channel) => !channel.disabled);

    const targetFolder = folder?.trim();
    const isUncategorized =
      targetFolder?.toLowerCase() === "n/a" || targetFolder?.toLowerCase() === "uncategorized";

    let filteredChannels = targetFolder
      ? isUncategorized
        ? enabledChannels.filter((c) => !c.category || c.category.trim() === "")
        : enabledChannels.filter(
            (c) => (c.category ?? "").trim().toLowerCase() === targetFolder.toLowerCase(),
          )
      : enabledChannels;

    if (channelId) {
      filteredChannels = filteredChannels.filter((c) => c.channelId === channelId);
    }

    const enabledChannelIds = new Set(
      filteredChannels.map((channel) => channel.channelId),
    );
    const filtersById = new Map(
      filteredChannels.map((channel) => [channel.channelId, channel.titleFilters ?? []]),
    );
    const rulesById = new Map(
      filteredChannels.map((channel) => [channel.channelId, channel.rulesText ?? ""]),
    );

    const unseen = await ctx.db
      .query("videos")
      .filter((f) => f.eq(f.field("isNew"), true))
      .collect();

    return unseen
      .filter((video) => enabledChannelIds.has(video.channelId))
      .filter((video) => !video.isWatchLater)
      .filter((video) => {
        const rulesText = rulesById.get(video.channelId);
        const fallbackFilters = filtersById.get(video.channelId) ?? [];
        return passesPlaylistFilter(video, rulesText, fallbackFilters) ||
          titleMatchesRules(video.title, rulesText, fallbackFilters);
      })
      .filter((video) => !hideShorts || !isShortVideo(video)).length;
  },
});

export const counts = query({
  args: {
    folder: v.optional(v.string()),
    channelId: v.optional(v.string()),
    playlistId: v.optional(v.string()),
  },
  handler: async (ctx, { folder, channelId, playlistId }) => {
    const hideShortsSetting = await ctx.db
      .query("settings")
      .withIndex("by_key", (q) => q.eq("key", "hide_shorts"))
      .first();
    const hideShorts = Boolean(hideShortsSetting?.value);

    const hidePrivateSettingCounts = await ctx.db
      .query("settings")
      .withIndex("by_key", (q) => q.eq("key", "hide_private"))
      .first();
    const hidePrivate = Boolean(hidePrivateSettingCounts?.value);

    const channels = await ctx.db.query("channels").collect();
    const enabledChannels = channels.filter((channel) => !channel.disabled);

    const targetFolder = folder?.trim();
    const isUncategorized =
      targetFolder?.toLowerCase() === "n/a" || targetFolder?.toLowerCase() === "uncategorized";

    let filteredChannels = targetFolder
      ? isUncategorized
        ? enabledChannels.filter((c) => !c.category || c.category.trim() === "")
        : enabledChannels.filter(
            (c) => (c.category ?? "").trim().toLowerCase() === targetFolder.toLowerCase(),
          )
      : enabledChannels;

    if (channelId) {
      filteredChannels = filteredChannels.filter((c) => c.channelId === channelId);
    }

    const enabledChannelIds = new Set(
      filteredChannels.map((channel) => channel.channelId),
    );
    const filtersById = new Map(
      filteredChannels.map((channel) => [channel.channelId, channel.titleFilters ?? []]),
    );
    const rulesById = new Map(
      filteredChannels.map((channel) => [channel.channelId, channel.rulesText ?? ""]),
    );

    const allVideos = await ctx.db.query("videos").collect();

    // channelVideos = all videos belonging to enabled/filtered channels (optionally filtered by playlist)
    const channelVideos = allVideos
      .filter((video) => enabledChannelIds.has(video.channelId))
      .filter((video) => !playlistId || video.sourcePlaylistId === playlistId);

    // validVideos = those that pass playlist OR title filter (shown in main/shorts/watchlater)
    const validVideos = channelVideos
      .filter((video) => {
        const rulesText = rulesById.get(video.channelId);
        const fallbackFilters = filtersById.get(video.channelId) ?? [];
        return passesPlaylistFilter(video, rulesText, fallbackFilters) ||
          titleMatchesRules(video.title, rulesText, fallbackFilters);
      });

    const main = validVideos.filter(
      (video) => video.isNew && !video.isWatchLater && titleMatchesRules(video.title, rulesById.get(video.channelId), filtersById.get(video.channelId) ?? []) && (!hideShorts || !isShortVideo(video)) && (!hidePrivate || !isPrivateVideo(video)),
    ).length;

    const shorts = validVideos.filter(
      (video) => video.isNew && !video.isWatchLater && titleMatchesRules(video.title, rulesById.get(video.channelId), filtersById.get(video.channelId) ?? []) && isShortVideo(video) && (!hidePrivate || !isPrivateVideo(video)),
    ).length;

    const watchLater = validVideos.filter(
      (video) => video.isWatchLater && titleMatchesRules(video.title, rulesById.get(video.channelId), filtersById.get(video.channelId) ?? []) && (!hidePrivate || !isPrivateVideo(video)),
    ).length;

    // blocked = any channel video that fails either playlist filter or title rules
    const blocked = channelVideos.filter(
      (video) => isTitleBlocked(video.title, video, rulesById.get(video.channelId), filtersById.get(video.channelId) ?? []),
    ).length;

    return { main, shorts, watchLater, blocked };
  },
});


export const toggleRead = mutation({
  args: { id: v.id("videos") },
  handler: async (ctx, { id }) => {
    const video = await ctx.db.get(id);
    if (!video) return;
    await ctx.db.patch(id, { isNew: !video.isNew });
  },
});

export const markAllSeen = mutation({
  args: {
    folder: v.optional(v.string()),
  },
  handler: async (ctx, { folder }) => {
    const channels = await ctx.db.query("channels").collect();
    const enabledChannels = channels.filter((channel) => !channel.disabled);

    const targetFolder = folder?.trim();
    const isUncategorized =
      targetFolder?.toLowerCase() === "n/a" || targetFolder?.toLowerCase() === "uncategorized";

    const filteredChannels = targetFolder
      ? isUncategorized
        ? enabledChannels.filter((c) => !c.category || c.category.trim() === "")
        : enabledChannels.filter(
            (c) => (c.category ?? "").trim().toLowerCase() === targetFolder.toLowerCase(),
          )
      : enabledChannels;

    const enabledChannelIds = new Set(
      filteredChannels.map((channel) => channel.channelId),
    );

    const unseen = await ctx.db
      .query("videos")
      .filter((f) => f.eq(f.field("isNew"), true))
      .collect();

    let marked = 0;
    for (const video of unseen) {
      if (enabledChannelIds.has(video.channelId)) {
        await ctx.db.patch(video._id, { isNew: false });
        marked++;
      }
    }
    return { marked };
  },
});

export const getChannelVideoCount = internalQuery({
  args: { channelId: v.string() },
  handler: async (ctx, { channelId }) => {
    const videos = await ctx.db
      .query("videos")
      .withIndex("by_channelId", (q) => q.eq("channelId", channelId))
      .collect();
    return videos.length;
  },
});


export const missingDurations = internalQuery({
  args: { limit: v.number() },
  handler: async (ctx, { limit }) => {
    const videos = await ctx.db
      .query("videos")
      .withIndex("by_published")
      .order("desc")
      .take(limit);

    return videos
      .filter((video) => !video.duration)
      .map((video) => ({
        _id: video._id,
        videoId: video.videoId,
      }));
  },
});

export const updateDurations = internalMutation({
  args: {
    updates: v.array(
      v.object({
        id: v.id("videos"),
        duration: v.string(),
      }),
    ),
  },
  handler: async (ctx, { updates }) => {
    let updated = 0;
    for (const update of updates) {
      const video = await ctx.db.get(update.id);
      if (!video || video.duration) continue;
      await ctx.db.patch(update.id, { duration: update.duration });
      updated += 1;
    }
    return { updated };
  },
});

/** Insert videos from a channel's feed that we haven't seen yet. */
export const addFromFeed = internalMutation({
  args: {
    channelId: v.string(),
    entries: v.array(
      v.object({
        videoId: v.string(),
        title: v.string(),
        link: v.string(),
        duration: v.optional(v.string()),
        published: v.string(),
      }),
    ),
    skipTitleFilter: v.optional(v.boolean()),
    sourcePlaylistId: v.optional(v.string()),
    sourcePlaylistTitle: v.optional(v.string()),
  },
  handler: async (ctx, { channelId, entries, skipTitleFilter, sourcePlaylistId, sourcePlaylistTitle }) => {
    const channel = await ctx.db
      .query("channels")
      .withIndex("by_channelId", (q) => q.eq("channelId", channelId))
      .first();
    const titleFilters = channel?.titleFilters ?? [];
    let newVideos = 0;
    let durationsUpdated = 0;
    for (const entry of entries) {
      if (!entry.videoId) continue;
      if (!skipTitleFilter && !titleMatchesRules(entry.title, channel?.rulesText, titleFilters)) continue;
      const existing = await ctx.db
        .query("videos")
        .withIndex("by_videoId", (q) => q.eq("videoId", entry.videoId))
        .first();
      if (!existing) {
        await ctx.db.insert("videos", {
          channelId,
          videoId: entry.videoId,
          title: entry.title,
          link: entry.link,
          duration: entry.duration || undefined,
          published: entry.published,
          isNew: true,
          sourcePlaylistId: sourcePlaylistId || undefined,
          sourcePlaylistTitle: sourcePlaylistTitle || undefined,
        });
        newVideos += 1;
      } else {
        const patch: { duration?: string; sourcePlaylistId?: string; sourcePlaylistTitle?: string } = {};
        if (!existing.duration && entry.duration) patch.duration = entry.duration;
        if (sourcePlaylistId && !existing.sourcePlaylistId) patch.sourcePlaylistId = sourcePlaylistId;
        if (sourcePlaylistTitle && !existing.sourcePlaylistTitle) patch.sourcePlaylistTitle = sourcePlaylistTitle;
        if (Object.keys(patch).length > 0) {
          await ctx.db.patch(existing._id, patch);
          if (patch.duration) durationsUpdated += 1;
        }
      }
    }
    return { newVideos, durationsUpdated };
  },
});

import { extractPlaylistId, parseRulesText } from "./youtube";

function extractPlaylistTerms(playlistLine: string): string[] {
  const terms: string[] = [];
  const raw = playlistLine.trim();
  if (!raw) return terms;

  terms.push(raw);

  const clean = raw.replace(/[()]/g, " ").replace(/\s+/g, " ").trim();
  if (clean) terms.push(clean);

  const segments = raw
    .split(/[|/:-]/)
    .map((s) => s.trim())
    .filter(Boolean);

  const fillerRegex = /^(all\s+episodes?|full\s+playlist|official\s+playlist|playlist|all\s+videos?|episodes?)$/i;

  for (const seg of segments) {
    if (seg.length >= 2 && !fillerRegex.test(seg)) {
      terms.push(seg);
    }
  }

  const meaningfulSegs = segments.filter((s) => !fillerRegex.test(s));
  if (meaningfulSegs.length > 1) {
    terms.push(meaningfulSegs.join(" "));
  }

  return terms;
}

function titleMatchesRules(title: string, rawText?: string, fallbackFilters: string[] = []) {
  const rules = parseRulesText(rawText, fallbackFilters);
  const normalizedTitle = title.toLocaleLowerCase();

  // 1. Block-Rules check: reject if title matches any block rule
  const blockMatches = rules.block.filter(Boolean).map((b) => b.toLocaleLowerCase());
  if (blockMatches.some((b) => normalizedTitle.includes(b))) {
    return false;
  }

  // 2. Allow-Rules & Playlist rules check
  const allowTerms = [...rules.allow];

  if (rules.playlists.length > 0) {
    for (const pl of rules.playlists) {
      const cleanPl = pl.trim();
      if (!cleanPl) continue;
      if (extractPlaylistId(cleanPl) !== null) continue;
      const extracted = extractPlaylistTerms(cleanPl);
      allowTerms.push(...extracted);
    }
  }

  const activeAllow = Array.from(new Set(allowTerms.map((a) => a.trim().toLocaleLowerCase()).filter(Boolean)));
  if (activeAllow.length > 0) {
    return activeAllow.some((term) => normalizedTitle.includes(term));
  }

  return true;
}

function matchesPlaylistRule(title: string, rawText?: string): boolean {
  const rules = parseRulesText(rawText);
  if (rules.playlists.length === 0) return false;
  const normalizedTitle = title.toLocaleLowerCase();
  // Only use entries that are NOT a playlist URL — URL-only entries are for direct fetching, not title matching
  const textOnlyMatches = rules.playlists
    .filter(Boolean)
    .filter((p) => extractPlaylistId(p.trim()) === null)
    .map((p) => p.toLocaleLowerCase());
  if (textOnlyMatches.length === 0) return false;
  return textOnlyMatches.some((p) => normalizedTitle.includes(p));
}

function passesPlaylistFilter(
  video: { sourcePlaylistId?: string },
  rulesText?: string,
  fallbackFilters: string[] = [],
): boolean {
  const rules = parseRulesText(rulesText, fallbackFilters);
  const hasPlaylistUrls = rules.playlists.some((p) => extractPlaylistId(p.trim()) !== null);
  
  if (!hasPlaylistUrls) return true; // No playlist URL rules → allow all
  
  // Strict playlist mode: only show videos from allowed playlists
  const allowedPlaylistIds = rules.playlists
    .map((p) => extractPlaylistId(p.trim()))
    .filter((id): id is string => Boolean(id));
  
  if (allowedPlaylistIds.length === 0) return true; // No valid playlist IDs → allow all
  
  if (!video.sourcePlaylistId) return false; // Video has no source playlist → hide
  
  return allowedPlaylistIds.includes(video.sourcePlaylistId); // Check if video's playlist is allowed
}

function isTitleBlocked(
  title: string,
  video: { sourcePlaylistId?: string },
  rawText?: string,
  fallbackFilters: string[] = [],
): boolean {
  // A video is NOT blocked if it passes either the playlist filter OR the title rules
  const fromAllowedPlaylist = passesPlaylistFilter(video, rawText, fallbackFilters);
  if (fromAllowedPlaylist) return false; // Comes from an allowed playlist → not blocked

  const rules = parseRulesText(rawText, fallbackFilters);
  const hasTextRules =
    rules.block.length > 0 ||
    rules.allow.length > 0 ||
    rules.playlists.some((p) => extractPlaylistId(p) === null);
  if (!hasTextRules) {
    // No text rules — only playlist URL rules exist. Video fails playlist filter → blocked.
    const hasPlaylistUrls = rules.playlists.some((p) => extractPlaylistId(p.trim()) !== null);
    return hasPlaylistUrls;
  }
  // Has text rules — blocked if title doesn't match
  return !titleMatchesRules(title, rawText, fallbackFilters);
}


function isShortVideo(video: { title: string; link: string; duration?: string; isShort?: boolean }) {
  if (video.isShort !== undefined) return video.isShort;
  if (video.link.includes("/shorts/")) return true;
  if (/#shorts?\b/i.test(video.title)) return true;
  if (video.duration) {
    const parts = video.duration.split(":").map(Number);
    if (parts.length === 2) {
      const [minutes, seconds] = parts;
      if (minutes === 0 || (minutes === 1 && seconds === 0)) return true;
    }
  }
  return false;
}

function isPrivateVideo(video: { title: string }) {
  return video.title === "Private video" || video.title === "Deleted video";
}

/** Returns all channels that have at least one playlist, with per-playlist video + unseen counts. */
export const listPlaylists = query({
  args: {},
  handler: async (ctx) => {
    const channels = await ctx.db.query("channels").collect();
    const enabledChannels = channels.filter((c) => !c.disabled);

    // Only channels that have playlist URL rules
    const channelsWithPlaylists = enabledChannels.filter((c) => {
      if (!c.rulesText) return false;
      const rules = parseRulesText(c.rulesText);
      return rules.playlists.some((p) => extractPlaylistId(p.trim()) !== null);
    });

    if (channelsWithPlaylists.length === 0) return [];

    const allVideos = await ctx.db.query("videos").collect();

    return channelsWithPlaylists.map((channel) => {
      const rules = parseRulesText(channel.rulesText ?? "");
      const playlistIds = rules.playlists
        .map((p) => extractPlaylistId(p.trim()))
        .filter((id): id is string => Boolean(id));

      // Build title lookup from stored playlistMeta, fall back to scanning videos
      const metaMap = new Map((channel.playlistMeta ?? []).map((m) => [m.id, m.title]));

      const channelVideos = allVideos.filter((v) => v.channelId === channel.channelId);

      const playlists = playlistIds.map((plId) => {
        const plVideos = channelVideos.filter((v) => v.sourcePlaylistId === plId);
        // Use stored meta title first, then video-level title, then raw ID
        const title =
          metaMap.get(plId) ??
          plVideos.find((v) => v.sourcePlaylistTitle)?.sourcePlaylistTitle ??
          plId;
        return {
          playlistId: plId,
          title,
          total: plVideos.length,
          unseen: plVideos.filter((v) => v.isNew && !v.isWatchLater).length,
        };
      }).filter((pl) => pl.total > 0);

      return {
        channelId: channel.channelId,
        channelName: channel.channelName,
        thumbnail: channel.thumbnail ?? null,
        playlists,
        totalUnseen: playlists.reduce((sum, pl) => sum + pl.unseen, 0),
      };
    }).filter((c) => c.playlists.length > 0);
  },
});
