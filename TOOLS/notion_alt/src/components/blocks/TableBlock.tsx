import { useRef, useState } from 'react'
import { useMutation, useQuery } from 'convex/react'
import { api } from '@convex/_generated/api'
import { Id } from '@convex/_generated/dataModel'
import { Plus, Trash2, GripVertical } from 'lucide-react'

interface TableBlockProps {
  blockId: Id<'blocks'>
  readOnly?: boolean
}

export function TableBlock({ blockId, readOnly }: TableBlockProps) {
  const data = useQuery(api.tables.getByBlock, { blockId })
  const updateCell = useMutation(api.tables.updateCell)
  const updateColName = useMutation(api.tables.updateColumnName)
  const addRow = useMutation(api.tables.addRow)
  const removeRow = useMutation(api.tables.removeRow)
  const addCol = useMutation(api.tables.addColumn)
  const removeCol = useMutation(api.tables.removeColumn)
  const [editingHeader, setEditingHeader] = useState<number | null>(null)
  const [headerVal, setHeaderVal] = useState('')

  if (!data) return <div className="text-sm" style={{ color: 'var(--text-tertiary)' }}>Loading table...</div>

  const { _id: tableId, columns, rows } = data

  const handleCellBlur = (ri: number, ci: number, value: string) => {
    updateCell({ id: tableId, rowIndex: ri, colIndex: ci, value })
  }

  const handleHeaderClick = (ci: number) => {
    setEditingHeader(ci)
    setHeaderVal(columns[ci].name)
  }

  const handleHeaderBlur = (ci: number) => {
    updateColName({ id: tableId, colIndex: ci, name: headerVal })
    setEditingHeader(null)
  }

  return (
    <div className="overflow-x-auto my-1">
      <table className="notion-table">
        <thead>
          <tr>
            {columns.map((col, ci) => (
              <th key={col.id} style={{ minWidth: col.width ?? 160, position: 'relative' }}>
                {editingHeader === ci ? (
                  <input
                    autoFocus
                    value={headerVal}
                    onChange={e => setHeaderVal(e.target.value)}
                    onBlur={() => handleHeaderBlur(ci)}
                    onKeyDown={e => e.key === 'Enter' && handleHeaderBlur(ci)}
                    className="w-full outline-none bg-transparent font-semibold"
                    style={{ color: 'var(--text)' }}
                  />
                ) : (
                  <div className="flex items-center justify-between group">
                    <span onClick={() => !readOnly && handleHeaderClick(ci)} className={readOnly ? '' : 'cursor-text'}>
                      {col.name}
                    </span>
                    {!readOnly && (
                      <button
                        onClick={() => removeCol({ id: tableId, colIndex: ci })}
                        className="opacity-0 group-hover:opacity-100 text-red-400 hover:text-red-600"
                        title="Remove column"
                      >
                        <Trash2 size={11} />
                      </button>
                    )}
                  </div>
                )}
              </th>
            ))}
            {!readOnly && (
              <th style={{ width: 40, background: 'var(--bg-secondary)' }}>
                <button
                  onClick={() => addCol({ id: tableId })}
                  className="w-full flex items-center justify-center hover:text-blue-500"
                  style={{ color: 'var(--text-tertiary)' }}
                  title="Add column"
                >
                  <Plus size={14} />
                </button>
              </th>
            )}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, ri) => (
            <tr key={ri}>
              {columns.map((col, ci) => (
                <TableCell
                  key={col.id}
                  value={row[ci] ?? ''}
                  onBlur={v => handleCellBlur(ri, ci, v)}
                  readOnly={readOnly}
                />
              ))}
              {!readOnly && (
                <td style={{ width: 40, textAlign: 'center' }}>
                  <button
                    onClick={() => removeRow({ id: tableId, rowIndex: ri })}
                    className="text-red-300 hover:text-red-500"
                    title="Remove row"
                  >
                    <Trash2 size={11} />
                  </button>
                </td>
              )}
            </tr>
          ))}
        </tbody>
      </table>
      {!readOnly && (
        <button
          onClick={() => addRow({ id: tableId })}
          className="mt-1 flex items-center gap-1 text-xs px-2 py-1 rounded hover:bg-gray-100"
          style={{ color: 'var(--text-tertiary)' }}
        >
          <Plus size={13} /> Add row
        </button>
      )}
    </div>
  )
}

function TableCell({ value, onBlur, readOnly }: { value: string; onBlur: (v: string) => void; readOnly?: boolean }) {
  const [val, setVal] = useState(value)
  const ref = useRef<HTMLTextAreaElement>(null)

  // Sync if prop changes
  if (value !== val && document.activeElement !== ref.current) {
    setVal(value)
  }

  if (readOnly) return <td className="selectable">{value}</td>

  return (
    <td>
      <textarea
        ref={ref}
        value={val}
        onChange={e => setVal(e.target.value)}
        onBlur={() => onBlur(val)}
        rows={1}
        className="selectable w-full resize-none outline-none bg-transparent"
        style={{ color: 'var(--text)', minHeight: '1.5em', fontSize: 'inherit' }}
      />
    </td>
  )
}
