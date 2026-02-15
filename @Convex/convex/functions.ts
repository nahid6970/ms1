import { query, mutation } from "./_generated/server";
import { v } from "convex/values";

// List all links
export const listLinks = query({
  args: {},
  handler: async (ctx) => {
    return await ctx.db.query("links").collect();
  },
});

// Add a new link
export const addLink = mutation({
  args: { 
    title: v.string(), 
    url: v.string(), 
    group: v.string(),
    description: v.optional(v.string())
  },
  handler: async (ctx, args) => {
    await ctx.db.insert("links", { 
      title: args.title, 
      url: args.url, 
      group: args.group,
      description: args.description || ""
    });
  },
});

// Remove a link
export const removeLink = mutation({
  args: { id: v.id("links") },
  handler: async (ctx, args) => {
    await ctx.db.delete(args.id);
  },
});
