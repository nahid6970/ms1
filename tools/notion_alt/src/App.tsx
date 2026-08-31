import { useState } from 'react'
import { ThemeProvider } from './lib/theme'
import { TitleBar } from './components/ui/TitleBar'
import { Sidebar } from './components/sidebar/Sidebar'
import { PageEditor } from './components/PageEditor'
import { EmptyState } from './components/EmptyState'
import { Id } from '../convex/_generated/dataModel'
import { PanelLeftClose, PanelLeftOpen } from 'lucide-react'

export default function App() {
  const [activePage, setActivePage] = useState<Id<'pages'> | null>(null)
  const [sidebarOpen, setSidebarOpen] = useState(true)

  return (
    <ThemeProvider>
      <div className="flex flex-col" style={{ height: '100vh', background: 'var(--bg)' }}>
        <TitleBar />
        <div className="flex flex-1 overflow-hidden" style={{ marginTop: 40 }}>
          {/* Sidebar toggle button */}
          <button
            onClick={() => setSidebarOpen(o => !o)}
            className="fixed left-0 z-50 p-1.5 rounded-r transition-all"
            style={{
              top: 48,
              left: sidebarOpen ? 'calc(var(--sidebar-width) - 1px)' : 0,
              background: 'var(--bg-secondary)',
              border: '1px solid var(--border)',
              borderLeft: sidebarOpen ? '1px solid var(--border)' : 'none',
              color: 'var(--text-tertiary)',
            }}
            title={sidebarOpen ? 'Close sidebar' : 'Open sidebar'}
          >
            {sidebarOpen ? <PanelLeftClose size={14} /> : <PanelLeftOpen size={14} />}
          </button>

          {/* Sidebar */}
          {sidebarOpen && (
            <div className="flex-shrink-0 slide-in" style={{ width: 'var(--sidebar-width)' }}>
              <Sidebar activePage={activePage} onSelectPage={setActivePage} />
            </div>
          )}

          {/* Main editor area */}
          <main className="flex flex-1 overflow-hidden" style={{ background: 'var(--editor-bg)' }}>
            {activePage
              ? <PageEditor key={activePage} pageId={activePage} />
              : <EmptyState onSelectPage={setActivePage} />
            }
          </main>
        </div>
      </div>
    </ThemeProvider>
  )
}
