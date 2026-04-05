import { mutation, query } from "./_generated/server";
import { v } from "convex/values";

/**
 * Save data for a specific extension.
 * If data for the extension already exists, it will be updated.
 */
export const save = mutation({
  args: { 
    extensionName: v.string(), 
    data: v.any() // Using any to handle different storage structures
  },
  handler: async (ctx, args) => {
    const { extensionName, data } = args;
    
    // Look for existing data for this extension using index
    const existing = await ctx.db
      .query("backups")
      .withIndex("by_extensionName", (q) => q.eq("extensionName", extensionName))
      .first();

    if (existing) {
      await ctx.db.patch(existing._id, { 
        data: data,
        updatedAt: Date.now()
      });
      return { success: true, action: "updated", id: existing._id };
    } else {
      const id = await ctx.db.insert("backups", {
        extensionName: extensionName,
        data: data,
        createdAt: Date.now(),
        updatedAt: Date.now()
      });
      return { success: true, action: "created", id: id };
    }
  },
});

/**
 * Retrieve data for a specific extension.
 */
export const get = query({
  args: { extensionName: v.string() },
  handler: async (ctx, args) => {
    const { extensionName } = args;
    const backup = await ctx.db
      .query("backups")
      .withIndex("by_extensionName", (q) => q.eq("extensionName", extensionName))
      .first();
    
    return backup ? backup.data : null;
  },
});
