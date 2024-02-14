how to use packer
add packages or use scripts to packer lua
use :so to source packages
use :PackerSync to sync the packages
for other lua packages need to create a lua file







to access my own version of lua i need to create lua folder here 
1. C:\Users\nahid\scoop\apps\neovim\current\bin\lua
2. put my own custom lua or whatever i want to make at startup
3.in init.lua add  require("name-of-lua")
ex-C:\Users\nahid\scoop\apps\neovim\current\bin\lua\ex.lua      +   require("ex")
also can use / to find in nvim explore