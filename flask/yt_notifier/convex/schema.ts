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
    rulesText: v.optional(v.string()),
    category: v.optional(v.string()),
    folderOnly: v.optional(v.boolean()),
    shortsThresholdSeconds: v.optional(v.number()),
    nextPageToken: v.optional(v.string()),
    // Map of playlistId → title for display in the Playlists panel
    playlistMeta: v.optional(v.array(v.object({ id: v.string(), title: v.string() }))),
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
    isFavorite: v.optional(v.boolean()),
    isWatchLater: v.optional(v.boolean()),
    isLong: v.optional(v.boolean()),
    isShort: v.optional(v.boolean()),
    sourcePlaylistId: v.optional(v.string()), // Playlist ID if loaded from a specific playlist
    sourcePlaylistTitle: v.optional(v.string()), // Playlist title for display
  })
    .index("by_channelId", ["channelId"])
    .index("by_channelId_published", ["channelId", "published"])
    .index("by_videoId", ["videoId"])
    .index("by_published", ["published"])
    .index("by_isNew", ["isNew", "published"])
    .index("by_isWatchLater", ["isWatchLater", "published"])
    .index("by_isLong", ["isLong", "published"]),

  settings: defineTable({
    key: v.string(),
    value: v.any(),
  }).index("by_key", ["key"]),

  apiQuota: defineTable({
    day: v.string(),
    units: v.number(),
    requests: v.number(),
  }).index("by_day", ["day"]),
});
