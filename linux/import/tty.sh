RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

# Function to configure SDDM with optional Sugar Candy theme and NumLock
tty_setup() {
  echo -e "${RED}🔧 Installing SDDM if not already present...${NC}"
  sudo pacman -S --needed sddm

  echo -e "${GREEN}🔧 Choose setup option:${NC}"
  echo -e "1) Auto Login"
  echo -e "2) Numlock Enable"
  read -rp "Enter your choice (1/2): " choice

  # Check for valid input
  if [[ "$choice" != "1" && "$choice" != "2" ]]; then
    echo -e "${RED}❌ Invalid choice. Exiting.${NC}"
    return 1
  fi

  if [[ "$choice" == "1" ]]; then

    local user=${1:-$USER}
    local service_dir="/etc/systemd/system/getty@tty1.service.d"
    local override_file="$service_dir/override.conf"
    echo "Setting up auto-login for user: $user on tty1..."
    sudo mkdir -p "$service_dir"
    sudo bash -c "cat > '$override_file'" <<EOF
[Service]
ExecStart=
ExecStart=-/usr/bin/agetty --autologin $user --noclear %I \$TERM
EOF
    echo "Reloading systemd and restarting getty@tty1..."
    sudo systemctl daemon-reexec
    sudo systemctl daemon-reload
    sudo systemctl restart getty@tty1
    echo "✅ Auto-login setup complete for user: $user on tty1."
  else
    # Install numlockx package if not already installed
    if ! command -v numlockx &> /dev/null; then
        echo "Installing numlockx package..."
        sudo pacman -S --noconfirm numlockx
    fi

    # Create the script to enable NumLock on TTYs
    echo "Creating numlock script..."
    sudo tee /usr/local/bin/numlock > /dev/null <<EOF
#!/bin/bash

# Enable NumLock on all TTYs (tty1 to tty6)
for tty in /dev/tty{1..6}
do
    /usr/bin/setleds -D +num < "\$tty"
done
EOF

    # Make the script executable
    sudo chmod +x /usr/local/bin/numlock

    # Create the systemd service to run the numlock script on startup
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

    # Enable and start the systemd service
    sudo systemctl daemon-reload
    sudo systemctl enable numlock.service
    sudo systemctl start numlock.service

    # Optionally, extend the getty service to enable NumLock on all TTYs
    echo "Creating getty service drop-in configuration..."
    sudo mkdir -p /etc/systemd/system/getty@.service.d
    sudo tee /etc/systemd/system/getty@.service.d/activate-numlock.conf > /dev/null <<EOF
[Service]
ExecStartPre=/bin/sh -c 'setleds -D +num < /dev/%I'
EOF

    # Reload systemd services
    sudo systemctl daemon-reload
    sudo systemctl restart systemd-logind.service

    echo "NumLock has been enabled on TTYs. The systemd service is now active."
}