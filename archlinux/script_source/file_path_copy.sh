# Fuzzy Finder setup
if command -v fzf >/dev/null 2>&1; then
    # Function to fuzzy find files, including hidden files
    find_path() {
        local file
        file=$(find . -type f -name '.*' -o -type f | fzf)

        if [[ -n $file ]]; then
            # Copy the file path to the clipboard
            echo -n "$file" | termux-clipboard-set  # Use `pbcopy` on macOS or `xclip` on Linux
            echo "Copieddddddd: $file"  # Optional: Notify that the path was copied
        fi
    }

    # Bind the function to a shortcut, for example, Ctrl+F
    bind -x '"\C-p": fp'
    
    # Bind Alt+C to copy the file path
    bind -x '"\e[1;5;67": fp'  # Alt+C in some terminal emulators
fi
