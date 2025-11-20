import tkinter as tk
from tkinter import ttk, messagebox
import winreg
import os

class AutostartManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Autostart Program Manager")
        self.root.geometry("800x600")
        
        # Create main frame
        main_frame = ttk.Frame(root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights for resizing
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="Autostart Program Manager", font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # Create frames for each tab
        self.current_user_frame = ttk.Frame(self.notebook, padding="5")
        self.all_users_frame = ttk.Frame(self.notebook, padding="5")
        
        self.notebook.add(self.current_user_frame, text="Current User")
        self.notebook.add(self.all_users_frame, text="All Users")
        
        # Current User tab
        self.setup_tab(self.current_user_frame, "HKEY_CURRENT_USER", winreg.HKEY_CURRENT_USER)
        
        # All Users tab
        self.setup_tab(self.all_users_frame, "HKEY_LOCAL_MACHINE", winreg.HKEY_LOCAL_MACHINE)
        
        # Refresh button
        refresh_btn = ttk.Button(main_frame, text="Refresh List", command=self.refresh_all_tabs)
        refresh_btn.grid(row=2, column=0, pady=(10, 0))
        
        # Configure weights for resizing
        main_frame.rowconfigure(1, weight=1)
        self.current_user_frame.columnconfigure(0, weight=1)
        self.current_user_frame.rowconfigure(1, weight=1)
        self.all_users_frame.columnconfigure(0, weight=1)
        self.all_users_frame.rowconfigure(1, weight=1)
        
        # Load initial data
        self.refresh_all_tabs()
    
    def setup_tab(self, parent, reg_path, reg_hkey):
        """Setup a tab with a treeview and buttons"""
        # Create treeview to display programs
        columns = ("name", "path", "enabled")
        tree = ttk.Treeview(parent, columns=columns, show="headings", height=15)
        
        tree.heading("name", text="Program Name")
        tree.heading("path", text="Path")
        tree.heading("enabled", text="Status")
        
        tree.column("name", width=150)
        tree.column("path", width=450)
        tree.column("enabled", width=80, anchor="center")
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Buttons frame
        buttons_frame = ttk.Frame(parent)
        buttons_frame.grid(row=1, column=0, pady=(10, 0), sticky=(tk.W, tk.E))
        buttons_frame.columnconfigure(0, weight=1)
        
        # Toggle button
        toggle_btn = ttk.Button(buttons_frame, text="Toggle Selected", command=lambda: self.toggle_selected(tree, reg_hkey))
        toggle_btn.grid(row=0, column=0, padx=(0, 5))
        
        # Remove button
        remove_btn = ttk.Button(buttons_frame, text="Remove Selected", command=lambda: self.remove_selected(tree, reg_hkey))
        remove_btn.grid(row=0, column=1, padx=(0, 5))
        
        # Add button
        add_btn = ttk.Button(buttons_frame, text="Add Program", command=lambda: self.add_program(tree, reg_hkey))
        add_btn.grid(row=0, column=2)
        
        # Store tree reference for later use
        if reg_hkey == winreg.HKEY_CURRENT_USER:
            self.current_user_tree = tree
        else:
            self.all_users_tree = tree
    
    def get_autostart_programs(self, reg_hkey):
        """Get list of autostart programs from registry"""
        programs = []
        try:
            with winreg.OpenKey(reg_hkey, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_READ) as key:
                i = 0
                while True:
                    try:
                        name, value, _ = winreg.EnumValue(key, i)
                        # Check if the program path exists
                        path_exists = os.path.exists(value) or (value.startswith('"') and os.path.exists(value.split('"')[1]))
                        status = "Enabled" if path_exists else "Missing"
                        programs.append((name, value, status))
                        i += 1
                    except WindowsError:
                        break
        except FileNotFoundError:
            # Key doesn't exist, return empty list
            pass

        return programs
    
    def refresh_tab(self, tree, reg_hkey):
        """Refresh a specific tab"""
        # Clear existing items
        for item in tree.get_children():
            tree.delete(item)

        # Get programs from registry
        programs = self.get_autostart_programs(reg_hkey)

        # Insert programs into treeview
        for name, path, status in programs:
            tree.insert("", tk.END, values=(name, path, status))
    
    def refresh_all_tabs(self):
        """Refresh both tabs"""
        self.refresh_tab(self.current_user_tree, winreg.HKEY_CURRENT_USER)
        self.refresh_tab(self.all_users_tree, winreg.HKEY_LOCAL_MACHINE)
    
    def toggle_selected(self, tree, reg_hkey):
        """Toggle the selected program's autostart status"""
        selected_items = tree.selection()
        if not selected_items:
            messagebox.showwarning("No Selection", "Please select a program to toggle.")
            return

        for item in selected_items:
            program_name = tree.item(item, "values")[0]

            # Check if the program is currently in autostart by trying to read it
            current_path = None
            try:
                with winreg.OpenKey(reg_hkey, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_READ) as key:
                    current_path = winreg.QueryValueEx(key, program_name)[0]
            except FileNotFoundError:
                # This shouldn't happen in this context since we're selecting from the list
                # but just in case
                pass

            # If current_path exists, the program is enabled, so we'll disable it
            # If it doesn't exist, that's unexpected since we're selecting from the list of active entries
            if current_path:
                # Entry exists, so disable by removing it
                if messagebox.askyesno("Disable Program", f"Do you want to disable '{program_name}' from autostart?"):
                    try:
                        with winreg.OpenKey(reg_hkey, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_WRITE) as key:
                            winreg.DeleteValue(key, program_name)
                        messagebox.showinfo("Success", f"'{program_name}' has been disabled from autostart.")
                    except Exception as e:
                        messagebox.showerror("Error", f"Could not disable program '{program_name}': {str(e)}")

        self.refresh_all_tabs()
    
    def remove_selected(self, tree, reg_hkey):
        """Remove the selected program from autostart"""
        selected_items = tree.selection()
        if not selected_items:
            messagebox.showwarning("No Selection", "Please select a program to remove.")
            return
        
        for item in selected_items:
            program_name = tree.item(item, "values")[0]
            
            if messagebox.askyesno("Confirm Deletion", f"Are you sure you want to remove '{program_name}' from autostart?"):
                try:
                    with winreg.OpenKey(reg_hkey, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_WRITE) as key:
                        winreg.DeleteValue(key, program_name)
                    messagebox.showinfo("Success", f"'{program_name}' has been removed from autostart.")
                except Exception as e:
                    messagebox.showerror("Error", f"Could not remove program '{program_name}': {str(e)}")
        
        self.refresh_all_tabs()
    
    def add_program(self, tree, reg_hkey):
        """Add a new program to autostart"""
        # Create a dialog to select the program
        dialog = tk.Toplevel(self.root)
        dialog.title("Add Autostart Program")
        dialog.geometry("500x200")
        dialog.transient(self.root)
        dialog.grab_set()
        
        ttk.Label(dialog, text="Program Name:").grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)
        name_entry = ttk.Entry(dialog, width=40)
        name_entry.grid(row=0, column=1, padx=10, pady=10)
        
        ttk.Label(dialog, text="Program Path:").grid(row=1, column=0, padx=10, pady=10, sticky=tk.W)
        path_frame = ttk.Frame(dialog)
        path_frame.grid(row=1, column=1, padx=10, pady=10, sticky=(tk.W, tk.E))
        
        path_entry = ttk.Entry(path_frame, width=30)
        path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        def browse_file():
            from tkinter import filedialog
            file_path = filedialog.askopenfilename(
                title="Select Program",
                filetypes=[("Executables", "*.exe"), ("All Files", "*.*")]
            )
            if file_path:
                path_entry.delete(0, tk.END)
                path_entry.insert(0, file_path)
        
        browse_btn = ttk.Button(path_frame, text="Browse...", command=browse_file)
        browse_btn.pack(side=tk.LEFT, padx=(5, 0))
        
        def add_program_action():
            name = name_entry.get().strip()
            path = path_entry.get().strip()
            
            if not name or not path:
                messagebox.showerror("Error", "Please enter both program name and path.")
                return
            
            if not os.path.exists(path):
                messagebox.showerror("Error", "The specified program path does not exist.")
                return
            
            try:
                with winreg.OpenKey(reg_hkey, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_WRITE) as key:
                    winreg.SetValueEx(key, name, 0, winreg.REG_SZ, path)
                messagebox.showinfo("Success", f"'{name}' has been added to autostart.")
                dialog.destroy()
                self.refresh_all_tabs()
            except Exception as e:
                messagebox.showerror("Error", f"Could not add program: {str(e)}")
        
        button_frame = ttk.Frame(dialog)
        button_frame.grid(row=2, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="Add", command=add_program_action).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT)
        
        dialog.columnconfigure(1, weight=1)
        dialog.rowconfigure(0, weight=1)
        path_frame.columnconfigure(0, weight=1)

if __name__ == "__main__":
    root = tk.Tk()
    app = AutostartManager(root)
    root.mainloop()