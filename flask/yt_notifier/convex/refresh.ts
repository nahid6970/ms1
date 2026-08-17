import { v } from "convex/values";
import { ConvexError } from "convex/values";
import { action, internalAction, internalMutation, internalQuery } from "./_generated/server";
import { api, internal } from "./_generated/api";
import {
  extractPlaylistId,
  fetchChannelFeedWithApiKey,
  fetchFeedViaApiPaginated,
  fetchPlaylistFeedWithApiKey,
  fetchVideoDurations,
  parseRulesText,
  resolveChannelInfoWithApiKey,
} from "./youtube";

export interface RefreshChannelResult {
  channelId: string;
  channelName: string | null;
  newVideos: number;
  durationsUpdated: number;
}

export interface FetchMoreResult {
  channelId: string;
  channelName: string;
  newVideos: number;
}

export const refreshChannel = action({
  args: { channelId: v.string() },
  handler: async (ctx, { channelId }): Promise<RefreshChannelResult> => {
    const apiKey =
      (await ctx.runQuery(internal.settings.youtubeDataApiKey)) ??
      process.env.YT_DATA_API_KEY ??
      null;
    const feed = await fetchChannelFeedWithApiKey(channelId, apiKey);

    const channel = await ctx.runQuery(internal.channels.getByChannelId, {
      channelId,
    });

    const entries = (feed?.entries ?? []).map((e) => ({
      videoId: e.videoId,
      title: e.title,
      link: e.link,
      duration: e.duration,
      published: e.published ? new Date(e.published).toISOString() : "",
    }));

    const rulesText = channel?.rulesText ?? "";
    const rules = parseRulesText(rulesText);
    const playlistIds = rules.playlists
      .map(extractPlaylistId)
      .filter((id: string | null): id is string => Boolean(id));

    let playlistNewVideos = 0;
    let playlistDurationsUpdated = 0;

    for (const plId of playlistIds) {
      try {
        const plFeed = await fetchPlaylistFeedWithApiKey(plId, apiKey);
        if (plFeed && plFeed.entries.length > 0) {
          // Save playlist videos separately with their sourcePlaylistId so the
          // passesPlaylistFilter check in the feed can show them correctly.
          const plEntries = plFeed.entries.map((e) => ({
            videoId: e.videoId,
            title: e.title,
            link: e.link,
            duration: e.duration,
            published: e.published ? new Date(e.published).toISOString() : "",
          }));
          const plResult = await ctx.runMutation(internal.videos.addFromFeed, {
            channelId,
            entries: plEntries,
            skipTitleFilter: true,
            sourcePlaylistId: plId,
            sourcePlaylistTitle: plFeed.title || undefined,
          });
          // Store playlist title in channel meta for the Playlists panel
          if (plFeed.title) {
            await ctx.runMutation(internal.channels.upsertPlaylistMeta, {
              channelId,
              playlistId: plId,
              title: plFeed.title,
            });
          }
          playlistNewVideos += plResult.newVideos;
          playlistDurationsUpdated += plResult.durationsUpdated;
        }
      } catch (err) {
        console.error(`Failed to fetch playlist ${plId}:`, err);
      }
    }

    if (entries.length === 0 && playlistIds.length > 0) {
      // Only playlist rules — no regular channel feed needed
      return { channelId, channelName: channel?.channelName ?? null, newVideos: playlistNewVideos, durationsUpdated: playlistDurationsUpdated };
    }

    if (entries.length === 0) {
      return { channelId, channelName: channel?.channelName ?? null, newVideos: 0, durationsUpdated: 0 };
    }

    if (channel && !channel.thumbnail) {
      const info = await resolveChannelInfoWithApiKey(channel.url, apiKey);
      if (info.thumbnail) {
        await ctx.runMutation(internal.channels.updateRow, {
          channelId,
          thumbnail: info.thumbnail,
        });
      }
    }

    const channelTitle = feed?.title ?? channel?.channelName ?? "Unknown Channel";

    await ctx.runMutation(internal.channels.updateRow, {
      channelId,
      channelName: channelTitle,
    });

    const result = await ctx.runMutation(internal.videos.addFromFeed, {
      channelId,
      entries,
    });
    if (apiKey) {
      await ctx.runMutation(internal.settings.recordQuotaUsage, { units: 2 });
    }
    return {
      channelId,
      channelName: channelTitle,
      newVideos: result.newVideos + playlistNewVideos,
      durationsUpdated: result.durationsUpdated + playlistDurationsUpdated,
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
      channels.map(async (channel: { channelId: string }) => {
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

export const fetchMoreChannelVideos = action({
  args: { channelId: v.string() },
  handler: async (ctx, { channelId }): Promise<FetchMoreResult> => {
    const apiKey =
      (await ctx.runQuery(internal.settings.youtubeDataApiKey)) ??
      process.env.YT_DATA_API_KEY ??
      null;

    if (!apiKey) {
      throw new ConvexError(
        "A YouTube Data API v3 Key is required in Settings to fetch older past videos.",
      );
    }

    const channel = await ctx.runQuery(internal.channels.getByChannelId, {
      channelId,
    });
    if (!channel) throw new ConvexError("Channel not found.");

    const pageToken = channel.nextPageToken ?? undefined;
    const result = await fetchFeedViaApiPaginated(channelId, apiKey, pageToken);
    if (!result.feed || result.feed.entries.length === 0) {
      return { channelId, channelName: channel.channelName, newVideos: 0 };
    }

    if (result.nextPageToken) {
      await ctx.runMutation(internal.channels.updateNextPageToken, {
        channelId,
        nextPageToken: result.nextPageToken,
      });
    }

    const entries = result.feed.entries.map((e) => ({
      videoId: e.videoId,
      title: e.title,
      link: e.link,
      duration: e.duration,
      published: e.published ? new Date(e.published).toISOString() : "",
    }));

    const addResult: { newVideos: number; durationsUpdated: number } = await ctx.runMutation(internal.videos.addFromFeed, {
      channelId,
      entries,
    });

    await ctx.runMutation(internal.settings.recordQuotaUsage, { units: 2 });

    return {
      channelId,
      channelName: channel.channelName,
      newVideos: addResult.newVideos,
    };
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
        batch.map((video: { videoId: string }) => video.videoId),
        apiKey,
      );
      const updates = batch
        .map((video: { _id: any; videoId: string }) => {
          const duration = durationsById.get(video.videoId);
          return duration ? { id: video._id, duration } : null;
        })
        .filter((update: { id: any; duration: string } | null): update is { id: any; duration: string } => Boolean(update));
      if (updates.length === 0) continue;
      const result = await ctx.runMutation(internal.videos.updateDurations, {
        updates,
      });
      updated += result.updated;
    }

    return { updated, checked: videos.length };
  },
});

/** Load videos from a specific playlist (with an optional item limit) into the feed. */
export const loadPlaylistVideos = action({
  args: {
    channelId: v.string(),
    playlistId: v.string(),
    maxItems: v.optional(v.number()), // 0 = all
  },
  handler: async (ctx, { channelId, playlistId, maxItems }): Promise<{ newVideos: number; channelName: string }> => {
    const apiKey =
      (await ctx.runQuery(internal.settings.youtubeDataApiKey)) ??
      process.env.YT_DATA_API_KEY ??
      null;

    if (!apiKey) {
      throw new ConvexError(
        "A YouTube Data API v3 Key is required in Settings to load playlist videos.",
      );
    }

    const channel = await ctx.runQuery(internal.channels.getByChannelId, { channelId });
    if (!channel) throw new ConvexError("Channel not found.");

    const feed = await fetchPlaylistFeedWithApiKey(playlistId, apiKey, maxItems ?? 0);
    if (!feed || feed.entries.length === 0) {
      return { newVideos: 0, channelName: channel.channelName ?? "Unknown Channel" };
    }

    const entries = feed.entries.map((e) => ({
      videoId: e.videoId,
      title: e.title,
      link: e.link,
      duration: e.duration,
      published: e.published ? new Date(e.published).toISOString() : "",
    }));

    const result: { newVideos: number; durationsUpdated: number } = await ctx.runMutation(
      internal.videos.addFromFeed,
      { channelId, entries, skipTitleFilter: true, sourcePlaylistId: playlistId, sourcePlaylistTitle: feed.title || undefined },
    );

    // Store playlist title in channel meta for the Playlists panel
    if (feed.title) {
      await ctx.runMutation(internal.channels.upsertPlaylistMeta, {
        channelId,
        playlistId,
        title: feed.title,
      });
    }

    await ctx.runMutation(internal.settings.recordQuotaUsage, { units: 2 });

    return {
      newVideos: result.newVideos,
      channelName: channel.channelName ?? "Unknown Channel",
    };
  },
});

/** Cron entry point — crons must call internal functions. */
export const refreshAllCron = internalAction({
  args: {},
  handler: async (ctx): Promise<void> => {
    await ctx.runAction(api.refresh.refreshAll, {});
  },
});
