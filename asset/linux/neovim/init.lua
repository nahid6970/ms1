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
  -- {'EdenEast/nightfox.nvim' },
  {'L3MON4D3/LuaSnip'},
  {'MunifTanjim/nui.nvim'},
  {'NvChad/nvim-colorizer.lua'},
  {'ThePrimeagen/harpoon'},
  {'VonHeikemen/lsp-zero.nvim', branch = 'v2.x'},
  {'crusj/bookmarks.nvim', keys = {{ "<tab><tab>", mode = { "n" } }}, branch = 'main', config = function() 
      require("bookmarks").setup() 
      require("telescope").load_extension("bookmarks") 
    end
  },
  {'folke/neodev.nvim'},
  -- {'folke/tokyonight.nvim'},
  {'folke/trouble.nvim'},
  {'folke/which-key.nvim', event = "VeryLazy", init = function() 
      vim.o.timeout = true 
      vim.o.timeoutlen = 300 
    end, opts = {}
  },
  {'hrsh7th/cmp-nvim-lsp'},
  {'hrsh7th/nvim-cmp'},
  {'kdheepak/lazygit.nvim'},
  {'kylechui/nvim-surround', version = "*", event = "VeryLazy", config = function() 
      require("nvim-surround").setup({ }) 
    end
  },
  {'mg979/vim-visual-multi', branch = 'master'},
  {'neovim/nvim-lspconfig'},
  {'nvim-lua/plenary.nvim'},
  {'nvim-lualine/lualine.nvim'},
  {'nvim-neo-tree/neo-tree.nvim', branch = "v3.x"},
  {'nvim-telescope/telescope.nvim', tag = '0.1.3', config = function()
      require('telescope').setup{
        defaults = {
          mappings = {
            i = { ["<C-h>"] = "which_key" } -- Example for Telescope key mappings
          },
        },
      }
    end
  },
  {'nvim-tree/nvim-web-devicons'},
  {'nvim-treesitter/nvim-treesitter', build = ":TSUpdate"},
  {'nvim-treesitter/playground'},
  {'rafamadriz/friendly-snippets'},
  {'roobert/surround-ui.nvim', config = function() 
      require("surround-ui").setup({ root_key = "S" }) 
    end
  },
  {'saadparwaiz1/cmp_luasnip'},
  {'startup-nvim/startup.nvim', config = function() require("startup").setup() end}, -- Intro
  {'sunjon/shade.nvim'},
  {'williamboman/mason-lspconfig.nvim'},
  {'williamboman/mason.nvim'},
  {'yorik1984/lualine-theme.nvim'},
  {'akinsho/bufferline.nvim', version = "*"},
})
-- Set space as the leader key
vim.g.mapleader = " "

-- Key mappings using which-key
local wk = require("which-key")
wk.add({
  { "<leader>f", group = "file" }, -- group
  { "<leader>ff", "<cmd>Telescope find_files<cr>", desc = "Find File", mode = "n" },
  { "<leader>fb", function() print("hello") end, desc = "Foobar" },
  { "<leader>fn", desc = "New File" },
  { "<leader>f1", hidden = true }, -- hide this keymap
  { "<leader>fe", function() vim.cmd("Ex") end, desc = "Explorer" }, -- hide this keymap
  { "<leader>fn", function() vim.cmd("Neotree") end, desc = "NeoTree Explorer" }, -- hide this keymap



  { "<leader>w", proxy = "<c-w>", group = "windows" }, -- proxy to window mappings
  { "<leader>b", group = "buffers", expand = function() return require("which-key.extras").expand.buf() end },
  {
    -- Nested mappings are allowed and can be added in any order
    -- Most attributes can be inherited or overridden on any level
    -- There's no limit to the depth of nesting
    mode = { "n", "v" }, -- NORMAL and VISUAL mode
    { "<leader>q", "<cmd>q!<cr>", desc = "Quit!" }, -- no need to specify mode since it's inherited
    { "<leader>w", "<cmd>w<cr>", desc = "Write" },
  }
})


--Help key suggestion--
vim.cmd([[
  function! FunctionalKeys()
    echohl Function
    echom "! = +Filter throug external progrem-->sent to a command and replace with output"
    echom "' = +Mark"
    echom "* = Highlight Similar Words"
    echom "<Ctrl-v> = Visual Block mode"
    echom "Double quotation = +registers"
    echom "V = +Visual Line mode"
    echom "[] = Go to Matched Items i.e (),{},[]"
    echom "c = +Change(Delete+Insert-Mode)"
    echom "d = +Delete"
    echom "g = +Character-Modification"
    echom "ggvG = ->Go to to first line -> insert selectmode/visualselect -> Go to Last line / Select whole Doc"
    echom "o = Isert Blank Line + Insert Mode"
    echom "v = +Visual-Mode / Select-Mode"
    echom "xGvyG:sort = Sort lines from x to y [x & y is variable]"
    echom "y = +Yank(Copy)"
    echom "z = +Fold ❤️  "
    echom "v to select mode then doublequota & + & y to copy to sysclipboard"
    echom "% on ()/{}/[]= Rotate cursor between matching () {} [] brackets"
    echohl None
  endfunction
]])
vim.keymap.set("n", "<leader><leader>", ":call FunctionalKeys()<CR>", { noremap = true, silent = true })
