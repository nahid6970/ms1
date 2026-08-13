import { v } from "convex/values";
import { action, internalAction, internalMutation, internalQuery } from "./_generated/server";
import { api, internal } from "./_generated/api";
import { fetchChannelFeed, resolveChannelInfo } from "./youtube";

export interface RefreshChannelResult {
  channelId: string;
  channelName: string | null;
  newVideos: number;
}

export const refreshChannel = action({
  args: { channelId: v.string() },
  handler: async (ctx, { channelId }): Promise<RefreshChannelResult> => {
    const feed = await fetchChannelFeed(channelId);
    if (!feed || feed.entries.length === 0) {
      return { channelId, channelName: null, newVideos: 0 };
    }

    const entries = feed.entries.map((e) => ({
      videoId: e.videoId,
      title: e.title,
      link: e.link,
      published: e.published ? new Date(e.published).toISOString() : "",
    }));

    const channel = await ctx.runQuery(internal.channels.getByChannelId, {
      channelId,
    });

    // Backfill the channel thumbnail if it was missing at add time.
    if (channel && !channel.thumbnail) {
      const info = await resolveChannelInfo(channel.url);
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
    return { channelId, channelName: feed.title, newVideos: result.newVideos };
  },
});

export const refreshAll = action({
  args: {},
  handler: async (ctx): Promise<{ totalNew: number }> => {
    const channels = await ctx.runQuery(internal.channels.listRows);
    let totalNew = 0;
    for (const channel of channels) {
      try {
        const result = await ctx.runAction(api.refresh.refreshChannel, {
          channelId: channel.channelId,
        });
        totalNew += result.newVideos;
      } catch (err) {
        console.error(`Failed to refresh channel ${channel.channelId}:`, err);
      }
    }
    return { totalNew };
  },
});

/** Cron entry point — crons must call internal functions. */
export const refreshAllCron = internalAction({
  args: {},
  handler: async (ctx): Promise<void> => {
    await ctx.runAction(api.refresh.refreshAll, {});
  },
});
