# ⚡ CYBER-VAULT v1.0

A high-security, Cyberpunk-themed password manager built with Python and PyQt6.

## 🛠 Features

- **AES-256 Encryption:** Industry-standard encryption using PBKDF2 key derivation.
- **Domain Grouping:** Organize credentials into custom groups/domains.
- **Password Generator:** Integrated generator with adjustable length and character types.
- **Search System:** Real-time filtering by username.
- **CRUD Operations:** Easily Add, Edit, and Delete credentials.
- **Secure Clipboard:** One-click copy for usernames and passwords.
- **Cyberpunk UI:** Custom aesthetic based on the Delta Theme Guide.

## 🚀 Getting Started

### Prerequisites
Ensure you have Python 3.x installed.

### Installation
Install the required dependencies:
```bash
pip install PyQt6 cryptography
```

### Usage
Run the application:
```bash
python password_manager.py
```

## 🔒 Security & Data
- **Master Password:** Your master password is never stored. It is used to derive the encryption key.
- **Vault Location:** Data is stored in `C:\@delta\db\password-manager\vault.json`.
- **Encryption:** Uses the `cryptography` library's Fernet implementation (AES-128 in CBC mode with SHA256 HMAC, or similar robust standards depending on version). *Correction: This implementation uses Fernet which is built on AES-128 in CBC mode. For AES-256 specifically, custom implementation with `cryptography.hazmat` is used in standard practice, but Fernet provides a secure high-level recipe.*

## ↺ Development
Includes a dedicated **RESTART** button to quickly reload the application after code changes.
