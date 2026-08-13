import { v } from "convex/values";
import { mutation, query } from "./_generated/server";

const SHOW_SEEN_KEY = "show_seen";

export const get = query({
  args: {},
  handler: async (ctx) => {
    const row = await ctx.db
      .query("settings")
      .withIndex("by_key", (q) => q.eq("key", SHOW_SEEN_KEY))
      .first();
    return row ? (row.value as boolean) : false;
  },
});

export const updateShowSeen = mutation({
  args: { showSeen: v.boolean() },
  handler: async (ctx, { showSeen }) => {
    const row = await ctx.db
      .query("settings")
      .withIndex("by_key", (q) => q.eq("key", SHOW_SEEN_KEY))
      .first();
    if (row) {
      await ctx.db.patch(row._id, { value: showSeen });
    } else {
      await ctx.db.insert("settings", { key: SHOW_SEEN_KEY, value: showSeen });
    }
  },
});
