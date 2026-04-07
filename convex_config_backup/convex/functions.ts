import { mutation, query } from "./_generated/server";
import { v } from "convex/values";

// Save a new backup snapshot (always inserts, never overwrites — keeps history)
export const save = mutation({
  args: {
    scriptName: v.string(),
    label: v.string(),
    data: v.any(),
  },
  handler: async (ctx, args) => {
    const id = await ctx.db.insert("backups", {
      scriptName: args.scriptName,
      label: args.label,
      data: args.data,
      createdAt: Date.now(),
    });
    return { success: true, id };
  },
});

// List all backups for a script (newest first)
export const list = query({
  args: { scriptName: v.string() },
  handler: async (ctx, args) => {
    const rows = await ctx.db
      .query("backups")
      .withIndex("by_scriptName", (q) => q.eq("scriptName", args.scriptName))
      .collect();
    return rows
      .sort((a, b) => b.createdAt - a.createdAt)
      .map((r) => ({ id: r._id, label: r.label, createdAt: r.createdAt }));
  },
});

// Get the full data for a specific backup by ID
export const get = query({
  args: { id: v.id("backups") },
  handler: async (ctx, args) => {
    const row = await ctx.db.get(args.id);
    return row ? row.data : null;
  },
});

// Delete a specific backup
export const remove = mutation({
  args: { id: v.id("backups") },
  handler: async (ctx, args) => {
    await ctx.db.delete(args.id);
    return { success: true };
  },
});
