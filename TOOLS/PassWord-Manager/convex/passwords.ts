import { query, mutation } from "./_generated/server";
import { v } from "convex/values";

export const list = query({
  args: {},
  handler: async (ctx) => {
    return await ctx.db.query("vault").collect();
  },
});

export const getCanary = query({
  args: {},
  handler: async (ctx) => {
    return await ctx.db.query("vault").filter(q => q.eq(q.field("domain"), "SYSTEM_CANARY")).first();
  },
});

export const add = mutation({
  args: {
    domain: v.string(),
    salt: v.string(),
    iv: v.string(),
    u: v.string(),
    p: v.string(),
    fields: v.string(),
  },
  handler: async (ctx, args) => {
    return await ctx.db.insert("vault", {
      ...args,
      createdAt: Date.now(),
    });
  },
});

export const update = mutation({
  args: {
    id: v.id("vault"),
    domain: v.string(),
    salt: v.string(),
    iv: v.string(),
    u: v.string(),
    p: v.string(),
    fields: v.string(),
  },
  handler: async (ctx, args) => {
    const { id, ...rest } = args;
    await ctx.db.patch(id, rest);
  },
});

export const remove = mutation({
  args: { id: v.id("vault") },
  handler: async (ctx, args) => {
    await ctx.db.delete(args.id);
  },
});
