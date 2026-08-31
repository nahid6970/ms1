import { mutation, query } from './_generated/server'
import { v } from 'convex/values'

export const listByPage = query({
  args: { pageId: v.id('pages') },
  handler: async (ctx, { pageId }) => {
    return await ctx.db
      .query('blocks')
      .withIndex('by_page_order', (q) => q.eq('pageId', pageId))
      .order('asc')
      .collect()
  },
})

export const create = mutation({
  args: {
    pageId: v.id('pages'),
    type: v.string(),
    content: v.optional(v.string()),
    order: v.number(),
    parentBlockId: v.optional(v.id('blocks')),
    properties: v.optional(v.any()),
  },
  handler: async (ctx, args) => {
    const id = await ctx.db.insert('blocks', {
      pageId: args.pageId,
      type: args.type,
      content: args.content ?? '',
      order: args.order,
      parentBlockId: args.parentBlockId,
      properties: args.properties,
    })
    // If table type, create default table data
    if (args.type === 'table') {
      await ctx.db.insert('tableBlocks', {
        blockId: id,
        columns: [
          { id: 'col1', name: 'Name', width: 200 },
          { id: 'col2', name: 'Value', width: 200 },
          { id: 'col3', name: 'Notes', width: 200 },
        ],
        rows: [['', '', ''], ['', '', '']],
      })
    }
    return id
  },
})

export const update = mutation({
  args: {
    id: v.id('blocks'),
    type: v.optional(v.string()),
    content: v.optional(v.string()),
    checked: v.optional(v.boolean()),
    properties: v.optional(v.any()),
  },
  handler: async (ctx, { id, ...patch }) => {
    const filtered = Object.fromEntries(
      Object.entries(patch).filter(([, v]) => v !== undefined)
    )
    await ctx.db.patch(id, filtered)
  },
})

export const remove = mutation({
  args: { id: v.id('blocks') },
  handler: async (ctx, { id }) => {
    const tableData = await ctx.db
      .query('tableBlocks')
      .withIndex('by_block', (q) => q.eq('blockId', id))
      .first()
    if (tableData) await ctx.db.delete(tableData._id)
    await ctx.db.delete(id)
  },
})

export const reorderMany = mutation({
  args: {
    updates: v.array(v.object({ id: v.id('blocks'), order: v.number() })),
  },
  handler: async (ctx, { updates }) => {
    for (const { id, order } of updates) {
      await ctx.db.patch(id, { order })
    }
  },
})
