import { query, mutation } from "./_generated/server";
import { v } from "convex/values";

export const get = query({
  args: {},
  handler: async (ctx) => {
    const counter = await ctx.db.query("counters").first();
    return counter?.value ?? 0;
  },
});

export const increment = mutation({
  args: {},
  handler: async (ctx) => {
    const counter = await ctx.db.query("counters").first();
    if (counter) {
      await ctx.db.patch(counter._id, { value: counter.value + 1 });
    } else {
      await ctx.db.insert("counters", { value: 1 });
    }
  },
});
