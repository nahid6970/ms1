import { useState } from 'react'
import { useMutation, useQuery } from 'convex/react'
import { api } from '@convex/_generated/api'
import { Id } from '@convex/_generated/dataModel'
import { Page } from '../../types'
import {
  Plus, ChevronRight, ChevronDown, Trash2, Star, StarOff,
  FileText, Search, Settings, Home, Archive
} from 'lucide-react'

interface SidebarProps {
  activePage: Id<'pages'> | null
  onSelectPage: (id: Id<'pages'>) => void
}

export function Sidebar({ activePage, onSelectPage }: SidebarProps) {
  const pages = useQuery(api.pages.list) ?? []
  const createPage = useMutation(api.pages.create)
  const updatePage = useMutation(api.pages.update)
  const removePage = useMutation(api.pages.remove)
  const [expanded, setExpanded] = useState<Set<string>>(new Set())
  const [showTrash, setShowTrash] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')
  const [showSearch, setShowSearch] = useState(false)
  const deletedPages = useQuery(api.pages.listDeleted) ?? []

  const rootPages = pages
    .filter(p => !p.parentId && !p.isDeleted)
    .sort((a, b) => a.order - b.order)

  const favorites = pages.filter(p => p.isFavorite && !p.isDeleted)

  const handleCreate = async (parentId?: Id<'pages'>) => {
    const id = await createPage({ parentId })
    if (parentId) setExpanded(e => new Set([...e, parentId]))
    onSelectPage(id)
  }

  const toggleExpand = (id: string) => {
    setExpanded(e => {
      const n = new Set(e)
      n.has(id) ? n.delete(id) : n.add(id)
      return n
    })
  }

  const filtered = searchQuery
    ? pages.filter(p => !p.isDeleted && p.title.toLowerCase().includes(searchQuery.toLowerCase()))
    : null

  return (
    <div
      className="flex flex-col h-full"
      style={{ background: 'var(--sidebar-bg)', width: 'var(--sidebar-width)', borderRight: '1px solid var(--border)' }}
    >
      {/* Header */}
      <div className="p-3 pt-2">
        <div className="sidebar-item" onClick={() => setShowSearch(s => !s)}>
          <Search size={15} style={{ color: 'var(--text-secondary)' }} />
          <span style={{ color: 'var(--text-secondary)' }}>Search</span>
        </div>
        {showSearch && (
          <input
            autoFocus
            value={searchQuery}
            onChange={e => setSearchQuery(e.target.value)}
            placeholder="Search pages..."
            className="w-full mt-1 px-2 py-1.5 text-sm rounded outline-none"
            style={{ background: 'var(--bg-active)', color: 'var(--text)', border: '1px solid var(--border)' }}
          />
        )}
      </div>

      <div className="flex-1 overflow-y-auto px-2 pb-4 space-y-0.5">
        {/* Search results */}
        {filtered && (
          <div className="mb-2">
            <div className="px-2 py-1 text-xs font-semibold" style={{ color: 'var(--text-tertiary)' }}>Results</div>
            {filtered.map(p => (
              <div key={p._id} className={`sidebar-item ${activePage === p._id ? 'active' : ''}`}
                onClick={() => { onSelectPage(p._id); setShowSearch(false); setSearchQuery('') }}>
                <span>{p.icon ?? '📄'}</span>
                <span className="truncate">{p.title || 'Untitled'}</span>
              </div>
            ))}
          </div>
        )}

        {/* Favorites */}
        {favorites.length > 0 && !filtered && (
          <div className="mb-2">
            <div className="px-2 py-1 text-xs font-semibold" style={{ color: 'var(--text-tertiary)' }}>
              FAVORITES
            </div>
            {favorites.map(p => (
              <PageItem
                key={p._id}
                page={p}
                level={0}
                active={activePage === p._id}
                onSelect={onSelectPage}
                onCreate={handleCreate}
                onDelete={() => removePage({ id: p._id })}
                onToggleFav={() => updatePage({ id: p._id, isFavorite: !p.isFavorite })}
                expanded={expanded}
                onExpand={toggleExpand}
                allPages={pages}
              />
            ))}
          </div>
        )}

        {/* Pages */}
        {!filtered && (
          <>
            <div className="flex items-center justify-between px-2 py-1">
              <span className="text-xs font-semibold" style={{ color: 'var(--text-tertiary)' }}>PAGES</span>
              <button
                onClick={() => handleCreate()}
                className="opacity-0 group-hover:opacity-100 hover:opacity-100 p-0.5 rounded hover:bg-gray-200"
                style={{ color: 'var(--text-secondary)' }}
                title="New page"
              >
                <Plus size={14} />
              </button>
            </div>
            {rootPages.map(p => (
              <PageItem
                key={p._id}
                page={p}
                level={0}
                active={activePage === p._id}
                onSelect={onSelectPage}
                onCreate={handleCreate}
                onDelete={() => removePage({ id: p._id })}
                onToggleFav={() => updatePage({ id: p._id, isFavorite: !p.isFavorite })}
                expanded={expanded}
                onExpand={toggleExpand}
                allPages={pages}
              />
            ))}
            <button
              onClick={() => handleCreate()}
              className="sidebar-item w-full text-left mt-1"
              style={{ color: 'var(--text-tertiary)' }}
            >
              <Plus size={14} />
              <span>New page</span>
            </button>
          </>
        )}
      </div>

      {/* Bottom */}
      <div className="p-2 border-t" style={{ borderColor: 'var(--border)' }}>
        <button
          onClick={() => setShowTrash(t => !t)}
          className="sidebar-item w-full"
          style={{ color: 'var(--text-secondary)' }}
        >
          <Trash2 size={14} />
          <span>Trash</span>
          {deletedPages.length > 0 && (
            <span className="ml-auto text-xs rounded-full px-1.5 py-0.5"
              style={{ background: 'var(--bg-active)', color: 'var(--text-secondary)' }}>
              {deletedPages.length}
            </span>
          )}
        </button>
        {showTrash && <TrashPanel pages={deletedPages} onSelectPage={onSelectPage} />}
      </div>
    </div>
  )
}

interface PageItemProps {
  page: Page
  level: number
  active: boolean
  onSelect: (id: Id<'pages'>) => void
  onCreate: (parentId?: Id<'pages'>) => void
  onDelete: () => void
  onToggleFav: () => void
  expanded: Set<string>
  onExpand: (id: string) => void
  allPages: Page[]
}

function PageItem({ page, level, active, onSelect, onCreate, onDelete, onToggleFav, expanded, onExpand, allPages }: PageItemProps) {
  const children = allPages.filter(p => p.parentId === page._id && !p.isDeleted)
  const hasChildren = children.length > 0
  const isExpanded = expanded.has(page._id)
  const [hover, setHover] = useState(false)
  const updatePage = useMutation(api.pages.update)

  return (
    <div>
      <div
        className={`sidebar-item ${active ? 'active' : ''} group`}
        style={{ paddingLeft: `${8 + level * 16}px` }}
        onMouseEnter={() => setHover(true)}
        onMouseLeave={() => setHover(false)}
        onClick={() => onSelect(page._id)}
      >
        <button
          className="flex-shrink-0 w-4 h-4 flex items-center justify-center rounded"
          style={{ color: 'var(--text-tertiary)' }}
          onClick={e => { e.stopPropagation(); if (hasChildren) onExpand(page._id) }}
        >
          {hasChildren
            ? (isExpanded ? <ChevronDown size={12} /> : <ChevronRight size={12} />)
            : <span style={{ fontSize: 12 }}>{page.icon ?? '📄'}</span>
          }
        </button>
        {hasChildren && <span style={{ fontSize: 12 }}>{page.icon ?? '📄'}</span>}
        <span className="truncate flex-1">{page.title || 'Untitled'}</span>
        {hover && (
          <div className="flex items-center gap-0.5 ml-auto">
            <button
              onClick={e => { e.stopPropagation(); onToggleFav() }}
              className="p-0.5 rounded hover:bg-gray-300"
              title={page.isFavorite ? 'Remove from favorites' : 'Add to favorites'}
            >
              {page.isFavorite ? <StarOff size={12} /> : <Star size={12} />}
            </button>
            <button
              onClick={e => { e.stopPropagation(); onCreate(page._id) }}
              className="p-0.5 rounded hover:bg-gray-300"
              title="Add sub-page"
            >
              <Plus size={12} />
            </button>
            <button
              onClick={e => { e.stopPropagation(); onDelete() }}
              className="p-0.5 rounded hover:bg-red-200 hover:text-red-600"
              title="Delete"
            >
              <Trash2 size={12} />
            </button>
          </div>
        )}
      </div>
      {isExpanded && children.sort((a, b) => a.order - b.order).map(child => (
        <PageItem
          key={child._id}
          page={child}
          level={level + 1}
          active={active && false}
          onSelect={onSelect}
          onCreate={onCreate}
          onDelete={() => updatePage({ id: child._id, isDeleted: true })}
          onToggleFav={() => updatePage({ id: child._id, isFavorite: !child.isFavorite })}
          expanded={expanded}
          onExpand={onExpand}
          allPages={allPages}
        />
      ))}
    </div>
  )
}

function TrashPanel({ pages, onSelectPage }: { pages: Page[]; onSelectPage: (id: Id<'pages'>) => void }) {
  const restorePage = useMutation(api.pages.restore)
  const deletePermanent = useMutation(api.pages.permanentDelete)

  if (pages.length === 0) {
    return <div className="px-3 py-2 text-xs" style={{ color: 'var(--text-tertiary)' }}>Trash is empty</div>
  }

  return (
    <div className="mt-1 space-y-0.5">
      {pages.map(p => (
        <div key={p._id} className="sidebar-item group" onClick={() => onSelectPage(p._id)}>
          <span style={{ fontSize: 12 }}>{p.icon ?? '📄'}</span>
          <span className="truncate flex-1 line-through" style={{ color: 'var(--text-tertiary)' }}>
            {p.title || 'Untitled'}
          </span>
          <button
            onClick={e => { e.stopPropagation(); restorePage({ id: p._id }) }}
            className="p-0.5 rounded hover:bg-green-200 hover:text-green-700 opacity-0 group-hover:opacity-100"
            title="Restore"
          >
            <Archive size={12} />
          </button>
          <button
            onClick={e => { e.stopPropagation(); deletePermanent({ id: p._id }) }}
            className="p-0.5 rounded hover:bg-red-200 hover:text-red-600 opacity-0 group-hover:opacity-100"
            title="Delete permanently"
          >
            <Trash2 size={12} />
          </button>
        </div>
      ))}
    </div>
  )
}
