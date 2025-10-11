#!/usr/bin/env python3
"""
Font availability test for PyQt6
"""

import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFontDatabase

def main():
    app = QApplication(sys.argv)
    
    available_fonts = QFontDatabase.families()
    
    print("=== Font Search Results ===")
    
    # Search for JetBrains fonts
    jetbrains_fonts = [f for f in available_fonts if 'jet' in f.lower()]
    print(f"\nJetBrains fonts found: {len(jetbrains_fonts)}")
    for font in jetbrains_fonts:
        print(f"  - {font}")
    
    # Search for monospace fonts
    mono_fonts = [f for f in available_fonts if 'mono' in f.lower()]
    print(f"\nMonospace fonts found: {len(mono_fonts)}")
    for font in mono_fonts[:10]:  # Show first 10
        print(f"  - {font}")
    
    # Search for Nerd Font
    nerd_fonts = [f for f in available_fonts if 'nerd' in f.lower() or 'nf' in f.lower()]
    print(f"\nNerd fonts found: {len(nerd_fonts)}")
    for font in nerd_fonts:
        print(f"  - {font}")
    
    # Test specific font names
    test_fonts = [
        "JetBrainsMono NFP",
        "JetBrainsMono Nerd Font",
        "JetBrains Mono",
        "JetBrainsMono NF",
        "Consolas"
    ]
    
    print(f"\n=== Testing Specific Fonts ===")
    for font_name in test_fonts:
        available = font_name in available_fonts
        print(f"  {font_name}: {'✓ Available' if available else '✗ Not found'}")
    
    print(f"\nTotal fonts available: {len(available_fonts)}")
    
    app.quit()

if __name__ == "__main__":
    main()