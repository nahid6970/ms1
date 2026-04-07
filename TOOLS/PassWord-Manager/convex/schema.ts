import { defineSchema, defineTable } from "convex/server";
import { v } from "convex/values";

export default defineSchema({
  vault: defineTable({
    domain: v.string(),     // Unencrypted for grouping/searching
    salt: v.string(),       // Base64 salt for key derivation
    iv: v.string(),         // Base64 IV for AES-GCM
    u: v.string(),          // Encrypted username
    p: v.string(),          // Encrypted password
    fields: v.string(),     // Encrypted JSON string of extra fields
    createdAt: v.number(),  // Timestamp
  }).index("by_domain", ["domain"]),
});
