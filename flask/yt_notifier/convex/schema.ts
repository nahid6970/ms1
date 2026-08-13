import { defineSchema, defineTable } from "convex/server";
import { v } from "convex/values";

export default defineSchema({
  channels: defineTable({
    url: v.string(),
    channelName: v.string(),
    channelId: v.string(),
    thumbnail: v.optional(v.string()),
    disabled: v.optional(v.boolean()),
    titleFilters: v.optional(v.array(v.string())),
  })
    .index("by_channelId", ["channelId"])
    .index("by_url", ["url"]),

  videos: defineTable({
    channelId: v.string(),
    videoId: v.string(),
    title: v.string(),
    link: v.string(),
    duration: v.optional(v.string()),
    // ISO-8601 UTC string so lexicographic ordering is chronological
    published: v.string(),
    isNew: v.boolean(),
  })
    .index("by_channelId", ["channelId"])
    .index("by_videoId", ["videoId"])
    .index("by_published", ["published"]),

  settings: defineTable({
    key: v.string(),
    value: v.any(),
  }).index("by_key", ["key"]),
});
