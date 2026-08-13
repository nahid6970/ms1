import { v } from "convex/values";
import { ConvexError } from "convex/values";
import { action, internalMutation, internalQuery, mutation, query } from "./_generated/server";
import { api, internal } from "./_generated/api";
import { normalizeUrl, resolveChannelInfoWithApiKey } from "./youtube";
import type { RefreshChannelResult } from "./refresh";

export const list = query({
  args: {},
  handler: async (ctx) => {
    const channels = await ctx.db.query("channels").collect();
    return channels.map((channel) => ({
      ...channel,
      disabled: channel.disabled ?? false,
      titleFilters: channel.titleFilters ?? [],
    }));
  },
});

export const getByChannelId = internalQuery({
  args: { channelId: v.string() },
  handler: async (ctx, { channelId }) => {
    return await ctx.db
      .query("channels")
      .withIndex("by_channelId", (q) => q.eq("channelId", channelId))
      .first();
  },
});

export const listRows = internalQuery({
  args: {},
  handler: async (ctx) => {
    const channels = await ctx.db.query("channels").collect();
    return channels.filter((channel) => !channel.disabled);
  },
});

export const insertRow = internalMutation({
  args: {
    url: v.string(),
    channelName: v.string(),
    channelId: v.string(),
    thumbnail: v.optional(v.string()),
  },
  handler: async (ctx, { url, channelName, channelId, thumbnail }) => {
    return await ctx.db.insert("channels", {
      url,
      channelName,
      channelId,
      thumbnail,
      disabled: false,
      titleFilters: [],
    });
  },
});

export const updateRow = internalMutation({
  args: {
    channelId: v.string(),
    channelName: v.optional(v.string()),
    thumbnail: v.optional(v.string()),
  },
  handler: async (ctx, { channelId, channelName, thumbnail }) => {
    const row = await ctx.db
      .query("channels")
      .withIndex("by_channelId", (q) => q.eq("channelId", channelId))
      .first();
    if (!row) return;
    const patch: { channelName?: string; thumbnail?: string } = {};
    if (channelName !== undefined) patch.channelName = channelName;
    if (thumbnail !== undefined) patch.thumbnail = thumbnail;
    if (Object.keys(patch).length > 0) await ctx.db.patch(row._id, patch);
  },
});

/**
 * Resolve the channel from the given URL, insert it, and pull its latest
 * videos. Runs as an action because it makes external network requests.
 */
export const add = action({
  args: { url: v.string() },
  handler: async (ctx, { url }): Promise<RefreshChannelResult> => {
    const apiKey =
      (await ctx.runQuery(internal.settings.youtubeDataApiKey)) ??
      process.env.YT_DATA_API_KEY ??
      null;
    const info = await resolveChannelInfoWithApiKey(url, apiKey);
    if (!info.channelId) {
      throw new ConvexError(
        "Could not resolve YouTube Channel ID. Please check the URL.",
      );
    }

    const existing = await ctx.runQuery(internal.channels.getByChannelId, {
      channelId: info.channelId,
    });
    if (existing) {
      throw new ConvexError("Channel already exists in your list.");
    }

    await ctx.runMutation(internal.channels.insertRow, {
      url: normalizeUrl(url),
      channelName: info.title ?? "Fetching...",
      channelId: info.channelId,
      thumbnail: info.thumbnail ?? undefined,
    });

    return await ctx.runAction(api.refresh.refreshChannel, {
      channelId: info.channelId,
    });
  },
});

export const remove = mutation({
  args: { channelId: v.string() },
  handler: async (ctx, { channelId }) => {
    const channel = await ctx.db
      .query("channels")
      .withIndex("by_channelId", (q) => q.eq("channelId", channelId))
      .first();
    if (!channel) return;

    await ctx.db.delete(channel._id);
    const videos = await ctx.db
      .query("videos")
      .withIndex("by_channelId", (q) => q.eq("channelId", channelId))
      .collect();
    for (const video of videos) {
      await ctx.db.delete(video._id);
    }
  },
});

export const toggleDisabled = mutation({
  args: { channelId: v.string() },
  handler: async (ctx, { channelId }) => {
    const channel = await ctx.db
      .query("channels")
      .withIndex("by_channelId", (q) => q.eq("channelId", channelId))
      .first();
    if (!channel) return;
    await ctx.db.patch(channel._id, { disabled: !(channel.disabled ?? false) });
  },
});

export const updateTitleFilters = mutation({
  args: {
    channelId: v.string(),
    filters: v.array(v.string()),
  },
  handler: async (ctx, { channelId, filters }) => {
    const channel = await ctx.db
      .query("channels")
      .withIndex("by_channelId", (q) => q.eq("channelId", channelId))
      .first();
    if (!channel) return;
    const normalized = Array.from(
      new Set(
        filters
          .map((filter) => filter.trim())
          .filter(Boolean)
          .map((filter) => filter.slice(0, 120)),
      ),
    );
    await ctx.db.patch(channel._id, { titleFilters: normalized });
  },
});
