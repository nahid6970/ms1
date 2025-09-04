import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox, filedialog
import json
import re
import os
import threading

# Set the appearance mode and default color theme
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

AHK_SCRIPT_PATH = "ahk_v2.ahk"
SHORTCUTS_JSON_PATH = "ahk_shortcuts.json"

class AddEditShortcutDialog(ctk.CTkToplevel):
    def __init__(self, master, shortcut_type, shortcut_data=None, *, font=None):
        super().__init__(master)
        self.master = master
        self.shortcut_type = shortcut_type  # "script" or "text"
        self.shortcut_data = shortcut_data  # None for add, dict for edit
        self.font = font if font else ("sans-serif", 12, "normal")
        self.transient(master)
        self.grab_set()
        self.geometry("500x500")

        if self.shortcut_data:
            self.title(f"Edit {shortcut_type.capitalize()} Shortcut")
        else:
            self.title(f"Add New {shortcut_type.capitalize()} Shortcut")

        self.create_widgets()
        if self.shortcut_data:
            self.populate_fields()

    def get_existing_categories(self):
        """Get list of existing categories from all shortcuts"""
        categories = set()
        
        # Get categories from script shortcuts
        for shortcut in self.master.script_shortcuts:
            category = shortcut.get('category', '').strip()
            if category:
                categories.add(category)
        
        # Get categories from text shortcuts
        for shortcut in self.master.text_shortcuts:
            category = shortcut.get('category', '').strip()
            if category:
                categories.add(category)
        
        # Return sorted list, with common categories first
        common_categories = ["System", "Navigation", "Text", "Media", "AutoHotkey", "General"]
        existing_sorted = sorted(categories)
        
        # Combine common categories (if they exist) with other existing ones
        result = []
        for cat in common_categories:
            if cat in existing_sorted:
                result.append(cat)
                existing_sorted.remove(cat)
        
        # Add remaining categories
        result.extend(existing_sorted)
        
        return result

    def create_widgets(self):
        # Name input (for both types)
        ctk.CTkLabel(self, text="Name:", font=self.font).pack(padx=20, pady=5, anchor="w")
        self.name_entry = ctk.CTkEntry(self, placeholder_text="e.g., Open Terminal, Version 1 Text", font=self.font)
        self.name_entry.pack(padx=20, pady=5, fill="x")
        
        # Category input (for both types) - ComboBox with existing categories
        ctk.CTkLabel(self, text="Category:", font=self.font).pack(padx=20, pady=5, anchor="w")
        
        # Get existing categories from master
        existing_categories = self.get_existing_categories()
        
        self.category_combobox = ctk.CTkComboBox(self, values=existing_categories, font=self.font)
        self.category_combobox.pack(padx=20, pady=5, fill="x")
        self.category_combobox.set("")  # Start with empty value
        
        # Description input (for both types)
        ctk.CTkLabel(self, text="Description:", font=self.font).pack(padx=20, pady=5, anchor="w")
        self.description_entry = ctk.CTkEntry(self, placeholder_text="Brief description of what this does", font=self.font)
        self.description_entry.pack(padx=20, pady=5, fill="x")
        
        if self.shortcut_type == "script":
            # Hotkey input
            ctk.CTkLabel(self, text="Hotkey:", font=self.font).pack(padx=20, pady=5, anchor="w")
            self.hotkey_entry = ctk.CTkEntry(self, placeholder_text="e.g., !Space, ^!n, #x", font=self.font)
            self.hotkey_entry.pack(padx=20, pady=5, fill="x")
            
            # Action input
            ctk.CTkLabel(self, text="Action:", font=self.font).pack(padx=20, pady=5, anchor="w")
            self.action_entry = ctk.CTkTextbox(self, height=100, font=self.font)
            self.action_entry.pack(padx=20, pady=5, fill="both", expand=True)
            
        else:  # text shortcut
            # Trigger input
            ctk.CTkLabel(self, text="Trigger (without ::):", font=self.font).pack(padx=20, pady=5, anchor="w")
            self.trigger_entry = ctk.CTkEntry(self, placeholder_text="e.g., ;v1, ;run", font=self.font)
            self.trigger_entry.pack(padx=20, pady=5, fill="x")
            
            # Replacement text input
            ctk.CTkLabel(self, text="Replacement Text:", font=self.font).pack(padx=20, pady=5, anchor="w")
            self.replacement_entry = ctk.CTkTextbox(self, height=100, font=self.font)
            self.replacement_entry.pack(padx=20, pady=5, fill="both", expand=True)

        # Save button
        if self.shortcut_data:
            save_button = ctk.CTkButton(self, text="Save Changes", command=self.save_changes, font=self.font)
        else:
            save_button = ctk.CTkButton(self, text="Add Shortcut", command=self.add_shortcut, font=self.font)
        save_button.pack(padx=20, pady=10)

    def populate_fields(self):
        self.name_entry.insert(0, self.shortcut_data.get("name", ""))
        self.category_combobox.set(self.shortcut_data.get("category", ""))
        self.description_entry.insert(0, self.shortcut_data.get("description", ""))
        
        if self.shortcut_type == "script":
            self.hotkey_entry.insert(0, self.shortcut_data.get("hotkey", ""))
            self.action_entry.insert("1.0", self.shortcut_data.get("action", ""))
        else:
            self.trigger_entry.insert(0, self.shortcut_data.get("trigger", ""))
            self.replacement_entry.insert("1.0", self.shortcut_data.get("replacement", ""))

    def add_shortcut(self):
        name = self.name_entry.get().strip()
        category = self.category_combobox.get().strip()
        description = self.description_entry.get().strip()
        
        if not name:
            messagebox.showwarning("Warning", "Name is required.", parent=self)
            return
        
        if self.shortcut_type == "script":
            hotkey = self.hotkey_entry.get().strip()
            action = self.action_entry.get("1.0", "end-1c").strip()
            
            if not hotkey or not action:
                messagebox.showwarning("Warning", "Both hotkey and action are required.", parent=self)
                return
                
            new_shortcut = {
                "name": name,
                "category": category or "General",
                "description": description,
                "hotkey": hotkey, 
                "action": action,
                "enabled": True
            }
            self.master.script_shortcuts.append(new_shortcut)
            
        else:  # text shortcut
            trigger = self.trigger_entry.get().strip()
            replacement = self.replacement_entry.get("1.0", "end-1c").strip()
            
            if not trigger or not replacement:
                messagebox.showwarning("Warning", "Both trigger and replacement are required.", parent=self)
                return
                
            new_shortcut = {
                "name": name,
                "category": category or "General",
                "description": description,
                "trigger": trigger, 
                "replacement": replacement,
                "enabled": True
            }
            self.master.text_shortcuts.append(new_shortcut)

        self.master.update_list_displays()
        self.master.save_shortcuts_json()
        self.destroy()

    def save_changes(self):
        name = self.name_entry.get().strip()
        category = self.category_combobox.get().strip()
        description = self.description_entry.get().strip()
        
        if not name:
            messagebox.showwarning("Warning", "Name is required.", parent=self)
            return
        
        self.shortcut_data["name"] = name
        self.shortcut_data["category"] = category or "General"
        self.shortcut_data["description"] = description
        
        if self.shortcut_type == "script":
            hotkey = self.hotkey_entry.get().strip()
            action = self.action_entry.get("1.0", "end-1c").strip()
            
            if not hotkey or not action:
                messagebox.showwarning("Warning", "Both hotkey and action are required.", parent=self)
                return
                
            self.shortcut_data["hotkey"] = hotkey
            self.shortcut_data["action"] = action
            
        else:  # text shortcut
            trigger = self.trigger_entry.get().strip()
            replacement = self.replacement_entry.get("1.0", "end-1c").strip()
            
            if not trigger or not replacement:
                messagebox.showwarning("Warning", "Both trigger and replacement are required.", parent=self)
                return
                
            self.shortcut_data["trigger"] = trigger
            self.shortcut_data["replacement"] = replacement

        self.master.update_list_displays()
        self.master.save_shortcuts_json()
        self.destroy()


class AHKShortcutEditor(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("AutoHotkey Script Editor")
        self.geometry("1000x700")

        self.app_font = ("jetbrainsmono nfp", 12, "normal")
        self.bold_font = ("jetbrainsmono nfp", 16, "bold")

        self.script_shortcuts = []
        self.text_shortcuts = []
        self.other_content = []  # Store non-shortcut content
        self.script_widgets = {}
        self.text_widgets = {}
        self.show_categories = tk.BooleanVar(value=True)
        
        self.load_shortcuts_json()
        self.create_widgets()
        self.update_list_displays()

    def create_widgets(self):
        # Configure grid layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=0)  # Search bar
        self.grid_rowconfigure(1, weight=1)  # Main content
        self.grid_rowconfigure(2, weight=0)  # Buttons

        # Search Bar
        self.search_frame = ctk.CTkFrame(self)
        self.search_frame.grid(row=0, column=0, columnspan=2, padx=10, pady=5, sticky="ew")
        self.search_frame.grid_columnconfigure(1, weight=1)

        self.settings_button = ctk.CTkButton(self.search_frame, text="⚙", width=30, command=self.toggle_categories)
        self.settings_button.grid(row=0, column=0, padx=5, pady=5)
        
        self.search_entry = ctk.CTkEntry(self.search_frame, placeholder_text="Search shortcuts...", font=self.app_font)
        self.search_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.search_entry.bind("<KeyRelease>", self.filter_list_displays)

        # Script Shortcuts Section (Left)
        self.script_frame = ctk.CTkFrame(self)
        self.script_frame.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")
        self.script_frame.grid_columnconfigure(0, weight=1)
        self.script_frame.grid_rowconfigure(0, weight=0)
        self.script_frame.grid_rowconfigure(1, weight=1)

        self.script_label = ctk.CTkLabel(self.script_frame, text="Script Shortcuts", font=self.bold_font)
        self.script_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")

        self.script_scroll_frame = ctk.CTkScrollableFrame(self.script_frame)
        self.script_scroll_frame.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")
        self.script_scroll_frame.grid_columnconfigure(0, weight=1)
        self.script_list_items = []
        self.selected_script_shortcut = None

        # Text Shortcuts Section (Right)
        self.text_frame = ctk.CTkFrame(self)
        self.text_frame.grid(row=1, column=1, padx=10, pady=5, sticky="nsew")
        self.text_frame.grid_columnconfigure(0, weight=1)
        self.text_frame.grid_rowconfigure(0, weight=0)
        self.text_frame.grid_rowconfigure(1, weight=1)

        self.text_label = ctk.CTkLabel(self.text_frame, text="Text Shortcuts", font=self.bold_font)
        self.text_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")

        self.text_scroll_frame = ctk.CTkScrollableFrame(self.text_frame)
        self.text_scroll_frame.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")
        self.text_scroll_frame.grid_columnconfigure(0, weight=1)
        self.text_list_items = []
        self.selected_text_shortcut = None

        # Buttons Frame (Bottom)
        self.button_frame = ctk.CTkFrame(self)
        self.button_frame.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
        self.button_frame.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)

        self.add_script_button = ctk.CTkButton(self.button_frame, text="Add Script Shortcut", 
                                             command=self.open_add_script_dialog, font=self.app_font)
        self.add_script_button.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        self.add_text_button = ctk.CTkButton(self.button_frame, text="Add Text Shortcut", 
                                           command=self.open_add_text_dialog, font=self.app_font)
        self.add_text_button.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        self.edit_button = ctk.CTkButton(self.button_frame, text="Edit Selected", 
                                       command=self.open_edit_dialog, font=self.app_font)
        self.edit_button.grid(row=0, column=2, padx=5, pady=5, sticky="ew")

        self.remove_button = ctk.CTkButton(self.button_frame, text="Remove Selected", 
                                         fg_color="red", command=self.remove_selected_item, font=self.app_font)
        self.remove_button.grid(row=0, column=3, padx=5, pady=5, sticky="ew")

        self.save_button = ctk.CTkButton(self.button_frame, text="Generate AHK Script", 
                                       fg_color="green", command=self.generate_ahk_script, font=self.app_font)
        self.save_button.grid(row=0, column=4, padx=5, pady=5, sticky="ew")

    def load_shortcuts_json(self):
        if os.path.exists(SHORTCUTS_JSON_PATH):
            try:
                with open(SHORTCUTS_JSON_PATH, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.script_shortcuts = data.get("script_shortcuts", [])
                    self.text_shortcuts = data.get("text_shortcuts", [])
                    self.show_categories.set(data.get("show_categories", True))
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load shortcuts JSON: {e}")
                self.create_default_shortcuts()
        else:
            # If JSON doesn't exist, try to parse existing AHK script
            self.import_from_ahk_script()

    def create_default_shortcuts(self):
        """Create some default shortcuts as examples"""
        self.script_shortcuts = [
            {
                "name": "Open Terminal",
                "category": "System",
                "description": "Opens PowerShell as admin",
                "hotkey": "!x",
                "action": 'RunWait("pwsh -Command `"cd $env:USERPROFILE; Start-Process pwsh -Verb RunAs`"", , "Hide")'
            }
        ]
        self.text_shortcuts = [
            {
                "name": "AHK Version 1",
                "category": "AutoHotkey",
                "description": "AutoHotkey v1 header",
                "trigger": ";v1",
                "replacement": "#Requires AutoHotkey v1.0"
            },
            {
                "name": "AHK Version 2", 
                "category": "AutoHotkey",
                "description": "AutoHotkey v2 header",
                "trigger": ";v2",
                "replacement": "#Requires AutoHotkey v2.0"
            }
        ]

    def save_shortcuts_json(self):
        try:
            data = {
                "script_shortcuts": self.script_shortcuts,
                "text_shortcuts": self.text_shortcuts,
                "show_categories": self.show_categories.get()
            }
            with open(SHORTCUTS_JSON_PATH, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save shortcuts JSON: {e}")

    def import_from_ahk_script(self):
        """Import shortcuts from existing AHK script if JSON doesn't exist"""
        if not os.path.exists(AHK_SCRIPT_PATH):
            self.create_default_shortcuts()
            return

        try:
            with open(AHK_SCRIPT_PATH, 'r', encoding='utf-8') as f:
                content = f.read()
            
            self.parse_ahk_content(content)
            # Save the imported shortcuts to JSON
            self.save_shortcuts_json()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to import from AHK script: {e}")
            self.create_default_shortcuts()

    def parse_ahk_content(self, content):
        lines = content.split('\n')
        current_block = []
        in_function = False
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            # Skip empty lines and comments at the top level
            if not line or line.startswith(';'):
                current_block.append(lines[i])
                i += 1
                continue
            
            # Check for text shortcuts (::trigger::replacement)
            text_match = re.match(r'^::([^:]+)::\s*(.*)$', line)
            if text_match:
                trigger = text_match.group(1)
                replacement = text_match.group(2)
                self.text_shortcuts.append({
                    "name": f"Text: {trigger}",
                    "category": "Imported",
                    "description": "Imported from AHK script",
                    "trigger": trigger, 
                    "replacement": replacement
                })
                i += 1
                continue
            
            # Check for script shortcuts (hotkey::action or hotkey:: { ... })
            script_match = re.match(r'^([^:]+)::\s*(.*)$', line)
            if script_match:
                hotkey = script_match.group(1)
                action_start = script_match.group(2)
                
                if action_start.strip() == '{':
                    # Multi-line function
                    action_lines = []
                    i += 1
                    brace_count = 1
                    
                    while i < len(lines) and brace_count > 0:
                        current_line = lines[i]
                        action_lines.append(current_line)
                        
                        # Count braces to find the end
                        brace_count += current_line.count('{') - current_line.count('}')
                        i += 1
                    
                    action = '\n'.join(action_lines[:-1])  # Exclude the closing brace line
                else:
                    # Single line action
                    action = action_start
                    i += 1
                
                self.script_shortcuts.append({
                    "name": f"Script: {hotkey}",
                    "category": "Imported",
                    "description": "Imported from AHK script",
                    "hotkey": hotkey, 
                    "action": action
                })
                continue
            
            # Everything else goes to other_content
            current_block.append(lines[i])
            i += 1
        
        # Store remaining content
        if current_block:
            self.other_content = current_block

    def update_list_displays(self, search_query=""):
        self.update_script_display(search_query)
        self.update_text_display(search_query)

    def update_script_display(self, search_query=""):
        # Clear existing items
        for item in self.script_list_items:
            item.destroy()
        self.script_list_items.clear()
        self.script_widgets.clear()
        self.selected_script_shortcut = None

        # Filter shortcuts
        filtered_shortcuts = [
            shortcut for shortcut in self.script_shortcuts
            if search_query.lower() in f"{shortcut.get('name', '')} {shortcut.get('hotkey', '')} {shortcut.get('description', '')} {shortcut.get('category', '')}".lower()
        ]
        
        row = 0
        if self.show_categories.get():
            # Group by category
            categories = {}
            for shortcut in filtered_shortcuts:
                category = shortcut.get('category', 'General')
                if category not in categories:
                    categories[category] = []
                categories[category].append(shortcut)
            
            # Sort categories and shortcuts within each category
            for category in sorted(categories.keys()):
                # Add category header
                category_label = ctk.CTkLabel(self.script_scroll_frame, text=f"📁 {category}", 
                                            anchor="w", font=self.bold_font, 
                                            text_color=("gray10", "gray90"))
                category_label.grid(row=row, column=0, padx=5, pady=(10, 2), sticky="ew")
                self.script_list_items.append(category_label)
                row += 1
                
                # Sort shortcuts within category by hotkey
                category_shortcuts = sorted(categories[category], key=lambda x: x.get('hotkey', '').lower())
                
                for shortcut in category_shortcuts:
                    name = shortcut.get('name', 'Unnamed')
                    hotkey = shortcut.get('hotkey', '')
                    description = shortcut.get('description', '')

                    item_frame = ctk.CTkFrame(self.script_scroll_frame, fg_color="transparent")
                    item_frame.grid(row=row, column=0, sticky="ew", pady=1, padx=5)
                    item_frame.grid_columnconfigure(1, weight=1)

                    enabled = shortcut.get('enabled', True)
                    icon = "\uf205" if enabled else "\uf204"
                    color = "#9ef959" if enabled else "gray"

                    icon_label = ctk.CTkLabel(item_frame, text=icon, text_color=color, font=self.app_font, width=3)
                    icon_label.grid(row=0, column=0)
                    icon_label.bind("<Button-1>", lambda e, s=shortcut, i=icon_label: self.toggle_enabled(s, i))

                    display_text = f"{hotkey}  {name}"
                    if description:
                        display_text += f" ({description[:25]}...)" if len(description) > 25 else f" ({description})"
                    
                    label = ctk.CTkLabel(item_frame, text=display_text, anchor="w", font=self.app_font)
                    label.grid(row=0, column=1, sticky="ew", padx=5)
                    label.shortcut_obj = shortcut
                    label.bind("<Button-1>", lambda event, l=label: self.select_script_shortcut(l))
                    label.bind("<Double-Button-1>", lambda event: self.open_edit_dialog())

                    self.script_widgets[shortcut['hotkey']] = {'icon': icon_label, 'label': label}
                    self.script_list_items.append(item_frame)
                    row += 1
        else:
            # Display as a flat list
            sorted_shortcuts = sorted(filtered_shortcuts, key=lambda x: x.get('hotkey', '').lower())
            for shortcut in sorted_shortcuts:
                name = shortcut.get('name', 'Unnamed')
                hotkey = shortcut.get('hotkey', '')
                description = shortcut.get('description', '')

                item_frame = ctk.CTkFrame(self.script_scroll_frame, fg_color="transparent")
                item_frame.grid(row=row, column=0, sticky="ew", pady=1, padx=5)
                item_frame.grid_columnconfigure(1, weight=1)

                enabled = shortcut.get('enabled', True)
                icon = "\uf205" if enabled else "\uf204"
                color = "#9ef959" if enabled else "gray"

                icon_label = ctk.CTkLabel(item_frame, text=icon, text_color=color, font=self.app_font, width=3)
                icon_label.grid(row=0, column=0)
                icon_label.bind("<Button-1>", lambda e, s=shortcut, i=icon_label: self.toggle_enabled(s, i))

                display_text = f"{hotkey}  {name}"
                if description:
                    display_text += f" ({description[:25]}...)" if len(description) > 25 else f" ({description})"
                
                label = ctk.CTkLabel(item_frame, text=display_text, anchor="w", font=self.app_font)
                label.grid(row=0, column=1, sticky="ew", padx=5)
                label.shortcut_obj = shortcut
                label.bind("<Button-1>", lambda event, l=label: self.select_script_shortcut(l))
                label.bind("<Double-Button-1>", lambda event: self.open_edit_dialog())

                self.script_widgets[shortcut['hotkey']] = {'icon': icon_label, 'label': label}
                self.script_list_items.append(item_frame)
                row += 1

    def update_text_display(self, search_query=""):
        # Clear existing items
        for item in self.text_list_items:
            item.destroy()
        self.text_list_items.clear()
        self.text_widgets.clear()
        self.selected_text_shortcut = None

        # Filter shortcuts
        filtered_shortcuts = [
            shortcut for shortcut in self.text_shortcuts
            if search_query.lower() in f"{shortcut.get('name', '')} {shortcut.get('trigger', '')} {shortcut.get('description', '')} {shortcut.get('category', '')}".lower()
        ]
        
        row = 0
        if self.show_categories.get():
            # Group by category
            categories = {}
            for shortcut in filtered_shortcuts:
                category = shortcut.get('category', 'General')
                if category not in categories:
                    categories[category] = []
                categories[category].append(shortcut)
            
            # Sort categories and shortcuts within each category
            for category in sorted(categories.keys()):
                # Add category header
                category_label = ctk.CTkLabel(self.text_scroll_frame, text=f"📁 {category}", 
                                            anchor="w", font=self.bold_font, 
                                            text_color=("gray10", "gray90"))
                category_label.grid(row=row, column=0, padx=5, pady=(10, 2), sticky="ew")
                self.text_list_items.append(category_label)
                row += 1
                
                # Sort shortcuts within category by trigger
                category_shortcuts = sorted(categories[category], key=lambda x: x.get('trigger', '').lower())
                
                for shortcut in category_shortcuts:
                    name = shortcut.get('name', 'Unnamed')
                    trigger = shortcut.get('trigger', '')
                    description = shortcut.get('description', '')
                    
                    item_frame = ctk.CTkFrame(self.text_scroll_frame, fg_color="transparent")
                    item_frame.grid(row=row, column=0, sticky="ew", pady=1, padx=5)
                    item_frame.grid_columnconfigure(1, weight=1)

                    enabled = shortcut.get('enabled', True)
                    icon = "\uf205" if enabled else "\uf204"
                    color = "#9ef959" if enabled else "gray"

                    icon_label = ctk.CTkLabel(item_frame, text=icon, text_color=color, font=self.app_font, width=3)
                    icon_label.grid(row=0, column=0)
                    icon_label.bind("<Button-1>", lambda e, s=shortcut, i=icon_label: self.toggle_enabled(s, i))

                    display_text = f"{trigger}  {name}"
                    if description:
                        display_text += f" ({description[:25]}...)" if len(description) > 25 else f" ({description})"
                    
                    label = ctk.CTkLabel(item_frame, text=display_text, anchor="w", font=self.app_font)
                    label.grid(row=0, column=1, sticky="ew", padx=5)
                    label.shortcut_obj = shortcut
                    label.bind("<Button-1>", lambda event, l=label: self.select_text_shortcut(l))
                    label.bind("<Double-Button-1>", lambda event: self.open_edit_dialog())

                    self.text_widgets[shortcut['trigger']] = {'icon': icon_label, 'label': label}
                    self.text_list_items.append(item_frame)
                    row += 1
        else:
            # Display as a flat list
            sorted_shortcuts = sorted(filtered_shortcuts, key=lambda x: x.get('trigger', '').lower())
            for shortcut in sorted_shortcuts:
                name = shortcut.get('name', 'Unnamed')
                trigger = shortcut.get('trigger', '')
                description = shortcut.get('description', '')
                
                item_frame = ctk.CTkFrame(self.text_scroll_frame, fg_color="transparent")
                item_frame.grid(row=row, column=0, sticky="ew", pady=1, padx=5)
                item_frame.grid_columnconfigure(1, weight=1)

                enabled = shortcut.get('enabled', True)
                icon = "\uf205" if enabled else "\uf204"
                color = "#9ef959" if enabled else "gray"

                icon_label = ctk.CTkLabel(item_frame, text=icon, text_color=color, font=self.app_font, width=3)
                icon_label.grid(row=0, column=0)
                icon_label.bind("<Button-1>", lambda e, s=shortcut, i=icon_label: self.toggle_enabled(s, i))

                display_text = f"{trigger}  {name}"
                if description:
                    display_text += f" ({description[:25]}...)" if len(description) > 25 else f" ({description})"
                
                label = ctk.CTkLabel(item_frame, text=display_text, anchor="w", font=self.app_font)
                label.grid(row=0, column=1, sticky="ew", padx=5)
                label.shortcut_obj = shortcut
                label.bind("<Button-1>", lambda event, l=label: self.select_text_shortcut(l))
                label.bind("<Double-Button-1>", lambda event: self.open_edit_dialog())

                self.text_widgets[shortcut['trigger']] = {'icon': icon_label, 'label': label}
                self.text_list_items.append(item_frame)
                row += 1

    def select_script_shortcut(self, label):
        # Deselect previous selections
        self.clear_selections()
        
        # Select new script shortcut
        self.selected_script_shortcut = label.shortcut_obj
        label.master.configure(fg_color=ctk.ThemeManager.theme["CTkButton"]["fg_color"])

    def select_text_shortcut(self, label):
        # Deselect previous selections
        self.clear_selections()
        
        # Select new text shortcut
        self.selected_text_shortcut = label.shortcut_obj
        label.master.configure(fg_color=ctk.ThemeManager.theme["CTkButton"]["fg_color"])

    def clear_selections(self):
        # Clear script selection
        if self.selected_script_shortcut:
            for item_frame in self.script_list_items:
                # The frame itself doesn't have shortcut_obj, the label inside it does.
                # So we search for the label with the matching shortcut_obj and then configure the frame.
                for widget in item_frame.winfo_children():
                    if hasattr(widget, 'shortcut_obj') and widget.shortcut_obj == self.selected_script_shortcut:
                        item_frame.configure(fg_color="transparent")
                        break
            self.selected_script_shortcut = None
        
        # Clear text selection
        if self.selected_text_shortcut:
            for item_frame in self.text_list_items:
                for widget in item_frame.winfo_children():
                    if hasattr(widget, 'shortcut_obj') and widget.shortcut_obj == self.selected_text_shortcut:
                        item_frame.configure(fg_color="transparent")
                        break
            self.selected_text_shortcut = None

    def filter_list_displays(self, event=None):
        self.update_list_displays(search_query=self.search_entry.get())

    def toggle_categories(self):
        self.show_categories.set(not self.show_categories.get())
        self.save_shortcuts_json()
        self.update_list_displays(search_query=self.search_entry.get())

    def open_add_script_dialog(self):
        AddEditShortcutDialog(self, "script", font=self.app_font)

    def open_add_text_dialog(self):
        AddEditShortcutDialog(self, "text", font=self.app_font)

    def open_edit_dialog(self):
        if self.selected_script_shortcut:
            AddEditShortcutDialog(self, "script", self.selected_script_shortcut, font=self.app_font)
        elif self.selected_text_shortcut:
            AddEditShortcutDialog(self, "text", self.selected_text_shortcut, font=self.app_font)
        else:
            messagebox.showwarning("Warning", "Please select a shortcut to edit.")

    def remove_selected_item(self):
        if self.selected_script_shortcut:
            if self.selected_script_shortcut in self.script_shortcuts:
                self.script_shortcuts.remove(self.selected_script_shortcut)
                self.update_list_displays()
                self.save_shortcuts_json()
            self.selected_script_shortcut = None
        elif self.selected_text_shortcut:
            if self.selected_text_shortcut in self.text_shortcuts:
                self.text_shortcuts.remove(self.selected_text_shortcut)
                self.update_list_displays()
                self.save_shortcuts_json()
            self.selected_text_shortcut = None
        else:
            messagebox.showwarning("Warning", "No shortcut selected to remove.")

    def update_shortcut_visuals(self, shortcut):
        """Update the visuals of a single shortcut widget."""
        widget_dict = None
        key = None
        if 'hotkey' in shortcut:
            key = shortcut['hotkey']
            widget_dict = self.script_widgets.get(key)
        elif 'trigger' in shortcut:
            key = shortcut['trigger']
            widget_dict = self.text_widgets.get(key)

        if widget_dict:
            icon_label = widget_dict['icon']
            enabled = shortcut.get('enabled', True)
            icon = "\uf205" if enabled else "\uf204"
            color = "#9ef959" if enabled else "gray"
            icon_label.configure(text=icon, text_color=color)

    def toggle_enabled(self, shortcut, icon_label):
        """Toggle enabled state with smooth visual feedback."""
        icon_label.configure(text="⟳", text_color="#63dbff")

        def toggle_operation():
            try:
                shortcut["enabled"] = not shortcut.get("enabled", True)
                self.save_shortcuts_json()
                self.after(100, lambda: self.update_shortcut_visuals(shortcut))
            except Exception as e:
                self.after(100, lambda: self.update_shortcut_visuals(shortcut))
                messagebox.showerror("Error", f"Failed to toggle shortcut: {e}", parent=self)

        threading.Thread(target=toggle_operation, daemon=True).start()

    def generate_ahk_script(self):
        try:
            # Build the new script content
            output_lines = []
            
            # Add AHK header
            output_lines.append("#Requires AutoHotkey v2.0")
            output_lines.append("#SingleInstance")
            output_lines.append("Persistent")
            output_lines.append("")
            
            # Add script shortcuts
            if self.script_shortcuts:
                output_lines.append(";! === SCRIPT SHORTCUTS ===")
                for shortcut in self.script_shortcuts:
                    if not shortcut.get('enabled', True):
                        continue
                    # Add comment with name and description
                    output_lines.append(f";! {shortcut.get('name', 'Unnamed')}")
                    if shortcut.get('description'):
                        output_lines.append(f";! {shortcut.get('description')}")
                    
                    if '\n' in shortcut.get('action', ''):
                        # Multi-line action
                        output_lines.append(f"{shortcut.get('hotkey', '')}:: {{")
                        for line in shortcut.get('action', '').split('\n'):
                            if line.strip():
                                output_lines.append(f"    {line}")
                        output_lines.append("}")
                    else:
                        # Single line action
                        output_lines.append(f"{shortcut.get('hotkey', '')}::{shortcut.get('action', '')}")
                    output_lines.append("")
            
            # Add text shortcuts
            if self.text_shortcuts:
                output_lines.append(";! === TEXT SHORTCUTS ===")
                for shortcut in self.text_shortcuts:
                    if not shortcut.get('enabled', True):
                        continue
                    # Add comment with name and description
                    output_lines.append(f";! {shortcut.get('name', 'Unnamed')}")
                    if shortcut.get('description'):
                        output_lines.append(f";! {shortcut.get('description')}")
                    output_lines.append(f"::{shortcut.get('trigger', '')}::{shortcut.get('replacement', '')}")
                    output_lines.append("")
            
            # Write to file
            output_file = "generated_shortcuts.ahk"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(output_lines))
            
            messagebox.showinfo("Success", f"AHK script generated successfully as '{output_file}'!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate AHK script: {e}")


if __name__ == "__main__":
    app = AHKShortcutEditor()
    app.mainloop()