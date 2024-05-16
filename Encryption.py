import tkinter as tk
from tkinter import filedialog
from Cryptodome.Cipher import AES 
from Cryptodome.Util.Padding import pad, unpad
from Cryptodome.Protocol.KDF import PBKDF2
from Cryptodome.Random import get_random_bytes
import os

# Initialize the Tkinter window
root = tk.Tk()
root.title("File Encryptor/Decryptor")

# Function to handle file selection
def select_files():
    file_paths = filedialog.askopenfilenames()
    file_entry.delete(0, tk.END)
    file_entry.insert(0, ";".join(file_paths))

# Function to derive key from password
def derive_key(password, salt, key_length=32):
    kdf = PBKDF2(password.encode(), salt, dkLen=key_length)
    return kdf[:key_length]

# Function to perform encryption
def encrypt_files():
    file_paths = file_entry.get().split(";")
    password = password_entry.get()

    for file_path in file_paths:
        try:
            with open(file_path, 'rb') as file:
                plaintext = file.read()
                salt = get_random_bytes(16)
                key = derive_key(password, salt)
                cipher = AES.new(key, AES.MODE_EAX)
                ciphertext, tag = cipher.encrypt_and_digest(plaintext)

            encrypted_file_path = file_path + ".enc"
            with open(encrypted_file_path, 'wb') as enc_file:
                enc_file.write(salt)
                enc_file.write(tag)
                enc_file.write(cipher.nonce)
                enc_file.write(ciphertext)

            result_label.config(text=f"File encrypted successfully: {encrypted_file_path}")
        except Exception as e:
            result_label.config(text=f"Error: {str(e)}")

# Function to perform decryption
def decrypt_files():
    file_paths = file_entry.get().split(";")
    password = password_entry.get()

    for file_path in file_paths:
        try:
            with open(file_path, 'rb') as enc_file:
                salt = enc_file.read(16)
                tag = enc_file.read(16)
                nonce = enc_file.read(16)
                ciphertext = enc_file.read()

                key = derive_key(password, salt)
                cipher = AES.new(key, AES.MODE_EAX, nonce=nonce)
                plaintext = cipher.decrypt_and_verify(ciphertext, tag)

            decrypted_file_path = os.path.splitext(file_path)[0]
            with open(decrypted_file_path, 'wb') as dec_file:
                dec_file.write(plaintext)

            result_label.config(text=f"File decrypted successfully: {decrypted_file_path}")
        except Exception as e:
            result_label.config(text=f"Error: {str(e)}")

# Create GUI elements
file_label = tk.Label(root, text="Select files:")
file_entry = tk.Entry(root, width=50)
file_button = tk.Button(root, text="Browse", command=select_files)

password_label = tk.Label(root, text="Enter password:")
password_entry = tk.Entry(root, show="*")

encrypt_button = tk.Button(root, text="Encrypt", command=encrypt_files)
decrypt_button = tk.Button(root, text="Decrypt", command=decrypt_files)

result_label = tk.Label(root, text="")

# Arrange GUI elements
file_label.grid(row=0, column=0, padx=10, pady=5)
file_entry.grid(row=0, column=1, padx=10, pady=5)
file_button.grid(row=0, column=2, padx=10, pady=5)

password_label.grid(row=1, column=0, padx=10, pady=5)
password_entry.grid(row=1, column=1, padx=10, pady=5)

encrypt_button.grid(row=2, column=0, padx=10, pady=5)
decrypt_button.grid(row=2, column=1, padx=10, pady=5)

result_label.grid(row=3, columnspan=3, padx=10, pady=5)

root.mainloop()
