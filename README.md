# WirelessADB - Secure Wireless ADB Connection Manager

A production-grade command-line tool for managing wireless ADB connections with enhanced security features. Built for developers who want safer, more convenient wireless debugging.

## 🚀 Why WirelessADB?

Traditional wireless ADB (`adb tcpip 5555`) has several security issues:
- **Fixed port (5555)** makes devices easy targets for port scanners
- **No automatic cleanup** - connections persist after you're done
- **Manual IP/port management** is tedious and error-prone
- **No security warnings** about network risks

**WirelessADB solves these problems:**
- ✅ Random high ports (30000-50000) for each session
- ✅ Automatic connection management and cleanup
- ✅ Network security warnings and subnet detection
- ✅ Connection profiles and easy reconnection
- ✅ Multi-device support with selection menu
- ✅ Cross-platform (Windows & Linux)

---

## 🔒 Security Improvements

### Random Port Selection
Instead of using the well-known port 5555, WirelessADB generates a random port in the range 30000-50000 for each connection:

```
Traditional:  adb tcpip 5555  (predictable, scannable)
WirelessADB:  Random port like 37482, 42193, 31847, etc.
```

**Why this matters:**
- Attackers commonly scan for port 5555 on networks
- Random ports significantly reduce exposure to automated attacks
- Even if someone scans your IP, they won't know which port to target
- Each session uses a different port

### Network Security Features
- **Subnet checking**: Warns if device and host are on different networks
- **Security warnings**: Clear notices about wireless ADB risks
- **Auto-disconnect**: Cleans up connections when you exit
- **USB reset**: Optionally switches device back to USB-only mode
- **Connection logging**: Tracks when/where devices were connected

### Important Security Disclaimer
⚠️ **Wireless ADB is inherently insecure** - anyone on your network can potentially access your device. Random ports reduce risk but don't eliminate it. Best practices:

- ✅ Use only on trusted private networks (home, office VPN)
- ✅ Disconnect when done (`wireless-adb disconnect`)
- ✅ Never use on public Wi-Fi (coffee shops, airports, etc.)
- ✅ Consider using a USB cable for sensitive operations
- ✅ Monitor connected devices regularly (`wireless-adb status`)

---

## 📋 Requirements

- **Python 3.7+** (cross-platform)
- **Android Debug Bridge (ADB)** installed and in PATH
- **Android device** running Android 8.1+ with USB debugging enabled
- **USB cable** (for initial connection)
- **Wi-Fi connection** on both device and host

---

## 🛠️ Installation

### Windows

#### Option 1: Direct Download (Easiest)
1. Download `wireless_adb.py` from this repository
2. Install Python from [python.org](https://www.python.org/downloads/) (ensure "Add to PATH" is checked)
3. Install ADB:
   - Download [Platform Tools](https://developer.android.com/studio/releases/platform-tools)
   - Extract to `C:\platform-tools\`
   - Add to PATH: `setx PATH "%PATH%;C:\platform-tools"`

4. Make it easily accessible:
```powershell
# Create a batch wrapper (run as Administrator)
echo @python "%USERPROFILE%\wireless_adb.py" %* > C:\Windows\wireless-adb.bat
```

5. Test installation:
```powershell
wireless-adb status
```

#### Option 2: Git Clone
```powershell
git clone https://github.com/yourusername/wireless-adb.git
cd wireless-adb
python wireless_adb.py status
```

### Linux

#### Option 1: System-wide Install (Recommended)
```bash
# Install dependencies
sudo apt update
sudo apt install android-tools-adb python3 python3-pip

# Download the tool
wget https://raw.githubusercontent.com/yourusername/wireless-adb/main/wireless_adb.py
chmod +x wireless_adb.py

# Install system-wide
sudo mv wireless_adb.py /usr/local/bin/wireless-adb
sudo chmod +x /usr/local/bin/wireless-adb

# Test
wireless-adb status
```

#### Option 2: User Install
```bash
# Install to ~/.local/bin
mkdir -p ~/.local/bin
cp wireless_adb.py ~/.local/bin/wireless-adb
chmod +x ~/.local/bin/wireless-adb

# Add to PATH (add to ~/.bashrc or ~/.zshrc)
export PATH="$HOME/.local/bin:$PATH"

# Reload shell
source ~/.bashrc

# Test
wireless-adb status
```

#### Option 3: Git Clone
```bash
git clone https://github.com/yourusername/wireless-adb.git
cd wireless-adb
chmod +x wireless_adb.py
./wireless_adb.py status
```

### Verify Installation

```bash
# Check Python version
python3 --version  # Should be 3.7+

# Check ADB
adb version        # Should show ADB version

# Check WirelessADB
wireless-adb status
```

---

## 🎯 Usage

### Basic Workflow

```bash
# 1. Connect device via USB and enable USB debugging

# 2. Connect wirelessly (generates random port automatically)
wireless-adb connect

# 3. Unplug USB cable and continue working

# 4. When done, clean up
wireless-adb disconnect
```

### All Commands

#### `connect` - Initial Wireless Connection
Detects USB device, generates random port, and establishes wireless connection.

```bash
wireless-adb connect

# Verbose mode (shows all ADB commands)
wireless-adb connect -v

# Quiet mode (minimal output)
wireless-adb connect -q
```

**Example Output:**
```
============================================================
  WirelessADB - Secure Wireless ADB Connection Manager
============================================================

[1/5] Detecting USB-connected Android devices...
[OK] Selected: Pixel 6 Pro (1A2B3C4D5E6F)

[2/5] Retrieving device Wi-Fi IP address...
[OK] Device IP: 192.168.1.145

[3/5] Generating secure random port...
[OK] Using port: 37482

[4/5] Switching device to TCP/IP mode...
[OK] TCP/IP mode enabled on port 37482

[5/5] Connecting to device wirelessly...
[OK] Connected wirelessly to 192.168.1.145:37482

[SECURITY] Wireless ADB is INSECURE on untrusted networks!
           • Anyone on the network can access your device
           • Use only on trusted private networks
           • Random ports reduce (but don't eliminate) risk

============================================================
  ✓ CONNECTED SUCCESSFULLY
============================================================
  Device: Pixel 6 Pro
  Target: 192.168.1.145:37482

  You can now disconnect the USB cable.
  Run 'wireless-adb disconnect' to cleanup when done.
```

#### `disconnect` - Clean Disconnect
Disconnects all wireless connections and optionally resets devices to USB mode.

```bash
wireless-adb disconnect

# Disconnect but don't reset to USB mode
wireless-adb disconnect --no-reset
```

#### `status` - Connection Status
Shows all connected devices (USB and wireless) and saved profiles.

```bash
wireless-adb status
```

**Example Output:**
```
============================================================
  WirelessADB - Connection Status
============================================================

USB Devices (1):
  • 1A2B3C4D5E6F device product:raven model:Pixel_6_Pro device:raven

Wireless Devices (1):
  • 192.168.1.145:37482 device product:raven model:Pixel_6_Pro device:raven

Saved Profiles (2):
  • Pixel 6 Pro (1A2B3C4D5E6F)
    Last: 192.168.1.145:37482 @ 2026-02-16 14:32:15
  • Galaxy S21 (9Z8Y7X6W5V4U)
    Last: 192.168.1.158:42193 @ 2026-02-15 18:45:22
```

#### `reconnect` - Quick Reconnect
Reconnects to the last successfully connected device.

```bash
wireless-adb reconnect
```

Useful when:
- Your device disconnected temporarily
- You restarted your computer
- Network connection was interrupted

### Advanced Usage

#### Multiple Devices
If multiple USB devices are connected, you'll get a selection menu:

```bash
wireless-adb connect

[FOUND] 2 devices connected:
        [1] Pixel 6 Pro (1A2B3C4D5E6F)
        [2] Galaxy S21 (9Z8Y7X6W5V4U)
Select device [1-2]: 1
```

#### Verbose Debugging
See all ADB commands and output:

```bash
wireless-adb connect -v

[DEBUG] Running: adb version
[DEBUG] Output: Android Debug Bridge version 1.0.41
[DEBUG] Running: adb devices
[DEBUG] Running: adb -s 1A2B3C4D5E6F shell ip addr show wlan0
...
```

#### Windows CMD (No Color)
If colors don't display properly:

```bash
wireless-adb connect --no-color
```

---

## 🔧 Configuration

### Config File Location

WirelessADB stores connection profiles in:
- **Windows**: `C:\Users\YourName\.wireless_adb\profiles.json`
- **Linux**: `~/.wireless_adb/profiles.json`

### Profile Format

```json
{
  "1A2B3C4D5E6F": {
    "ip": "192.168.1.145",
    "port": 37482,
    "last_connected": 1708099935.123456,
    "device_name": "Pixel 6 Pro"
  }
}
```

You can manually edit this file if needed, but it's automatically managed by the tool.

---

## 🐛 Troubleshooting

### "ADB not found in PATH"

**Windows:**
```powershell
# Download Platform Tools from Android website
# Extract to C:\platform-tools\
# Add to PATH:
setx PATH "%PATH%;C:\platform-tools"
# Restart terminal
adb version
```

**Linux:**
```bash
sudo apt install android-tools-adb
# or
sudo pacman -S android-tools
```

### "No USB devices found"

1. **Enable USB Debugging:**
   - Settings → About Phone → Tap "Build Number" 7 times
   - Settings → Developer Options → Enable "USB Debugging"

2. **Authorize Computer:**
   - Unlock device
   - Allow USB debugging popup

3. **Check USB Connection:**
   ```bash
   adb devices
   ```
   Should show your device, not "unauthorized"

4. **Try Different Cable/Port:**
   - Some cables are charge-only
   - Try different USB ports

### "Could not get Wi-Fi IP"

1. **Ensure Wi-Fi is Connected:**
   - Device must be on Wi-Fi (not just mobile data)
   - Pull down notification shade → verify Wi-Fi icon

2. **Check Wi-Fi Interface:**
   Some devices use different interface names:
   ```bash
   adb shell ip addr
   ```
   Look for your IP address

### "Wireless connection failed"

1. **Same Network:**
   - Device and computer must be on same Wi-Fi network
   - Corporate networks may block device-to-device communication

2. **Firewall:**
   - **Windows:** Allow Python through Windows Defender Firewall
   - **Linux:** Check `iptables` or `ufw` rules
   ```bash
   sudo ufw allow from 192.168.1.0/24
   ```

3. **Router Settings:**
   - Disable "AP Isolation" / "Client Isolation"
   - Enable local network communication

4. **Retry Connection:**
   ```bash
   wireless-adb disconnect
   wireless-adb connect -v
   ```

### "Command timed out"

- Increase timeout in code (line 70, `timeout=30`)
- Check network speed/stability
- Device may be overloaded

### Random Port Conflicts

Extremely rare (1 in 20,000 chance), but if port is in use:
```bash
# Just reconnect - new random port will be generated
wireless-adb connect
```

### Multiple Devices Not Showing

```bash
# List all devices manually
adb devices -l

# Kill and restart ADB server
adb kill-server
adb start-server
```

---

## 🏗️ Architecture

### Code Structure

```
wireless_adb.py
├── Colors              # Terminal color codes
├── LogLevel           # Verbosity levels
├── DeviceProfile      # Device connection data
├── ADBWrapper         # Low-level ADB command wrapper
│   ├── _verify_adb()
│   ├── run_command()
│   ├── get_devices()
│   ├── get_device_ip()
│   ├── enable_tcpip()
│   ├── connect_wireless()
│   ├── disconnect()
│   └── usb_mode()
├── WirelessADBManager # High-level connection manager
│   ├── connect()
│   ├── disconnect()
│   ├── status()
│   ├── reconnect()
│   ├── _generate_random_port()
│   ├── _check_network_security()
│   ├── _save_profile()
│   └── _load_profile()
└── main()             # CLI entry point
```

### Design Principles

1. **Separation of Concerns:**
   - `ADBWrapper`: Raw ADB command execution
   - `WirelessADBManager`: Business logic and user interaction
   - `main()`: CLI argument parsing

2. **Error Handling:**
   - Try/catch blocks around all ADB operations
   - Graceful degradation (network check is best-effort)
   - Clear error messages with actionable solutions

3. **Cross-Platform:**
   - Pure Python 3.7+ (no platform-specific dependencies)
   - Color disable for Windows CMD
   - IP detection works on both Windows and Linux

4. **Testability:**
   - Modular functions
   - Dependency injection (ADBWrapper passed to Manager)
   - Verbose mode for debugging

---

## 🔐 Security Deep Dive

### Why Random Ports Are Better

**Traditional Approach (Port 5555):**
```python
# Attacker's script
for ip in network_scan("192.168.1.0/24"):
    if port_open(ip, 5555):
        connect_adb(ip, 5555)  # Easy target!
```

**WirelessADB Approach (Random Ports):**
```python
# Attacker must scan ALL high ports (30000-50000)
for ip in network_scan("192.168.1.0/24"):
    for port in range(30000, 50000):  # 20,000 ports!
        if port_open(ip, port):
            connect_adb(ip, port)  # Takes hours, device may disconnect
```

**Attack Surface Reduction:**
- Port 5555: 1 predictable target
- Random port: 1 in 20,000 chance per attempt
- Even with port scanning tools, takes significant time
- User likely disconnects before scan completes

### Threat Model

**Protects Against:**
- ✅ Automated port 5555 scanners
- ✅ Opportunistic attacks on public networks
- ✅ Accidental persistent connections

**Does NOT Protect Against:**
- ❌ Determined attacker on your network (they can scan all ports)
- ❌ ARP spoofing / MITM attacks
- ❌ Compromised router
- ❌ Malicious apps on the device itself

### Best Practices

```bash
# ✅ Good: Trusted home network
wireless-adb connect
# Work on project
wireless-adb disconnect

# ❌ Bad: Coffee shop Wi-Fi
wireless-adb connect  # DON'T DO THIS

# ✅ Good: Use VPN for untrusted networks
sudo openvpn ~/my-vpn.ovpn
wireless-adb connect  # Now both on VPN
```

### Additional Hardening (Advanced)

For extra security, you can:

1. **Firewall Rules:**
   ```bash
   # Linux: Only allow ADB from specific IP
   sudo ufw allow from 192.168.1.145 to any port 30000:50000
   
   # Windows: Create inbound rule for Python.exe
   ```

2. **Port Knocking:**
   Modify code to require a "knock sequence" before connecting

3. **Certificate-Based Auth:**
   ADB supports RSA key authentication (requires device modification)

4. **Network Isolation:**
   Use a dedicated IoT/dev network for Android devices

---

## 🚀 Advanced Features

### Custom Port Range

Edit `wireless_adb.py`:
```python
class WirelessADBManager:
    PORT_MIN = 40000  # Change this
    PORT_MAX = 45000  # And this
```

### Auto-Reconnect on IP Change

Add to your crontab (Linux):
```bash
*/5 * * * * /usr/local/bin/wireless-adb reconnect --quiet
```

### Integration with Other Tools

```bash
# Use in scripts
wireless-adb connect -q && flutter run

# Check status before deploying
wireless-adb status | grep "Wireless Devices: None" && wireless-adb connect
```

### Multiple Profiles

The tool automatically saves profiles for all devices you connect to:
```bash
wireless-adb status  # Shows all saved profiles
```

---

## 🤝 Contributing

Found a bug? Have a feature request? Contributions welcome!

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Setup

```bash
git clone https://github.com/yourusername/wireless-adb.git
cd wireless-adb

# Install in development mode
pip install -e .

# Run tests (if implemented)
python -m pytest tests/
```

---

## 📝 License

MIT License - see LICENSE file for details

---

## 🙏 Acknowledgments

- Android Debug Bridge (ADB) team at Google
- The Android developer community
- Built with security and convenience in mind

---

## 📞 Support

- **Issues:** [GitHub Issues](https://github.com/yourusername/wireless-adb/issues)
- **Discussions:** [GitHub Discussions](https://github.com/yourusername/wireless-adb/discussions)
- **Security:** Report vulnerabilities privately via email

---

## 🎓 Learn More

- [Android ADB Documentation](https://developer.android.com/studio/command-line/adb)
- [USB Debugging Guide](https://developer.android.com/studio/debug/dev-options)
- [Network Security Best Practices](https://owasp.org/www-project-mobile-security/)

---

**Happy (Safe) Wireless Debugging! 🚀🔒**
