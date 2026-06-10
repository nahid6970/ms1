import { useMutation } from 'convex/react'
import { api } from '@convex/_generated/api'
import { Id } from '@convex/_generated/dataModel'
import { Plus, FileText } from 'lucide-react'

export function EmptyState({ onSelectPage }: { onSelectPage: (id: Id<'pages'>) => void }) {
  const createPage = useMutation(api.pages.create)

  return (
    <div className="flex-1 flex items-center justify-center" style={{ background: 'var(--editor-bg)' }}>
      <div className="text-center fade-in">
        <div style={{ fontSize: 64, marginBottom: 16 }}>📝</div>
        <h2 style={{ fontSize: '1.5rem', fontWeight: 700, color: 'var(--text)', marginBottom: 8 }}>
          Your workspace
        </h2>
        <p style={{ color: 'var(--text-secondary)', marginBottom: 24, maxWidth: 320 }}>
          Create pages, write notes, build tables, and organize your work.
        </p>
        <button
          onClick={async () => {
            const id = await createPage({ title: 'Getting Started', icon: '🚀' })
            onSelectPage(id)
          }}
          className="flex items-center gap-2 px-5 py-2.5 rounded-lg font-medium mx-auto transition-opacity hover:opacity-80"
          style={{ background: 'var(--accent)', color: 'white', fontSize: '0.9rem' }}
        >
          <Plus size={16} /> New page
        </button>
      </div>
    </div>
  )
}
