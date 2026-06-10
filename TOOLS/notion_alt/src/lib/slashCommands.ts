import { SlashCommand } from '../types'

export const SLASH_COMMANDS: SlashCommand[] = [
  { label: 'Text', description: 'Plain paragraph', icon: '¶', type: 'paragraph', keywords: ['text', 'paragraph', 'p'] },
  { label: 'Heading 1', description: 'Large heading', icon: 'H1', type: 'heading1', keywords: ['h1', 'heading', 'title', 'big'] },
  { label: 'Heading 2', description: 'Medium heading', icon: 'H2', type: 'heading2', keywords: ['h2', 'heading', 'subtitle'] },
  { label: 'Heading 3', description: 'Small heading', icon: 'H3', type: 'heading3', keywords: ['h3', 'heading', 'small'] },
  { label: 'To-do', description: 'Track tasks', icon: '☑', type: 'todo', keywords: ['todo', 'task', 'check', 'checkbox'] },
  { label: 'Bulleted List', description: 'Unordered list', icon: '•', type: 'bulleted_list', keywords: ['bullet', 'list', 'ul', 'unordered'] },
  { label: 'Numbered List', description: 'Ordered list', icon: '1.', type: 'numbered_list', keywords: ['number', 'ordered', 'ol', 'list'] },
  { label: 'Toggle', description: 'Collapsible section', icon: '▶', type: 'toggle', keywords: ['toggle', 'collapse', 'expand'] },
  { label: 'Quote', description: 'Blockquote', icon: '"', type: 'quote', keywords: ['quote', 'blockquote', 'cite'] },
  { label: 'Callout', description: 'Highlighted note', icon: '💡', type: 'callout', keywords: ['callout', 'note', 'info', 'highlight'] },
  { label: 'Code', description: 'Code block', icon: '<>', type: 'code', keywords: ['code', 'codeblock', 'snippet', 'pre'] },
  { label: 'Table', description: 'Grid of data', icon: '⊞', type: 'table', keywords: ['table', 'grid', 'database', 'spreadsheet'] },
  { label: 'Image', description: 'Insert image', icon: '🖼', type: 'image', keywords: ['image', 'photo', 'picture', 'img'] },
  { label: 'Divider', description: 'Horizontal rule', icon: '—', type: 'divider', keywords: ['divider', 'hr', 'separator', 'line'] },
]
