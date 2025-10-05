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
        { "<leader>f", group = "File" },
        { "<leader>ff", ":e ", desc = "Find file", mode = "n" },
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
        { "<leader>sn", "n", desc = "Next match", mode = "n" },
        { "<leader>sp", "N", desc = "Previous match", mode = "n" },
        { "<leader>sc", ":nohl<CR>", desc = "Clear search", mode = "n" },
        
        { "<leader>e", group = "Edit" },
        { "<leader>er", ":%s/", desc = "Replace in file", mode = "n" },
        { "<leader>el", ":s/", desc = "Replace in line", mode = "n" },
        { "<leader>eu", "u", desc = "Undo", mode = "n" },
        { "<leader>er", "<C-r>", desc = "Redo", mode = "n" },
        
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
        
        { "<leader>c", group = "Code" },
        { "<leader>cc", "gcc", desc = "Comment line", mode = "n", remap = true },
        { "<leader>cb", "gbc", desc = "Comment block", mode = "n", remap = true },
        { "<leader>cd", "<C-S-d>", desc = "Duplicate line", mode = "n" },
        
        { "<leader>m", group = "Multi-cursor" },
        { "<leader>md", "<C-d>", desc = "Select next occurrence", mode = "n" },
        { "<leader>mk", "<C-k>", desc = "Skip current", mode = "n" },
        { "<leader>mq", "<C-q>", desc = "Remove selection", mode = "n" },
        { "<leader>ma", "<C-S-a>", desc = "Select all occurrences", mode = "n" },
      })
      
      -- Visual mode mappings
      wk.add({
        { "<leader>c", "gc", desc = "Comment selection", mode = "v", remap = true },
        { "<leader>r", ":s/", desc = "Replace in selection", mode = "v" },
        { "<leader>y", "y", desc = "Yank selection", mode = "v" },
        { "<leader>d", "d", desc = "Delete selection", mode = "v" },
      })
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
  
  -- Optional: Better syntax highlighting (with Windows compatibility)
  {
    "nvim-treesitter/nvim-treesitter",
    build = function()
      -- Check if we're on Windows and have a C compiler
      if vim.fn.has("win32") == 1 then
        -- Try to use zig as compiler if available, otherwise skip
        if vim.fn.executable("zig") == 1 then
          vim.cmd("TSUpdate")
        else
          -- Silently skip compilation if no compiler found
        end
      else
        vim.cmd("TSUpdate")
      end
    end,
    config = function()
      -- Only setup if treesitter loaded successfully
      local status_ok, treesitter = pcall(require, "nvim-treesitter.configs")
      if not status_ok then
        return
      end
      
      treesitter.setup({
        ensure_installed = {},  -- Don't auto-install on Windows
        auto_install = false,   -- Disable auto-install to prevent errors
        highlight = {
          enable = true,
          additional_vim_regex_highlighting = false,
        },
        indent = {
          enable = true,
        },
      })
    end
  }
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

