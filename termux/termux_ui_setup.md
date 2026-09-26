# 🚀 Termux UI Customization & Restore Guide

This guide documents the complete setup to restore the customized **Catppuccin Mocha** Termux UI with custom prompt, fastfetch banner, Nerd Font, and optimized shell aliases.

---

## 🛠️ Step 1: Install Required Packages

Run this command in Termux:

```bash
pkg update && pkg upgrade -y
pkg install -y bash eza fastfetch zoxide fzf oh-my-posh git curl
```

---

## 🎨 Step 2: Install Color Theme (`~/.termux/colors.properties`)

Create or update `~/.termux/colors.properties` with the Catppuccin Mocha palette:

```bash
mkdir -p ~/.termux

cat << 'EOF' > ~/.termux/colors.properties
# Catppuccin Mocha Color Theme for Termux
background=#1e1e2e
foreground=#cdd6f4
cursor=#f5e0dc
cursor_background=#f5e0dc

# Black
color0=#45475a
color8=#585b70

# Red
color1=#f38ba8
color9=#f38ba8

# Green
color2=#a6e3a1
color10=#a6e3a1

# Yellow
color3=#f9e2af
color11=#f9e2af

# Blue
color4=#89b4fa
color12=#89b4fa

# Magenta
color5=#f5c2e7
color13=#f5c2e7

# Cyan
color6=#94e2d5
color14=#94e2d5

# White
color7=#bac2de
color15=#a6adc8
EOF
```

---

## 🔤 Step 3: Install Font (`~/.termux/font.ttf`)

Download JetBrainsMono Nerd Font v3.2.1:

```bash
curl -fLo ~/.termux/font.ttf "https://raw.githubusercontent.com/ryanoasis/nerd-fonts/v3.2.1/patched-fonts/JetBrainsMono/NoLigatures/Regular/JetBrainsMonoNLNerdFont-Regular.ttf"
chmod 644 ~/.termux/font.ttf
termux-reload-settings
```

---

## ⚙️ Step 4: Configure Termux Preferences (`~/.termux/termux.properties`)

```bash
cat << 'EOF' > ~/.termux/termux.properties
extra-keys = [ \
 [{macro: "CTRL t", display: "New"}, \
  {macro: "CTRL 1", display: "<"}, \
  {macro: "CTRL 2", display: ">"}, \
  {macro: "CTRL c", display: "STOP"}, \
  {macro: "CTRL d", display: "EXIT"}, \
  {macro: "c l e a r ENTER", display: "CLS"}, \
  {macro: "CTRL k", display: "|->"}, \
  {macro: "CTRL u", display: "<-|"}], \
 ['ESC','|','/','HOME','UP','END','PGUP','DEL'], \
 ['TAB','CTRL','ALT','LEFT','DOWN','RIGHT','PGDN','BKSP'] \
]

terminal-cursor-style=bar
bell-character=ignore
allow-external-apps=true
EOF

termux-reload-settings
```

---

## 📊 Step 5: Configure Minimal Fastfetch Header (`~/.config/fastfetch/config.jsonc`)

```bash
mkdir -p ~/.config/fastfetch

cat << 'EOF' > ~/.config/fastfetch/config.jsonc
{
  "$schema": "https://github.com/fastfetch-cli/fastfetch/raw/dev/doc/json_schema.json",
  "logo": {
    "type": "none"
  },
  "display": {
    "separator": " ➜ ",
    "color": {
      "keys": "38;2;137;180;250",
      "title": "38;2;166;227;161"
    }
  },
  "modules": [
    {
      "type": "title",
      "format": "  Welcome back, {1}! 🚀"
    },
    {
      "type": "custom",
      "format": "  ───────────────────────────────────────"
    },
    {
      "type": "os",
      "key": "  💻 OS       ",
      "keyColor": "38;2;137;180;250"
    },
    {
      "type": "host",
      "key": "  📱 Device   ",
      "keyColor": "38;2;137;220;235"
    },
    {
      "type": "uptime",
      "key": "  🕒 Uptime   ",
      "keyColor": "38;2;249;226;175"
    },
    {
      "type": "memory",
      "key": "  🧠 RAM      ",
      "keyColor": "38;2;203;166;247"
    },
    {
      "type": "battery",
      "key": "  🔋 Battery  ",
      "keyColor": "38;2;166;227;161"
    },
    {
      "type": "localip",
      "key": "  🌐 Network  ",
      "keyColor": "38;2;148;226;213"
    },
    {
      "type": "custom",
      "format": "  ───────────────────────────────────────"
    },
    "colors"
  ]
}
EOF
```

---

## ⚡ Step 6: Configure Oh My Posh Prompt (`~/.config/ohmyposh/catppuccin.omp.json`)

```bash
mkdir -p ~/.config/ohmyposh

cat << 'EOF' > ~/.config/ohmyposh/catppuccin.omp.json
{
  "$schema": "https://raw.githubusercontent.com/JanDeDobbeleer/oh-my-posh/main/themes/schema.json",
  "version": 2,
  "final_space": true,
  "console_title_template": "{{ .Shell }} | {{ .Folder }}",
  "blocks": [
    {
      "type": "prompt",
      "alignment": "left",
      "newline": true,
      "segments": [
        {
          "type": "text",
          "style": "plain",
          "foreground": "#89b4fa",
          "template": "╭─"
        },
        {
          "type": "os",
          "style": "plain",
          "foreground": "#89b4fa",
          "template": " 🤖 termux"
        },
        {
          "type": "text",
          "style": "plain",
          "foreground": "#585b70",
          "template": " •"
        },
        {
          "type": "path",
          "style": "plain",
          "foreground": "#89dceb",
          "properties": {
            "style": "folder"
          },
          "template": " 📁 {{ .Path }}"
        },
        {
          "type": "git",
          "style": "plain",
          "foreground": "#a6e3a1",
          "foreground_templates": [
            "{{ if or (.Working.Changed) (.Staging.Changed) }}#f9e2af{{ end }}",
            "{{ if .Ahead }}#cba6f7{{ end }}",
            "{{ if .Behind }}#f38ba8{{ end }}"
          ],
          "properties": {
            "branch_icon": "🌿 ",
            "fetch_status": true
          },
          "template": " • 🌿 {{ .HEAD }}{{ if .Working.Changed }} *{{ end }}"
        },
        {
          "type": "status",
          "style": "plain",
          "foreground": "#a6e3a1",
          "foreground_templates": [
            "{{ if gt .Code 0 }}#f38ba8{{ end }}"
          ],
          "properties": {
            "always_enabled": true
          },
          "template": " • {{ if gt .Code 0 }}✘ {{ .Code }}{{ else }}✔{{ end }}"
        }
      ]
    },
    {
      "type": "prompt",
      "alignment": "left",
      "newline": true,
      "segments": [
        {
          "type": "text",
          "style": "plain",
          "foreground": "#89b4fa",
          "template": "╰─❯"
        }
      ]
    }
  ],
  "transient_prompt": {
    "foreground": "#89b4fa",
    "background": "transparent",
    "template": "❯ "
  }
}
EOF
```

---

## 🧹 Step 7: Remove Default Termux Welcome Banner & Logs

```bash
touch ~/.hushlogin
echo "" > $PREFIX/etc/motd
echo "" > $PREFIX/etc/motd-playstore
if [ -f "$PREFIX/etc/motd.sh" ]; then
    echo "#!/bin/sh" > $PREFIX/etc/motd.sh
fi
```

---

## 🐚 Step 8: Update Shell Config (`~/.bashrc`)

Add the following to the end of `~/.bashrc`:

```bash
# Aliases
alias cls='clear'
alias ls='eza --group-directories-first'
alias la='eza -a --group-directories-first'
alias ll='eza -l --header --group-directories-first'
alias lla='eza -la --header --group-directories-first'
alias tree='eza --tree'
alias grep='grep --color=auto'
alias diff='diff --color=auto'
alias rb='termux-reload-settings'
alias update='pkg update && pkg upgrade -y'

# Fastfetch on interactive startup
if [[ $- == *i* ]]; then
    fastfetch
fi

# Shell Prompts & Navigation
eval "$(oh-my-posh init bash --config ~/.config/ohmyposh/catppuccin.omp.json)"
eval "$(zoxide init bash --cmd cd)"
```

---

## 🔄 Instant Full Restore Command

If you ever reset Termux, you can restore everything at once by running this single command:

```bash
curl -sSL https://raw.githubusercontent.com/nahid6970/ms1/main/termux/termux_ui_setup.md | bash
```

Or clone your repo and run:
```bash
source ~/.bashrc
```
