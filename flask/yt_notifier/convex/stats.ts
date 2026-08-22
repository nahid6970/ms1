import { v } from "convex/values";
import { query } from "./_generated/server";
import { extractPlaylistId, parseRulesText } from "./youtube";

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
      .take(1000);

    const rawAllVideos = await ctx.db
      .query("videos")
      .withIndex("by_published")
      .order("desc")
      .take(1500);

    const channels = await ctx.db.query("channels").collect();
    const enabledChannels = channels.filter((channel) => !channel.disabled);
    const shortsThresholdById = new Map(
      enabledChannels.map((channel) => [channel.channelId, channel.shortsThresholdSeconds ?? 60]),
    );
    const videos = hideShorts
      ? rawVideos.filter((v) => !isShortVideo(v, shortsThresholdById.get(v.channelId) ?? 60))
      : rawVideos;
    const allVideos = hideShorts
      ? rawAllVideos.filter((v) => !isShortVideo(v, shortsThresholdById.get(v.channelId) ?? 60))
      : rawAllVideos;
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
    const rulesById = new Map(
      enabledChannels.map((c) => [c.channelId, c.rulesText ?? ""]),
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
      if (!titleMatchesRules(video.title, rulesById.get(video.channelId), filtersById.get(video.channelId) ?? [])) {
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
    result.sort((a, b) => b.total - a.total);

    const visibleVideos = allVideos.filter(
      (video) =>
        enabledChannelIds.has(video.channelId) &&
        titleMatchesRules(video.title, rulesById.get(video.channelId), filtersById.get(video.channelId) ?? []),
    );
    const visiblePeriodVideos = videos.filter(
      (video) =>
        enabledChannelIds.has(video.channelId) &&
        titleMatchesRules(video.title, rulesById.get(video.channelId), filtersById.get(video.channelId) ?? []),
    );

    const unseenVisible = visiblePeriodVideos.filter((video) => video.isNew).length;
    const filteredVideos = rawVideos.length - visiblePeriodVideos.length;
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

    const totalVideosInDb = rawAllVideos.length;
    const unseenVideosInDb = rawAllVideos.filter((v) => v.isNew).length;
    const seenVideosInDb = totalVideosInDb - unseenVideosInDb;
    const favoriteVideosInDb = rawAllVideos.filter((v) => v.isFavorite).length;

    const estimatedDbBytes = totalVideosInDb * 1200 + channels.length * 800;
    const estimatedDbMb = Math.round((estimatedDbBytes / (1024 * 1024)) * 100) / 100;

    const todayStr = new Date().toISOString().slice(0, 10);
    const allQuotaRows = await ctx.db.query("apiQuota").collect();
    const todayQuotaRows = allQuotaRows.filter((row) => row.day === todayStr);

    const totalQuotaUnits = allQuotaRows.reduce((acc, row) => acc + (row.units ?? 0), 0);
    const totalQuotaRequests = allQuotaRows.reduce((acc, row) => acc + (row.requests ?? 0), 0);

    const todayQuotaUnits = todayQuotaRows.reduce((acc, row) => acc + (row.units ?? 0), 0);
    const todayQuotaRequests = todayQuotaRows.reduce((acc, row) => acc + (row.requests ?? 0), 0);
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
      convexDb: {
        totalVideosInDb,
        unseenVideosInDb,
        seenVideosInDb,
        favoriteVideosInDb,
        totalChannels: channels.length,
        enabledChannels: enabledChannels.length,
        estimatedDbMb,
        freeTierMbLimit: 1000,
        percentStorageUsed: Math.min(100, Math.round((estimatedDbMb / 1000) * 10000) / 100),
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

function extractPlaylistTerms(playlistLine: string): string[] {
  const terms: string[] = [];
  const raw = playlistLine.trim();
  if (!raw) return terms;

  terms.push(raw);

  const clean = raw.replace(/[()]/g, " ").replace(/\s+/g, " ").trim();
  if (clean) terms.push(clean);

  const segments = raw
    .split(/[|/:-]/)
    .map((s) => s.trim())
    .filter(Boolean);

  const fillerRegex = /^(all\s+episodes?|full\s+playlist|official\s+playlist|playlist|all\s+videos?|episodes?)$/i;

  for (const seg of segments) {
    if (seg.length >= 2 && !fillerRegex.test(seg)) {
      terms.push(seg);
    }
  }

  const meaningfulSegs = segments.filter((s) => !fillerRegex.test(s));
  if (meaningfulSegs.length > 1) {
    terms.push(meaningfulSegs.join(" "));
  }

  return terms;
}

function titleMatchesRules(title: string, rawText?: string, fallbackFilters: string[] = []) {
  const rules = parseRulesText(rawText, fallbackFilters);
  const normalizedTitle = title.toLocaleLowerCase();

  const blockMatches = rules.block.filter(Boolean).map((b) => b.toLocaleLowerCase());
  if (blockMatches.some((b) => normalizedTitle.includes(b))) {
    return false;
  }

  const allowTerms = [...rules.allow];

  if (rules.playlists.length > 0) {
    for (const pl of rules.playlists) {
      const cleanPl = pl.trim();
      if (!cleanPl) continue;
      if (extractPlaylistId(cleanPl) !== null) continue;
      const extracted = extractPlaylistTerms(cleanPl);
      allowTerms.push(...extracted);
    }
  }

  const activeAllow = Array.from(new Set(allowTerms.map((a) => a.trim().toLocaleLowerCase()).filter(Boolean)));
  if (activeAllow.length > 0) {
    return activeAllow.some((term) => normalizedTitle.includes(term));
  }

  return true;
}

function isShortVideo(video: { title: string; link: string; duration?: string; isShort?: boolean }, thresholdSeconds = 60) {
  if (video.isShort !== undefined) return video.isShort;
  if (video.link.includes("/shorts/")) return true;
  if (/#shorts?\b/i.test(video.title)) return true;
  if (video.duration) {
    const parts = video.duration.split(":").map(Number);
    if (parts.every(Number.isFinite) && parts.length >= 2) {
      const totalSeconds = parts.reduce((total, part) => total * 60 + part, 0);
      if (totalSeconds <= thresholdSeconds) return true;
    }
  }
  return false;
}
