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
    const channels = await ctx.db.query("channels").collect();
    const nameById = new Map(channels.map((c) => [c.channelId, c.channelName]));

    const dayStrs: string[] = [];
    for (let i = 0; i < days; i++) {
      const d = new Date();
      d.setDate(d.getDate() - (days - 1 - i));
      dayStrs.push(toDayStr(d));
    }

    const counts = new Map<string, Map<string, number>>();
    for (const video of videos) {
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

    return { days: dayStrs, channels: result };
  },
});
