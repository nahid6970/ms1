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

    const hideShortsSetting = await ctx.db
      .query("settings")
      .withIndex("by_key", (q) => q.eq("key", "hide_shorts"))
      .first();
    const hideShorts = Boolean(hideShortsSetting?.value);

    const rawVideos = await ctx.db
      .query("videos")
      .withIndex("by_published", (q) => q.gte("published", cutoffIso))
      .collect();
    const rawAllVideos = await ctx.db.query("videos").collect();

    const videos = hideShorts ? rawVideos.filter((v) => !isShortVideo(v)) : rawVideos;
    const allVideos = hideShorts ? rawAllVideos.filter((v) => !isShortVideo(v)) : rawAllVideos;

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

    const filteredVideos = rawVideos.length - visiblePeriodVideos.length;

    const todayStr = new Date().toISOString().slice(0, 10);
    const todayQuotaRow = await ctx.db
      .query("apiQuota")
      .withIndex("by_day", (q) => q.eq("day", todayStr))
      .first();

    const allQuotaRows = await ctx.db.query("apiQuota").collect();
    const totalQuotaUnits = allQuotaRows.reduce((acc, row) => acc + (row.units ?? 0), 0);
    const totalQuotaRequests = allQuotaRows.reduce((acc, row) => acc + (row.requests ?? 0), 0);

    const todayQuotaUnits = todayQuotaRow?.units ?? 0;
    const todayQuotaRequests = todayQuotaRow?.requests ?? 0;
    const dailyQuotaLimit = 10000;

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
        filteredVideos,
        filteredChannels,
      },
      quota: {
        todayUnits: todayQuotaUnits,
        todayRequests: todayQuotaRequests,
        todayPercent: Math.min(100, Math.round((todayQuotaUnits / dailyQuotaLimit) * 10000) / 100),
        remainingToday: Math.max(0, dailyQuotaLimit - todayQuotaUnits),
        limit: dailyQuotaLimit,
        totalUnits: totalQuotaUnits,
        totalRequests: totalQuotaRequests,
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

function isShortVideo(video: { title: string; link: string; duration?: string; isShort?: boolean }) {
  if (video.isShort !== undefined) return video.isShort;
  if (video.link.includes("/shorts/")) return true;
  if (/#shorts?\b/i.test(video.title)) return true;
  if (video.duration) {
    const parts = video.duration.split(":").map(Number);
    if (parts.length === 2) {
      const [minutes, seconds] = parts;
      if (minutes === 0 || (minutes === 1 && seconds === 0)) return true;
    }
  }
  return false;
}

