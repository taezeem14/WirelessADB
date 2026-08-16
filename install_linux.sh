#!/usr/bin/env bash
# ==============================================================================
# ⚡ WirelessADB - Linux One-Click Installer & Setup Suite
# ==============================================================================

set -e

# Color definitions
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BOLD='\033[1m'
NC='\033[0m'

echo -e "${CYAN}"
echo "  =============================================================="
echo "    ⚡ WIRELESS ADB - NEXT-GEN SUITE INSTALLER (LINUX) 🚀"
echo "  =============================================================="
echo -e "${NC}"

# Check Python 3
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}[FATAL] Python 3 is not installed.${NC}"
    echo "Install via your package manager:"
    echo "  Ubuntu/Debian : sudo apt install -y python3 python3-pip"
    echo "  Fedora/RHEL   : sudo dnf install -y python3"
    echo "  Arch Linux    : sudo pacman -S --noconfirm python"
    exit 1
fi
echo -e "${GREEN}[OK]${NC} Python 3 detected: $(python3 --version)"

# Check ADB
if ! command -v adb &> /dev/null; then
    echo -e "${YELLOW}[WARN] ADB not detected in PATH!${NC}"
    read -p "Attempt automatic ADB package installation? [Y/n]: " -r confirm
    confirm=${confirm:-Y}
    if [[ $confirm =~ ^[Yy]$ ]]; then
        if command -v apt &> /dev/null; then
            sudo apt update && sudo apt install -y android-tools-adb
        elif command -v pacman &> /dev/null; then
            sudo pacman -S --noconfirm android-tools
        elif command -v dnf &> /dev/null; then
            sudo dnf install -y android-tools
        elif command -v zypper &> /dev/null; then
            sudo zypper install -y android-tools
        else
            echo -e "${RED}Could not detect supported package manager. Please install adb manually.${NC}"
        fi
    fi
fi

if command -v adb &> /dev/null; then
    echo -e "${GREEN}[OK]${NC} ADB detected: $(adb version | head -n1)"
fi

# Target Directory
if [ "$EUID" -eq 0 ]; then
    INSTALL_DIR="/usr/local/bin"
    echo -e "${CYAN}[SYSTEM] Installing system-wide to $INSTALL_DIR...${NC}"
else
    INSTALL_DIR="$HOME/.local/bin"
    echo -e "${CYAN}[USER] Installing for current user to $INSTALL_DIR...${NC}"
    mkdir -p "$INSTALL_DIR"
fi

# Copy binary
cp wireless_adb.py "$INSTALL_DIR/wireless-adb"
chmod +x "$INSTALL_DIR/wireless-adb"

# Create shortcut alias wadb
ln -sf "$INSTALL_DIR/wireless-adb" "$INSTALL_DIR/wadb"

echo -e "${GREEN}[OK]${NC} Installed binary: ${BOLD}$INSTALL_DIR/wireless-adb${NC}"
echo -e "${GREEN}[OK]${NC} Created alias   : ${BOLD}$INSTALL_DIR/wadb${NC}"

# Check PATH
if [[ ":$PATH:" != *":$INSTALL_DIR:"* ]]; then
    echo -e "${YELLOW}[NOTE] $INSTALL_DIR is not in your current PATH.${NC}"
    echo "Add the following line to your ~/.bashrc or ~/.zshrc:"
    echo -e "  ${CYAN}export PATH=\"\$HOME/.local/bin:\$PATH\"${NC}"
fi

echo ""
echo -e "${GREEN}==============================================================${NC}"
echo -e "${GREEN}  🎉 INSTALLATION COMPLETE! SYSTEM IS ONLINE. 🚀🔥${NC}"
echo -e "${GREEN}==============================================================${NC}"
echo ""
echo "Run 'wireless-adb' or 'wadb' in your terminal to begin."
