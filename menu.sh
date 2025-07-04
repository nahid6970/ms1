#!/bin/bash

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

# Function to display only the main menu (used when no submenu is active)
display_main_menu_only() {
    clear
    get_main_menu_string
}

# Function to handle Initial Setup submenu
initial_setup_menu() {
    local main_menu_str=$(get_main_menu_string)
    while true; do
        local submenu_str=$(get_initial_setup_menu_string)
        display_side_by_side "$main_menu_str" "$submenu_str"
        read -p "Enter your choice: " choice
        case $choice in
            1)
                echo "Executing Example Initial Setup 1..."
                read -p "Press Enter to continue..."
                ;;
            2)
                echo "Executing Example Initial Setup 2..."
                read -p "Press Enter to continue..."
                ;;
            0)
                break
                ;;
            *)
                echo "Invalid choice. Please try again."
                read -p "Press Enter to continue..."
                ;;
        esac
    done
}

# Function to handle Application Setup submenu
application_setup_menu() {
    local main_menu_str=$(get_main_menu_string)
    while true; do
        local submenu_str=$(get_application_setup_menu_string)
        display_side_by_side "$main_menu_str" "$submenu_str"
        read -p "Enter your choice: " choice
        case $choice in
            1)
                echo "Executing Example App Setup 1..."
                read -p "Press Enter to continue..."
                ;;
            2)
                echo "Executing Example App Setup 2..."
                read -p "Press Enter to continue..."
                ;;
            0)
                break
                ;;
            *)
                echo "Invalid choice. Please try again."
                read -p "Press Enter to continue..."
                ;;
        esac
    done
}

# Function to handle Clone Projects submenu
clone_projects_menu() {
    local main_menu_str=$(get_main_menu_string)
    while true; do
        local submenu_str=$(get_clone_projects_menu_string)
        display_side_by_side "$main_menu_str" "$submenu_str"
        read -p "Enter your choice: " choice
        case $choice in
            1)
                echo "Executing Example Clone Project 1..."
                read -p "Press Enter to continue..."
                ;;
            2)
                echo "Executing Example Clone Project 2..."
                read -p "Press Enter to continue..."
                ;;
            0)
                break
                ;;
            *)
                echo "Invalid choice. Please try again."
                read -p "Press Enter to continue..."
                ;;
        esac
    done
}

# Function to handle Backup & Restore submenu
backup_restore_menu() {
    local main_menu_str=$(get_main_menu_string)
    while true; do
        local submenu_str=$(get_backup_restore_menu_string)
        display_side_by_side "$main_menu_str" "$submenu_str"
        read -p "Enter your choice: " choice
        case $choice in
            1)
                echo "Executing Example Backup 1..."
                read -p "Press Enter to continue..."
                ;;
            2)
                echo "Executing Example Restore 1..."
                read -p "Press Enter to continue..."
                ;;
            0)
                break
                ;;
            *)
                echo "Invalid choice. Please try again."
                read -p "Press Enter to continue..."
                ;;
        esac
    done
}

# Function to handle Port Management submenu
port_management_menu() {
    local main_menu_str=$(get_main_menu_string)
    while true; do
        local submenu_str=$(get_port_management_menu_string)
        display_side_by_side "$main_menu_str" "$submenu_str"
        read -p "Enter your choice: " choice
        case $choice in
            1)
                echo "Executing Example Port 1..."
                read -p "Press Enter to continue..."
                ;;
            2)
                echo "Executing Example Port 2..."
                read -p "Press Enter to continue..."
                ;;
            0)
                break
                ;;
            *)
                echo "Invalid choice. Please try again."
                read -p "Press Enter to continue..."
                ;;
        esac
    done
}

# Function to handle Symbolic Links submenu
symbolic_links_menu() {
    local main_menu_str=$(get_main_menu_string)
    while true; do
        local submenu_str=$(get_symbolic_links_menu_string)
        display_side_by_side "$main_menu_str" "$submenu_str"
        read -p "Enter your choice: " choice
        case $choice in
            1)
                echo "Executing Example Symlink 1..."
                read -p "Press Enter to continue..."
                ;;
            2)
                echo "Executing Example Symlink 2..."
                read -p "Press Enter to continue..."
                ;;
            0)
                break
                ;;
            *)
                echo "Invalid choice. Please try again."
                read -p "Press Enter to continue..."
                ;;
        esac
    done
}

# Main loop
while true; do
    display_main_menu_only
    read -p "Enter your choice: " main_choice
    case $main_choice in
        1)
            initial_setup_menu
            ;;
        2)
            application_setup_menu
            ;;
        3)
            clone_projects_menu
            ;;
        4)
            backup_restore_menu
            ;;
        5)
            port_management_menu
            ;;
        6)
            symbolic_links_menu
            ;;
        7)
            local main_menu_str=$(get_main_menu_string)
            local submenu_str=$(get_github_projects_info_string)
            display_side_by_side "$main_menu_str" "$submenu_str"
            read -p "Press Enter to return to Main Menu..."
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
done
