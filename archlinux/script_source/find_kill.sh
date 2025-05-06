# Fuzzy Killall setup
if command -v fzf >/dev/null 2>&1; then
    # Function to fuzzy find processes and kill them with killall
    kill_proc() {
        local proc
        proc=$(ps -eo comm | tail -n +2 | sort | uniq | fzf)
        if [[ -n $proc ]]; then
            killall "$proc"
        fi
    }
    # Bind the function to a shortcut, for example Ctrl+K
    bind -x '"\C-k": kill_proc'
fi
