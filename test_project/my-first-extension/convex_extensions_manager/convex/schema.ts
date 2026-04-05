import { defineSchema, defineTable } from "convex/server";
import { v } from "convex/values";

export default defineSchema({
  backups: defineTable({
    extensionName: v.string(),
    data: v.any(),
    createdAt: v.number(),
    updatedAt: v.number(),
  }).index("by_extensionName", ["extensionName"]),
});
