-- Lazy.nvim installation path
local lazypath = vim.fn.stdpath("data") .. "/lazy/lazy.nvim"
if not vim.loop.fs_stat(lazypath) then
  vim.fn.system({
    "git",
    "clone",
    "--filter=blob:none",
    "https://github.com/folke/lazy.nvim.git",
    "--branch=stable", -- latest stable release
    lazypath,
  })
end
vim.opt.rtp:prepend(lazypath)

-- Lazy.nvim setup with plugins
require("lazy").setup({
  -- Required dependencies
  {'nvim-lua/plenary.nvim'}, -- Required by Telescope

  -- Telescope plugin for fuzzy finding and more
  {'nvim-telescope/telescope.nvim', tag = '0.1.3', config = function()
    require('telescope').setup{
      defaults = {
        mappings = {
          i = { ["<C-h>"] = "which_key" } -- Example for Telescope key mappings
        },
      },
    }
  end},

  -- which-key plugin for shortcut hints
  {'folke/which-key.nvim', config = function()
    vim.o.timeout = true
    vim.o.timeoutlen = 300
    require("which-key").setup {}
  end},
})

-- Set space as the leader key
vim.g.mapleader = " "

-- Key mappings using which-key
local wk = require("which-key")

wk.register({
  ["<leader>"] = {
    f = {
      name = "File", -- Group name displayed in the popup
      f = { "<cmd>Telescope find_files<cr>", "Find Files" },
      g = { "<cmd>Telescope live_grep<cr>", "Live Grep" },
    },
    b = {
      name = "Buffer",
      l = { "<cmd>ls<cr>", "List Buffers" },
      d = { "<cmd>bd<cr>", "Delete Buffer" }
    },
    q = { "<cmd>q<cr>", "Quit" },
    w = { "<cmd>w<cr>", "Write" },
  },
}, { prefix = "<leader>" })
