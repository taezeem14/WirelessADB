# ⚡ WirelessADB Quickstart Guide (30 Seconds Onboarding)

Get up and running with WirelessADB in under 30 seconds.

---

## 🏎️ 30-Second Fast Path

### 1. Launch Control Center
Open your terminal and type:
```bash
wireless-adb
# or using the short alias:
wadb
```

### 2. Method A: USB Fast Switch (Recommended for First-Time)
```bash
# 1. Connect phone via USB cable (with USB Debugging ON)
# 2. Run:
wireless-adb connect

# 3. Unplug USB cable and enjoy wireless debugging!
```

### 3. Method B: Zero-Cable Pairing (Android 11+)
```bash
# 1. On phone: Developer Options -> Wireless Debugging -> "Pair device with pairing code"
# 2. Run:
wireless-adb pair

# 3. Enter the IP:Port and 6-digit PIN displayed on your phone screen.
```

---

## 📊 Live HUD & Telemetry
Check active wireless connections, battery %, and ping latency anytime:
```bash
wireless-adb status
```

---

## 🖥️ Screen Mirroring in 1-Click
If you have [`scrcpy`](https://github.com/Genymobile/scrcpy) installed:
```bash
wireless-adb mirror
```
Launches ultra-smooth 60 FPS screen mirroring over Wi-Fi!

---

## 🔌 Safe Teardown
When you are done debugging:
```bash
wireless-adb disconnect
```
Safely closes remote TCP sockets and switches devices back to USB mode.
