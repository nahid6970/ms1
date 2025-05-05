# Fuzzy Finder setup
if command -v fzf >/dev/null 2>&1; then
    # Function to fuzzy find files, including hidden files
    fp() {
        local file
        file=$(find . -type f -name '.*' -o -type f | fzf)

        if [[ -n $file ]]; then
            # Copy the file path to the clipboard
            echo -n "$file" | termux-clipboard-set  # Use `pbcopy` on macOS or `xclip` on Linux
            echo "Copieddddddd: $file"  # Optional: Notify that the path was copied
        fi
    }
fi
