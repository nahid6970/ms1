import { Id } from '../convex/_generated/dataModel'

export type BlockType =
  | 'paragraph'
  | 'heading1'
  | 'heading2'
  | 'heading3'
  | 'todo'
  | 'bulleted_list'
  | 'numbered_list'
  | 'toggle'
  | 'quote'
  | 'divider'
  | 'callout'
  | 'code'
  | 'image'
  | 'table'

export interface Block {
  _id: Id<'blocks'>
  _creationTime: number
  pageId: Id<'pages'>
  type: BlockType
  content: string
  checked?: boolean
  order: number
  parentBlockId?: Id<'blocks'>
  properties?: Record<string, unknown>
}

export interface Page {
  _id: Id<'pages'>
  _creationTime: number
  title: string
  icon?: string
  coverImage?: string
  parentId?: Id<'pages'>
  isDeleted?: boolean
  isFavorite?: boolean
  order: number
}

export interface TableData {
  _id: Id<'tableBlocks'>
  blockId: Id<'blocks'>
  columns: { id: string; name: string; width?: number }[]
  rows: string[][]
}

export interface SlashCommand {
  label: string
  description: string
  icon: string
  type: BlockType
  keywords: string[]
}

declare global {
  interface Window {
    electronAPI?: {
      minimize: () => Promise<void>
      maximize: () => Promise<void>
      close: () => Promise<void>
      isMaximized: () => Promise<boolean>
      openImageDialog: () => Promise<string | null>
      onMessage: (cb: (msg: string) => void) => void
    }
  }
}
