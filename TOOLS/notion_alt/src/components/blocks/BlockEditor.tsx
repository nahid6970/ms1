import { useRef, useState, useCallback, KeyboardEvent } from 'react'
import { useMutation } from 'convex/react'
import { api } from '@convex/_generated/api'
import { Id } from '@convex/_generated/dataModel'
import { Block, BlockType } from '../../types'
import { GripVertical, Plus, Trash2, ChevronDown, ChevronRight } from 'lucide-react'
import { SlashMenu } from '../ui/SlashMenu'
import { TableBlock } from './TableBlock'
import { useSortable } from '@dnd-kit/sortable'
import { CSS } from '@dnd-kit/utilities'

interface BlockEditorProps {
  block: Block
  pageId: Id<'pages'>
  allBlocks: Block[]
  onFocus?: () => void
}

export function BlockEditor({ block, pageId, allBlocks, onFocus }: BlockEditorProps) {
  const updateBlock = useMutation(api.blocks.update)
  const removeBlock = useMutation(api.blocks.remove)
  const createBlock = useMutation(api.blocks.create)

  const [content, setContent] = useState(block.content)
  const [showSlash, setShowSlash] = useState(false)
  const [slashQuery, setSlashQuery] = useState('')
  const [slashPos, setSlashPos] = useState({ top: 0, left: 0 })
  const [toggleOpen, setToggleOpen] = useState(false)
  const [hover, setHover] = useState(false)
  const contentRef = useRef<HTMLDivElement>(null)
  const slashStartRef = useRef(-1)
  const suppressBlurRef = useRef(false)

  const { attributes, listeners, setNodeRef, transform, transition, isDragging } = useSortable({ id: block._id })
  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    opacity: isDragging ? 0.4 : 1,
  }

  const saveContent = useCallback((val: string) => {
    if (val !== block.content) updateBlock({ id: block._id, content: val })
  }, [block._id, block.content, updateBlock])

  const getCaretPosition = (): { top: number; left: number } => {
    const sel = window.getSelection()
    if (!sel || !sel.rangeCount) return { top: 200, left: 300 }
    const range = sel.getRangeAt(0).cloneRange()
    range.collapse(true)
    const rect = range.getBoundingClientRect()
    return { top: rect.bottom + 4, left: rect.left }
  }

  const handleInput = (e: React.FormEvent<HTMLDivElement>) => {
    const text = e.currentTarget.innerText
    setContent(text)

    // Use innerText-based caret position for reliable slash detection
    const sel = window.getSelection()
    if (!sel || !sel.rangeCount) return

    // Get caret offset in the full innerText
    const range = sel.getRangeAt(0)
    const preRange = range.cloneRange()
    preRange.selectNodeContents(e.currentTarget)
    preRange.setEnd(range.endContainer, range.endOffset)
    const caretPos = preRange.toString().length

    if (text[caretPos - 1] === '/') {
      slashStartRef.current = caretPos  // position right after '/'
      setSlashQuery('')
      setSlashPos(getCaretPosition())
      setShowSlash(true)
    } else if (showSlash && slashStartRef.current >= 0) {
      const query = text.slice(slashStartRef.current, caretPos)
      if (query.includes(' ') || caretPos < slashStartRef.current) {
        setShowSlash(false)
        slashStartRef.current = -1
      } else {
        setSlashQuery(query)
      }
    }
  }

  const handleKeyDown = (e: KeyboardEvent<HTMLDivElement>) => {
    if (showSlash && ['ArrowDown', 'ArrowUp', 'Enter'].includes(e.key)) return // let SlashMenu handle

    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      // Create new block below
      const sortedBlocks = [...allBlocks].sort((a, b) => a.order - b.order)
      const idx = sortedBlocks.findIndex(b => b._id === block._id)
      const newOrder = idx >= 0 ? (sortedBlocks[idx + 1]?.order ?? block.order + 1) : block.order + 1
      createBlock({ pageId, type: 'paragraph', content: '', order: (block.order + newOrder) / 2 })
      saveContent(contentRef.current?.innerText ?? content)
    }

    if (e.key === 'Backspace') {
      const text = contentRef.current?.innerText ?? ''
      if (text === '' || text === '\n') {
        e.preventDefault()
        removeBlock({ id: block._id })
      }
    }

    if (e.key === 'Escape') setShowSlash(false)
  }

  const handleBlur = () => {
    if (suppressBlurRef.current) return
    const text = contentRef.current?.innerText ?? ''
    saveContent(text)
    setShowSlash(false)
  }

  const insertBlock = async (type: BlockType) => {
    suppressBlurRef.current = false
    setShowSlash(false)
    const currentText = contentRef.current?.innerText ?? ''
    // Remove the slash + query from the content
    const slashIdx = slashStartRef.current - 1  // position of '/'
    const cleanText = slashIdx >= 0
      ? currentText.slice(0, slashIdx) + currentText.slice(slashStartRef.current + slashQuery.length)
      : currentText
    slashStartRef.current = -1

    if (contentRef.current) contentRef.current.innerText = cleanText
    saveContent(cleanText)

    // Always change the current block's type (simpler and more Notion-like)
    await updateBlock({ id: block._id, type, content: cleanText })
    // Refocus
    setTimeout(() => contentRef.current?.focus(), 0)
  }

  const blockType = block.type

  const renderContent = () => {
    switch (blockType) {
      case 'divider':
        return <hr style={{ border: 'none', borderTop: '1px solid var(--border)', margin: '8px 0', cursor: 'default' }} />

      case 'image':
        if (block.content) {
          return (
            <div className="my-2">
              <img
                src={block.content.startsWith('/') ? `file://${block.content}` : block.content}
                alt=""
                className="max-w-full rounded"
                style={{ maxHeight: 500 }}
              />
              <div
                className="text-xs mt-1 outline-none selectable"
                contentEditable
                suppressContentEditableWarning
                onBlur={e => updateBlock({ id: block._id, properties: { caption: e.currentTarget.innerText } })}
                data-placeholder="Add a caption..."
                style={{ color: 'var(--text-tertiary)' }}
              >
                {(block.properties as { caption?: string })?.caption ?? ''}
              </div>
            </div>
          )
        }
        return (
          <div
            className="flex items-center gap-2 p-3 rounded border-2 border-dashed cursor-pointer hover:bg-gray-50 transition-colors"
            style={{ borderColor: 'var(--border)' }}
            onClick={async () => {
              const path = await window.electronAPI?.openImageDialog()
              if (path) updateBlock({ id: block._id, content: path })
            }}
          >
            <span style={{ fontSize: 24 }}>🖼</span>
            <div>
              <div className="font-medium" style={{ color: 'var(--text-secondary)' }}>Click to add image</div>
              <div className="text-xs" style={{ color: 'var(--text-tertiary)' }}>or paste an image URL</div>
            </div>
          </div>
        )

      case 'table':
        return <TableBlock blockId={block._id} />

      default:
        return null
    }
  }

  const isContentBlock = !['divider', 'image', 'table'].includes(blockType)

  const getPlaceholder = () => {
    switch (blockType) {
      case 'heading1': return 'Heading 1'
      case 'heading2': return 'Heading 2'
      case 'heading3': return 'Heading 3'
      case 'todo': return 'To-do'
      case 'bulleted_list': return 'List'
      case 'numbered_list': return 'List'
      case 'toggle': return 'Toggle'
      case 'quote': return 'Quote'
      case 'callout': return 'Callout'
      case 'code': return 'Code'
      default: return "Type '/' for commands"
    }
  }

  const wrapperStyle: React.CSSProperties = {
    display: 'flex',
    alignItems: 'flex-start',
    gap: 4,
    padding: '2px 0',
    position: 'relative',
  }

  return (
    <div ref={setNodeRef} style={style} {...attributes}>
      <div
        className="block-wrapper"
        style={wrapperStyle}
        onMouseEnter={() => setHover(true)}
        onMouseLeave={() => setHover(false)}
      >
        {/* Drag handle */}
        <div
          className="drag-handle flex-shrink-0 mt-0.5"
          style={{ visibility: hover ? 'visible' : 'hidden', width: 20 }}
          {...listeners}
        >
          <GripVertical size={14} style={{ color: 'var(--text-tertiary)' }} />
        </div>

        {/* Block prefix (checkbox, bullet, number, toggle) */}
        <div className="flex-shrink-0 mt-0.5" style={{ minWidth: 20, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          {blockType === 'todo' && (
            <input
              type="checkbox"
              checked={block.checked ?? false}
              onChange={e => updateBlock({ id: block._id, checked: e.target.checked })}
              className="w-4 h-4 cursor-pointer"
              style={{ accentColor: 'var(--accent)' }}
            />
          )}
          {blockType === 'bulleted_list' && (
            <span style={{ fontSize: 18, lineHeight: 1, color: 'var(--text)' }}>•</span>
          )}
          {blockType === 'toggle' && (
            <button onClick={() => setToggleOpen(o => !o)} className="hover:opacity-60">
              {toggleOpen ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
            </button>
          )}
        </div>

        {/* Main content */}
        <div className="flex-1 min-w-0">
          {blockType === 'quote' && (
            <div style={{ borderLeft: '3px solid var(--text-secondary)', paddingLeft: 12 }}>
              <div
                ref={contentRef}
                className="block-content selectable"
                contentEditable
                suppressContentEditableWarning
                onInput={handleInput}
                onKeyDown={handleKeyDown}
                onBlur={handleBlur}
                onFocus={onFocus}
                data-placeholder={getPlaceholder()}
                style={{ fontStyle: 'italic', color: 'var(--text-secondary)' }}
                dangerouslySetInnerHTML={undefined}
              >{block.content}</div>
            </div>
          )}

          {blockType === 'callout' && (
            <div className="callout-block">
              <div className="flex items-start gap-2">
                <span style={{ fontSize: 18, lineHeight: '1.4em' }}>
                  {(block.properties as { emoji?: string })?.emoji ?? '💡'}
                </span>
                <div
                  ref={contentRef}
                  className="block-content selectable flex-1"
                  contentEditable
                  suppressContentEditableWarning
                  onInput={handleInput}
                  onKeyDown={handleKeyDown}
                  onBlur={handleBlur}
                  onFocus={onFocus}
                  data-placeholder={getPlaceholder()}
                >{block.content}</div>
              </div>
            </div>
          )}

          {blockType === 'code' && (
            <div className="code-block">
              <div
                ref={contentRef}
                className="block-content selectable"
                contentEditable
                suppressContentEditableWarning
                onInput={handleInput}
                onKeyDown={handleKeyDown}
                onBlur={handleBlur}
                onFocus={onFocus}
                data-placeholder="// Code here..."
                spellCheck={false}
                style={{ fontFamily: '"JetBrains Mono", "Fira Code", Consolas, monospace', fontSize: '0.875em' }}
              >{block.content}</div>
            </div>
          )}

          {isContentBlock && !['quote', 'callout', 'code'].includes(blockType) && (
            <div
              ref={contentRef}
              className={`block-content selectable ${blockType === 'heading1' ? 'block-h1' : blockType === 'heading2' ? 'block-h2' : blockType === 'heading3' ? 'block-h3' : ''}`}
              contentEditable
              suppressContentEditableWarning
              onInput={handleInput}
              onKeyDown={handleKeyDown}
              onBlur={handleBlur}
              onFocus={onFocus}
              data-placeholder={getPlaceholder()}
              style={{
                textDecoration: (blockType === 'todo' && block.checked) ? 'line-through' : undefined,
                opacity: (blockType === 'todo' && block.checked) ? 0.6 : 1,
                paddingLeft: blockType === 'numbered_list' ? 4 : 0,
              }}
            >{block.content}</div>
          )}

          {!isContentBlock && renderContent()}

          {/* Toggle children */}
          {blockType === 'toggle' && toggleOpen && (
            <div className="toggle-content mt-1">
              <div
                ref={contentRef}
                className="block-content selectable"
                contentEditable
                suppressContentEditableWarning
                onInput={handleInput}
                onKeyDown={handleKeyDown}
                onBlur={handleBlur}
                onFocus={onFocus}
                data-placeholder="Toggle content..."
              >{block.content}</div>
            </div>
          )}
        </div>

        {/* Delete button */}
        {hover && blockType !== 'divider' && (
          <button
            className="block-actions flex-shrink-0 mt-0.5 p-0.5 rounded hover:bg-red-100 hover:text-red-500"
            style={{ color: 'var(--text-tertiary)' }}
            onClick={() => removeBlock({ id: block._id })}
            title="Delete block"
          >
            <Trash2 size={13} />
          </button>
        )}
      </div>

      {/* Slash command menu */}
      {showSlash && (
        <SlashMenu
          query={slashQuery}
          position={slashPos}
          onSelect={insertBlock}
          onClose={() => setShowSlash(false)}
        />
      )}
    </div>
  )
}
