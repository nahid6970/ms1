import { v } from "convex/values";
import { internalMutation, mutation, query } from "./_generated/server";

export const list = query({
  args: {
    category: v.union(v.literal("all"), v.literal("unseen"), v.literal("seen")),
  },
  handler: async (ctx, { category }) => {
    const channels = await ctx.db.query("channels").collect();
    const nameById = new Map(channels.map((c) => [c.channelId, c.channelName]));
    const thumbById = new Map(
      channels.map((c) => [c.channelId, c.thumbnail ?? null]),
    );

    let q = ctx.db.query("videos").withIndex("by_published").order("desc");
    if (category === "unseen") {
      q = q.filter((f) => f.eq(f.field("isNew"), true));
    } else if (category === "seen") {
      q = q.filter((f) => f.eq(f.field("isNew"), false));
    }
    const videos = await q.take(30);

    return videos.map((video) => ({
      _id: video._id,
      videoId: video.videoId,
      title: video.title,
      link: video.link,
      published: video.published,
      isNew: video.isNew,
      channelId: video.channelId,
      channelName: nameById.get(video.channelId) ?? "Unknown Channel",
      channelThumbnail: thumbById.get(video.channelId) ?? null,
    }));
  },
});

export const unreadCount = query({
  args: {},
  handler: async (ctx) => {
    const unseen = await ctx.db
      .query("videos")
      .filter((f) => f.eq(f.field("isNew"), true))
      .collect();
    return unseen.length;
  },
});

export const toggleRead = mutation({
  args: { id: v.id("videos") },
  handler: async (ctx, { id }) => {
    const video = await ctx.db.get(id);
    if (!video) return;
    await ctx.db.patch(id, { isNew: !video.isNew });
  },
});

/** Insert videos from a channel's feed that we haven't seen yet. */
export const addFromFeed = internalMutation({
  args: {
    channelId: v.string(),
    entries: v.array(
      v.object({
        videoId: v.string(),
        title: v.string(),
        link: v.string(),
        published: v.string(),
      }),
    ),
  },
  handler: async (ctx, { channelId, entries }) => {
    let newVideos = 0;
    for (const entry of entries) {
      if (!entry.videoId) continue;
      const existing = await ctx.db
        .query("videos")
        .withIndex("by_videoId", (q) => q.eq("videoId", entry.videoId))
        .first();
      if (!existing) {
        await ctx.db.insert("videos", {
          channelId,
          videoId: entry.videoId,
          title: entry.title,
          link: entry.link,
          published: entry.published,
          isNew: true,
        });
        newVideos += 1;
      }
    }
    return { newVideos };
  },
});
