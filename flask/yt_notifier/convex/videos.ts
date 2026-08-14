import { v } from "convex/values";
import { internalMutation, internalQuery, mutation, query } from "./_generated/server";

export const list = query({
  args: {
    category: v.union(v.literal("all"), v.literal("unseen"), v.literal("seen"), v.literal("favorites")),
    folder: v.optional(v.string()),
  },
  handler: async (ctx, { category, folder }) => {
    const hideShortsSetting = await ctx.db
      .query("settings")
      .withIndex("by_key", (q) => q.eq("key", "hide_shorts"))
      .first();
    const hideShorts = Boolean(hideShortsSetting?.value);

    const channels = await ctx.db.query("channels").collect();
    const enabledChannels = channels.filter((channel) => !channel.disabled);
    
    const targetFolder = folder?.trim();
    const isUncategorized = targetFolder?.toLowerCase() === "n/a" || targetFolder?.toLowerCase() === "uncategorized";

    const filteredChannels = targetFolder
      ? isUncategorized
        ? enabledChannels.filter((c) => !c.category || c.category.trim() === "")
        : enabledChannels.filter((c) => (c.category ?? "").trim().toLowerCase() === targetFolder.toLowerCase())
      : enabledChannels;

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
    const channelCategoryMap = new Map(
      enabledChannels.map((c) => [c.channelId, c.category ?? ""]),
    );

    let q = ctx.db.query("videos").withIndex("by_published").order("desc");
    if (category === "unseen") {
      q = q.filter((f) => f.eq(f.field("isNew"), true));
    } else if (category === "seen") {
      q = q.filter((f) => f.eq(f.field("isNew"), false));
    } else if (category === "favorites") {
      q = q.filter((f) => f.eq(f.field("isFavorite"), true));
    }
    const videos = await q.take(300);

    return videos
      .filter((video) => enabledChannelIds.has(video.channelId))
      .filter((video) =>
        titleMatchesFilters(video.title, filtersById.get(video.channelId) ?? []),
      )
      .filter((video) => !hideShorts || !isShortVideo(video))
      .slice(0, 50)
      .map((video) => ({
        _id: video._id,
        videoId: video.videoId,
        title: video.title,
        link: video.link,
        duration: video.duration,
        published: video.published,
        isNew: video.isNew,
        isFavorite: video.isFavorite ?? false,
        isShort: isShortVideo(video),
        channelId: video.channelId,
        channelName: nameById.get(video.channelId) ?? "Unknown Channel",
        channelThumbnail: thumbById.get(video.channelId) ?? null,
        channelCategory: channelCategoryMap.get(video.channelId) ?? "",
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

export const unreadCount = query({
  args: {
    folder: v.optional(v.string()),
  },
  handler: async (ctx, { folder }) => {
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
    const filtersById = new Map(
      filteredChannels.map((channel) => [channel.channelId, channel.titleFilters ?? []]),
    );

    const unseen = await ctx.db
      .query("videos")
      .filter((f) => f.eq(f.field("isNew"), true))
      .collect();

    return unseen
      .filter((video) => enabledChannelIds.has(video.channelId))
      .filter((video) =>
        titleMatchesFilters(video.title, filtersById.get(video.channelId) ?? []),
      )
      .filter((video) => !hideShorts || !isShortVideo(video)).length;
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
  },
  handler: async (ctx, { channelId, entries }) => {
    const channel = await ctx.db
      .query("channels")
      .withIndex("by_channelId", (q) => q.eq("channelId", channelId))
      .first();
    const titleFilters = channel?.titleFilters ?? [];
    let newVideos = 0;
    let durationsUpdated = 0;
    for (const entry of entries) {
      if (!entry.videoId) continue;
      if (!titleMatchesFilters(entry.title, titleFilters)) continue;
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
        });
        newVideos += 1;
      } else if (!existing.duration && entry.duration) {
        await ctx.db.patch(existing._id, { duration: entry.duration });
        durationsUpdated += 1;
      }
    }
    return { newVideos, durationsUpdated };
  },
});

function titleMatchesFilters(title: string, filters: string[]) {
  const activeFilters = filters
    .map((filter) => filter.trim().toLocaleLowerCase())
    .filter(Boolean);
  if (activeFilters.length === 0) return true;
  const normalizedTitle = title.toLocaleLowerCase();
  return activeFilters.some((filter) => normalizedTitle.includes(filter));
}

function isShortVideo(video: { title: string; link: string; duration?: string }) {
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
