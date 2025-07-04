#!/bin/bash

# Global variable to track the current menu state
current_menu="main"

# Function to get the main menu string
get_main_menu_string() {
    cat << EOF
========================================
          Arch Linux Setup Menu         
========================================
Main Menu:
  1) Initial Setup
  2) Application Setup
  3) Clone Projects
  4) Backup & Restore
  5) Port Management
  6) Symbolic Links (mklink equivalents)
  7) Github Projects (Windows-specific)
  0) Exit
----------------------------------------
EOF
}

# Function to get the Initial Setup submenu string
get_initial_setup_menu_string() {
    cat << EOF
========================================
          Initial Setup Menu            
========================================
  1) Example Initial Setup 1
  2) Example Initial Setup 2
  0) Back to Main Menu
----------------------------------------
EOF
}

# Function to get the Application Setup submenu string
get_application_setup_menu_string() {
    cat << EOF
========================================
        Application Setup Menu          
========================================
  1) Example App Setup 1
  2) Example App Setup 2
  0) Back to Main Menu
----------------------------------------
EOF
}

# Function to get the Clone Projects submenu string
get_clone_projects_menu_string() {
    cat << EOF
========================================
          Clone Projects Menu           
========================================
  1) Example Clone Project 1
  2) Example Clone Project 2
  0) Back to Main Menu
----------------------------------------
EOF
}

# Function to get the Backup & Restore submenu string
get_backup_restore_menu_string() {
    cat << EOF
========================================
         Backup & Restore Menu          
========================================
  1) Example Backup 1
  2) Example Restore 1
  0) Back to Main Menu
----------------------------------------
EOF
}

# Function to get the Port Management submenu string
get_port_management_menu_string() {
    cat << EOF
========================================
         Port Management Menu           
========================================
  1) Example Port 1
  2) Example Port 2
  0) Back to Main Menu
----------------------------------------
EOF
}

# Function to get the Symbolic Links submenu string
get_symbolic_links_menu_string() {
    cat << EOF
========================================
        Symbolic Links Menu             
========================================
  1) Example Symlink 1
  2) Example Symlink 2
  0) Back to Main Menu
----------------------------------------
EOF
}

# Function to get the Github Projects info string
get_github_projects_info_string() {
    cat << EOF
========================================
        Github Projects Menu            
========================================
These are placeholder examples for Windows-specific projects.
  - Example Project A
  - Example Project B
----------------------------------------
EOF
}

# Function to display content side-by-side
display_side_by_side() {
    local left_content="$1"
    local right_content="$2"

    clear

    # Read contents into arrays of lines
    IFS=$'\n' read -d '' -ra left_lines <<< "$left_content"
    IFS=$'\n' read -d '' -ra right_lines <<< "$right_content"

    local max_left_width=0
    for line in "${left_lines[@]}"; do
        if (( ${#line} > max_left_width )); then
            max_left_width=${#line}
        fi
    done

    local num_lines=$(( ${#left_lines[@]} > ${#right_lines[@]} ? ${#left_lines[@]} : ${#right_lines[@]} ))

    for (( i=0; i<num_lines; i++ )); do
        local left_line="${left_lines[i]:-}"
        local right_line="${right_lines[i]:-}"

        printf "%-${max_left_width}s" "$left_line"
        printf "   " # Separator
        printf "%s\n" "$right_line"
    done
}

# Function to execute actions for Initial Setup submenu
execute_initial_setup_action() {
    local choice="$1"
    case $choice in
        1)
            echo "Executing Example Initial Setup 1..."
            read -p "Press Enter to continue..."
            ;;
        2)
            echo "Executing Example Initial Setup 2..."
            read -p "Press Enter to continue..."
            ;;
        *)
            echo "Invalid choice. Please try again."
            read -p "Press Enter to continue..."
            ;;
    esac
}

# Function to execute actions for Application Setup submenu
execute_application_setup_action() {
    local choice="$1"
    case $choice in
        1)
            echo "Executing Example App Setup 1..."
            read -p "Press Enter to continue..."
            ;;
        2)
            echo "Executing Example App Setup 2..."
            read -p "Press Enter to continue..."
            ;;
        *)
            echo "Invalid choice. Please try again."
            read -p "Press Enter to continue..."
            ;;
    esac
}

# Function to execute actions for Clone Projects submenu
execute_clone_projects_action() {
    local choice="$1"
    case $choice in
        1)
            echo "Executing Example Clone Project 1..."
            read -p "Press Enter to continue..."
            ;;
        2)
            echo "Executing Example Clone Project 2..."
            read -p "Press Enter to continue..."
            ;;
        *)
            echo "Invalid choice. Please try again."
            read -p "Press Enter to continue..."
            ;;
    esac
}

# Function to execute actions for Backup & Restore submenu
execute_backup_restore_action() {
    local choice="$1"
    case $choice in
        1)
            echo "Executing Example Backup 1..."
            read -p "Press Enter to continue..."
            ;;
        2)
            echo "Executing Example Restore 1..."
            read -p "Press Enter to continue..."
            ;;
        *)
            echo "Invalid choice. Please try again."
            read -p "Press Enter to continue..."
            ;;
    esac
}

# Function to execute actions for Port Management submenu
execute_port_management_action() {
    local choice="$1"
    case $choice in
        1)
            echo "Executing Example Port 1..."
            read -p "Press Enter to continue..."
            ;;
        2)
            echo "Executing Example Port 2..."
            read -p "Press Enter to continue..."
            ;;
        *)
            echo "Invalid choice. Please try again."
            read -p "Press Enter to continue..."
            ;;
    esac
}

# Function to execute actions for Symbolic Links submenu
execute_symbolic_links_action() {
    local choice="$1"
    case $choice in
        1)
            echo "Executing Example Symlink 1..."
            read -p "Press Enter to continue..."
            ;;
        2)
            echo "Executing Example Symlink 2..."
            read -p "Press Enter to continue..."
            ;;
        *)
            echo "Invalid choice. Please try again."
            read -p "Press Enter to continue..."
            ;;
    esac
}

# Main loop for dynamic menu navigation
while true; do
    main_menu_str=$(get_main_menu_string)
    submenu_str=""

    case $current_menu in
        "main")
            clear
            echo "$main_menu_str"
            read -p "Enter your choice: " choice
            case $choice in
                1) current_menu="initial_setup" ;;
                2) current_menu="application_setup" ;;
                3) current_menu="clone_projects" ;;
                4) current_menu="backup_restore" ;;
                5) current_menu="port_management" ;;
                6) current_menu="symbolic_links" ;;
                7)
                    submenu_str=$(get_github_projects_info_string)
                    display_side_by_side "$main_menu_str" "$submenu_str"
                    read -p "Press Enter to return to Main Menu..."
                    current_menu="main"
                    ;;
                0)
                    echo "Exiting. Goodbye!"
                    exit 0
                    ;;
                *)
                    echo "Invalid choice. Please try again."
                    read -p "Press Enter to continue..."
                    ;;
            esac
            ;;
        "initial_setup")
            submenu_str=$(get_initial_setup_menu_string)
            display_side_by_side "$main_menu_str" "$submenu_str"
            read -p "Enter your choice: " choice
            if [[ "$choice" == "0" ]]; then
                current_menu="main"
            else
                execute_initial_setup_action "$choice"
            fi
            ;;
        "application_setup")
            submenu_str=$(get_application_setup_menu_string)
            display_side_by_side "$main_menu_str" "$submenu_str"
            read -p "Enter your choice: " choice
            if [[ "$choice" == "0" ]]; then
                current_menu="main"
            else
                execute_application_setup_action "$choice"
            fi
            ;;
        "clone_projects")
            submenu_str=$(get_clone_projects_menu_string)
            display_side_by_side "$main_menu_str" "$submenu_str"
            read -p "Enter your choice: " choice
            if [[ "$choice" == "0" ]]; then
                current_menu="main"
            else
                execute_clone_projects_action "$choice"
            fi
            ;;
        "backup_restore")
            submenu_str=$(get_backup_restore_menu_string)
            display_side_by_side "$main_menu_str" "$submenu_str"
            read -p "Enter your choice: " choice
            if [[ "$choice" == "0" ]]; then
                current_menu="main"
            else
                execute_backup_restore_action "$choice"
            fi
            ;;
        "port_management")
            submenu_str=$(get_port_management_menu_string)
            display_side_by_side "$main_menu_str" "$submenu_str"
            read -p "Enter your choice: " choice
            if [[ "$choice" == "0" ]]; then
                current_menu="main"
            else
                execute_port_management_action "$choice"
            fi
            ;;
        "symbolic_links")
            submenu_str=$(get_symbolic_links_menu_string)
            display_side_by_side "$main_menu_str" "$submenu_str"
            read -p "Enter your choice: " choice
            if [[ "$choice" == "0" ]]; then
                current_menu="main"
            else
                execute_symbolic_links_action "$choice"
            fi
            ;;
    esac
done