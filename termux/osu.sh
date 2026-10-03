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
    echo -e "  ${YELLOW}q)${NC} Quit"
    echo
    read -r -p 'Enter choice [1/2/3/q]: ' choice

    case "$choice" in
        1) install_ubuntu ;;
        2) setup_ubuntu_environment ;;
        3) remove_ubuntu ;;
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

show_menu
