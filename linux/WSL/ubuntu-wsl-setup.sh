#!/bin/bash

# Ubuntu WSL Setup & Optimization Script
# Fixes common issues and adds useful features

set -e

echo "🚀 Starting Ubuntu WSL optimization..."

# Update system
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

# Install modern terminal tools
echo "💻 Installing modern terminal tools..."

# Install zsh and oh-my-zsh
sudo apt install -y zsh
if [ ! -d "$HOME/.oh-my-zsh" ]; then
    sh -c "$(curl -fsSL https://raw.github.com/ohmyzsh/ohmyzsh/master/tools/install.sh)" "" --unattended
fi

# Install useful CLI tools
sudo apt install -y \
    bat eza fd-find ripgrep fzf \
    tmux screen ncdu duf \
    jq yq

# Create aliases for better commands
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
alias apti='apt list --upgradable 2>/dev/null | fzf --multi --preview "apt show {1}" | cut -d/ -f1 | xargs -r sudo apt install'
alias apts='apt search {} 2>/dev/null | fzf --preview "apt show {1}" | cut -d/ -f1'
alias snapf='snap find {} | fzf --preview "snap info {1}" | awk "{print \$1}"'
alias brewf='brew search {} | fzf --preview "brew info {}"'

# FZF file operations
alias ff='find . -type f | fzf --preview "batcat --color=always {}"'
alias fd='find . -type d | fzf'
EOF

# Install Docker
echo "🐳 Installing Docker..."
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io
sudo usermod -aG docker $USER

# Install additional package managers
echo "📦 Installing additional package managers..."

# Install Homebrew (optional - can be slow)
read -p "Install Homebrew? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    if ! command -v brew &> /dev/null; then
        echo "Installing Homebrew (this may take 30-60 minutes)..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        echo 'eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"' >> ~/.bashrc
    fi
else
    echo "Skipping Homebrew installation"
fi

# Setup Git with better defaults
echo "🔧 Configuring Git..."
git config --global init.defaultBranch main
git config --global pull.rebase false

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

# WSL integration improvements
echo "🔗 Improving WSL integration..."
# Add Windows PATH integration
echo 'export PATH="$PATH:/mnt/c/Windows/System32"' >> ~/.bashrc

# Enable GUI apps (VNC support)
echo "🖥️ Setting up GUI support with VNC..."
sudo apt install -y xfce4 xfce4-goodies tightvncserver

# Create VNC startup script
cat > ~/start-vnc.sh << 'EOF'
#!/bin/bash
# Kill any existing VNC sessions
vncserver -kill :0 2>/dev/null || true

# Start VNC server with XFCE desktop
vncserver :0 -geometry 1920x1080 -depth 24

echo "VNC server started on :0"
echo "Connect with TightVNC Viewer to: localhost:5900"
EOF
chmod +x ~/start-vnc.sh

# Install GUI apps for testing
sudo apt install -y gedit mousepad

# Performance optimizations
echo "⚡ Applying performance optimizations..."
# Increase file watchers limit
echo 'fs.inotify.max_user_watches=524288' | sudo tee -a /etc/sysctl.conf

# Clean up
echo "🧹 Cleaning up..."
sudo apt autoremove -y
sudo apt autoclean

# Final setup
echo "✅ Final configuration..."
# Make zsh default shell
sudo chsh -s $(which zsh) $USER

echo ""
echo "🎉 Ubuntu WSL setup complete!"
echo ""
echo "📋 What was installed/configured:"
echo "  • System updates and fixes"
echo "  • Modern CLI tools (eza, bat, ripgrep, etc.)"
echo "  • Zsh with Oh My Zsh"
echo "  • Docker"
echo "  • Flatpak and Snap stores"
echo "  • Homebrew package manager"
echo "  • Useful aliases and FZF shortcuts"
echo "  • VS Code integration"
echo "  • GUI app support (VNC with XFCE)"
echo ""
echo "🔄 Please restart your terminal or run: source ~/.bashrc"
echo "🐚 To use zsh: exec zsh"
echo "📱 Install Flatpak apps: flatpak install flathub <app-name>"
echo "🏪 Install Snap apps: snap install <app-name>"
echo "🍺 Install Homebrew packages: brew install <package-name>"
echo ""
echo "🖥️ For GUI apps: Run ~/start-vnc.sh then connect TightVNC to localhost:5900"
echo "🧪 Test GUI: gedit or mousepad"
echo "💡 Run ~/sysinfo.sh to see system information"
echo "💡 Run ~/install-vscode-extensions.sh to install VS Code extensions"
