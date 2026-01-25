#!/bin/bash

# Ubuntu WSL Setup & Optimization Script
# Fixes common issues and adds useful features

set -e

echo "🚀 Ubuntu WSL Setup Script"
echo ""
echo "Choose an option:"
echo "1. Full initial setup (complete installation)"
echo "2. Quick fixes only (aliases, configs, scripts)"
echo ""
read -p "Enter choice (1 or 2): " choice

case $choice in
    1)
        echo "Starting full setup..."
        FULL_SETUP=true
        ;;
    2)
        echo "Starting quick fixes..."
        FULL_SETUP=false
        ;;
    *)
        echo "Invalid choice. Exiting."
        exit 1
        ;;
esac

if [ "$FULL_SETUP" = true ]; then
    # Switch to home directory to avoid /mnt/c performance issues
    cd "$HOME"
    
    echo "📦 Updating system packages..."
    # Wait for any existing apt processes to finish
    sudo fuser -vki /var/lib/dpkg/lock-frontend 2>/dev/null || true
    sudo fuser -vki /var/cache/apt/archives/lock 2>/dev/null || true
    sudo rm -f /var/lib/dpkg/lock-frontend /var/cache/apt/archives/lock 2>/dev/null || true
    sudo dpkg --configure -a
    sudo apt update && sudo apt upgrade -y

    # Fix common WSL issues
    echo "🔧 Fixing WSL-specific issues..."

    # Fix DNS issues
    sudo rm -f /etc/resolv.conf
    echo "nameserver 8.8.8.8" | sudo tee /etc/resolv.conf
    echo "nameserver 8.8.4.4" | sudo tee -a /etc/resolv.conf

    # Fix locale issues
    sudo apt install -y locales
    sudo locale-gen en_US.UTF-8
    sudo update-locale LANG=en_US.UTF-8

    # Install essential tools
    echo "🛠️ Installing essential development tools..."
    sudo apt install -y \
        curl wget git vim nano \
        build-essential software-properties-common \
        apt-transport-https ca-certificates gnupg \
        unzip zip tree htop neofetch \
        python3 python3-pip nodejs npm

    # Add Flatpak for more app stores
    echo "📱 Adding Flatpak app store..."
    sudo apt install -y flatpak
    sudo flatpak remote-add --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo

    # Add Snap store
    echo "🏪 Enabling Snap store..."
    sudo apt install -y snapd

    # Install useful CLI tools
    sudo apt install -y \
        bat eza fd-find ripgrep fzf \
        tmux screen ncdu duf \
        jq yq

    # Enable GUI apps (VcXsrv support)
    echo "🖥️ Configuring GUI support (VcXsrv)..."
    # Auto-set DISPLAY for VcXsrv on Windows
    # Use ip route to find the host IP (more reliable than resolv.conf)
    echo '# VcXsrv Display Configuration' >> ~/.bashrc
    echo 'export DISPLAY=$(ip route list default | awk "{print \$3}"):0' >> ~/.bashrc
    echo 'export LIBGL_ALWAYS_INDIRECT=1' >> ~/.bashrc

    # Install GUI apps for testing
    sudo apt install -y gedit mousepad

    # Install Docker
    echo "🐳 Installing Docker..."
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
    echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    sudo apt update
    sudo apt install -y docker-ce docker-ce-cli containerd.io
    sudo usermod -aG docker $USER

    # Setup Git with better defaults (do this before Homebrew to prevent timeouts)
    echo "🔧 Configuring Git..."
    git config --global init.defaultBranch main
    git config --global pull.rebase false
    # Increase buffer size to prevent hangs during large clones (like Homebrew)
    git config --global http.postBuffer 524288000
    git config --global http.lowSpeedLimit 0
    git config --global http.lowSpeedTime 999999
    # Force HTTP/1.1 to fix "RPC failed; curl 92 HTTP/2" errors
    git config --global http.version HTTP/1.1

    # Install additional package managers
    echo "📦 Installing additional package managers..."

    # Install Homebrew (optional - can be slow)
    read -p "Install Homebrew? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        if ! command -v brew &> /dev/null; then
            echo "Installing Homebrew via Tarball (Faster for slow connections)..."
            
            # 1. Create directory structure
            sudo mkdir -p /home/linuxbrew/.linuxbrew/Homebrew
            sudo chown -R $USER:$USER /home/linuxbrew/.linuxbrew
            
            # 2. Download and extract tarball (Avoids git clone history/timeouts)
            echo "Downloading Homebrew..."
            curl -L https://github.com/Homebrew/brew/tarball/master | tar xz --strip 1 -C /home/linuxbrew/.linuxbrew/Homebrew
            
            # 3. Configure environment
            echo 'eval "$(/home/linuxbrew/.linuxbrew/Homebrew/bin/brew shellenv)"' >> ~/.bashrc
            eval "$(/home/linuxbrew/.linuxbrew/Homebrew/bin/brew shellenv)"
            
            # 4. Verify installation
            echo "Homebrew installed. initializing..."
            brew --version
        fi
    else
        echo "Skipping Homebrew installation"
    fi

    # WSL integration improvements
    echo "🔗 Improving WSL integration..."
    # Add Windows PATH integration
    echo 'export PATH="$PATH:/mnt/c/Windows/System32"' >> ~/.bashrc

    # Performance optimizations
    echo "⚡ Applying performance optimizations..."
    # Increase file watchers limit
    echo 'fs.inotify.max_user_watches=524288' | sudo tee -a /etc/sysctl.conf

    # Clean up
    echo "🧹 Cleaning up..."
    sudo apt autoremove -y
    sudo apt autoclean

    # Make bash default shell
    sudo chsh -s $(which bash) $USER
fi

# Apply Quick Fixes (common to both full setup and quick fix option)
if [ "$FULL_SETUP" = false ]; then
     echo "🔧 Applying quick fixes..."
     
     # Fix VcXsrv DISPLAY variable (remove old incorrect one first)
     sed -i '/VcXsrv Display Configuration/d' ~/.bashrc
     sed -i '/export DISPLAY=/d' ~/.bashrc
     sed -i '/export LIBGL_ALWAYS_INDIRECT=/d' ~/.bashrc
     
     echo '# VcXsrv Display Configuration' >> ~/.bashrc
     echo 'export DISPLAY=$(ip route list default | awk "{print \$3}"):0' >> ~/.bashrc
     echo 'export LIBGL_ALWAYS_INDIRECT=1' >> ~/.bashrc
fi

# Create aliases for better commands (runs for both options)
echo "⚡ Setting up useful aliases..."
cat >> ~/.bashrc << 'EOF'

# Enable partial history search with up/down arrows
bind '"\e[A": history-search-backward'
bind '"\e[B": history-search-forward'

# FZF key bindings for enhanced search
source /usr/share/doc/fzf/examples/key-bindings.bash 2>/dev/null || true
source /usr/share/doc/fzf/examples/completion.bash 2>/dev/null || true

# Modern CLI aliases
alias ll='eza -la --icons'
alias ls='eza --icons'
alias cat='batcat'
alias find='fd'
alias grep='rg'
alias du='ncdu'
alias df='duf'
alias top='htop'

# Git shortcuts
alias gs='git status'
alias ga='git add'
alias gc='git commit'
alias gp='git push'
alias gl='git log --oneline'

# WSL shortcuts
alias open='explorer.exe'
alias code='code.exe'

# FZF shortcuts for easier package management
alias apti='apt list --upgradable 2>/dev/null | tail -n +2 | fzf --multi --preview "apt show {1}" --bind "enter:execute(echo {1} | cut -d/ -f1 | xargs sudo apt install)"'
alias apts='apt-cache search . | fzf --preview "apt show {1}" --bind "enter:execute(echo {1} | cut -d\" \" -f1 | xargs sudo apt install)"'
alias snapf='snap find "" 2>/dev/null | tail -n +2 | head -100 | fzf --preview "snap info {1}" --bind "enter:execute(echo {1} | awk \"{print \\$1}\" | xargs sudo snap install)"'
alias brewf='brew search 2>/dev/null | fzf --preview "brew info {}" --bind "enter:execute(echo {} | xargs brew install)"'

# FZF file operations
alias ff='find . -type f | fzf --preview "batcat --color=always {}"'
alias fd='find . -type d | fzf'
EOF

# Install VS Code extensions helper
echo "🔌 Setting up VS Code integration..."
cat > ~/install-vscode-extensions.sh << 'EOF'
#!/bin/bash
# Common VS Code extensions for WSL development
extensions=(
    "ms-vscode-remote.remote-wsl"
    "ms-python.python"
    "ms-vscode.cpptools"
    "bradlc.vscode-tailwindcss"
    "esbenp.prettier-vscode"
    "ms-vscode.vscode-json"
)

for ext in "${extensions[@]}"; do
    code.exe --install-extension "$ext"
done
EOF
chmod +x ~/install-vscode-extensions.sh

# Create useful scripts
echo "📝 Creating utility scripts..."

# Quick system info script
cat > ~/sysinfo.sh << 'EOF'
#!/bin/bash
echo "=== System Information ==="
neofetch --stdout
echo ""
echo "=== Disk Usage ==="
duf
echo ""
echo "=== Memory Usage ==="
free -h
EOF
chmod +x ~/sysinfo.sh

echo ""
if [ "$FULL_SETUP" = true ]; then
    echo "🎉 Ubuntu WSL full setup complete!"
    echo ""
    echo "📋 What was installed/configured:"
    echo "  • System updates and fixes"
    echo "  • Modern CLI tools (eza, bat, ripgrep, etc.)"
    echo "  • Bash optimization"
    echo "  • Docker"
    echo "  • Flatpak and Snap stores"
    echo "  • Homebrew package manager (if selected)"
    echo "  • Useful aliases and FZF shortcuts"
    echo "  • VS Code integration"
    echo "  • GUI app support (VcXsrv configured)"
    echo ""
    echo "🔄 Please restart your terminal or run: source ~/.bashrc"
else
    echo "🎉 Quick fixes applied!"
    echo ""
    echo "📋 What was updated:"
    echo "  • Aliases and FZF shortcuts"
    echo "  • VcXsrv display config"
    echo "  • VS Code extensions helper"
    echo "  • System info script"
    echo ""
    echo "🔄 Run: source ~/.bashrc (or restart terminal)"
fi

echo "📱 Install Flatpak apps: flatpak install flathub <app-name>"
echo "🏪 Install Snap apps: snap install <app-name>"
echo "🍺 Install Homebrew packages: brew install <package-name>"
echo ""
echo "🖥️ For GUI apps:"
echo "  1. Install VcXsrv on Windows (https://sourceforge.net/projects/vcxsrv/)"
echo "  2. Launch 'XLaunch' on Windows with:"
echo "     - Multiple windows"
echo "     - Display number: 0"
echo "     - Start no client"
echo "     - ☑️ Disable access control"
echo "  3. Run GUI apps (e.g., 'gedit' or 'mousepad')"
echo ""
echo "💡 Run ~/sysinfo.sh to see system information"
echo "💡 Run ~/install-vscode-extensions.sh to install VS Code extensions"
