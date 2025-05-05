#!/bin/bash

# Fuzzy Finder function
ff() {
    local file
    file=$(find . -type f \( -path '*/.*' -o -print \) 2>/dev/null | fzf)
    if [[ -n $file ]]; then
        nvim "$file"  # Or nano/micro
    fi
}

# Optional: bind Ctrl+F to ff
if [[ $- == *i* ]]; then
    bind -x '"\C-f":ff'
fi
