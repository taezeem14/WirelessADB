#!/usr/bin/env bash
# ==============================================================================
# ⚡ WirelessADB - macOS One-Click Installer & Homebrew Integrator
# ==============================================================================

set -e

GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BOLD='\033[1m'
NC='\033[0m'

echo -e "${CYAN}"
echo "  =============================================================="
echo "    ⚡ WIRELESS ADB - MACOS INSTALLATION SUITE 🍏🚀"
echo "  =============================================================="
echo -e "${NC}"

# Check Python 3
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}[FATAL] Python 3 not found.${NC}"
    echo "Install via Homebrew: brew install python"
    exit 1
fi
echo -e "${GREEN}[OK]${NC} Python 3 detected: $(python3 --version)"

# Check ADB
if ! command -v adb &> /dev/null; then
    echo -e "${YELLOW}[WARN] ADB not detected in PATH!${NC}"
    if command -v brew &> /dev/null; then
        echo "Installing Android Platform Tools via Homebrew..."
        brew install android-platform-tools
    else
        echo "Please install Homebrew (https://brew.sh) or Android Platform Tools manually."
    fi
fi

if command -v adb &> /dev/null; then
    echo -e "${GREEN}[OK]${NC} ADB detected: $(adb version | head -n1)"
fi

INSTALL_DIR="/usr/local/bin"
if [ ! -w "$INSTALL_DIR" ]; then
    INSTALL_DIR="$HOME/.local/bin"
    mkdir -p "$INSTALL_DIR"
fi

TARGET_BIN="$INSTALL_DIR/wireless-adb"
if [ -f "wireless_adb.py" ]; then
    cp wireless_adb.py "$TARGET_BIN"
    echo -e "${GREEN}[OK]${NC} Copied local wireless_adb.py to $TARGET_BIN"
else
    echo -e "${CYAN}[*] Downloading latest wireless_adb.py from GitHub...${NC}"
    curl -fsSL https://raw.githubusercontent.com/taezeem14/WirelessADB/main/wireless_adb.py -o "$TARGET_BIN"
    echo -e "${GREEN}[OK]${NC} Downloaded payload to $TARGET_BIN"
fi

chmod +x "$TARGET_BIN"
ln -sf "$TARGET_BIN" "$INSTALL_DIR/wadb"

echo -e "${GREEN}[OK]${NC} Installed binary: ${BOLD}$TARGET_BIN${NC}"
echo -e "${GREEN}[OK]${NC} Created alias   : ${BOLD}$INSTALL_DIR/wadb${NC}"

if [[ ":$PATH:" != *":$INSTALL_DIR:"* ]]; then
    echo -e "${YELLOW}[NOTE] Add $INSTALL_DIR to your ~/.zshrc or ~/.bash_profile:${NC}"
    echo -e "  ${CYAN}export PATH=\"$INSTALL_DIR:\$PATH\"${NC}"
fi

echo ""
echo -e "${GREEN}🎉 Done! Launch with 'wireless-adb' or 'wadb'.${NC}"
