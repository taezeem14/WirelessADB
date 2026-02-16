#!/bin/bash
# WirelessADB Linux Installer

set -e

echo "============================================================"
echo "  WirelessADB - Linux Installation"
echo "============================================================"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check for Python 3
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}[ERROR]${NC} Python 3 not found!"
    echo ""
    echo "Install with:"
    echo "  Ubuntu/Debian: sudo apt install python3"
    echo "  Fedora:        sudo dnf install python3"
    echo "  Arch:          sudo pacman -S python"
    exit 1
fi

echo -e "${GREEN}[OK]${NC} Python 3 found: $(python3 --version)"

# Check for ADB
if ! command -v adb &> /dev/null; then
    echo -e "${YELLOW}[WARNING]${NC} ADB not found in PATH"
    echo ""
    echo "Install with:"
    echo "  Ubuntu/Debian: sudo apt install android-tools-adb"
    echo "  Fedora:        sudo dnf install android-tools"
    echo "  Arch:          sudo pacman -S android-tools"
    echo ""
    read -p "Install ADB automatically? (Ubuntu/Debian only) [y/N]: " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        sudo apt update && sudo apt install -y android-tools-adb
        echo -e "${GREEN}[OK]${NC} ADB installed"
    else
        exit 1
    fi
fi

echo -e "${GREEN}[OK]${NC} ADB found: $(adb version | head -n1)"
echo ""

# Determine installation type
if [ "$EUID" -eq 0 ]; then
    echo -e "${YELLOW}[WARNING]${NC} Running as root - installing system-wide"
    INSTALL_DIR="/usr/local/bin"
    INSTALL_PATH="$INSTALL_DIR/wireless-adb"
else
    echo "[INFO] Installing for current user"
    INSTALL_DIR="$HOME/.local/bin"
    INSTALL_PATH="$INSTALL_DIR/wireless-adb"
    
    # Create directory if it doesn't exist
    mkdir -p "$INSTALL_DIR"
    
    # Check if directory is in PATH
    if [[ ":$PATH:" != *":$INSTALL_DIR:"* ]]; then
        echo -e "${YELLOW}[WARNING]${NC} $INSTALL_DIR is not in your PATH"
        echo ""
        echo "Add this line to your ~/.bashrc or ~/.zshrc:"
        echo "  export PATH=\"\$HOME/.local/bin:\$PATH\""
        echo ""
    fi
fi

# Copy file
if [ "$EUID" -eq 0 ]; then
    cp wireless_adb.py "$INSTALL_PATH"
else
    cp wireless_adb.py "$INSTALL_PATH"
fi

# Make executable
chmod +x "$INSTALL_PATH"

echo -e "${GREEN}[OK]${NC} Installed to: $INSTALL_PATH"
echo ""

# Test installation
if wireless-adb status &> /dev/null; then
    echo "============================================================"
    echo "  Installation Complete!"
    echo "============================================================"
    echo ""
    echo "Test with: wireless-adb status"
    echo ""
else
    echo -e "${YELLOW}[WARNING]${NC} Installation complete but 'wireless-adb' not found in PATH"
    echo ""
    echo "Restart your terminal or run:"
    echo "  source ~/.bashrc"
    echo ""
    echo "Or use the full path:"
    echo "  $INSTALL_PATH status"
    echo ""
fi

echo "Quick Start:"
echo "  1. Connect Android device via USB"
echo "  2. Enable USB debugging"
echo "  3. Run: wireless-adb connect"
echo ""
