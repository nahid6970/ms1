import { v } from "convex/values";
import { internalQuery, mutation, query } from "./_generated/server";

const SHOW_SEEN_KEY = "show_seen";
const HIDE_SHORTS_KEY = "hide_shorts";
const FEED_LIMIT_KEY = "feed_limit";
const YOUTUBE_DATA_API_KEY = "youtube_data_api_key";

async function getSetting(ctx: { db: any }, key: string) {
  return await ctx.db
    .query("settings")
    .withIndex("by_key", (q: any) => q.eq("key", key))
    .first();
}

async function upsertSetting(ctx: { db: any }, key: string, value: unknown) {
  const row = await getSetting(ctx, key);
  if (row) {
    await ctx.db.patch(row._id, { value });
  } else {
    await ctx.db.insert("settings", { key, value });
  }
}

export const get = query({
  args: {},
  handler: async (ctx) => {
    const row = await getSetting(ctx, SHOW_SEEN_KEY);
    return row ? (row.value as boolean) : false;
  },
});

export const config = query({
  args: {},
  handler: async (ctx) => {
    const showSeenRow = await getSetting(ctx, SHOW_SEEN_KEY);
    const hideShortsRow = await getSetting(ctx, HIDE_SHORTS_KEY);
    const feedLimitRow = await getSetting(ctx, FEED_LIMIT_KEY);
    const apiKeyRow = await getSetting(ctx, YOUTUBE_DATA_API_KEY);
    const apiKey =
      typeof apiKeyRow?.value === "string" ? apiKeyRow.value.trim() : "";
    return {
      showSeen: showSeenRow ? (showSeenRow.value as boolean) : false,
      hideShorts: hideShortsRow ? (hideShortsRow.value as boolean) : false,
      feedLimit: feedLimitRow ? Number(feedLimitRow.value) : 50,
      hasYoutubeDataApiKey: apiKey.length > 0,
    };
  },
});

export const updateShowSeen = mutation({
  args: { showSeen: v.boolean() },
  handler: async (ctx, { showSeen }) => {
    await upsertSetting(ctx, SHOW_SEEN_KEY, showSeen);
  },
});

export const updateConfig = mutation({
  args: {
    showSeen: v.boolean(),
    hideShorts: v.optional(v.boolean()),
    feedLimit: v.optional(v.number()),
    youtubeDataApiKey: v.optional(v.string()),
    clearYoutubeDataApiKey: v.optional(v.boolean()),
  },
  handler: async (ctx, { showSeen, hideShorts, feedLimit, youtubeDataApiKey, clearYoutubeDataApiKey }) => {
    await upsertSetting(ctx, SHOW_SEEN_KEY, showSeen);
    if (hideShorts !== undefined) {
      await upsertSetting(ctx, HIDE_SHORTS_KEY, hideShorts);
    }
    if (feedLimit !== undefined && feedLimit >= 0 && feedLimit <= 5000) {
      await upsertSetting(ctx, FEED_LIMIT_KEY, feedLimit);
    }

    if (clearYoutubeDataApiKey) {
      await upsertSetting(ctx, YOUTUBE_DATA_API_KEY, "");
      return;
    }

    const trimmedKey = youtubeDataApiKey?.trim();
    if (trimmedKey) {
      await upsertSetting(ctx, YOUTUBE_DATA_API_KEY, trimmedKey);
    }
  },
});

export const youtubeDataApiKey = internalQuery({
  args: {},
  handler: async (ctx) => {
    const row = await getSetting(ctx, YOUTUBE_DATA_API_KEY);
    return typeof row?.value === "string" && row.value.trim()
      ? row.value.trim()
      : null;
  },
});

export const recordQuotaUsage = internalMutation({
  args: {
    units: v.number(),
  },
  handler: async (ctx, { units }) => {
    const today = new Date().toISOString().slice(0, 10);
    const existing = await ctx.db
      .query("apiQuota")
      .withIndex("by_day", (q) => q.eq("key", today))
      .first();
    if (existing) {
      await ctx.db.patch(existing._id, {
        units: existing.units + units,
        requests: existing.requests + 1,
      });
    } else {
      await ctx.db.insert("apiQuota", {
        day: today,
        units,
        requests: 1,
      });
    }
  },
});

