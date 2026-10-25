#!/usr/bin/env bash

# Ubuntu setup and management, kept separate from os.sh.
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$HOME/ms1"
BASHRC_SOURCE="$REPO_DIR/termux/bashrc"
if [[ ! -f "$BASHRC_SOURCE" && -f "$SCRIPT_DIR/bashrc" ]]; then
    BASHRC_SOURCE="$SCRIPT_DIR/bashrc"
fi

inside_ubuntu() {
    [[ -r /etc/os-release ]] && grep -qi '^ID=ubuntu$' /etc/os-release
}

show_menu() {
    clear
    echo -e "${MAGENTA}╔══════════════════════════════════════╗${NC}"
    echo -e "${MAGENTA}║           Ubuntu Setup               ║${NC}"
    echo -e "${MAGENTA}╚══════════════════════════════════════╝${NC}"
    echo
    echo -e "  ${GREEN}1)${NC} Install Ubuntu in Termux (proot-distro)"
    echo -e "  ${CYAN}2)${NC} Set up Ubuntu environment (bashrc, nano, packages)"
    echo -e "  ${RED}3)${NC} Remove Ubuntu completely (Termux only)"
    echo -e "  ${BLUE}4)${NC} Install AI coding agents"
    echo -e "  ${CYAN}5)${NC} Configure Ubuntu environment variables"
    echo -e "  ${GREEN}6)${NC} Simplify Ubuntu terminal startup"
    echo -e "  ${YELLOW}q)${NC} Quit"
    echo
    read -r -p 'Enter choice [1/2/3/4/5/6/q]: ' choice

    case "$choice" in
        1) install_ubuntu ;;
        2) setup_ubuntu_environment ;;
        3) remove_ubuntu ;;
        4) install_ai_agents ;;
        5) configure_ubuntu_environment ;;
        6) simplify_ubuntu_terminal ;;
        q|Q) return 0 ;;
        *) echo -e "${RED}Invalid choice.${NC}" ;;
    esac
}

install_ubuntu() {
    clear
    if inside_ubuntu; then
        echo -e "${RED}Run this option from Termux, not inside Ubuntu.${NC}"
        return 1
    fi

    echo -e "${MAGENTA}Installing Ubuntu via proot-distro...${NC}"
    if ! command -v proot-distro >/dev/null 2>&1; then
        echo -e "${CYAN}Installing proot-distro...${NC}"
        pkg install proot-distro -y || {
            echo -e "${RED}Failed to install proot-distro.${NC}"
            return 1
        }
    fi

    if proot-distro list 2>/dev/null | grep -qi 'ubuntu.*installed' || \
       [[ -d "$HOME/.local/share/proot-distro/installed-rootfs/ubuntu" ]]; then
        echo -e "${GREEN}Ubuntu is already installed.${NC}"
    else
        echo -e "${CYAN}Downloading and installing Ubuntu...${NC}"
        proot-distro install ubuntu || {
            echo -e "${RED}Failed to install Ubuntu.${NC}"
            return 1
        }
        echo -e "${GREEN}Ubuntu installed successfully.${NC}"
    fi

    proot-distro login ubuntu -- bash -c '
        apt update -y && apt upgrade -y
        apt install -y curl wget git nano vim sudo locales tzdata
        locale-gen en_US.UTF-8
        echo "Ubuntu ready. Run: proot-distro login ubuntu"
    '
    echo -e "${GREEN}Done! Launch Ubuntu with:${NC} proot-distro login ubuntu"
}

remove_ubuntu() {
    clear
    if inside_ubuntu; then
        echo -e "${RED}Run this option from Termux, not inside Ubuntu.${NC}"
        return 1
    fi
    if ! command -v proot-distro >/dev/null 2>&1; then
        echo -e "${YELLOW}proot-distro is not installed; there is no Ubuntu installation to remove.${NC}"
        return 0
    fi
    if ! proot-distro list 2>/dev/null | grep -qi 'ubuntu.*installed' && \
       [[ ! -d "$HOME/.local/share/proot-distro/installed-rootfs/ubuntu" ]]; then
        echo -e "${YELLOW}Ubuntu is not installed.${NC}"
        return 0
    fi

    echo -e "${RED}This will permanently remove the Ubuntu root filesystem and its files.${NC}"
    read -r -p 'Remove Ubuntu? [y/N]: ' confirmation
    case "$confirmation" in
        y|Y|yes|YES)
            proot-distro remove ubuntu && echo -e "${GREEN}Ubuntu has been removed.${NC}" || {
                echo -e "${RED}Failed to remove Ubuntu.${NC}"
                return 1
            }
            ;;
        *) echo -e "${YELLOW}Removal cancelled.${NC}" ;;
    esac
}

setup_ubuntu_environment() {
    clear
    echo -e "${CYAN}Setting up Ubuntu environment...${NC}"

    local is_ubuntu=false
    if inside_ubuntu; then
        is_ubuntu=true
    elif ! command -v proot-distro >/dev/null 2>&1 || {
        ! proot-distro list 2>/dev/null | grep -qi 'ubuntu.*installed' &&
        [[ ! -d "$HOME/.local/share/proot-distro/installed-rootfs/ubuntu" ]]
    }; then
        echo -e "${RED}Ubuntu is not installed yet. Run option 1 first.${NC}"
        return 1
    fi

    local ubuntu_home
    if [[ "$is_ubuntu" == true ]]; then
        ubuntu_home="$HOME"
    else
        ubuntu_home="$HOME/.local/share/proot-distro/installed-rootfs/ubuntu/root"
    fi

    mkdir -p "$ubuntu_home/projects" "$ubuntu_home/scripts" \
        "$ubuntu_home/tmp" "$ubuntu_home/bin"

    if [[ ! -f "$BASHRC_SOURCE" ]]; then
        echo -e "${RED}Shared bashrc not found: $BASHRC_SOURCE${NC}"
        return 1
    fi
    cp "$BASHRC_SOURCE" "$ubuntu_home/.bashrc" || return 1

    cat > "$ubuntu_home/.nanorc" <<'NANORC'
set autoindent
set linenumbers
set mouse
set tabsize 4
set tabstospaces
set trimblanks
set constantshow
include "/usr/share/nano/*.nanorc"
NANORC

    local apt_setup='apt update -y && apt install -y curl wget git nano vim htop tree zsh tmux unzip zip python3 python3-pip build-essential'
    local git_setup="git config --global core.editor nano
git config --global pull.rebase false
git config --global init.defaultBranch main
git config --global color.ui auto
git config --global alias.st status
git config --global alias.lg 'log --oneline --graph --decorate -15'"

    if [[ "$is_ubuntu" == true ]]; then
        bash -c "$apt_setup" || return 1
        bash -c "$git_setup" || return 1
    else
        proot-distro login ubuntu -- bash -c "$apt_setup" || return 1
        proot-distro login ubuntu -- bash -c "$git_setup" || return 1
    fi

    echo -e "${GREEN}Ubuntu environment setup complete.${NC}"
    if [[ "$is_ubuntu" == true ]]; then
        echo -e "Configured $ubuntu_home/.bashrc, $ubuntu_home/.nanorc, and standard directories."
    else
        echo -e "Login with: proot-distro login ubuntu"
    fi
}

run_in_ubuntu() {
    local command_string="$1"
    if inside_ubuntu; then
        bash -lc "$command_string"
    elif command -v proot-distro >/dev/null 2>&1 && \
         { proot-distro list 2>/dev/null | grep -qi 'ubuntu.*installed' ||
           [[ -d "$HOME/.local/share/proot-distro/installed-rootfs/ubuntu" ]]; }; then
        proot-distro login ubuntu -- bash -lc "$command_string"
    else
        echo -e "${RED}Ubuntu is not installed. Install it with option 1 first.${NC}"
        return 1
    fi
}

ubuntu_home_dir() {
    if inside_ubuntu; then
        printf '%s\n' "$HOME"
    elif command -v proot-distro >/dev/null 2>&1 && \
         { proot-distro list 2>/dev/null | grep -qi 'ubuntu.*installed' ||
           [[ -d "$HOME/.local/share/proot-distro/installed-rootfs/ubuntu" ]]; }; then
        printf '%s\n' "$HOME/.local/share/proot-distro/installed-rootfs/ubuntu/root"
    else
        echo -e "${RED}Ubuntu is not installed. Install it with option 1 first.${NC}" >&2
        return 1
    fi
}

simplify_ubuntu_terminal() {
    local ubuntu_home bashrc_dir
    clear
    echo -e "${CYAN}Simplifying Ubuntu terminal startup...${NC}"
    ubuntu_home=$(ubuntu_home_dir) || return 1
    bashrc_dir="$ubuntu_home/.bashrc"
    touch "$bashrc_dir" || return 1
    sed -i -e '/if .*fastfetch/,/^[[:space:]]*fi[[:space:]]*$/d' -e '/fastfetch/d' "$bashrc_dir" || return 1
    sed -i '/^# Simple Ubuntu prompt:/,+1d' "$bashrc_dir" || return 1
    printf '\n%s\n' '# Simple Ubuntu prompt: current directory and arrow' "PS1='\[\033[0;34m\]\w\[\033[0m\] \[\033[0;36m\]❯\[\033[0m\] '" >> "$bashrc_dir" || return 1
    echo -e "${GREEN}Removed Fastfetch startup lines from $bashrc_dir and set a current-directory prompt with an arrow.${NC}"
    echo -e "Exit Ubuntu and start it again to see the change."
}

add_ubuntu_path_entry() {
    local bashrc_dir="$1" entry="$2" escaped_entry
    mkdir -p "$(dirname "$bashrc_dir")" || return 1
    touch "$bashrc_dir" || return 1
    printf -v escaped_entry '%q' "$entry"
    if grep -Fq -- "# osu PATH entry: $entry" "$bashrc_dir"; then
        echo -e "${YELLOW}$entry is already configured.${NC}"
        return 0
    fi
    {
        printf '\n# osu PATH entry: %s\n' "$entry"
        printf 'case ":$PATH:" in *":%s:"*) ;; *) export PATH=%s:"$PATH" ;; esac\n' "$escaped_entry" "$escaped_entry"
    } >> "$bashrc_dir" || return 1
    echo -e "${GREEN}Added $entry to PATH.${NC}"
}

configure_ubuntu_environment() {
    local choice ubuntu_home bashrc_dir entry var_name var_value escaped_value path_entry
    while true; do
        clear
        echo -e "${MAGENTA}Ubuntu Environment Settings${NC}"
        echo
        echo -e "  ${GREEN}1)${NC} Add common CLI folders to PATH"
        echo -e "  ${CYAN}2)${NC} Add a custom directory to PATH"
        echo -e "  ${BLUE}3)${NC} Set or update an exported variable"
        echo -e "  ${MAGENTA}4)${NC} Show current PATH"
        echo -e "  ${YELLOW}q)${NC} Back"
        echo
        read -r -p 'Enter choice [1/2/3/4/q]: ' choice

        case "$choice" in
            1)
                ubuntu_home=$(ubuntu_home_dir) || { read -r -p 'Press Enter to continue...'; continue; }
                bashrc_dir="$ubuntu_home/.bashrc"
                for path_entry in "$ubuntu_home/bin" "$ubuntu_home/.local/bin" "$ubuntu_home/.cargo/bin" "$ubuntu_home/go/bin"; do
                    add_ubuntu_path_entry "$bashrc_dir" "$path_entry" || return 1
                done
                echo -e "Apply changes now with: ${CYAN}source ~/.bashrc${NC}"
                read -r -p 'Press Enter to continue...'
                ;;
            2)
                read -r -p 'Directory to add to PATH (e.g. /root/bin): ' entry
                [[ -n "$entry" ]] || { echo -e "${RED}Directory cannot be empty.${NC}"; read -r -p 'Press Enter to continue...'; continue; }
                ubuntu_home=$(ubuntu_home_dir) || { read -r -p 'Press Enter to continue...'; continue; }
                bashrc_dir="$ubuntu_home/.bashrc"
                add_ubuntu_path_entry "$bashrc_dir" "$entry" || return 1
                echo -e "Apply it now with: ${CYAN}source ~/.bashrc${NC}"
                read -r -p 'Press Enter to continue...'
                ;;
            3)
                read -r -p 'Variable name (e.g. ANDROID_HOME): ' var_name
                if [[ ! "$var_name" =~ ^[a-zA-Z_][a-zA-Z0-9_]*$ ]]; then
                    echo -e "${RED}Invalid variable name.${NC}"
                    read -r -p 'Press Enter to continue...'
                    continue
                fi
                read -r -p "Value for $var_name: " var_value
                ubuntu_home=$(ubuntu_home_dir) || { read -r -p 'Press Enter to continue...'; continue; }
                bashrc_dir="$ubuntu_home/.bashrc"
                mkdir -p "$ubuntu_home" || return 1
                touch "$bashrc_dir" || return 1
                printf -v escaped_value '%q' "$var_value"
                if grep -Fq "# osu environment variable: $var_name" "$bashrc_dir"; then
                    sed -i "/^# osu environment variable: ${var_name}$/,+1d" "$bashrc_dir" || return 1
                fi
                {
                    printf '\n# osu environment variable: %s\n' "$var_name"
                    printf 'export %s=%s\n' "$var_name" "$escaped_value"
                } >> "$bashrc_dir" || return 1
                echo -e "${GREEN}Saved $var_name in $bashrc_dir.${NC}"
                echo -e "Apply it now with: ${CYAN}source ~/.bashrc${NC}"
                read -r -p 'Press Enter to continue...'
                ;;
            4)
                run_in_ubuntu 'printf "PATH entries:\\n"; printf "%s\\n" "$PATH" | tr ":" "\\n"'
                read -r -p 'Press Enter to continue...'
                ;;
            q|Q) return 0 ;;
            *) echo -e "${RED}Invalid choice.${NC}"; read -r -p 'Press Enter to continue...' ;;
        esac
    done
}

install_ai_agents() {
    local choice
    clear
    echo -e "${MAGENTA}AI Coding Agents for Ubuntu${NC}"
    echo
    echo -e "  ${GREEN}1)${NC} Install Kiro CLI"
    echo -e "  ${CYAN}2)${NC} Install Codex CLI"
    echo -e "  ${BLUE}3)${NC} Install T3 Code"
    echo -e "  ${MAGENTA}4)${NC} Install Pi AI coding agent"
    echo -e "  ${YELLOW}5)${NC} Install OpenCode"
    echo -e "  ${YELLOW}q)${NC} Back"
    echo
    read -r -p 'Enter choice [1/2/3/4/5/q]: ' choice

    case "$choice" in
        1)
            echo -e "${CYAN}Installing Kiro CLI in Ubuntu...${NC}"
            run_in_ubuntu 'curl -fsSL https://cli.kiro.dev/install | bash'
            ;;
        2)
            echo -e "${CYAN}Installing Codex CLI in Ubuntu...${NC}"
            run_in_ubuntu 'curl -fsSL https://chatgpt.com/codex/install.sh | sh'
            ;;
        3)
            echo -e "${CYAN}Installing T3 Code in Ubuntu...${NC}"
            run_in_ubuntu 'curl -fsSL https://t3.codes/install.sh | sh'
            ;;
        4)
            echo -e "${CYAN}Installing Pi AI coding agent in Ubuntu...${NC}"
            run_in_ubuntu 'curl -fsSL https://pi.dev/install.sh | sh'
            ;;
        5)
            echo -e "${CYAN}Installing OpenCode in Ubuntu...${NC}"
            run_in_ubuntu 'curl -fsSL https://opencode.ai/install | bash'
            ;;
        q|Q) return 0 ;;
        *) echo -e "${RED}Invalid choice.${NC}"; return 1 ;;
    esac
}

show_menu
