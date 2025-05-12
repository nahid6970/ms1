#!/bin/bash

# Define some color variables
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Define some variables for installation and setup paths
REPO_DIR="$HOME/arch_setup"
BASHRC_SOURCE="$REPO_DIR/bashrc"
BASHRC_DEST="$HOME/.bashrc"

# Example function to install base packages
install_base_packages() {
    clear
    echo -e "${CYAN}Installing base packages...${NC}"
    sudo pacman -Syu --noconfirm base base-devel linux linux-headers
    echo -e "${GREEN}Base packages installed.${NC}"
}

# Function to set up desktop environment
install_desktop_environment() {
    clear
    echo -e "${CYAN}Installing desktop environment...${NC}"
    sudo pacman -S --noconfirm xorg plasma sddm
    sudo systemctl enable sddm
    echo -e "${GREEN}Desktop environment installed and SDDM enabled.${NC}"
}

# Function to install additional utilities
install_utilities() {
    clear
    echo -e "${CYAN}Installing utilities...${NC}"
    sudo pacman -S --noconfirm vim git zsh
    echo -e "${GREEN}Utilities installed.${NC}"
}

# Function to configure bashrc
copy_files() {
    clear
    echo -e "${CYAN}Copying .bashrc...${NC}"
    cp "$BASHRC_SOURCE" "$BASHRC_DEST"
    echo -e "${CYAN}.bashrc copied successfully.${NC}"
}

# Function to handle exit
close_script() {
    clear
    echo -e "${GREEN}Exiting the script. Goodbye!${NC}"
    exit 0
}

# Declare a combined array of menu options and function bindings
menu_items=(
    " 1: Install Base Packages        : install_base_packages               :$BLUE"
    " 2: Install Desktop Environment  : install_desktop_environment         :$BLUE"
    " 3: Install Utilities            : install_utilities                   :$BLUE"
    " 4: Copy Files                   : copy_files                          :$BLUE"
    " c: Close Script                 : close_script                        :$RED"
)

# Display the menu and handle user input
while true; do
    # Clear the screen to refresh the menu
    echo ""
    echo -e "${YELLOW}Select an option:${NC}"

    # Display menu options dynamically with assigned colors
    for item in "${menu_items[@]}"; do
        IFS=":" read -r number description functions color <<< "$item"
        echo -e "${color}$number. $description${NC}"
    done

    echo ""
    read -p "Enter choice: " choice

    # Handle 'c' choice for Close
    if [ "$choice" == "c" ]; then
        close_script
        continue
    fi

    # Check if the choice is numeric and valid
    valid_choice=false
    for item in "${menu_items[@]}"; do
        IFS=":" read -r number description functions color <<< "$item"
        if [ "$choice" -eq "$number" ]; then
            valid_choice=true
            IFS=" " read -r -a function_array <<< "$functions"
            for function in "${function_array[@]}"; do
                $function
            done
            break
        fi
    done

    # If the choice is invalid, show an error message
    if [ "$valid_choice" = false ]; then
        echo -e "${RED}Invalid option. Please try again.${NC}"
    fi
done
