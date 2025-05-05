# Fuzzy Finder setup for Arch Linux
if command -v fzf >/dev/null 2>&1; then
    # Function to fuzzy find files, including hidden files
    ff() {
        local file
        file=$(find . -type f \( -path '*/.*' -o -print \) 2>/dev/null | fzf)
        if [[ -n $file ]]; then
            nvim "$file"  # Change 'nvim' to 'micro', 'nano', etc., if you prefer
        fi
    }
fi
