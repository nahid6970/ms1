import { useState, useRef } from 'react'
import { useMutation, useQuery } from 'convex/react'
import { api } from '@convex/_generated/api'
import { Id } from '@convex/_generated/dataModel'
import { Block } from '../types'
import {
  DndContext, closestCenter, KeyboardSensor, PointerSensor,
  useSensor, useSensors, DragEndEvent
} from '@dnd-kit/core'
import {
  SortableContext, sortableKeyboardCoordinates, verticalListSortingStrategy
} from '@dnd-kit/sortable'
import { BlockEditor } from './blocks/BlockEditor'
import { Plus, Smile } from 'lucide-react'

const COVER_GRADIENTS = [
  'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
  'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
  'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
  'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)',
  'linear-gradient(135deg, #fa709a 0%, #fee140 100%)',
  'linear-gradient(135deg, #30cfd0 0%, #330867 100%)',
  'linear-gradient(135deg, #a18cd1 0%, #fbc2eb 100%)',
  'linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%)',
]

const EMOJI_OPTIONS = ['📄', '📝', '📊', '🚀', '💡', '🎯', '🔬', '📚', '🗂️', '✅', '🎨', '⚡', '🌟', '📌', '🔧', '💼']

interface PageEditorProps {
  pageId: Id<'pages'>
}

export function PageEditor({ pageId }: PageEditorProps) {
  const page = useQuery(api.pages.get, { id: pageId })
  const blocks = useQuery(api.blocks.listByPage, { pageId }) ?? []
  const updatePage = useMutation(api.pages.update)
  const createBlock = useMutation(api.blocks.create)
  const reorderBlocks = useMutation(api.blocks.reorderMany)

  const [editingTitle, setEditingTitle] = useState(false)
  const [titleVal, setTitleVal] = useState('')
  const [showEmojiPicker, setShowEmojiPicker] = useState(false)
  const [showCoverPicker, setShowCoverPicker] = useState(false)
  const titleRef = useRef<HTMLTextAreaElement>(null)

  const sensors = useSensors(
    useSensor(PointerSensor, { activationConstraint: { distance: 5 } }),
    useSensor(KeyboardSensor, { coordinateGetter: sortableKeyboardCoordinates })
  )

  if (!page) return (
    <div className="flex-1 flex items-center justify-center" style={{ color: 'var(--text-tertiary)' }}>
      Loading...
    </div>
  )

  const sortedBlocks = ([...blocks].sort((a, b) => a.order - b.order)) as Block[]

  const handleDragEnd = (event: DragEndEvent) => {
    const { active, over } = event
    if (!over || active.id === over.id) return

    const sorted = [...sortedBlocks]
    const oldIdx = sorted.findIndex(b => b._id === active.id)
    const newIdx = sorted.findIndex(b => b._id === over.id)
    if (oldIdx === -1 || newIdx === -1) return

    // Remove from old, insert at new
    const [moved] = sorted.splice(oldIdx, 1)
    sorted.splice(newIdx, 0, moved)

    // Assign new order values
    const updates = sorted.map((b, i) => ({ id: b._id, order: i }))
    reorderBlocks({ updates })
  }

  const addBlock = async () => {
    const lastOrder = sortedBlocks.length > 0 ? sortedBlocks[sortedBlocks.length - 1].order + 1 : 0
    await createBlock({ pageId, type: 'paragraph', content: '', order: lastOrder })
  }

  const handleTitleBlur = () => {
    setEditingTitle(false)
    if (titleVal !== page.title) updatePage({ id: pageId, title: titleVal })
  }

  const handleTitleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      e.preventDefault()
      titleRef.current?.blur()
    }
  }

  return (
    <div className="flex-1 overflow-y-auto" style={{ background: 'var(--editor-bg)' }}>
      {/* Cover */}
      {page.coverImage && (
        <div
          className="relative w-full group"
          style={{ height: 200, background: page.coverImage, backgroundSize: 'cover', backgroundPosition: 'center' }}
        >
          <div className="absolute inset-0 opacity-0 group-hover:opacity-100 flex items-end justify-end p-3 transition-opacity">
            <button
              className="px-3 py-1.5 rounded text-sm font-medium"
              style={{ background: 'rgba(0,0,0,0.5)', color: 'white' }}
              onClick={() => setShowCoverPicker(true)}
            >
              Change cover
            </button>
          </div>
        </div>
      )}

      {/* Page content */}
      <div className="max-w-3xl mx-auto px-12 py-8">
        {/* Cover picker */}
        {showCoverPicker && (
          <div className="mb-4 p-3 rounded-lg border" style={{ background: 'var(--bg-secondary)', borderColor: 'var(--border)' }}>
            <div className="text-sm font-semibold mb-2" style={{ color: 'var(--text-secondary)' }}>Cover image</div>
            <div className="flex flex-wrap gap-2">
              {COVER_GRADIENTS.map((g, i) => (
                <button
                  key={i}
                  onClick={() => { updatePage({ id: pageId, coverImage: g }); setShowCoverPicker(false) }}
                  className="w-16 h-10 rounded cursor-pointer hover:ring-2 ring-blue-400"
                  style={{ background: g }}
                />
              ))}
              <button
                onClick={() => { updatePage({ id: pageId, coverImage: undefined }); setShowCoverPicker(false) }}
                className="px-3 h-10 rounded text-sm"
                style={{ background: 'var(--bg-active)', color: 'var(--text)' }}
              >
                Remove
              </button>
            </div>
          </div>
        )}

        {/* Icon & Title */}
        <div className="mb-6">
          {/* Icon */}
          <div className="relative inline-block mb-3">
            <button
              className="text-5xl hover:opacity-70 transition-opacity"
              onClick={() => setShowEmojiPicker(e => !e)}
              title="Change icon"
            >
              {page.icon ?? '📄'}
            </button>
            {showEmojiPicker && (
              <div
                className="absolute top-full left-0 mt-1 p-2 rounded-lg border z-50 fade-in"
                style={{ background: 'var(--bg)', borderColor: 'var(--border)', boxShadow: 'var(--shadow-md)' }}
              >
                <div className="flex flex-wrap gap-1 w-48">
                  {EMOJI_OPTIONS.map(e => (
                    <button
                      key={e}
                      onClick={() => { updatePage({ id: pageId, icon: e }); setShowEmojiPicker(false) }}
                      className="text-xl p-1.5 rounded hover:bg-gray-100"
                    >{e}</button>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Page controls */}
          <div className="flex items-center gap-2 mb-3">
            {!page.coverImage && (
              <button
                onClick={() => { setShowCoverPicker(true) }}
                className="flex items-center gap-1 px-2 py-1 rounded text-xs hover:opacity-70"
                style={{ color: 'var(--text-tertiary)', background: 'var(--bg-secondary)' }}
              >
                <span>🖼</span> Add cover
              </button>
            )}
          </div>

          {/* Title */}
          {editingTitle ? (
            <textarea
              ref={titleRef}
              autoFocus
              value={titleVal}
              onChange={e => setTitleVal(e.target.value)}
              onBlur={handleTitleBlur}
              onKeyDown={handleTitleKeyDown}
              rows={1}
              className="w-full resize-none outline-none bg-transparent selectable"
              style={{
                fontSize: '2.5rem',
                fontWeight: 700,
                lineHeight: 1.2,
                color: 'var(--text)',
                border: 'none',
                padding: 0,
              }}
              placeholder="Untitled"
            />
          ) : (
            <h1
              className="selectable cursor-text hover:opacity-80 transition-opacity"
              style={{ fontSize: '2.5rem', fontWeight: 700, lineHeight: 1.2, color: 'var(--text)', wordBreak: 'break-word' }}
              onClick={() => { setTitleVal(page.title); setEditingTitle(true) }}
            >
              {page.title || <span style={{ color: 'var(--text-tertiary)' }}>Untitled</span>}
            </h1>
          )}
        </div>

        {/* Blocks */}
        <DndContext sensors={sensors} collisionDetection={closestCenter} onDragEnd={handleDragEnd}>
          <SortableContext items={sortedBlocks.map(b => b._id)} strategy={verticalListSortingStrategy}>
            <div className="space-y-0.5">
              {sortedBlocks.map(block => (
                <BlockEditor
                  key={block._id}
                  block={block}
                  pageId={pageId}
                  allBlocks={sortedBlocks}
                />
              ))}
            </div>
          </SortableContext>
        </DndContext>

        {/* Add block button */}
        <div
          className="mt-4 flex items-center gap-2 cursor-pointer group"
          onClick={addBlock}
        >
          <button
            className="flex items-center justify-center w-6 h-6 rounded border opacity-0 group-hover:opacity-100 transition-opacity"
            style={{ borderColor: 'var(--border)', color: 'var(--text-tertiary)' }}
          >
            <Plus size={14} />
          </button>
          <span
            className="text-sm opacity-0 group-hover:opacity-100 transition-opacity"
            style={{ color: 'var(--text-tertiary)' }}
          >
            Click to add a block, or type '/' for commands
          </span>
        </div>

        <div style={{ height: 200 }} />
      </div>
    </div>
  )
}
