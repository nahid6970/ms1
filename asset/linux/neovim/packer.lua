--Packer Package Manager
--C:\Users\nahid\scoop\apps\neovim\current\bin\lua

-- This file can be loaded by calling `lua require('plugins')` from your init.vim

-- Only required if you have packer configured as `opt`
vim.cmd [[packadd packer.nvim]]

return require('packer').startup(function(use)
-- Packer can manage itself
use 'wbthomason/packer.nvim'
use {'nvim-telescope/telescope.nvim', tag = '0.1.3', requires = { {'nvim-lua/plenary.nvim'} }}
use {"folke/which-key.nvim", config = function() vim.o.timeout = true vim.o.timeoutlen = 300 require("which-key").setup { } end}
use ('nvim-treesitter/nvim-treesitter', { run =':TSUpdate'})
use ('nvim-lua/plenary.nvim') 
use ('ThePrimeagen/harpoon')
use {"EdenEast/nightfox.nvim"} -- Packer



end)
