import tkinter as tk
from tkinter import ttk, filedialog
from tkinterdnd2 import DND_FILES, TkinterDnD
from Cryptodome.Cipher import AES
from Cryptodome.Protocol.KDF import PBKDF2
from Cryptodome.Random import get_random_bytes
import os

class FileLockerApp(TkinterDnD.Tk):
    def __init__(self):
        super().__init__()
        self.title("File Locker - Drag & Drop Supported")
        self.geometry("600x480")
        self.configure(bg="#282c34")
        self.set_style()
        self.selected_files = [] 
        self.create_widgets()

    def set_style(self):
        style = ttk.Style(self)
        style.theme_use("clam")

        # --- Colors and Fonts ---
        BG_COLOR = "#282c34"
        FG_COLOR = "#abb2bf"
        ENTRY_BG = "#21252b"
        ENTRY_FG = "#abb2bf"
        BUTTON_BG = "#41abff"
        BUTTON_FG = "black"
        ENCRYPT_BG = "#e06c75"
        ENCRYPT_FG = "white"
        SUCCESS_FG = "#98c379"
        ERROR_FG = "#e06c75"
        FONT_FAMILY = "JetBrainsMono NF"
        FONT_SIZE = 10

        # --- Configure Styles ---
        style.configure("TFrame", background=BG_COLOR)
        style.configure("TLabel", background=BG_COLOR, foreground=FG_COLOR, font=(FONT_FAMILY, FONT_SIZE))
        style.configure("TButton", font=(FONT_FAMILY, FONT_SIZE, "bold"), borderwidth=0)
        style.map("TButton",
                  background=[("active", "#528bff")],
                  foreground=[("active", BUTTON_FG)])

        style.configure("TEntry",
                        fieldbackground=ENTRY_BG,
                        foreground=ENTRY_FG,
                        insertcolor=FG_COLOR,
                        borderwidth=1,
                        relief="flat",
                        font=(FONT_FAMILY, FONT_SIZE))
        style.map("TEntry",
                  bordercolor=[("focus", BUTTON_BG)],
                  relief=[("focus", "solid")])

        # --- Specific Button Styles ---
        style.configure("Browse.TButton", background=BUTTON_BG, foreground=BUTTON_FG)
        style.configure("Decrypt.TButton", background=BUTTON_BG, foreground=BUTTON_FG)
        style.configure("Encrypt.TButton", background=ENCRYPT_BG, foreground=ENCRYPT_FG)
        style.map("Encrypt.TButton", background=[("active", "#e57b84")])

        # --- Result Label Styles ---
        style.configure("Success.TLabel", foreground=SUCCESS_FG)
        style.configure("Error.TLabel", foreground=ERROR_FG)


    def create_widgets(self):
        main_frame = ttk.Frame(self, padding="20")
        main_frame.pack(expand=True, fill="both")

        # --- Header ---
        header_label = ttk.Label(main_frame, text="Drag and drop files below or use Browse", font=("JetBrainsMono NF", 11, "italic"))
        header_label.pack(pady=(0, 10))

        # --- File Selection ---
        file_frame = ttk.Frame(main_frame)
        file_frame.pack(fill="both", expand=True, pady=(0, 10))
        
        header_frame = ttk.Frame(file_frame)
        header_frame.pack(fill="x", pady=(0, 5))
        
        ttk.Label(header_frame, text="Selected Files:").pack(side="left")
        ttk.Button(header_frame, text="Browse Files", command=self.select_files, style="Browse.TButton").pack(side="right")
        
        # Listbox for files with DND support
        self.file_listbox = tk.Listbox(
            file_frame,
            bg="#21252b",
            fg="#abb2bf",
            selectbackground="#41abff",
            selectforeground="black",
            font=("JetBrainsMono NF", 10),
            borderwidth=1,
            relief="flat",
            highlightthickness=1,
            highlightbackground="#333333",
            highlightcolor="#41abff"
        )
        self.file_listbox.pack(fill="both", expand=True)
        
        # Enable Drag and Drop
        self.file_listbox.drop_target_register(DND_FILES)
        self.file_listbox.dnd_bind('<<Drop>>', self.drop_files)

        # --- Password ---
        password_frame = ttk.Frame(main_frame)
        password_frame.pack(fill="x", pady=10)
        password_frame.columnconfigure(1, weight=1)

        ttk.Label(password_frame, text="Password:").grid(row=0, column=0, sticky="w", padx=(0, 10))
        self.password_entry = ttk.Entry(password_frame, show="*")
        self.password_entry.grid(row=0, column=1, sticky="ew")

        # --- Action Buttons ---
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x", pady=20)
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)

        ttk.Button(button_frame, text="Encrypt", command=self.encrypt_files, style="Encrypt.TButton", padding=10).grid(row=0, column=0, sticky="ew", padx=(0, 5))
        ttk.Button(button_frame, text="Decrypt", command=self.decrypt_files, style="Decrypt.TButton", padding=10).grid(row=0, column=1, sticky="ew", padx=(5, 0))

        # --- Result Label ---
        self.result_label = ttk.Label(main_frame, text="", wraplength=550, justify="center")
        self.result_label.pack(pady=(10, 0))

    def drop_files(self, event):
        files = self.tk.splitlist(event.data)
        for f in files:
            if f not in self.selected_files:
                self.selected_files.append(f)
                self.file_listbox.insert(tk.END, f)

    def select_files(self):
        file_paths = filedialog.askopenfilenames()
        if file_paths:
            # Add to existing instead of replace? User might want to accumulate
            # But previous behavior was replace. Let's append actually, better UX for DND context
            for path in file_paths:
                if path not in self.selected_files:
                    self.selected_files.append(path)
                    self.file_listbox.insert(tk.END, path)

    def derive_key(self, password, salt, key_length=32):
        return PBKDF2(password.encode(), salt, dkLen=key_length)

    def encrypt_files(self):
        password = self.password_entry.get()

        if not self.selected_files or not password:
            self.show_result("Please select files and enter a password.", "error")
            return

        processed_files = []
        for file_path in self.selected_files:
            if not file_path: continue
            try:
                with open(file_path, 'rb') as f:
                    plaintext = f.read()

                salt = get_random_bytes(16)
                key = self.derive_key(password, salt)
                cipher = AES.new(key, AES.MODE_EAX)
                ciphertext, tag = cipher.encrypt_and_digest(plaintext)

                encrypted_file_path = file_path + ".enc"
                with open(encrypted_file_path, 'wb') as f:
                    f.write(salt)
                    f.write(tag)
                    f.write(cipher.nonce)
                    f.write(ciphertext)
                processed_files.append(os.path.basename(encrypted_file_path))
            except Exception as e:
                self.show_result(f"Encryption Error: {e}", "error")
                return
        
        self.show_result(f"Successfully encrypted: {', '.join(processed_files)}", "success")


    def decrypt_files(self):
        password = self.password_entry.get()

        if not self.selected_files or not password:
            self.show_result("Please select files and enter a password.", "error")
            return

        processed_files = []
        for file_path in self.selected_files:
            if not file_path: continue
            try:
                with open(file_path, 'rb') as f:
                    salt, tag, nonce, ciphertext = [f.read(x) for x in (16, 16, 16, -1)]

                key = self.derive_key(password, salt)
                cipher = AES.new(key, AES.MODE_EAX, nonce=nonce)
                plaintext = cipher.decrypt_and_verify(ciphertext, tag)

                decrypted_file_path = os.path.splitext(file_path)[0]
                with open(decrypted_file_path, 'wb') as f:
                    f.write(plaintext)
                processed_files.append(os.path.basename(decrypted_file_path))
            except (ValueError, KeyError) as e:
                self.show_result("Decryption failed. Check password or file integrity.", "error")
                return
            except Exception as e:
                self.show_result(f"Decryption Error: {e}", "error")
                return
        
        self.show_result(f"Successfully decrypted: {', '.join(processed_files)}", "success")

    def show_result(self, message, level="info"):
        self.result_label.config(text=message)
        if level == "success":
            self.result_label.config(style="Success.TLabel")
        elif level == "error":
            self.result_label.config(style="Error.TLabel")
        else:
            self.result_label.config(style="TLabel")


if __name__ == "__main__":
    app = FileLockerApp()
    app.mainloop()
