import { mutation, query } from './_generated/server'
import { v } from 'convex/values'

export const list = query({
  args: {},
  handler: async (ctx) => {
    return await ctx.db
      .query('pages')
      .filter((q) => q.eq(q.field('isDeleted'), false))
      .collect()
  },
})

export const listDeleted = query({
  args: {},
  handler: async (ctx) => {
    return await ctx.db
      .query('pages')
      .filter((q) => q.eq(q.field('isDeleted'), true))
      .collect()
  },
})

export const get = query({
  args: { id: v.id('pages') },
  handler: async (ctx, { id }) => {
    return await ctx.db.get(id)
  },
})

export const create = mutation({
  args: {
    title: v.optional(v.string()),
    parentId: v.optional(v.id('pages')),
    icon: v.optional(v.string()),
  },
  handler: async (ctx, args) => {
    const pages = await ctx.db.query('pages').collect()
    const order = pages.length
    const id = await ctx.db.insert('pages', {
      title: args.title ?? 'Untitled',
      parentId: args.parentId,
      icon: args.icon ?? '📄',
      isDeleted: false,
      isFavorite: false,
      order,
    })
    // Add a default paragraph block
    await ctx.db.insert('blocks', {
      pageId: id,
      type: 'paragraph',
      content: '',
      order: 0,
    })
    return id
  },
})

export const update = mutation({
  args: {
    id: v.id('pages'),
    title: v.optional(v.string()),
    icon: v.optional(v.string()),
    coverImage: v.optional(v.string()),
    isFavorite: v.optional(v.boolean()),
    isDeleted: v.optional(v.boolean()),
    parentId: v.optional(v.union(v.id('pages'), v.null())),
  },
  handler: async (ctx, { id, ...patch }) => {
    const filtered = Object.fromEntries(
      Object.entries(patch).filter(([, v]) => v !== undefined)
    )
    await ctx.db.patch(id, filtered)
  },
})

export const remove = mutation({
  args: { id: v.id('pages') },
  handler: async (ctx, { id }) => {
    // Soft delete: mark as deleted
    await ctx.db.patch(id, { isDeleted: true })
    // Recursively soft delete children
    const children = await ctx.db
      .query('pages')
      .withIndex('by_parent', (q) => q.eq('parentId', id))
      .collect()
    for (const child of children) {
      await ctx.db.patch(child._id, { isDeleted: true })
    }
  },
})

export const restore = mutation({
  args: { id: v.id('pages') },
  handler: async (ctx, { id }) => {
    await ctx.db.patch(id, { isDeleted: false })
  },
})

export const permanentDelete = mutation({
  args: { id: v.id('pages') },
  handler: async (ctx, { id }) => {
    const blocks = await ctx.db
      .query('blocks')
      .withIndex('by_page', (q) => q.eq('pageId', id))
      .collect()
    for (const block of blocks) {
      const tableData = await ctx.db
        .query('tableBlocks')
        .withIndex('by_block', (q) => q.eq('blockId', block._id))
        .first()
      if (tableData) await ctx.db.delete(tableData._id)
      await ctx.db.delete(block._id)
    }
    await ctx.db.delete(id)
  },
})

export const reorder = mutation({
  args: { id: v.id('pages'), order: v.number() },
  handler: async (ctx, { id, order }) => {
    await ctx.db.patch(id, { order })
  },
})
