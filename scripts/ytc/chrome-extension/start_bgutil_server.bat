@echo off
cd /d "%USERPROFILE%\bgutil-ytdlp-pot-provider\server"
start /min "bgutil POT Server" node build/main.js
