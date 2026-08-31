import { useEffect, useRef, useState } from 'react'
import { SLASH_COMMANDS } from '../../lib/slashCommands'
import { BlockType } from '../../types'

interface SlashMenuProps {
  query: string
  position: { top: number; left: number }
  onSelect: (type: BlockType) => void
  onClose: () => void
}

export function SlashMenu({ query, position, onSelect, onClose }: SlashMenuProps) {
  const [activeIdx, setActiveIdx] = useState(0)
  const menuRef = useRef<HTMLDivElement>(null)

  const filtered = SLASH_COMMANDS.filter(cmd =>
    cmd.keywords.some(k => k.includes(query.toLowerCase())) ||
    cmd.label.toLowerCase().includes(query.toLowerCase())
  )

  useEffect(() => { setActiveIdx(0) }, [query])

  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if (e.key === 'ArrowDown') {
        e.preventDefault()
        setActiveIdx(i => (i + 1) % filtered.length)
      } else if (e.key === 'ArrowUp') {
        e.preventDefault()
        setActiveIdx(i => (i - 1 + filtered.length) % filtered.length)
      } else if (e.key === 'Enter') {
        e.preventDefault()
        if (filtered[activeIdx]) onSelect(filtered[activeIdx].type)
      } else if (e.key === 'Escape') {
        onClose()
      }
    }
    window.addEventListener('keydown', handler, true)
    return () => window.removeEventListener('keydown', handler, true)
  }, [filtered, activeIdx, onSelect, onClose])

  // Scroll active item into view
  useEffect(() => {
    const el = menuRef.current?.querySelector('.active') as HTMLElement
    el?.scrollIntoView({ block: 'nearest' })
  }, [activeIdx])

  if (filtered.length === 0) return null

  // Adjust position to stay in viewport
  const top = Math.min(position.top, window.innerHeight - 340)
  const left = Math.min(position.left, window.innerWidth - 240)

  return (
    <div
      ref={menuRef}
      className="slash-menu fade-in"
      style={{ position: 'fixed', top, left, zIndex: 1000 }}
      onMouseDown={e => e.preventDefault()}
    >
      <div className="px-3 py-2 text-xs font-semibold" style={{ color: 'var(--text-tertiary)', borderBottom: '1px solid var(--border)' }}>
        BLOCKS
      </div>
      {filtered.map((cmd, i) => (
        <div
          key={cmd.type}
          className={`slash-menu-item ${i === activeIdx ? 'active' : ''}`}
          onClick={() => onSelect(cmd.type)}
          onMouseEnter={() => setActiveIdx(i)}
        >
          <div
            className="w-8 h-8 rounded flex items-center justify-center text-sm font-bold flex-shrink-0"
            style={{ background: 'var(--bg-secondary)', color: 'var(--text)', border: '1px solid var(--border)' }}
          >
            {cmd.icon}
          </div>
          <div>
            <div className="text-sm font-medium" style={{ color: 'var(--text)' }}>{cmd.label}</div>
            <div className="text-xs" style={{ color: 'var(--text-tertiary)' }}>{cmd.description}</div>
          </div>
        </div>
      ))}
    </div>
  )
}
