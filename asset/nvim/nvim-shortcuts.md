# Nvim Essential Shortcuts & Commands

## Buffer Management

### Viewing Buffers
- `:ls` or `:buffers` - List all open buffers
- `:files` - Show all loaded files

### Switching Between Buffers
- `:bn` or `:bnext` - Go to next buffer
- `:bp` or `:bprev` - Go to previous buffer
- `:b<number>` - Jump to buffer by number (e.g., `:b2`)
- `:b <filename>` - Jump to buffer by name (supports tab completion)
- `Ctrl+6` or `Ctrl+^` - Toggle between current and last buffer

### Buffer Operations
- `:bd` or `:bdelete` - Close current buffer
- `:bd<number>` - Close specific buffer by number
- `:sb<number>` - Open buffer in horizontal split
- `:vert sb<number>` - Open buffer in vertical split

## Multi-Selection & Pattern Editing

### Quick Word Selection & Replace
1. Place cursor on word
2. Press `*` to highlight all instances
3. Press `cgn` to change next occurrence
4. Type replacement text
5. Press `Esc`, then `.` to repeat for next occurrence
6. Continue pressing `.` for each occurrence

### Search and Replace
```vim
:%s/old/new/g       # Replace all in file
:%s/old/new/gc      # Replace all with confirmation
:s/old/new/g        # Replace in current line only
:%s/\<word\>/new/g  # Replace whole words only
```

### Visual Selection Replace
1. Select text with `V` (line) or `v` (character)
2. Type `:s/old/new/g` - replaces only in selection

### Advanced Pattern Matching
```vim
:%s/pattern.*/replacement/g    # Replace from pattern to end of line
:%s/^/prefix/g                 # Add prefix to all lines
:%s/$/suffix/g                 # Add suffix to all lines
```

## Search Highlighting Control

### Clear Highlights
- `:noh` or `:nohlsearch` - Clear current search highlights
- `/` then `Enter` - Search for nothing (clears highlights)

### Toggle Highlighting
- `:set hlsearch!` - Toggle search highlighting on/off
- `:set hlsearch` - Turn on search highlighting
- `:set nohlsearch` - Turn off search highlighting

## Tab Management

### Opening Files in Tabs
```bash
nvim -p file1.txt file2.txt file3.txt  # Open files in separate tabs
```

### Tab Navigation
- `gt` - Go to next tab
- `gT` - Go to previous tab
- `<number>gt` - Go to specific tab number (e.g., `2gt`)
- `:tabn` - Next tab
- `:tabp` - Previous tab

### Tab Operations
- `:tabnew` - Create new tab
- `:tabclose` - Close current tab
- `:tabonly` - Close all tabs except current

## Useful Configuration Snippets

### For ~/.config/nvim/init.vim
```vim
" Clear highlights with double Esc
nnoremap <Esc><Esc> :nohlsearch<CR>

" Toggle search highlighting
nnoremap <leader>h :set hlsearch!<CR>

" Quick buffer navigation
nnoremap <leader>n :bnext<CR>
nnoremap <leader>p :bprev<CR>
```

### For ~/.config/nvim/init.lua
```lua
-- Clear highlights with double Esc
vim.keymap.set('n', '<Esc><Esc>', ':nohlsearch<CR>', { silent = true })

-- Toggle search highlighting
vim.keymap.set('n', '<leader>h', ':set hlsearch!<CR>')

-- Quick buffer navigation
vim.keymap.set('n', '<leader>n', ':bnext<CR>')
vim.keymap.set('n', '<leader>p', ':bprev<CR>')
```

## Quick Tips

- Use `:b` + Tab to cycle through buffer names with auto-completion
- The `*` + `cgn` + `.` workflow is fastest for multiple word changes
- `Ctrl+6` is the quickest way to switch between two files
- Use `:set number` to show line numbers for easier navigation
- Press `q:` to open command history for repeating complex commands

## Common Workflows

### Multi-file Editing
1. Open files: `nvim file1.txt file2.txt file3.txt`
2. Check what's loaded: `:ls`
3. Switch between files: `:bn`, `:bp`, or `:b<number>`
4. Make changes and save: `:w`

### Find and Replace Across Buffers
1. `:bufdo %s/old/new/ge` - Replace in all buffers
2. `:bufdo update` - Save all modified buffers

### Quick Word Changes
1. Cursor on word → `*` → `cgn` → type new word → `Esc` → `.` → `.` → ...

> in nvim how to select an whole paragraph or function and then also use indent  

✦ Of course. In Neovim (and Vim), this is a classic combination of Visual Mode and text objects.

  Here’s the breakdown:

  ### 1. Selecting a Paragraph

  The text object for a paragraph is p.


   * ap means "a paragraph". It selects the entire paragraph, including the blank line after it.
  Command:
  To select a whole paragraph, move your cursor inside it and in Normal mode, type:

  `
  vap
  `

  *   v enters Visual mode.
  *   ap is the text object you are selecting.

  ### 2. Selecting a Function


  This can depend on the programming language, but for languages that use curly braces {} (like C, Java,
  JavaScript, Rust, etc.), you can use the brace text objects.


   * a{ or aB selects "a block" (including the braces).
  If your function isn't defined by {} (like in Python), you can often still use paragraph selection (vap)
  or use Visual Line mode (V) and then use movement keys like } to move down by blocks until the function is
   selected.

  ### 3. Indenting the Selection

  Once you have any text selected in Visual mode (from the steps above), you can indent it.


   * > indent the selection one level.
  Putting It All Together: Workflow
   1. Place your cursor anywhere inside the function's curly braces.