import { defineSchema, defineTable } from 'convex/server'
import { v } from 'convex/values'

export default defineSchema({
  pages: defineTable({
    title: v.string(),
    icon: v.optional(v.string()),
    coverImage: v.optional(v.string()),
    parentId: v.optional(v.id('pages')),
    isDeleted: v.optional(v.boolean()),
    isFavorite: v.optional(v.boolean()),
    order: v.number(),
  })
    .index('by_parent', ['parentId'])
    .index('by_order', ['order']),

  blocks: defineTable({
    pageId: v.id('pages'),
    type: v.string(), // paragraph, heading1, heading2, heading3, todo, bulleted_list, numbered_list, toggle, quote, divider, callout, code, image, table
    content: v.string(), // main text content
    checked: v.optional(v.boolean()), // for todo
    order: v.number(),
    parentBlockId: v.optional(v.id('blocks')),
    properties: v.optional(v.any()), // extra per-type data
  })
    .index('by_page', ['pageId'])
    .index('by_page_order', ['pageId', 'order'])
    .index('by_parent_block', ['parentBlockId']),

  tableBlocks: defineTable({
    blockId: v.id('blocks'),
    columns: v.array(v.object({ id: v.string(), name: v.string(), width: v.optional(v.number()) })),
    rows: v.array(v.array(v.string())),
  }).index('by_block', ['blockId']),
})
