import { action } from "./_generated/server";
import { v } from "convex/values";

/**
 * Fetch a URL and extract the best possible favicon or social image.
 * This runs on the server to bypass CORS restrictions.
 */
export const getFavicon = action({
  args: { url: v.string() },
  handler: async (ctx, args) => {
    const { url } = args;
    try {
      // Use a browser-like User-Agent to avoid being blocked
      const response = await fetch(url, {
        headers: {
          "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
          "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
          "Accept-Language": "en-US,en;q=0.9",
        },
      });

      if (!response.ok) {
        console.error(`Failed to fetch ${url}: ${response.status} ${response.statusText}`);
        return null;
      }

      const html = await response.text();

      // Priority 1: Open Graph Image (usually best for profiles/pages)
      const ogImageMatch = html.match(/<meta\s+(?:property|name)=["']og:image["']\s+content=["']([^"']+)["']/i) ||
                           html.match(/<meta\s+content=["']([^"']+)["']\s+(?:property|name)=["']og:image["']/i);
      
      if (ogImageMatch && ogImageMatch[1]) {
        let iconUrl = ogImageMatch[1];
        // Decode HTML entities (basic)
        iconUrl = iconUrl.replace(/&amp;/g, '&');
        return iconUrl;
      }

      // Priority 2: Twitter Image
      const twitterImageMatch = html.match(/<meta\s+(?:property|name)=["']twitter:image["']\s+content=["']([^"']+)["']/i) ||
                                 html.match(/<meta\s+content=["']([^"']+)["']\s+(?:property|name)=["']twitter:image["']/i);
      if (twitterImageMatch && twitterImageMatch[1]) {
        return twitterImageMatch[1].replace(/&amp;/g, '&');
      }

      // Priority 3: Specific YouTube Avatar Logic (if needed)
      if (url.includes('youtube.com/@') || url.includes('youtube.com/channel/') || url.includes('youtube.com/c/')) {
         // YouTube channel pages usually have the avatar in og:image, 
         // but sometimes it's buried in JSON. og:image is usually sufficient.
      }

      // Priority 4: Standard Favicon
      const faviconMatch = html.match(/<link\s+rel=["'](?:shortcut )?icon["']\s+href=["']([^"']+)["']/i) ||
                           html.match(/<link\s+href=["']([^"']+)["']\s+rel=["'](?:shortcut )?icon["']/i) ||
                           html.match(/<link\s+rel=["']apple-touch-icon["']\s+href=["']([^"']+)["']/i);
      
      if (faviconMatch && faviconMatch[1]) {
        let iconUrl = faviconMatch[1].replace(/&amp;/g, '&');
        const urlObj = new URL(url);

        if (iconUrl.startsWith("//")) {
          return "https:" + iconUrl;
        } else if (iconUrl.startsWith("/")) {
          return urlObj.origin + iconUrl;
        } else if (!iconUrl.startsWith("http")) {
          return urlObj.origin + "/" + iconUrl;
        }
        return iconUrl;
      }

      return null;
    } catch (e) {
      console.error("Error fetching favicon:", e);
      return null;
    }
  },
});
