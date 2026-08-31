import { mutation, query } from './_generated/server'
import { v } from 'convex/values'

const columnSchema = v.object({ id: v.string(), name: v.string(), width: v.optional(v.number()) })

export const getByBlock = query({
  args: { blockId: v.id('blocks') },
  handler: async (ctx, { blockId }) => {
    return await ctx.db
      .query('tableBlocks')
      .withIndex('by_block', (q) => q.eq('blockId', blockId))
      .first()
  },
})

export const updateColumns = mutation({
  args: { id: v.id('tableBlocks'), columns: v.array(columnSchema) },
  handler: async (ctx, { id, columns }) => {
    await ctx.db.patch(id, { columns })
  },
})

export const updateCell = mutation({
  args: {
    id: v.id('tableBlocks'),
    rowIndex: v.number(),
    colIndex: v.number(),
    value: v.string(),
  },
  handler: async (ctx, { id, rowIndex, colIndex, value }) => {
    const table = await ctx.db.get(id)
    if (!table) return
    const rows = table.rows.map((r: string[]) => [...r])
    while (rows.length <= rowIndex) rows.push(new Array(table.columns.length).fill(''))
    rows[rowIndex][colIndex] = value
    await ctx.db.patch(id, { rows })
  },
})

export const addRow = mutation({
  args: { id: v.id('tableBlocks') },
  handler: async (ctx, { id }) => {
    const table = await ctx.db.get(id)
    if (!table) return
    const newRow = new Array(table.columns.length).fill('')
    await ctx.db.patch(id, { rows: [...table.rows, newRow] })
  },
})

export const removeRow = mutation({
  args: { id: v.id('tableBlocks'), rowIndex: v.number() },
  handler: async (ctx, { id, rowIndex }) => {
    const table = await ctx.db.get(id)
    if (!table) return
    const rows = table.rows.filter((_: string[], i: number) => i !== rowIndex)
    await ctx.db.patch(id, { rows })
  },
})

export const addColumn = mutation({
  args: { id: v.id('tableBlocks') },
  handler: async (ctx, { id }) => {
    const table = await ctx.db.get(id)
    if (!table) return
    const colId = `col${Date.now()}`
    const columns = [...table.columns, { id: colId, name: 'Column', width: 160 }]
    const rows = table.rows.map((r: string[]) => [...r, ''])
    await ctx.db.patch(id, { columns, rows })
  },
})

export const removeColumn = mutation({
  args: { id: v.id('tableBlocks'), colIndex: v.number() },
  handler: async (ctx, { id, colIndex }) => {
    const table = await ctx.db.get(id)
    if (!table) return
    const columns = table.columns.filter((_: unknown, i: number) => i !== colIndex)
    const rows = table.rows.map((r: string[]) => r.filter((_: string, i: number) => i !== colIndex))
    await ctx.db.patch(id, { columns, rows })
  },
})

export const updateColumnName = mutation({
  args: { id: v.id('tableBlocks'), colIndex: v.number(), name: v.string() },
  handler: async (ctx, { id, colIndex, name }) => {
    const table = await ctx.db.get(id)
    if (!table) return
    const columns = table.columns.map((c: { id: string; name: string; width?: number }, i: number) =>
      i === colIndex ? { ...c, name } : c
    )
    await ctx.db.patch(id, { columns })
  },
})
