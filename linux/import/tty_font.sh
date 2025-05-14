#!/bin/bash

tty_font(){
# Check for root privileges
if [[ $EUID -ne 0 ]]; then
    echo "Please run as root"
    exit 1
fi

# Location of console fonts
FONT_DIR="/usr/share/kbd/consolefonts"

# Check if the font directory exists
if [[ ! -d $FONT_DIR ]]; then
    echo "Font directory not found: $FONT_DIR"
    exit 1
fi

# List available fonts
echo "Available console fonts:"
fonts=( $(ls $FONT_DIR/*.gz | xargs -n 1 basename | sed 's/\.gz$//') )

# Display fonts
for i in "${!fonts[@]}"; do
    echo "$i) ${fonts[$i]}"
done

# Prompt the user to select a font
read -p "Select a font by number: " font_index

# Validate input
if ! [[ $font_index =~ ^[0-9]+$ ]] || [ $font_index -ge ${#fonts[@]} ]; then
    echo "Invalid selection. Exiting."
    exit 1
fi

selected_font="${fonts[$font_index]}"
echo "You selected: $selected_font"

# Change the font temporarily
setfont "$FONT_DIR/$selected_font.gz"
echo "Font changed to $selected_font."

# Save the selection to /etc/vconsole.conf
echo "FONT=$selected_font" > /etc/vconsole.conf

echo "Font setting saved to /etc/vconsole.conf"
}