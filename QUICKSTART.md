# WirelessADB - Quick Start Guide

**5-minute setup for Android wireless debugging with enhanced security.**

---

## ⚡ Ultra-Fast Setup

### For Linux Users
```bash
# 1. Install ADB if needed
sudo apt install android-tools-adb  # Ubuntu/Debian
# sudo pacman -S android-tools      # Arch
# sudo dnf install android-tools    # Fedora

# 2. Download and install WirelessADB
wget https://raw.githubusercontent.com/yourusername/wireless-adb/main/wireless_adb.py
chmod +x wireless_adb.py
sudo mv wireless_adb.py /usr/local/bin/wireless-adb

# 3. Connect your device
wireless-adb connect

# Done! Unplug USB cable.
```

### For Windows Users
```powershell
# 1. Install Python (if needed)
# Download from: https://www.python.org/downloads/
# ✓ Check "Add Python to PATH"

# 2. Install ADB (if needed)
# Download: https://developer.android.com/studio/releases/platform-tools
# Extract to C:\platform-tools\
# Add to PATH: setx PATH "%PATH%;C:\platform-tools"

# 3. Download WirelessADB
# Save wireless_adb.py to Downloads

# 4. Create shortcut
cd %USERPROFILE%
echo @python "%USERPROFILE%\Downloads\wireless_adb.py" %%* > wireless-adb.bat

# 5. Connect your device
wireless-adb connect

# Done! Unplug USB cable.
```

---

## 📱 First Connection (60 seconds)

```bash
# Step 1: Enable USB Debugging on your Android device
# Settings → About Phone → Tap "Build Number" 7 times
# Settings → Developer Options → Enable "USB Debugging"

# Step 2: Connect USB cable
# Accept authorization popup on device

# Step 3: Run WirelessADB
wireless-adb connect

# Step 4: Unplug USB cable
# You're now wireless!

# Step 5: Test it
adb devices
# Should show: 192.168.1.XXX:XXXXX device

# Step 6: When done, cleanup
wireless-adb disconnect
```

---

## 🎯 Common Commands

```bash
# Connect wirelessly (generates random port)
wireless-adb connect

# Disconnect and cleanup
wireless-adb disconnect

# Check connection status
wireless-adb status

# Reconnect to last device
wireless-adb reconnect

# Verbose mode (see all details)
wireless-adb connect -v

# Quiet mode (minimal output)
wireless-adb connect -q
```

---

## 🔥 Why WirelessADB is Better

### Traditional ADB (Insecure)
```bash
adb tcpip 5555              # ⚠️ Predictable port
adb connect 192.168.1.100   # ⚠️ Manual IP management
# ⚠️ No cleanup
# ⚠️ Device stays exposed
# ⚠️ Easy target for hackers
```

### WirelessADB (Secure)
```bash
wireless-adb connect        # ✅ Random port (30000-50000)
                           # ✅ Auto IP detection
                           # ✅ Auto cleanup on exit
                           # ✅ Security warnings
                           # ✅ 10,000x harder to attack
```

---

## 🚨 Security Quick Tips

### ✅ Safe Usage
- Use on home Wi-Fi ✓
- Use on corporate VPN ✓
- Disconnect when done ✓

### ❌ Unsafe Usage
- Public Wi-Fi (coffee shops) ✗
- Hotel networks ✗
- Conference Wi-Fi ✗
- Shared apartment Wi-Fi ✗

### 🔒 Always Remember
```bash
# When you're done developing:
wireless-adb disconnect

# Check what's connected:
wireless-adb status
```

---

## 🐛 Quick Troubleshooting

### "ADB not found"
```bash
# Linux
sudo apt install android-tools-adb

# Mac
brew install android-platform-tools

# Windows
# Download: https://developer.android.com/studio/releases/platform-tools
# Add to PATH
```

### "No USB devices found"
1. Enable USB Debugging on device
2. Accept authorization popup
3. Try different USB cable/port
4. Run: `adb devices` to verify

### "Could not get Wi-Fi IP"
1. Connect device to Wi-Fi (not just mobile data)
2. Verify: Settings → Wi-Fi → Connected
3. Retry: `wireless-adb connect`

### "Wireless connection failed"
1. Ensure device and computer on same network
2. Disable firewall temporarily to test
3. Check router settings (disable AP isolation)
4. Run verbose mode: `wireless-adb connect -v`

---

## 💡 Pro Tips

### Tip 1: Create Aliases
```bash
# Add to ~/.bashrc or ~/.zshrc
alias wadb='wireless-adb'
alias wadb-c='wireless-adb connect -q'
alias wadb-d='wireless-adb disconnect -q'
```

### Tip 2: Auto-Reconnect After Reboot
```bash
# Just run:
wireless-adb reconnect

# Uses saved profile from last connection
```

### Tip 3: Multiple Devices
```bash
# WirelessADB will show a menu:
[1] Pixel 6 Pro
[2] Galaxy S21
Select device [1-2]: 1
```

### Tip 4: Use in Scripts
```bash
#!/bin/bash
wireless-adb connect -q || exit 1
./gradlew assembleDebug
adb install -r app.apk
wireless-adb disconnect -q
```

### Tip 5: Monitor Connection
```bash
# Check status anytime:
wireless-adb status

# Shows USB devices, wireless devices, and saved profiles
```

---

## 🎯 Common Use Cases

### Flutter Development
```bash
wireless-adb connect
flutter run
# Hot reload works wirelessly!
wireless-adb disconnect
```

### React Native
```bash
wireless-adb connect
npm start
npx react-native run-android
wireless-adb disconnect
```

### Android Studio
```bash
wireless-adb connect
# Device appears in Android Studio
# Run/Debug works normally
wireless-adb disconnect
```

### ADB Commands
```bash
wireless-adb connect

adb shell pm list packages
adb install my-app.apk
adb logcat
adb shell screencap /sdcard/screenshot.png
adb pull /sdcard/screenshot.png

wireless-adb disconnect
```

---

## 📚 More Information

- **Full Guide:** See [README.md](README.md)
- **Examples:** See [EXAMPLES.md](EXAMPLES.md)
- **Security:** See [SECURITY.md](SECURITY.md)

---

## 🆘 Need Help?

1. **Run verbose mode:**
   ```bash
   wireless-adb connect -v
   ```

2. **Check status:**
   ```bash
   wireless-adb status
   adb devices
   ```

3. **Kill and restart ADB:**
   ```bash
   adb kill-server
   adb start-server
   wireless-adb connect
   ```

4. **Check logs:**
   ```bash
   # Linux
   cat ~/.android/adb.log
   
   # Windows
   type %USERPROFILE%\.android\adb.log
   ```

5. **Open an issue:**
   - [GitHub Issues](https://github.com/yourusername/wireless-adb/issues)

---

## 🎉 That's It!

You're now set up for secure wireless Android debugging!

**Remember:**
- ✅ Connect on trusted networks
- ✅ Disconnect when done
- ✅ Random ports protect you

**Happy wireless debugging! 🚀**

---

## 🔥 One-Liner Cheat Sheet

```bash
# Connect → Work → Disconnect
wireless-adb connect && adb shell pm list packages && wireless-adb disconnect

# Flutter run wireless
wireless-adb connect && flutter run; wireless-adb disconnect

# Install APK and launch
wireless-adb connect && adb install -r app.apk && adb shell monkey -p com.example -1 && wireless-adb disconnect

# Take screenshot and pull
wireless-adb connect && adb shell screencap /sdcard/s.png && adb pull /sdcard/s.png && wireless-adb disconnect

# Check battery stats
wireless-adb connect && adb shell dumpsys battery && wireless-adb disconnect
```

---

**Built for developers who value both security and convenience.** 🔒⚡
