#!/bin/bash

# Function to list and preview TTY fonts
tty_font() {
    FONT_DIR="/usr/share/consolefonts"
    echo "Available TTY Fonts:"

    # Check if the font directory exists
    if [ ! -d "$FONT_DIR" ]; then
        echo "Console font directory not found."
        return 1
    fi

    # Use fzf for interactive font selection
    selected_font=$(find "$FONT_DIR" -type f -name '*.psf*' | fzf --preview 'setfont {} && echo -e "\033[1;32mPreview: {}\033[0m"' --preview-window=up:5)

    # If a font is selected, set it as the current font
    if [ -n "$selected_font" ]; then
        sudo setfont "$selected_font"
        echo "Font changed to: $(basename "$selected_font")"
    else
        echo "No font selected."
    fi
}

