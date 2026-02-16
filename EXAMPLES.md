# WirelessADB Usage Examples & Scenarios

Complete guide with real-world examples and workflows.

---

## 📱 Basic Scenarios

### Scenario 1: First-Time Setup (Single Device)

**Goal:** Connect your Pixel 6 Pro wirelessly for Flutter development

```bash
# 1. Connect device via USB
# 2. Enable Developer Options and USB Debugging on device
# 3. Accept authorization popup on device

# 4. Run WirelessADB
wireless-adb connect
```

**Output:**
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

```bash
# 5. Unplug USB cable
# 6. Verify connection
adb devices

# Should show:
# 192.168.1.145:37482    device

# 7. Use ADB normally
adb shell pm list packages
flutter run

# 8. When done, cleanup
wireless-adb disconnect
```

---

### Scenario 2: Multiple Devices

**Goal:** You have both a phone and tablet connected via USB

```bash
wireless-adb connect
```

**Output:**
```
[1/5] Detecting USB-connected Android devices...
[FOUND] 2 devices connected:
        [1] Pixel 6 Pro (1A2B3C4D5E6F)
        [2] Galaxy Tab S8 (9Z8Y7X6W5V4U)
Select device [1-2]:
```

**Choose device:**
```
Select device [1-2]: 1
[OK] Selected: Pixel 6 Pro (1A2B3C4D5E6F)
...
```

**Connect both devices:**
```bash
# Connect first device
wireless-adb connect
# Select [1]

# Keep USB connected, run again for second device
wireless-adb connect
# Select [2]

# Now unplug both USB cables
adb devices

# Should show both:
# 192.168.1.145:37482    device
# 192.168.1.158:42193    device
```

---

### Scenario 3: Quick Reconnect After Reboot

**Goal:** Your computer restarted but device is still on the network

```bash
# Check saved profiles
wireless-adb status

# Output shows:
# Saved Profiles (1):
#   • Pixel 6 Pro (1A2B3C4D5E6F)
#     Last: 192.168.1.145:37482 @ 2026-02-16 14:32:15

# Reconnect using saved profile
wireless-adb reconnect
```

**Output:**
```
[RECONNECT] Attempting to reconnect to last device...
[FOUND] Last device: Pixel 6 Pro
        Target: 192.168.1.145:37482
[OK] Reconnected successfully!
```

---

## 🛠️ Developer Workflows

### Flutter Development

```bash
# Setup
wireless-adb connect

# Unplug USB
# Start development
flutter run

# Hot reload works wirelessly
# Press 'r' in terminal

# When done
wireless-adb disconnect
flutter clean  # Optional
```

### React Native Development

```bash
# Connect device
wireless-adb connect

# Start Metro bundler
npm start

# In another terminal, run app
npx react-native run-android

# Device will appear in Metro
# Shake device → "Dev Settings" → "Debug server host & port"
# Enter: YOUR_COMPUTER_IP:8081

# Develop normally
wireless-adb disconnect  # When done
```

### Android Studio

```bash
# Connect wirelessly
wireless-adb connect

# Open Android Studio
# Device appears in device dropdown
# Run/Debug works normally

# Logcat works wirelessly
# Layout Inspector works
# Profiler works

# When done
wireless-adb disconnect
```

### ADB Shell Sessions

```bash
# Connect
wireless-adb connect

# Interactive shell
adb shell
# Now you're in device shell

# Or one-off commands
adb shell pm list packages | grep chrome
adb shell dumpsys battery
adb shell screenrecord /sdcard/demo.mp4

# File transfers
adb push myfile.txt /sdcard/
adb pull /sdcard/photo.jpg ./

# Cleanup
wireless-adb disconnect
```

---

## 🔧 Advanced Usage

### Scripting Integration

**Auto-connect before deployment:**
```bash
#!/bin/bash
# deploy.sh

echo "Connecting to Android device..."
wireless-adb connect -q || {
    echo "Connection failed!"
    exit 1
}

echo "Building and deploying..."
./gradlew assembleDebug
adb install -r app/build/outputs/apk/debug/app-debug.apk

echo "Launching app..."
adb shell am start -n com.example.app/.MainActivity

echo "Cleaning up..."
wireless-adb disconnect -q

echo "Deployment complete!"
```

**Automated testing:**
```bash
#!/bin/bash
# test_runner.sh

# Connect to device
wireless-adb reconnect -q || wireless-adb connect -q

# Run instrumented tests
./gradlew connectedAndroidTest

# Pull test results
adb pull /sdcard/test_results ./results/

# Disconnect
wireless-adb disconnect -q
```

### Continuous Integration (CI/CD)

**GitHub Actions example:**
```yaml
name: Android Tests

on: [push]

jobs:
  test:
    runs-on: self-hosted  # Must have Android device connected
    steps:
      - uses: actions/checkout@v2
      
      - name: Setup Wireless ADB
        run: |
          pip install wireless-adb
          wireless-adb connect -q
      
      - name: Run Tests
        run: ./gradlew connectedAndroidTest
      
      - name: Cleanup
        run: wireless-adb disconnect -q
        if: always()
```

### Multi-Device Testing

```bash
#!/bin/bash
# multi_device_test.sh

# Connect all USB devices wirelessly
for i in 1 2 3; do
    wireless-adb connect -q
done

# Get all wireless device IPs
DEVICES=$(adb devices | grep ":.*device" | cut -f1)

# Run tests on each device
for DEVICE in $DEVICES; do
    echo "Testing on $DEVICE..."
    adb -s $DEVICE install -r app-debug.apk
    adb -s $DEVICE shell am instrument -w com.example.test/androidx.test.runner.AndroidJUnitRunner
done

# Cleanup
wireless-adb disconnect -q
```

---

## 🐛 Debugging Workflows

### Scenario: Connection Drops During Development

```bash
# Connection lost
adb devices
# Shows: 192.168.1.145:37482    offline

# Quick fix - reconnect
wireless-adb reconnect

# If that fails, full reconnect
wireless-adb disconnect
# Plug in USB cable
wireless-adb connect
# Unplug USB cable
```

### Scenario: Wrong Network

```bash
# You connected to wrong Wi-Fi
wireless-adb connect

# Output:
# [WARNING] Device and host appear to be on different subnets!
#           Device: 192.168.1.145 | Host: 10.0.0.15

# Fix: Connect both to same network
# Then reconnect
wireless-adb disconnect
wireless-adb connect
```

### Scenario: Firewall Blocking

```bash
# Connection fails
wireless-adb connect -v

# Output shows timeout
# Fix: Allow Python through firewall

# Windows
# Control Panel → Windows Defender Firewall → Allow an app
# Add Python.exe

# Linux
sudo ufw allow from 192.168.1.0/24

# Then reconnect
wireless-adb connect
```

---

## 🎯 Specific Use Cases

### Use Case: Couch Development

**Setup:**
- Desktop computer: Hardwired Ethernet
- Phone: Wi-Fi on same network
- You: On the couch with laptop and phone

**Workflow:**
```bash
# On desktop (one-time)
# Connect phone via USB to desktop
wireless-adb connect
# Note the IP:PORT shown (e.g., 192.168.1.145:37482)
# Unplug phone

# On laptop (where you're coding)
adb connect 192.168.1.145:37482
# Now laptop can deploy to phone wirelessly
```

### Use Case: Demo Preparation

**Setup:**
- Presentation in conference room
- Need to demo app on phone
- Don't want cables during demo

**Workflow:**
```bash
# Before demo (at desk)
wireless-adb connect
# Unplug USB cable
# Keep phone in pocket

# Walk to conference room
# Phone stays connected

# During demo
# Screen mirror phone to projector
# Run commands from laptop
adb shell input keyevent KEYCODE_HOME
adb shell am start -n com.example.app/.MainActivity

# After demo
wireless-adb disconnect  # Save battery
```

### Use Case: Automated Screenshots

```bash
#!/bin/bash
# screenshot_automation.sh

wireless-adb connect -q

# Navigate app and take screenshots
adb shell input tap 500 1000  # Tap button
sleep 1
adb shell screencap /sdcard/screenshot1.png
adb pull /sdcard/screenshot1.png ./

adb shell input swipe 200 800 200 200  # Swipe up
sleep 1
adb shell screencap /sdcard/screenshot2.png
adb pull /sdcard/screenshot2.png ./

wireless-adb disconnect -q

echo "Screenshots saved!"
```

### Use Case: Battery Testing

**Goal:** Monitor battery drain while testing

```bash
# Connect wirelessly to avoid USB charging
wireless-adb connect

# Reset battery stats
adb shell dumpsys batterystats --reset

# Run your test
adb shell am start -n com.example.app/.MainActivity
# Use app for 30 minutes

# Get battery stats
adb shell dumpsys batterystats > battery_log.txt

# Analyze
grep "Discharge" battery_log.txt

wireless-adb disconnect
```

---

## 🔒 Security-Focused Workflows

### Workflow: Trusted Network Only

```bash
#!/bin/bash
# secure_connect.sh

# Check if on home network
CURRENT_SSID=$(iwgetid -r)

if [ "$CURRENT_SSID" != "MyHomeWiFi" ]; then
    echo "ERROR: Not on trusted network!"
    echo "Current: $CURRENT_SSID"
    exit 1
fi

echo "On trusted network, connecting..."
wireless-adb connect

# Auto-disconnect after timeout
sleep 7200  # 2 hours
wireless-adb disconnect
echo "Auto-disconnected after timeout"
```

### Workflow: VPN-Only Connection

```bash
#!/bin/bash
# vpn_adb.sh

# Ensure VPN is active
if ! ip addr show tun0 &> /dev/null; then
    echo "VPN not active! Starting..."
    sudo openvpn --config ~/my-vpn.ovpn --daemon
    sleep 5
fi

echo "VPN active, connecting ADB..."
wireless-adb connect

# Your work here
flutter run

# Cleanup
wireless-adb disconnect
echo "Disconnected and VPN still running"
```

### Workflow: Port Monitoring

```bash
#!/bin/bash
# monitor_adb_port.sh

wireless-adb connect -v | tee connection.log

# Extract port from log
PORT=$(grep "Using port:" connection.log | grep -oP '\d{5}')

echo "Monitoring port $PORT..."

# Alert if unexpected connections
while true; do
    CONNECTIONS=$(netstat -an | grep ":$PORT" | grep ESTABLISHED | wc -l)
    if [ $CONNECTIONS -gt 1 ]; then
        echo "WARNING: Multiple connections detected on port $PORT!"
        notify-send "Security Alert" "Unexpected ADB connections"
    fi
    sleep 10
done
```

---

## 📊 Monitoring & Logging

### Check Connection Status

```bash
# Quick status check
wireless-adb status

# Monitor connection quality
watch -n 5 'wireless-adb status | grep Wireless'

# Detailed connection info
adb devices -l

# Check network latency
adb shell ping -c 5 $(hostname -I | awk '{print $1}')
```

### Log All ADB Commands

```bash
# Enable verbose mode
export ADB_TRACE=all

# Now all ADB commands are logged
adb logcat

# Check logs
tail -f ~/.android/adb.log
```

### Connection Health Check

```bash
#!/bin/bash
# health_check.sh

echo "Testing wireless ADB connection..."

# Test basic connectivity
if adb shell echo "test" &> /dev/null; then
    echo "✓ Shell access working"
else
    echo "✗ Shell access failed"
    exit 1
fi

# Test file transfer speed
dd if=/dev/zero bs=1M count=10 2>/dev/null | adb shell "cat > /dev/null"
echo "✓ File transfer working"

# Test app installation speed
START=$(date +%s)
adb install -r test.apk &> /dev/null
END=$(date +%s)
DURATION=$((END - START))
echo "✓ App install took ${DURATION}s"

echo "Connection health: GOOD"
```

---

## ⚡ Performance Tips

### Reduce Latency

```bash
# Use 5GHz Wi-Fi instead of 2.4GHz
# Ensure device and host are close to router
# Minimize interference

# Test connection latency
adb shell ping -c 10 $(hostname -I | awk '{print $1}')
```

### Optimize for Large File Transfers

```bash
# For large APK installs
wireless-adb connect

# Compress before transfer
gzip large_file.bin
adb push large_file.bin.gz /sdcard/
adb shell gunzip /sdcard/large_file.bin.gz

wireless-adb disconnect
```

### Battery Optimization

```bash
# Wireless ADB uses more battery than USB
# Disconnect when not actively developing

# Auto-disconnect script
wireless-adb connect
# Do your work
sleep 3600  # 1 hour max
wireless-adb disconnect  # Auto cleanup
```

---

## 🎓 Learning Exercises

### Exercise 1: Build an Auto-Deployer

Create a script that:
1. Watches for code changes
2. Auto-builds APK
3. Installs via wireless ADB
4. Launches app

### Exercise 2: Multi-Device Screenshot Tool

Build a tool that:
1. Connects to multiple devices
2. Takes synchronized screenshots
3. Saves with device name

### Exercise 3: Security Monitor

Create a monitor that:
1. Detects active ADB connections
2. Alerts on unknown IPs
3. Auto-disconnects suspicious connections

---

## 🚀 Pro Tips

1. **Alias for speed:**
   ```bash
   alias wadb='wireless-adb'
   alias wadb-c='wireless-adb connect -q'
   alias wadb-d='wireless-adb disconnect -q'
   ```

2. **Auto-connect on boot:**
   ```bash
   # Add to ~/.bashrc
   wireless-adb reconnect -q &> /dev/null &
   ```

3. **Quick status in prompt:**
   ```bash
   # Add to PS1
   PS1='$(wireless-adb status -q | grep -q Wireless && echo "📱 ") \u@\h:\w\$ '
   ```

4. **Use with tmux/screen:**
   ```bash
   # Keep connection alive in background session
   tmux new -d -s adb 'wireless-adb connect && sleep infinity'
   ```

5. **Combine with other tools:**
   ```bash
   wireless-adb connect && scrcpy  # Screen mirroring
   wireless-adb connect && vysor   # Remote control
   ```

---

**Happy Wireless Development! 🚀**
