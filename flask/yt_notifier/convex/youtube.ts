import { XMLParser } from "fast-xml-parser";

const USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64)";

export interface ChannelInfo {
  channelId: string | null;
  thumbnail: string | null;
  title: string | null;
}

export interface FeedEntry {
  videoId: string;
  title: string;
  link: string;
  duration?: string;
  published: string;
}

export interface ChannelFeed {
  title: string;
  entries: FeedEntry[];
}

export function normalizeUrl(input: string): string {
  let url = input.trim();
  if (!url.startsWith("http")) {
    url = url.startsWith("@")
      ? `https://www.youtube.com/${url}`
      : `https://www.youtube.com/@${url}`;
  }
  return url;
}

/**
 * Resolve a channel URL/handle to a channel ID, thumbnail, and title.
 *
 * Primary: YouTube Data API v3 (requires the YT_DATA_API_KEY env var).
 * Fallback: scrape the channel page (no key needed).
 */
export async function resolveChannelInfo(input: string): Promise<ChannelInfo> {
  return resolveChannelInfoWithApiKey(input, process.env.YT_DATA_API_KEY ?? null);
}

export async function resolveChannelInfoWithApiKey(
  input: string,
  apiKey: string | null,
): Promise<ChannelInfo> {
  const url = normalizeUrl(input);

  if (apiKey) {
    const lookup = await resolveViaApi(url, apiKey);
    if (lookup.channelId) return lookup;
  }
  return resolveViaScrape(url);
}

/**
 * Fetch a channel's recent videos (title + entries with published dates).
 *
 * Primary: YouTube Data API v3 uploads playlist (needs YT_DATA_API_KEY).
 * Fallback: the legacy RSS feed (currently returning 404 from YouTube as of
 * late 2025 / 2026, but kept in case it returns).
 */
export async function fetchChannelFeed(channelId: string): Promise<ChannelFeed | null> {
  return fetchChannelFeedWithApiKey(channelId, process.env.YT_DATA_API_KEY ?? null);
}

export async function fetchChannelFeedWithApiKey(
  channelId: string,
  apiKey: string | null,
): Promise<ChannelFeed | null> {
  if (apiKey) {
    const viaApi = await fetchFeedViaApi(channelId, apiKey);
    if (viaApi) return viaApi;
  }

  // Fallback: legacy RSS feed
  const url = `https://www.youtube.com/feeds/videos.xml?channel_id=${channelId}`;
  const res = await fetch(url, { headers: { "User-Agent": USER_AGENT } });
  if (!res.ok) return null;
  const xml = await res.text();
  return parseFeed(xml);
}

/* ------------------------------ Data API v3 ------------------------------- */

async function resolveViaApi(url: string, apiKey: string): Promise<ChannelInfo> {
  try {
    let query = "";
    const channelMatch = url.match(/\/channel\/(UC[A-Za-z0-9_-]{20,})/);
    const handleMatch = url.match(/\/@([^/?#]+)/);
    const userMatch = url.match(/\/user\/([^/?#]+)/);
    if (channelMatch) query = `id=${channelMatch[1]}`;
    else if (handleMatch) query = `forHandle=${encodeURIComponent(handleMatch[1])}`;
    else if (userMatch) query = `forUsername=${encodeURIComponent(userMatch[1])}`;
    else return { channelId: null, thumbnail: null, title: null };

    const res = await fetch(
      `https://www.googleapis.com/youtube/v3/channels?part=snippet&${query}&key=${apiKey}`,
    );
    if (!res.ok) return { channelId: null, thumbnail: null, title: null };
    const data = (await res.json()) as {
      items?: Array<{
        id?: string;
        snippet?: {
          title?: string;
          thumbnails?: { high?: { url?: string }; medium?: { url?: string }; default?: { url?: string } };
        };
      }>;
    };
    const item = data.items?.[0];
    if (!item?.id) return { channelId: null, thumbnail: null, title: null };
    const thumbs = item.snippet?.thumbnails;
    return {
      channelId: item.id,
      thumbnail: thumbs?.high?.url ?? thumbs?.medium?.url ?? thumbs?.default?.url ?? null,
      title: item.snippet?.title ?? null,
    };
  } catch (err) {
    console.error("YouTube Data API resolve error:", err);
    return { channelId: null, thumbnail: null, title: null };
  }
}

async function fetchFeedViaApi(channelId: string, apiKey: string): Promise<ChannelFeed | null> {
  try {
    // The uploads playlist for a channel is "UU" + channel ID without "UC".
    const playlistId = channelId.startsWith("UC")
      ? "UU" + channelId.slice(2)
      : channelId;
    const url =
      `https://www.googleapis.com/youtube/v3/playlistItems` +
      `?part=snippet&playlistId=${playlistId}&maxResults=15&key=${apiKey}`;
    const res = await fetch(url);
    if (!res.ok) {
      console.error(
        `YouTube Data API playlistItems error (${res.status}) for ${channelId}:`,
        (await res.text()).slice(0, 300),
      );
      return null;
    }
    const data = (await res.json()) as {
      items?: Array<{
        snippet?: {
          title?: string;
          channelTitle?: string;
          publishedAt?: string;
          resourceId?: { videoId?: string };
        };
      }>;
    };
    const items = data.items ?? [];
    const durationsById = await fetchVideoDurations(
      items
        .map((item) => item.snippet?.resourceId?.videoId)
        .filter((id): id is string => Boolean(id)),
      apiKey,
    );
    const entries: FeedEntry[] = items.map((item) => {
      const s = item.snippet ?? {};
      const videoId = s.resourceId?.videoId ?? "";
      return {
        videoId,
        title: s.title ?? "",
        link: `https://www.youtube.com/watch?v=${videoId}`,
        duration: durationsById.get(videoId),
        published: s.publishedAt ?? "",
      };
    });
    return {
      title: items[0]?.snippet?.channelTitle ?? "Unknown Channel",
      entries,
    };
  } catch (err) {
    console.error("YouTube Data API feed error:", err);
    return null;
  }
}

export async function fetchVideoDurations(
  videoIds: string[],
  apiKey: string,
): Promise<Map<string, string>> {
  const durations = new Map<string, string>();
  if (videoIds.length === 0) return durations;

  try {
    const res = await fetch(
      `https://www.googleapis.com/youtube/v3/videos` +
        `?part=contentDetails&id=${videoIds.join(",")}&key=${apiKey}`,
    );
    if (!res.ok) {
      console.error(
        `YouTube Data API videos error (${res.status}):`,
        (await res.text()).slice(0, 300),
      );
      return durations;
    }
    const data = (await res.json()) as {
      items?: Array<{
        id?: string;
        contentDetails?: { duration?: string };
      }>;
    };
    for (const item of data.items ?? []) {
      if (!item.id || !item.contentDetails?.duration) continue;
      durations.set(item.id, formatIsoDuration(item.contentDetails.duration));
    }
  } catch (err) {
    console.error("YouTube Data API duration error:", err);
  }

  return durations;
}

function formatIsoDuration(value: string): string {
  const match = value.match(/^PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?$/);
  if (!match) return "";
  const hours = Number(match[1] ?? 0);
  const minutes = Number(match[2] ?? 0);
  const seconds = Number(match[3] ?? 0);
  if (hours > 0) {
    return `${hours}:${String(minutes).padStart(2, "0")}:${String(seconds).padStart(2, "0")}`;
  }
  return `${minutes}:${String(seconds).padStart(2, "0")}`;
}

/* ------------------------------- Scraping -------------------------------- */

async function resolveViaScrape(url: string): Promise<ChannelInfo> {
  try {
    const res = await fetch(url, {
      headers: { "User-Agent": USER_AGENT },
      redirect: "follow",
    });
    if (!res.ok) return { channelId: null, thumbnail: null, title: null };
    const html = await res.text();

    let channelId: string | null = null;
    // Most reliable: canonical link on channel pages
    const canonical = html.match(/<link rel="canonical" href="[^"]*\/channel\/(UC[A-Za-z0-9_-]{20,})"/);
    if (canonical) channelId = canonical[1];
    // Fallback: meta tag
    if (!channelId) {
      const metaMatch = html.match(/<meta itemprop="identifier" content="(UC[A-Za-z0-9_-]{20,})"/);
      if (metaMatch) channelId = metaMatch[1];
    }
    // Fallback: channelId inside ytInitialData JSON
    if (!channelId) {
      const jsonMatch = html.match(/"channelId":"(UC[A-Za-z0-9_-]{20,})"/);
      if (jsonMatch) channelId = jsonMatch[1];
    }
    // Fallback: RSS alternate link with channel_id param
    if (!channelId) {
      const rssMatch = html.match(/channel_id=(UC[A-Za-z0-9_-]{20,})/);
      if (rssMatch) channelId = rssMatch[1];
    }

    const thumbnail =
      html.match(/<meta property="og:image" content="([^"]+)"/)?.[1] ?? null;
    const title =
      html.match(/<meta property="og:title" content="([^"]*)"/)?.[1] ?? null;

    return { channelId, thumbnail, title };
  } catch (err) {
    console.error("Channel page scrape error:", err);
    return { channelId: null, thumbnail: null, title: null };
  }
}

function parseFeed(xml: string): ChannelFeed | null {
  const parser = new XMLParser({
    ignoreAttributes: false,
    attributeNamePrefix: "@_",
    parseTagValue: false,
    isArray: (name: string) => name === "entry",
  });
  const doc = parser.parse(xml) as {
    feed?: { title?: string; entry?: unknown[] };
  };
  const feed = doc?.feed;
  if (!feed) return null;

  const rawEntries = Array.isArray(feed.entry) ? feed.entry : feed.entry ? [feed.entry] : [];
  const entries: FeedEntry[] = rawEntries
    .filter((e): e is Record<string, unknown> => !!e && typeof e === "object")
    .map((e) => {
      const link = e.link as unknown;
      const href =
        typeof link === "string"
          ? link
          : (link as { "@_href"?: string } | { "@_href"?: string }[] | undefined)
            ? Array.isArray(link)
              ? (link[0] as { "@_href"?: string } | undefined)?.["@_href"]
              : (link as { "@_href"?: string })["@_href"]
            : null;
      return {
        videoId: String(e["yt:videoId"] ?? ""),
        title: String(e.title ?? ""),
        link: href ?? "",
        published: String(e.published ?? ""),
      };
    });

  const title =
    typeof feed.title === "string" ? feed.title : "Unknown Channel";
  return { title, entries };
}
