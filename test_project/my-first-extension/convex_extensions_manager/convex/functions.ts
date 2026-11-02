import { mutation, query } from "./_generated/server";
import { v } from "convex/values";
import type { Id } from "./_generated/dataModel";

export const generateUploadUrl = mutation({
  args: {},
  handler: async (ctx) => await ctx.storage.generateUploadUrl(),
});

export const getAttachmentUrl = query({
  args: { storageId: v.id("_storage") },
  handler: async (ctx, args) => await ctx.storage.getUrl(args.storageId),
});

function attachmentStorageIds(data: any): Set<string> {
  const ids = new Set<string>();
  for (const tab of data?.savedTabs ?? []) {
    for (const attachment of tab.attachments ?? []) {
      if (typeof attachment?.storageId === "string") ids.add(attachment.storageId);
    }
  }
  return ids;
}

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
      if (extensionName === "tab_saver") {
        const retainedIds = attachmentStorageIds(data);
        for (const storageId of attachmentStorageIds(existing.data)) {
          if (!retainedIds.has(storageId)) {
            await ctx.storage.delete(storageId as Id<"_storage">);
          }
        }
      }
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
