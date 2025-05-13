#!/bin/bash

tty_setup() {

GREEN='\033[0;32m'
NC='\033[0m' # No Color

echo -e "${GREEN}🔧 Choose setup option:${NC}"
echo -e "1) Auto Login"
echo -e "2) Numlock Enable"
echo -e "3) Disable Terminal Bell"
read -rp "Enter your choice (1/2/3): " choice

enable_tty_autologin() {
    local user=${1:-$USER}
    local service_dir="/etc/systemd/system/getty@tty1.service.d"
    local override_file="$service_dir/override.conf"

    echo "Setting up auto-login for user: $user on tty1..."
    sudo mkdir -p "$service_dir"

    sudo bash -c "cat > '$override_file'" <<EOF
[Service]
ExecStart=
ExecStart=-/usr/bin/agetty --autologin $user --noclear %I $TERM
EOF

    echo "Reloading systemd and restarting getty@tty1..."
    sudo systemctl daemon-reexec
    sudo systemctl daemon-reload
    sudo systemctl restart getty@tty1

    echo "✅ Auto-login setup complete for user: $user on tty1."
}

enable_numlock_on_tty() {
    if ! command -v numlockx &> /dev/null; then
        echo "Installing numlockx package..."
        sudo pacman -S --noconfirm numlockx
    fi

    echo "Creating numlock script..."
    sudo tee /usr/local/bin/numlock > /dev/null <<EOF
#!/bin/bash
for tty in /dev/tty{1..6}
do
    /usr/bin/setleds -D +num < "$tty"
done
EOF
    sudo chmod +x /usr/local/bin/numlock

    echo "Creating systemd service..."
    sudo tee /etc/systemd/system/numlock.service > /dev/null <<EOF
[Unit]
Description=Enable NumLock on TTYs
[Service]
ExecStart=/usr/local/bin/numlock
StandardInput=tty
RemainAfterExit=yes
[Install]
WantedBy=multi-user.target
EOF

    sudo systemctl daemon-reload
    sudo systemctl enable numlock.service
    sudo systemctl start numlock.service

    echo "Creating getty service drop-in configuration..."
    sudo mkdir -p /etc/systemd/system/getty@.service.d
    sudo tee /etc/systemd/system/getty@.service.d/activate-numlock.conf > /dev/null <<EOF
[Service]
ExecStartPre=/bin/sh -c 'setleds -D +num < /dev/%I'
EOF

    sudo systemctl daemon-reload
    sudo systemctl restart systemd-logind.service

    echo "NumLock has been enabled on TTYs. The systemd service is now active."
}

disable_bell() {
    echo "Disabling terminal bell..."

    echo 'set bell-style none' >> ~/.inputrc
    bind -f ~/.inputrc

    if [ "$(id -u)" -eq 0 ]; then
        echo 'set bell-style none' >> /etc/inputrc
    else
        echo "To disable system-wide bell, run:"
        echo "  echo 'set bell-style none' | sudo tee -a /etc/inputrc"
    fi

    echo "blacklist pcspkr" | sudo tee /etc/modprobe.d/nobeep.conf > /dev/null
    sudo rmmod pcspkr 2>/dev/null

    echo "Bell disabled. Reboot or re-login for full effect."
}

case $choice in
    1) enable_tty_autologin ;;
    2) enable_numlock_on_tty ;;
    3) disable_bell ;;
    *) echo "Invalid choice." ;;
esac

}
