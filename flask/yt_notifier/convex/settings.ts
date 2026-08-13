import { v } from "convex/values";
import { internalQuery, mutation, query } from "./_generated/server";

const SHOW_SEEN_KEY = "show_seen";
const HIDE_SHORTS_KEY = "hide_shorts";
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
    const apiKeyRow = await getSetting(ctx, YOUTUBE_DATA_API_KEY);
    const apiKey =
      typeof apiKeyRow?.value === "string" ? apiKeyRow.value.trim() : "";
    return {
      showSeen: showSeenRow ? (showSeenRow.value as boolean) : false,
      hideShorts: hideShortsRow ? (hideShortsRow.value as boolean) : false,
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
    youtubeDataApiKey: v.optional(v.string()),
    clearYoutubeDataApiKey: v.optional(v.boolean()),
  },
  handler: async (ctx, { showSeen, hideShorts, youtubeDataApiKey, clearYoutubeDataApiKey }) => {
    await upsertSetting(ctx, SHOW_SEEN_KEY, showSeen);
    if (hideShorts !== undefined) {
      await upsertSetting(ctx, HIDE_SHORTS_KEY, hideShorts);
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
