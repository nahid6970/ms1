#!/bin/bash

function tty_font() {
    echo "Listing available console fonts..."
    fonts=(/usr/share/consolefonts/*.gz)

    # Display font list
    PS3="Select a font number: "
    select font in "${fonts[@]}"; do
        if [[ -n "$font" ]]; then
            chosen_font=$(basename "$font" .gz)
            echo "Selected font: $chosen_font"

            # Test the font using setfont
            setfont "$chosen_font"
            read -p "Press Enter to confirm and save this font to /etc/vconsole.conf..."

            # Save to vconsole.conf
            echo "FONT=$chosen_font" | sudo tee /etc/vconsole.conf
            echo "Font set and saved."
            break
        else
            echo "Invalid selection. Please try again."
        fi
    done
}

tty_font
