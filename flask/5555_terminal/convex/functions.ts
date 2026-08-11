import { query, mutation } from "./_generated/server";
import { v } from "convex/values";

// List history (latest first)
export const list = query({
  args: {},
  handler: async (ctx) => {
    return await ctx.db
      .query("history")
      .order("desc")
      .take(100);
  },
});

// Add to history
export const add = mutation({
  args: { command: v.string() },
  handler: async (ctx, args) => {
    const { command } = args;
    if (!command.trim()) return;

    // Check if it already exists to avoid duplicates
    const existing = await ctx.db
      .query("history")
      .filter((q) => q.eq(q.field("command"), command))
      .first();

    if (existing) {
      // If it exists, delete and re-insert to move it to the top of the "creation" order
      await ctx.db.delete(existing._id);
    }

    // Insert new entry (or re-insert existing one)
    return await ctx.db.insert("history", {
      command: command,
    });
  },
});

// Delete from history
export const remove = mutation({
  args: { command: v.string() },
  handler: async (ctx, args) => {
    const existing = await ctx.db
      .query("history")
      .filter((q) => q.eq(q.field("command"), args.command))
      .first();
    
    if (existing) {
      await ctx.db.delete(existing._id);
      return true;
    }
    return false;
  },
});

// Search history
export const search = query({
  args: { term: v.string() },
  handler: async (ctx, args) => {
    const { term } = args;
    if (!term) {
      return await ctx.db.query("history").order("desc").collect();
    }
    
    // Filter by term
    return await ctx.db
      .query("history")
      .filter((q) => q.contains(q.field("command"), term))
      .order("desc")
      .collect();
  },
});
