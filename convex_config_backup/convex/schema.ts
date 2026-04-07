import { defineSchema, defineTable } from "convex/server";
import { v } from "convex/values";

export default defineSchema({
  backups: defineTable({
    scriptName: v.string(),   // e.g. "script_manager", "my_other_tool"
    label: v.string(),        // user-defined label e.g. "before v2 update"
    data: v.any(),            // the full JSON config
    createdAt: v.number(),
  }).index("by_scriptName", ["scriptName"]),
});
