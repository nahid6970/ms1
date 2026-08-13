import { v } from "convex/values";
import { query } from "./_generated/server";

function toDayStr(d: Date): string {
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, "0");
  const day = String(d.getDate()).padStart(2, "0");
  return `${y}-${m}-${day}`;
}

export const heatmap = query({
  args: {
    period: v.union(v.literal("week"), v.literal("month")),
  },
  handler: async (ctx, { period }) => {
    const days = period === "week" ? 7 : 30;
    const cutoff = new Date();
    cutoff.setDate(cutoff.getDate() - days);
    const cutoffIso = cutoff.toISOString();

    const videos = await ctx.db
      .query("videos")
      .withIndex("by_published", (q) => q.gte("published", cutoffIso))
      .collect();
    const allVideos = await ctx.db.query("videos").collect();
    const channels = await ctx.db.query("channels").collect();
    const enabledChannels = channels.filter((channel) => !channel.disabled);
    const enabledChannelIds = new Set(
      enabledChannels.map((channel) => channel.channelId),
    );
    const nameById = new Map(
      enabledChannels.map((c) => [c.channelId, c.channelName]),
    );
    const thumbById = new Map(
      enabledChannels.map((c) => [c.channelId, c.thumbnail ?? null]),
    );
    const filtersById = new Map(
      enabledChannels.map((c) => [c.channelId, c.titleFilters ?? []]),
    );

    const dayStrs: string[] = [];
    for (let i = 0; i < days; i++) {
      const d = new Date();
      d.setDate(d.getDate() - (days - 1 - i));
      dayStrs.push(toDayStr(d));
    }

    const counts = new Map<string, Map<string, number>>();
    for (const video of videos) {
      if (!enabledChannelIds.has(video.channelId)) continue;
      if (!titleMatchesFilters(video.title, filtersById.get(video.channelId) ?? [])) {
        continue;
      }
      const date = new Date(video.published);
      if (isNaN(date.getTime())) continue;
      const day = toDayStr(date);
      if (!counts.has(video.channelId)) counts.set(video.channelId, new Map());
      const byDay = counts.get(video.channelId)!;
      byDay.set(day, (byDay.get(day) ?? 0) + 1);
    }

    const result = [];
    for (const [channelId, byDay] of counts) {
      const dailyCounts = dayStrs.map((day) => byDay.get(day) ?? 0);
      result.push({
        channelId,
        name: nameById.get(channelId) ?? "Unknown Channel",
        dailyCounts,
        total: dailyCounts.reduce((a, b) => a + b, 0),
      });
    }
    // Most active first
    result.sort((a, b) => b.total - a.total);

    const visibleVideos = allVideos.filter(
      (video) =>
        enabledChannelIds.has(video.channelId) &&
        titleMatchesFilters(video.title, filtersById.get(video.channelId) ?? []),
    );
    const visiblePeriodVideos = videos.filter(
      (video) =>
        enabledChannelIds.has(video.channelId) &&
        titleMatchesFilters(video.title, filtersById.get(video.channelId) ?? []),
    );
    const unseenVisible = visibleVideos.filter((video) => video.isNew).length;
    const hiddenByFilters = allVideos.filter((video) => {
      if (!enabledChannelIds.has(video.channelId)) return false;
      return !titleMatchesFilters(video.title, filtersById.get(video.channelId) ?? []);
    }).length;
    const filteredChannels = enabledChannels.filter(
      (channel) => (channel.titleFilters ?? []).length > 0,
    ).length;

    const channelSummaries = enabledChannels.map((channel) => {
      const channelVideos = visibleVideos.filter(
        (video) => video.channelId === channel.channelId,
      );
      const periodVideos = visiblePeriodVideos.filter(
        (video) => video.channelId === channel.channelId,
      );
      const lastVideo = channelVideos
        .slice()
        .sort((a, b) => b.published.localeCompare(a.published))[0];
      return {
        channelId: channel.channelId,
        name: channel.channelName,
        thumbnail: thumbById.get(channel.channelId),
        periodCount: periodVideos.length,
        unseenCount: channelVideos.filter((video) => video.isNew).length,
        totalShown: channelVideos.length,
        filterCount: (channel.titleFilters ?? []).length,
        lastUpload: lastVideo?.published ?? null,
      };
    });
    channelSummaries.sort((a, b) => {
      if (b.periodCount !== a.periodCount) return b.periodCount - a.periodCount;
      return String(b.lastUpload ?? "").localeCompare(String(a.lastUpload ?? ""));
    });

    return {
      days: dayStrs,
      channels: result,
      summary: {
        period,
        activeChannels: result.length,
        enabledChannels: enabledChannels.length,
        disabledChannels: channels.length - enabledChannels.length,
        uploadsInPeriod: visiblePeriodVideos.length,
        unseenVisible,
        hiddenByFilters,
        filteredChannels,
      },
      channelSummaries,
    };
  },
});

function titleMatchesFilters(title: string, filters: string[]) {
  const activeFilters = filters
    .map((filter) => filter.trim().toLocaleLowerCase())
    .filter(Boolean);
  if (activeFilters.length === 0) return true;
  const normalizedTitle = title.toLocaleLowerCase();
  return activeFilters.some((filter) => normalizedTitle.includes(filter));
}
