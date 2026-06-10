import { Minus, Square, X, Moon, Sun } from 'lucide-react'
import { useTheme } from '@/lib/theme'

export function TitleBar() {
  const { theme, toggle } = useTheme()
  const api = window.electronAPI

  return (
    <div
      className="titlebar flex items-center justify-between h-10 px-3 border-b"
      style={{ background: 'var(--sidebar-bg)', borderColor: 'var(--border)', position: 'fixed', top: 0, left: 0, right: 0, zIndex: 100 }}
    >
      <div className="flex items-center gap-2">
        <span style={{ fontSize: 16 }}>📝</span>
        <span style={{ fontSize: 13, fontWeight: 600, color: 'var(--text-secondary)' }}>Notion Alt</span>
      </div>
      <div className="titlebar-btn flex items-center gap-1">
        <button
          onClick={toggle}
          className="flex items-center justify-center w-7 h-7 rounded hover:opacity-70 transition-opacity"
          style={{ color: 'var(--text-secondary)' }}
          title={theme === 'dark' ? 'Light mode' : 'Dark mode'}
        >
          {theme === 'dark' ? <Sun size={14} /> : <Moon size={14} />}
        </button>
        <div style={{ width: 1, height: 16, background: 'var(--border)', margin: '0 4px' }} />
        <button
          onClick={() => api?.minimize()}
          className="titlebar-btn flex items-center justify-center w-7 h-7 rounded hover:bg-gray-200 dark:hover:bg-gray-700"
          style={{ color: 'var(--text-secondary)' }}
        >
          <Minus size={12} />
        </button>
        <button
          onClick={() => api?.maximize()}
          className="titlebar-btn flex items-center justify-center w-7 h-7 rounded hover:bg-gray-200 dark:hover:bg-gray-700"
          style={{ color: 'var(--text-secondary)' }}
        >
          <Square size={11} />
        </button>
        <button
          onClick={() => api?.close()}
          className="titlebar-btn flex items-center justify-center w-7 h-7 rounded hover:bg-red-500 hover:text-white transition-colors"
          style={{ color: 'var(--text-secondary)' }}
        >
          <X size={13} />
        </button>
      </div>
    </div>
  )
}
