import { v } from "convex/values";
import { action, internalAction, internalMutation, internalQuery } from "./_generated/server";
import { api, internal } from "./_generated/api";
import {
  fetchChannelFeedWithApiKey,
  fetchVideoDurations,
  resolveChannelInfoWithApiKey,
} from "./youtube";

export interface RefreshChannelResult {
  channelId: string;
  channelName: string | null;
  newVideos: number;
  durationsUpdated: number;
}

export const refreshChannel = action({
  args: { channelId: v.string() },
  handler: async (ctx, { channelId }): Promise<RefreshChannelResult> => {
    const apiKey =
      (await ctx.runQuery(internal.settings.youtubeDataApiKey)) ??
      process.env.YT_DATA_API_KEY ??
      null;
    const feed = await fetchChannelFeedWithApiKey(channelId, apiKey);
    if (!feed || feed.entries.length === 0) {
      return { channelId, channelName: null, newVideos: 0, durationsUpdated: 0 };
    }

    const entries = feed.entries.map((e) => ({
      videoId: e.videoId,
      title: e.title,
      link: e.link,
      duration: e.duration,
      published: e.published ? new Date(e.published).toISOString() : "",
    }));

    const channel = await ctx.runQuery(internal.channels.getByChannelId, {
      channelId,
    });

    // Backfill the channel thumbnail if it was missing at add time.
    if (channel && !channel.thumbnail) {
      const info = await resolveChannelInfoWithApiKey(channel.url, apiKey);
      if (info.thumbnail) {
        await ctx.runMutation(internal.channels.updateRow, {
          channelId,
          thumbnail: info.thumbnail,
        });
      }
    }

    await ctx.runMutation(internal.channels.updateRow, {
      channelId,
      channelName: feed.title,
    });

    const result = await ctx.runMutation(internal.videos.addFromFeed, {
      channelId,
      entries,
    });
    return {
      channelId,
      channelName: feed.title,
      newVideos: result.newVideos,
      durationsUpdated: result.durationsUpdated,
    };
  },
});

export const refreshAll = action({
  args: {},
  handler: async (ctx): Promise<{ totalNew: number; durationsUpdated: number }> => {
    const channels = await ctx.runQuery(internal.channels.listRows);
    let totalNew = 0;
    let durationsUpdated = 0;
    const results = await Promise.all(
      channels.map(async (channel) => {
        try {
          return await ctx.runAction(api.refresh.refreshChannel, {
            channelId: channel.channelId,
          });
        } catch (err) {
          console.error(`Failed to refresh channel ${channel.channelId}:`, err);
          return { channelId: channel.channelId, channelName: null, newVideos: 0, durationsUpdated: 0 };
        }
      }),
    );
    for (const result of results) {
      totalNew += result.newVideos;
      durationsUpdated += result.durationsUpdated;
    }
    return { totalNew, durationsUpdated };
  },
});

export const backfillDurations = action({
  args: { limit: v.optional(v.number()) },
  handler: async (ctx, { limit }): Promise<{ updated: number; checked: number; reason?: string }> => {
    const apiKey =
      (await ctx.runQuery(internal.settings.youtubeDataApiKey)) ??
      process.env.YT_DATA_API_KEY;
    if (!apiKey) {
      return {
        updated: 0,
        checked: 0,
        reason: "YT_DATA_API_KEY is not set in this Convex deployment.",
      };
    }

    const videos = await ctx.runQuery(internal.videos.missingDurations, {
      limit: limit ?? 50,
    });
    if (videos.length === 0) return { updated: 0, checked: 0 };

    let updated = 0;
    for (let i = 0; i < videos.length; i += 50) {
      const batch = videos.slice(i, i + 50);
      const durationsById = await fetchVideoDurations(
        batch.map((video) => video.videoId),
        apiKey,
      );
      const updates = batch
        .map((video) => {
          const duration = durationsById.get(video.videoId);
          return duration ? { id: video._id, duration } : null;
        })
        .filter((update): update is { id: typeof batch[number]["_id"]; duration: string } => Boolean(update));
      if (updates.length === 0) continue;
      const result = await ctx.runMutation(internal.videos.updateDurations, {
        updates,
      });
      updated += result.updated;
    }

    return { updated, checked: videos.length };
  },
});

/** Cron entry point — crons must call internal functions. */
export const refreshAllCron = internalAction({
  args: {},
  handler: async (ctx): Promise<void> => {
    await ctx.runAction(api.refresh.refreshAll, {});
  },
});
