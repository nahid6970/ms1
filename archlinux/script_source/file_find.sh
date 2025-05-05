# Fuzzy Finder setup
if command -v fzf >/dev/null 2>&1; then
    # Function to fuzzy find files, including hidden files
    ff() {
        local file
        file=$(find . -type f -name '.*' -o -type f | fzf)
        if [[ -n $file ]]; then
            nvim "$file"  # Or any other command you prefer to open the file
        fi
    }
fi