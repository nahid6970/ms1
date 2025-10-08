-- Neovim configuration with VS Code-like keybindings
-- Single file config for line movement, copying, and multi-cursor selection

-- Basic settings
vim.opt.number = true
vim.opt.relativenumber = true
vim.opt.expandtab = true
vim.opt.shiftwidth = 2
vim.opt.tabstop = 2
vim.opt.smartindent = true
vim.opt.wrap = false
vim.opt.ignorecase = true
vim.opt.smartcase = true
vim.opt.hlsearch = true
vim.opt.incsearch = true

-- Leader key
vim.g.mapleader = " "

-- Disable unused providers to clean up health check
vim.g.loaded_node_provider = 0
vim.g.loaded_perl_provider = 0
vim.g.loaded_ruby_provider = 0

-- Immediately set filetype for current buffer if empty
if vim.bo.filetype == '' then
  vim.bo.filetype = 'text'
end

-- Function to move lines up/down
local function move_line(direction)
  local line_count = vim.fn.line('$')
  local current_line = vim.fn.line('.')
  
  if direction == 'up' and current_line > 1 then
    vim.cmd('move .-2')
  elseif direction == 'down' and current_line < line_count then
    vim.cmd('move .+1')
  end
end

-- Function to move visual selection up/down
local function move_visual_selection(direction)
  local start_line = vim.fn.line("'<")
  local end_line = vim.fn.line("'>")
  local line_count = vim.fn.line('$')
  
  if direction == 'up' and start_line > 1 then
    vim.cmd("'<,'>move '<-2")
  elseif direction == 'down' and end_line < line_count then
    vim.cmd("'<,'>move '>+1")
  end
  
  -- Reselect the moved text
  vim.cmd("normal! gv")
end

-- Function to copy lines up/down
local function copy_line(direction)
  local current_line = vim.fn.line('.')
  local line_content = vim.fn.getline('.')
  
  if direction == 'up' then
    vim.fn.append(current_line - 1, line_content)
    vim.cmd('normal! k')
  else
    vim.fn.append(current_line, line_content)
    vim.cmd('normal! j')
  end
end

-- Function to copy visual selection up/down
local function copy_visual_selection(direction)
  -- Get the visual selection
  vim.cmd('normal! gv')  -- Restore visual selection
  vim.cmd('normal! y')   -- Yank the selection
  
  local start_line = vim.fn.line("'<")
  local end_line = vim.fn.line("'>")
  
  if direction == 'up' then
    -- Go to start of selection and paste above
    vim.fn.cursor(start_line, 1)
    vim.cmd('normal! O')  -- Open line above
    vim.cmd('normal! P')  -- Paste above
    vim.cmd('normal! k')  -- Move to pasted content
    -- Reselect the pasted content
    vim.cmd('normal! V' .. (end_line - start_line) .. 'j')
  else
    -- Go to end of selection and paste below
    vim.fn.cursor(end_line, 1)
    vim.cmd('normal! o')  -- Open line below
    vim.cmd('normal! P')  -- Paste below
    -- Reselect the pasted content
    vim.cmd('normal! V' .. (end_line - start_line) .. 'j')
  end
end

-- Alt + Up/Down: Move lines
vim.keymap.set('n', '<A-Up>', function() move_line('up') end, { desc = 'Move line up' })
vim.keymap.set('n', '<A-Down>', function() move_line('down') end, { desc = 'Move line down' })
vim.keymap.set('v', '<A-Up>', function() move_visual_selection('up') end, { desc = 'Move selection up' })
vim.keymap.set('v', '<A-Down>', function() move_visual_selection('down') end, { desc = 'Move selection down' })

-- Alt + Shift + Up/Down: Copy lines (multiple key notations for Windows compatibility)
vim.keymap.set('n', '<A-S-Up>', function() copy_line('up') end, { desc = 'Copy line up' })
vim.keymap.set('n', '<A-S-Down>', function() copy_line('down') end, { desc = 'Copy line down' })
vim.keymap.set('v', '<A-S-Up>', function() copy_visual_selection('up') end, { desc = 'Copy selection up' })
vim.keymap.set('v', '<A-S-Down>', function() copy_visual_selection('down') end, { desc = 'Copy selection down' })

-- Alternative keybindings for Alt+Shift (Windows compatibility)
vim.keymap.set('n', '<M-S-Up>', function() copy_line('up') end, { desc = 'Copy line up' })
vim.keymap.set('n', '<M-S-Down>', function() copy_line('down') end, { desc = 'Copy line down' })
vim.keymap.set('v', '<M-S-Up>', function() copy_visual_selection('up') end, { desc = 'Copy selection up' })
vim.keymap.set('v', '<M-S-Down>', function() copy_visual_selection('down') end, { desc = 'Copy selection down' })

-- Additional alternative using Ctrl+Alt for copying (more reliable on Windows)
vim.keymap.set('n', '<C-A-Up>', function() copy_line('up') end, { desc = 'Copy line up (Ctrl+Alt)' })
vim.keymap.set('n', '<C-A-Down>', function() copy_line('down') end, { desc = 'Copy line down (Ctrl+Alt)' })
vim.keymap.set('v', '<C-A-Up>', function() copy_visual_selection('up') end, { desc = 'Copy selection up (Ctrl+Alt)' })
vim.keymap.set('v', '<C-A-Down>', function() copy_visual_selection('down') end, { desc = 'Copy selection down (Ctrl+Alt)' })

-- Multi-cursor functionality using vim-visual-multi plugin
-- First, let's set up a simple package manager (lazy.nvim)
local lazypath = vim.fn.stdpath("data") .. "/lazy/lazy.nvim"
if not vim.loop.fs_stat(lazypath) then
  local result = vim.fn.system({
    "git",
    "clone",
    "--filter=blob:none",
    "https://github.com/folke/lazy.nvim.git",
    "--branch=stable",
    lazypath,
  })
  if vim.v.shell_error ~= 0 then
    return
  end
end
vim.opt.rtp:prepend(lazypath)

-- Plugin setup with error handling
local lazy_ok, lazy = pcall(require, "lazy")
if not lazy_ok then
  return
end

lazy.setup({
  -- Icons for file types and UI
  {
    "nvim-tree/nvim-web-devicons",
    config = function()
      require("nvim-web-devicons").setup()
    end
  },

  -- Which-key for keybinding hints
  {
    "folke/which-key.nvim",
    event = "VeryLazy",
    config = function()
      local wk = require("which-key")
      
      wk.setup({
        preset = "modern",
        delay = 300,
        expand = 1,
        notify = false,
        replace = {
          ["<leader>"] = "SPC",
          ["<cr>"] = "RET",
          ["<tab>"] = "TAB",
        },
      })

      -- Leader key mappings
      wk.add({
        { "<leader>f", group = "File & Find" },
        { "<leader>ff", ":Files<CR>", desc = "Find files (FZF)", mode = "n" },
        { "<leader>fg", ":GFiles<CR>", desc = "Find git files", mode = "n" },
        { "<leader>fr", ":History<CR>", desc = "Recent files", mode = "n" },
        { "<leader>fb", ":Buffers<CR>", desc = "Find buffers", mode = "n" },
        { "<leader>fl", ":BLines<CR>", desc = "Find lines in current buffer", mode = "n" },
        { "<leader>fL", ":Lines<CR>", desc = "Find lines in all buffers", mode = "n" },
        { "<leader>ft", ":Filetypes<CR>", desc = "Select filetype", mode = "n" },
        { "<leader>fs", ":w<CR>", desc = "Save file", mode = "n" },
        { "<leader>fq", ":q<CR>", desc = "Quit", mode = "n" },
        { "<leader>fx", ":x<CR>", desc = "Save and quit", mode = "n" },
        { "<leader>fn", ":enew<CR>", desc = "New file", mode = "n" },
        
        { "<leader>b", group = "Buffer" },
        { "<leader>bd", ":bd<CR>", desc = "Delete buffer", mode = "n" },
        { "<leader>bn", ":bnext<CR>", desc = "Next buffer", mode = "n" },
        { "<leader>bp", ":bprev<CR>", desc = "Previous buffer", mode = "n" },
        { "<leader>bl", ":ls<CR>", desc = "List buffers", mode = "n" },
        
        { "<leader>w", group = "Window" },
        { "<leader>wh", "<C-w>h", desc = "Go to left window", mode = "n" },
        { "<leader>wj", "<C-w>j", desc = "Go to bottom window", mode = "n" },
        { "<leader>wk", "<C-w>k", desc = "Go to top window", mode = "n" },
        { "<leader>wl", "<C-w>l", desc = "Go to right window", mode = "n" },
        { "<leader>ws", "<C-w>s", desc = "Split horizontal", mode = "n" },
        { "<leader>wv", "<C-w>v", desc = "Split vertical", mode = "n" },
        { "<leader>wc", "<C-w>c", desc = "Close window", mode = "n" },
        { "<leader>wo", "<C-w>o", desc = "Close other windows", mode = "n" },
        
        { "<leader>s", group = "Search" },
        { "<leader>sf", "/", desc = "Search forward", mode = "n" },
        { "<leader>sb", "?", desc = "Search backward", mode = "n" },
        { "<leader>sg", ":Rg<CR>", desc = "Search with ripgrep", mode = "n" },
        { "<leader>sw", ":Rg <C-R><C-W><CR>", desc = "Search word under cursor", mode = "n" },
        { "<leader>sl", ":BLines<CR>", desc = "Search lines in current buffer", mode = "n" },
        { "<leader>sL", ":Lines<CR>", desc = "Search lines in all buffers", mode = "n" },
        { "<leader>sh", ":Helptags<CR>", desc = "Search help tags", mode = "n" },
        { "<leader>sc", ":Commands<CR>", desc = "Search commands", mode = "n" },
        { "<leader>sk", ":Maps<CR>", desc = "Search keymaps", mode = "n" },
        { "<leader>sn", "n", desc = "Next match", mode = "n" },
        { "<leader>sp", "N", desc = "Previous match", mode = "n" },
        { "<leader>sx", ":nohl<CR>", desc = "Clear search", mode = "n" },
        
        { "<leader>e", group = "Edit" },
        { "<leader>er", ":%s/", desc = "Replace in file", mode = "n" },
        { "<leader>el", ":s/", desc = "Replace in line", mode = "n" },
        { "<leader>eu", "u", desc = "Undo", mode = "n" },
        { "<leader>eR", "<C-r>", desc = "Redo", mode = "n" },
        
        { "<leader>g", group = "Go to" },
        { "<leader>gg", "gg", desc = "Go to top", mode = "n" },
        { "<leader>gG", "G", desc = "Go to bottom", mode = "n" },
        { "<leader>gl", "$", desc = "Go to end of line", mode = "n" },
        { "<leader>gh", "0", desc = "Go to start of line", mode = "n" },
        
        { "<leader>t", group = "Toggle" },
        { "<leader>tn", ":set number!<CR>", desc = "Toggle line numbers", mode = "n" },
        { "<leader>tr", ":set relativenumber!<CR>", desc = "Toggle relative numbers", mode = "n" },
        { "<leader>tw", ":set wrap!<CR>", desc = "Toggle word wrap", mode = "n" },
        { "<leader>th", ":set hlsearch!<CR>", desc = "Toggle search highlight", mode = "n" },
        { "<leader>tf", ":filetype detect<CR>", desc = "Detect filetype", mode = "n" },
        { "<leader>ti", function() print("Filetype: " .. vim.bo.filetype) end, desc = "Show filetype info", mode = "n" },
        
        { "<leader>c", group = "Code" },
        { "<leader>cc", "gcc", desc = "Comment line", mode = "n", remap = true },
        { "<leader>cb", "gbc", desc = "Comment block", mode = "n", remap = true },
        { "<leader>cd", "<C-S-d>", desc = "Duplicate line", mode = "n" },
        
        { "<leader>m", group = "Multi-cursor" },
        { "<leader>md", "<C-d>", desc = "Select next occurrence", mode = "n" },
        { "<leader>mk", "<C-k>", desc = "Skip current", mode = "n" },
        { "<leader>mq", "<C-q>", desc = "Remove selection", mode = "n" },
        { "<leader>ma", "<C-S-a>", desc = "Select all occurrences", mode = "n" },
        
        { "<leader>h", group = "Harpoon" },
        { "<leader>ha", function() require("harpoon"):list():add() end, desc = "Add file to harpoon", mode = "n" },
        { "<leader>hh", function() require("harpoon").ui:toggle_quick_menu(require("harpoon"):list()) end, desc = "Toggle harpoon menu", mode = "n" },
        { "<leader>h1", function() require("harpoon"):list():select(1) end, desc = "Go to harpoon file 1", mode = "n" },
        { "<leader>h2", function() require("harpoon"):list():select(2) end, desc = "Go to harpoon file 2", mode = "n" },
        { "<leader>h3", function() require("harpoon"):list():select(3) end, desc = "Go to harpoon file 3", mode = "n" },
        { "<leader>h4", function() require("harpoon"):list():select(4) end, desc = "Go to harpoon file 4", mode = "n" },
        { "<leader>hn", function() require("harpoon"):list():next() end, desc = "Next harpoon file", mode = "n" },
        { "<leader>hp", function() require("harpoon"):list():prev() end, desc = "Previous harpoon file", mode = "n" },
        
        { "<leader>k", group = "Bookmarks" },
        { "<leader>ka", function() require("bookmarks").add_bookmarks() end, desc = "Add bookmark", mode = "n" },
        { "<leader>kk", function() require("bookmarks").toggle_bookmarks() end, desc = "Toggle bookmarks", mode = "n" },
        { "<leader>kd", function() require("bookmarks").delete_on_virt() end, desc = "Delete bookmark", mode = "n" },
        { "<leader>kc", function() require("bookmarks").delete_all_bookmarks() end, desc = "Clear all bookmarks", mode = "n" },
      })
      
      -- Visual mode mappings
      wk.add({
        { "<leader>c", "gc", desc = "Comment selection", mode = "v", remap = true },
        { "<leader>r", ":s/", desc = "Replace in selection", mode = "v" },
        { "<leader>y", "y", desc = "Yank selection", mode = "v" },
        { "<leader>d", "d", desc = "Delete selection", mode = "v" },
      })
      
      -- Visual mode space menu for selected text operations
      wk.add({
        { " ", group = "Selected Text", mode = "v" },
        { " s", function()
            -- Get selected text
            vim.cmd('normal! "vy')
            local selected = vim.fn.getreg('v')
            -- Start multi-cursor on selected text
            vim.cmd('normal! gv')
            vim.fn.feedkeys('\\<Plug>(VM-Find-Under)')
          end, desc = "Select all matching", mode = "v" },
        { " r", function()
            -- Get selected text and start replace
            vim.cmd('normal! "vy')
            local selected = vim.fn.getreg('v')
            vim.fn.feedkeys(':%s/' .. vim.fn.escape(selected, '/\\') .. '/')
          end, desc = "Replace all occurrences", mode = "v" },
        { " f", function()
            -- Search for selected text
            vim.cmd('normal! "vy')
            local selected = vim.fn.getreg('v')
            vim.fn.setreg('/', selected)
            vim.cmd('normal! n')
          end, desc = "Find next occurrence", mode = "v" },
        { " g", function()
            -- Search selected text with FZF
            vim.cmd('normal! "vy')
            local selected = vim.fn.getreg('v')
            vim.cmd('Rg ' .. vim.fn.shellescape(selected))
          end, desc = "Search in files", mode = "v" },
        { " c", "gc", desc = "Comment selection", mode = "v", remap = true },
        { " y", "y", desc = "Copy selection", mode = "v" },
        { " d", "d", desc = "Delete selection", mode = "v" },
        { " u", "u", desc = "Lowercase", mode = "v" },
        { " U", "U", desc = "Uppercase", mode = "v" },
        { " w", function()
            -- Wrap selection with characters
            vim.ui.input({ prompt = 'Wrap with (e.g., ", \', (, [, {): ' }, function(wrapper)
              if wrapper and wrapper ~= '' then
                local close_map = {
                  ['('] = ')', ['['] = ']', ['{'] = '}', 
                  ['<'] = '>', ['"'] = '"', ["'"] = "'", ['`'] = '`'
                }
                local close = close_map[wrapper] or wrapper
                vim.cmd('normal! `<i' .. wrapper .. '\\<Esc>`>a' .. close .. '\\<Esc>')
              end
            end)
          end, desc = "Wrap with characters", mode = "v" },
      })
    end
  },
  
  -- Harpoon for quick file navigation
  {
    "ThePrimeagen/harpoon",
    branch = "harpoon2",
    dependencies = { "nvim-lua/plenary.nvim" },
    config = function()
      local harpoon = require("harpoon")
      harpoon:setup({
        settings = {
          save_on_toggle = true,
          sync_on_ui_close = true,
          key = function()
            return "C:\\Users\\nahid"
          end,
        },
      })
    end
  },

  -- Simple bookmark system
  {
    "crusj/bookmarks.nvim",
    keys = {{ "<tab><tab>", mode = { "n" } }},
    branch = "main",
    config = function()
      require("bookmarks").setup({
        storage_dir = "C:\\Users\\nahid\\.nvim-bookmarks",
        mappings_enabled = true,
        keymap = {
          toggle = "<tab><tab>",
          close = "q",
          delete = "dd",
          order = "<space>o",
        }
      })
    end
  },

  -- FZF for fuzzy file finding
  {
    "junegunn/fzf",
    build = ":call fzf#install()"
  },
  
  {
    "junegunn/fzf.vim",
    dependencies = { "junegunn/fzf" },
    config = function()
      -- FZF configuration
      vim.g.fzf_preview_window = {'right:50%', 'ctrl-/'}
      vim.g.fzf_layout = { window = { width = 0.9, height = 0.6 } }
      
      -- Custom FZF colors to match theme
      vim.g.fzf_colors = {
        fg = {'fg', 'Normal'},
        bg = {'bg', 'Normal'},
        hl = {'fg', 'Comment'},
        ['fg+'] = {'fg', 'CursorLine', 'CursorColumn', 'Normal'},
        ['bg+'] = {'bg', 'CursorLine', 'CursorColumn'},
        ['hl+'] = {'fg', 'Statement'},
        info = {'fg', 'PreProc'},
        border = {'fg', 'Ignore'},
        prompt = {'fg', 'Conditional'},
        pointer = {'fg', 'Exception'},
        marker = {'fg', 'Keyword'},
        spinner = {'fg', 'Label'},
        header = {'fg', 'Comment'}
      }
    end
  },

  -- Multi-cursor plugin for Ctrl+D functionality
  {
    "mg979/vim-visual-multi",
    init = function()
      -- Configure vim-visual-multi before it loads
      vim.g.VM_default_mappings = 0  -- Disable default mappings
      vim.g.VM_maps = {
        ["Find Under"] = '<C-d>',           -- Ctrl+D to select word under cursor
        ["Find Subword Under"] = '<C-d>',   -- Same for subwords
        ["Select All"] = '<C-S-a>',         -- Ctrl+Shift+A to select all occurrences
        ["Skip Region"] = '<C-k>',          -- Ctrl+K to skip current and find next
        ["Remove Region"] = '<C-q>',        -- Ctrl+Q to remove current selection
        ["Add Cursor Down"] = '<C-j>',      -- Ctrl+J for cursor down (avoid conflict)
        ["Add Cursor Up"] = '<C-u>',        -- Ctrl+U for cursor up (avoid conflict)
      }
      
      -- Additional VM settings for better VS Code-like behavior
      vim.g.VM_theme = 'iceblue'
      vim.g.VM_highlight_matches = 'underline'
      vim.g.VM_silent_exit = 1
      vim.g.VM_show_warnings = 0
    end,
    config = function()
      -- Additional configuration after plugin loads
    end
  },
  

}, {
  -- Lazy.nvim configuration
  rocks = {
    enabled = false,  -- Disable luarocks support to avoid warnings
  },
})

-- Additional useful keybindings similar to VS Code
vim.keymap.set('n', '<C-s>', ':w<CR>', { desc = 'Save file' })
vim.keymap.set('i', '<C-s>', '<Esc>:w<CR>a', { desc = 'Save file in insert mode' })
vim.keymap.set('n', '<C-z>', 'u', { desc = 'Undo' })
vim.keymap.set('n', '<C-y>', '<C-r>', { desc = 'Redo' })
vim.keymap.set('n', '<C-a>', 'ggVG', { desc = 'Select all' })
vim.keymap.set('n', '<C-f>', '/', { desc = 'Find' })

-- Line duplication (Ctrl+Shift+D like in VS Code)
vim.keymap.set('n', '<C-S-d>', 'yyp', { desc = 'Duplicate line' })
vim.keymap.set('v', '<C-S-d>', 'y`>p', { desc = 'Duplicate selection' })

-- Comment toggle (Ctrl+/)
vim.keymap.set('n', '<C-/>', 'gcc', { desc = 'Toggle comment', remap = true })
vim.keymap.set('v', '<C-/>', 'gc', { desc = 'Toggle comment', remap = true })

-- Quick access keybindings (non-leader)
vim.keymap.set('n', '<Esc>', ':nohl<CR>', { desc = 'Clear search highlight', silent = true })
vim.keymap.set('n', 'H', '^', { desc = 'Go to first non-blank character' })
vim.keymap.set('n', 'L', '$', { desc = 'Go to end of line' })
vim.keymap.set('n', 'Y', 'y$', { desc = 'Yank to end of line' })

-- Better window navigation
vim.keymap.set('n', '<C-h>', '<C-w>h', { desc = 'Go to left window' })
vim.keymap.set('n', '<C-j>', '<C-w>j', { desc = 'Go to bottom window' })
vim.keymap.set('n', '<C-k>', '<C-w>k', { desc = 'Go to top window' })
vim.keymap.set('n', '<C-l>', '<C-w>l', { desc = 'Go to right window' })

-- Buffer navigation
vim.keymap.set('n', '<Tab>', ':bnext<CR>', { desc = 'Next buffer' })
vim.keymap.set('n', '<S-Tab>', ':bprev<CR>', { desc = 'Previous buffer' })

-- Quick access keybindings
vim.keymap.set('n', '<C-p>', ':Files<CR>', { desc = 'Find files (FZF)' })
vim.keymap.set('n', '<C-e>', function() require("harpoon").ui:toggle_quick_menu(require("harpoon"):list()) end, { desc = 'Toggle harpoon menu' })
vim.keymap.set('n', '<C-b>', function() require("bookmarks").toggle_bookmarks() end, { desc = 'Toggle bookmarks' })
vim.keymap.set('n', '<C-g>', ':Rg<CR>', { desc = 'Search with ripgrep' })

-- Harpoon quick access
vim.keymap.set('n', '<C-1>', function() require("harpoon"):list():select(1) end, { desc = 'Harpoon file 1' })
vim.keymap.set('n', '<C-2>', function() require("harpoon"):list():select(2) end, { desc = 'Harpoon file 2' })
vim.keymap.set('n', '<C-3>', function() require("harpoon"):list():select(3) end, { desc = 'Harpoon file 3' })
vim.keymap.set('n', '<C-4>', function() require("harpoon"):list():select(4) end, { desc = 'Harpoon file 4' })

-- Enable built-in syntax highlighting and filetype detection
vim.cmd('syntax enable')
vim.cmd('filetype plugin indent on')
vim.opt.syntax = 'on'

-- Better filetype detection
vim.filetype.add({
  extension = {
    js = 'javascript',
    jsx = 'javascriptreact',
    ts = 'typescript',
    tsx = 'typescriptreact',
    py = 'python',
    lua = 'lua',
    html = 'html',
    css = 'css',
    scss = 'scss',
    sass = 'sass',
    json = 'json',
    md = 'markdown',
    yml = 'yaml',
    yaml = 'yaml',
    toml = 'toml',
    xml = 'xml',
    sh = 'sh',
    bash = 'bash',
    zsh = 'zsh',
    ps1 = 'ps1',
    psm1 = 'ps1',
    psd1 = 'ps1',
    vim = 'vim',
    txt = 'text',
  },
  filename = {
    ['.gitignore'] = 'gitignore',
    ['.env'] = 'sh',
    ['Dockerfile'] = 'dockerfile',
    ['docker-compose.yml'] = 'yaml',
    ['docker-compose.yaml'] = 'yaml',
  },
  pattern = {
    ['.*%.env%..*'] = 'sh',
    ['.*%.config%.js'] = 'javascript',
    ['.*%.config%.ts'] = 'typescript',
  },
})

-- Force filetype detection on buffer enter
vim.api.nvim_create_autocmd({'BufRead', 'BufNewFile'}, {
  pattern = '*',
  callback = function()
    vim.cmd('filetype detect')
  end,
})

-- Set default filetype for empty/new buffers
vim.api.nvim_create_autocmd({'BufEnter', 'BufNewFile'}, {
  pattern = '*',
  callback = function()
    -- If buffer has no name and no filetype, it's likely an empty buffer
    if vim.bo.filetype == '' then
      if vim.fn.expand('%') == '' then
        -- Empty buffer (no filename)
        vim.bo.filetype = 'text'
      else
        -- File with name but no detected filetype
        vim.bo.filetype = 'text'
      end
    end
  end,
})

-- Ensure filetype is set immediately on startup
vim.api.nvim_create_autocmd('VimEnter', {
  callback = function()
    if vim.bo.filetype == '' then
      vim.bo.filetype = 'text'
    end
  end,
})

-- Force filetype to never be empty
vim.api.nvim_create_autocmd({'BufEnter', 'BufWinEnter', 'FileType'}, {
  pattern = '*',
  callback = function()
    vim.schedule(function()
      if vim.bo.filetype == '' or vim.bo.filetype == 'unknown' then
        vim.bo.filetype = 'text'
      end
    end)
  end,
})

-- Nice looking statusline
vim.opt.laststatus = 2  -- Always show status line

-- Define statusline colors
vim.api.nvim_set_hl(0, 'StatusLineMode', { fg = '#1e1e2e', bg = '#89b4fa', bold = true })
vim.api.nvim_set_hl(0, 'StatusLineFile', { fg = '#cdd6f4', bg = '#313244' })
vim.api.nvim_set_hl(0, 'StatusLineModified', { fg = '#f38ba8', bg = '#313244', bold = true })
vim.api.nvim_set_hl(0, 'StatusLineGit', { fg = '#a6e3a1', bg = '#313244' })
vim.api.nvim_set_hl(0, 'StatusLineInfo', { fg = '#89b4fa', bg = '#313244' })
vim.api.nvim_set_hl(0, 'StatusLinePosition', { fg = '#1e1e2e', bg = '#fab387', bold = true })
vim.api.nvim_set_hl(0, 'StatusLineFiletype', { fg = '#cba6f7', bg = '#313244' })

-- Function to get current mode with nice names
local function get_mode()
  local modes = {
    n = 'NORMAL',
    i = 'INSERT',
    v = 'VISUAL',
    V = 'V-LINE',
    [''] = 'V-BLOCK',
    c = 'COMMAND',
    s = 'SELECT',
    S = 'S-LINE',
    [''] = 'S-BLOCK',
    R = 'REPLACE',
    r = 'REPLACE',
    ['!'] = 'SHELL',
    t = 'TERMINAL'
  }
  return modes[vim.fn.mode()] or 'UNKNOWN'
end

-- Function to get git branch (simple version)
local function get_git_branch()
  local branch = vim.fn.system("git branch --show-current 2>/dev/null | tr -d '\n'")
  if vim.v.shell_error == 0 and branch ~= "" then
    return " " .. branch
  end
  return ""
end

-- Function to get file icon (simple version without devicons dependency)
local function get_file_icon()
  local filename = vim.fn.expand('%:t')
  local ext = vim.fn.expand('%:e')
  
  local icons = {
    lua = '🌙',
    js = '📜',
    ts = '📘',
    py = '🐍',
    html = '🌐',
    css = '🎨',
    json = '📋',
    md = '📝',
    txt = '📄',
    vim = '💚',
  }
  
  return icons[ext] or '📄'
end

-- Custom statusline function
local function statusline()
  local mode = get_mode()
  local file_icon = get_file_icon()
  local filename = vim.fn.expand('%:t')
  if filename == '' then filename = '[No Name]' end
  
  local modified = vim.bo.modified and ' ●' or ''
  local readonly = vim.bo.readonly and ' 🔒' or ''
  local git_branch = get_git_branch()
  local filetype = vim.bo.filetype ~= '' and vim.bo.filetype or 'text'
  local line = vim.fn.line('.')
  local col = vim.fn.col('.')
  local total_lines = vim.fn.line('$')
  local percentage = math.floor((line / total_lines) * 100)
  
  return table.concat({
    '%#StatusLineMode#',
    ' ' .. mode .. ' ',
    '%#StatusLineFile#',
    ' ' .. file_icon .. ' ' .. filename,
    '%#StatusLineModified#',
    modified,
    '%#StatusLineFile#',
    readonly,
    '%#StatusLineGit#',
    git_branch,
    '%=',  -- Right align from here
    '%#StatusLineInfo#',
    ' ' .. line .. ':' .. col .. ' ',
    '%#StatusLinePosition#',
    ' ' .. percentage .. '%% ',
    '%#StatusLineFiletype#',
    ' ' .. filetype .. ' ',
  })
end

-- Set the custom statusline
vim.opt.statusline = '%!v:lua.statusline()'

-- Make statusline function global
_G.statusline = statusline

