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

ubuntu_rootfs_dir() {
    local rootfs
    for rootfs in \
        "${PREFIX:-}/var/lib/proot-distro/installed-rootfs/ubuntu" \
        "$HOME/.local/share/proot-distro/installed-rootfs/ubuntu"; do
        [[ -n "$rootfs" && -r "$rootfs/etc/os-release" ]] || continue
        if grep -qi '^ID=ubuntu$' "$rootfs/etc/os-release"; then
            printf '%s\n' "$rootfs"
            return 0
        fi
    done
    return 1
}

ubuntu_is_installed() {
    inside_ubuntu && return 0
    command -v proot-distro >/dev/null 2>&1 || return 1
    ubuntu_rootfs_dir >/dev/null 2>&1 && return 0
    proot-distro login ubuntu -- /bin/true >/dev/null 2>&1
}

show_menu() {
    clear
    echo -e "${MAGENTA}╔══════════════════════════════════════╗${NC}"
    echo -e "${MAGENTA}║           Ubuntu Setup               ║${NC}"
    echo -e "${MAGENTA}╚══════════════════════════════════════╝${NC}"
    echo
    echo -e "  ${GREEN}1)${NC} Install Ubuntu in Termux (proot-distro)"
    echo -e "  ${CYAN}2)${NC} Set up Ubuntu environment (bashrc, nano, packages)"
    echo -e "  ${BLUE}3)${NC} Install AI coding agents"
    echo -e "  ${CYAN}4)${NC} Configure Ubuntu environment variables"
    echo -e "  ${GREEN}5)${NC} Simplify Ubuntu terminal startup"
    echo -e "  ${MAGENTA}6)${NC} Configure Pi Gemini proxy"
    echo -e "  ${GREEN}7)${NC} Start T3 server for Android app"
    echo -e "  ${YELLOW}q)${NC} Quit"
    echo
    read -r -p 'Enter choice [1/2/3/4/5/6/7/q]: ' choice

    case "$choice" in
        1) install_ubuntu ;;
        2) setup_ubuntu_environment ;;
        3) install_ai_agents ;;
        4) configure_ubuntu_environment ;;
        5) simplify_ubuntu_terminal ;;
        6) configure_pi_gemini_proxy ;;
        7) start_t3_android_server ;;
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

    if ubuntu_is_installed; then
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

setup_ubuntu_environment() {
    clear
    echo -e "${CYAN}Setting up Ubuntu environment...${NC}"

    local is_ubuntu=false
    if inside_ubuntu; then
        is_ubuntu=true
    elif ! ubuntu_is_installed; then
        echo -e "${RED}Ubuntu is not installed yet. Run option 1 first.${NC}"
        return 1
    fi

    local ubuntu_home
    if [[ "$is_ubuntu" == true ]]; then
        ubuntu_home="$HOME"
    else
        local rootfs
        rootfs=$(ubuntu_rootfs_dir) || {
            echo -e "${RED}Could not locate Ubuntu's installed root filesystem.${NC}"
            return 1
        }
        ubuntu_home="$rootfs/root"
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
    elif ubuntu_is_installed; then
        proot-distro login ubuntu -- bash -lc "$command_string"
    else
        echo -e "${RED}Ubuntu is not installed. Install it with option 1 first.${NC}"
        return 1
    fi
}

get_t3_host_ip() {
    local host_ip="" python_cmd
    if command -v getprop >/dev/null 2>&1; then
        host_ip="$(getprop dhcp.wlan0.ipaddress 2>/dev/null | tr -d '\r')"
    fi
    if [[ -z "$host_ip" ]]; then
        for python_cmd in python3 python; do
            if command -v "$python_cmd" >/dev/null 2>&1; then
                host_ip="$($python_cmd -c 'import socket; s=socket.socket(socket.AF_INET, socket.SOCK_DGRAM); s.connect(("192.0.2.1", 1)); print(s.getsockname()[0]); s.close()' 2>/dev/null)"
                [[ -n "$host_ip" ]] && break
            fi
        done
    fi
    if [[ -z "$host_ip" ]] && command -v hostname >/dev/null 2>&1; then
        host_ip="$(hostname -I 2>/dev/null | tr ' ' '\n' | awk '/^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$/ && $0 !~ /^127\./ {print; exit}')"
    fi
    [[ "$host_ip" =~ ^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$ ]] || return 1
    printf '%s\n' "$host_ip"
}

start_t3_android_server() {
    local host_ip status
    host_ip="$(get_t3_host_ip)" || {
        echo -e "${RED}Could not detect the phone's Wi-Fi IP. Connect to Wi-Fi and try again.${NC}"
        return 1
    }

    if inside_ubuntu; then
        if ! command -v t3 >/dev/null 2>&1; then
            echo -e "${RED}T3 CLI is not on PATH in Ubuntu. Open a fresh Ubuntu shell or fix its PATH first.${NC}"
            return 1
        fi
    elif ! ubuntu_is_installed; then
        echo -e "${RED}Ubuntu is not installed. Install it with option 1 first.${NC}"
        return 1
    fi

    if ! inside_ubuntu && ! run_in_ubuntu 'command -v t3 >/dev/null 2>&1'; then
        echo -e "${RED}T3 CLI is not on PATH in Ubuntu. Open a fresh Ubuntu shell or fix its PATH first.${NC}"
        return 1
    fi

    echo -e "${GREEN}Starting T3 in Ubuntu on ${CYAN}${host_ip}${GREEN}...${NC}"
    echo "Keep this server running. In another Termux tab, run: t3pair"
    echo "Then paste its pairing link into T3 Android > Settings > Environments."

    if ! inside_ubuntu && command -v termux-wake-lock >/dev/null 2>&1; then
        termux-wake-lock 2>/dev/null || true
        trap 'termux-wake-unlock 2>/dev/null || true; trap - INT TERM' INT TERM
    fi
    if inside_ubuntu; then
        t3 serve --host "$host_ip"
        status=$?
    else
        proot-distro login ubuntu -- t3 serve --host "$host_ip"
        status=$?
    fi

    if command -v termux-wake-unlock >/dev/null 2>&1; then
        termux-wake-unlock 2>/dev/null || true
    fi
    trap - INT TERM
    return "$status"
}

ubuntu_home_dir() {
    if inside_ubuntu; then
        printf '%s\n' "$HOME"
    elif ubuntu_is_installed; then
        local rootfs
        rootfs=$(ubuntu_rootfs_dir) || {
            echo -e "${RED}Could not locate Ubuntu's installed root filesystem.${NC}" >&2
            return 1
        }
        printf '%s\n' "$rootfs/root"
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
                for path_entry in "$ubuntu_home/bin" "$ubuntu_home/.local/bin" "$ubuntu_home/.opencode/bin" "$ubuntu_home/.cargo/bin" "$ubuntu_home/go/bin"; do
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

configure_pi_gemini_proxy() {
    local ubuntu_home pi_agent_dir pi_source_dir bashrc_path escaped_bashrc_source
    clear
    echo -e "${CYAN}Configuring Pi's Gemini failover provider for Ubuntu...${NC}"
    ubuntu_home=$(ubuntu_home_dir) || return 1
    pi_agent_dir="$ubuntu_home/.pi/agent"
    bashrc_path="$ubuntu_home/.bashrc"

    if [[ -d "$REPO_DIR/tools/Gemini_CLI/pi" ]]; then
        pi_source_dir="$REPO_DIR/tools/Gemini_CLI/pi"
    elif [[ -d "$SCRIPT_DIR/../tools/Gemini_CLI/pi" ]]; then
        pi_source_dir="$SCRIPT_DIR/../tools/Gemini_CLI/pi"
    else
        echo -e "${RED}Gemini CLI Pi config folder was not found.${NC}"
        return 1
    fi

    command -v python3 >/dev/null 2>&1 || {
        echo -e "${RED}python3 is required. Set up the Ubuntu environment first.${NC}"
        return 1
    }
    mkdir -p "$pi_agent_dir" || return 1
    touch "$bashrc_path" || return 1

    python3 - "$pi_source_dir" "$pi_agent_dir" <<'PY'
import json
import sys
from pathlib import Path

source_dir, target_dir = map(Path, sys.argv[1:3])

def read_json(path):
    if not path.exists():
        return {}
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"Expected a JSON object in {path}")
    return value

source_models = read_json(source_dir / "models.json")
source_settings = read_json(source_dir / "settings.json")
source_auth = read_json(source_dir / "auth.json")
source_provider = source_models.get("providers", {}).get("google-failover")
source_credential = source_auth.get("google-failover")
if not isinstance(source_provider, dict) or not isinstance(source_credential, dict):
    raise ValueError("The project Pi config is missing its Google failover provider or credential.")

models_path = target_dir / "models.json"
models = read_json(models_path)
providers = models.setdefault("providers", {})
if not isinstance(providers, dict):
    raise ValueError(f"Expected providers to be an object in {models_path}")
provider = dict(source_provider)
existing_provider = providers.get("google-failover", {})
if isinstance(existing_provider, dict):
    provider.update(existing_provider)
provider.update({
    "api": "google-generative-ai",
    "baseUrl": "http://127.0.0.1:8765/v1beta",
    "apiKey": source_provider.get("apiKey", "pi-local-secret"),
})
providers["google-failover"] = provider

settings_path = target_dir / "settings.json"
settings = read_json(settings_path)
enabled = settings.get("enabledModels", [])
if not isinstance(enabled, list):
    raise ValueError(f"Expected enabledModels to be a list in {settings_path}")
source_enabled = source_settings.get("enabledModels", [])
settings["enabledModels"] = list(dict.fromkeys(
    [*enabled, *(item for item in source_enabled if str(item).startswith("google-failover/"))]
))
settings.setdefault("defaultProvider", "google-failover")
settings.setdefault("defaultModel", source_settings.get("defaultModel", "gemini-3.1-flash-lite"))

auth_path = target_dir / "auth.json"
auth = read_json(auth_path)
auth["google-failover"] = source_credential

for path, data in ((models_path, models), (settings_path, settings), (auth_path, auth)):
    temp_path = path.with_suffix(path.suffix + ".tmp")
    temp_path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    temp_path.replace(path)
PY
    local result=$?
    if (( result != 0 )); then
        echo -e "${RED}Could not merge Pi's Gemini provider config.${NC}"
        return "$result"
    fi

    if [[ ! -f "$BASHRC_SOURCE" ]]; then
        echo -e "${RED}Shared bashrc was not found: $BASHRC_SOURCE${NC}"
        return 1
    fi
    if ! grep -Fq "# osu shared bashrc: $BASHRC_SOURCE" "$bashrc_path"; then
        printf -v escaped_bashrc_source '%q' "$BASHRC_SOURCE"
        {
            printf '\n# osu shared bashrc: %s\n' "$BASHRC_SOURCE"
            printf 'if [[ -r %s ]]; then source %s; fi\n' "$escaped_bashrc_source" "$escaped_bashrc_source"
        } >> "$bashrc_path" || return 1
    fi

    echo -e "${GREEN}Pi's Gemini provider is configured for Ubuntu.${NC}"
    echo -e "${GREEN}Ubuntu's bashrc now loads the shared config, including ${CYAN}gg${GREEN} and ${CYAN}ggproxy${GREEN}.${NC}"
    echo -e "In Ubuntu, run ${CYAN}ggproxy${NC} in one shell, then run Gemini CLI and enter ${CYAN}/test${NC} in another."
    echo -e "After testing, open Pi in Ubuntu and run ${CYAN}/reload${NC}."
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
    echo -e "  ${GREEN}6)${NC} Install Antigravity CLI (agy)"
    echo -e "  ${YELLOW}q)${NC} Back"
    echo
    read -r -p 'Enter choice [1/2/3/4/5/6/q]: ' choice

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
        6)
            echo -e "${CYAN}Installing Antigravity CLI (agy) in Ubuntu...${NC}"
            run_in_ubuntu 'curl -fsSL https://antigravity.google/cli/install.sh | bash'
            ;;
        q|Q) return 0 ;;
        *) echo -e "${RED}Invalid choice.${NC}"; return 1 ;;
    esac
}

if [[ "${1:-}" == "--start-t3" ]]; then
    start_t3_android_server "${@:2}"
    exit $?
fi

show_menu
