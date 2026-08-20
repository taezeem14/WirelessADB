# 🛠️ WirelessADB Developer Recipe Book & Examples

Practical workflows and advanced recipes for everyday Android development.

---

## 📱 1. React Native & Expo Workflow

```bash
# Step 1: Connect your phone wirelessly
wireless-adb connect

# Step 2: Start Metro bundler and run on Android
npx react-native run-android
# or for Expo:
npx expo start --android
```

---

## 💙 2. Flutter Multi-Device Wireless Debugging

```bash
# Connect phone wirelessly
wireless-adb connect

# List targets in Flutter
flutter devices

# Run directly on wireless target
flutter run
```

---

## 📸 3. Instant Screenshots & Screen Recording

```bash
# Capture full HD screenshot to default PNG
wireless-adb screenshot

# Save screenshot to custom path
wireless-adb screenshot -o ~/Desktop/bug_report.png

# Record 30 seconds of screen video
wireless-adb record --time 30 -o demo.mp4
```

---

## 📂 4. Wireless File Transfer (Push & Pull)

```bash
# Push test assets or data to device SDCard
wireless-adb push ./sample_video.mp4 /sdcard/Download/

# Pull photo or crash dump from device
wireless-adb pull /sdcard/DCIM/Camera/IMG_001.jpg ./
```

---

## 📱 5. App & Package Management

```bash
# List all 3rd-party user installed apps
wireless-adb apps

# Filter packages by keyword
wireless-adb apps --filter flutter

# Include system packages
wireless-adb apps --system --filter camera
```

---

## 📋 6. Live Wireless Logcat Streaming

```bash
# Stream all logs live
wireless-adb logcat

# Filter logcat by app tag
wireless-adb logcat --tag MyApp

# Stream and save to log file
wireless-adb logcat --tag Retrofit -o network_dump.log
```

---

## 🚀 7. Instant Screen Mirroring + Dev Shell

```bash
# Launch high-framerate wireless mirror
wireless-adb mirror

# Open interactive shell in another terminal tab
wireless-adb shell
```

---

## 📦 8. Wireless Drag-and-Drop APK Installation

```bash
# Deploy debug APK over Wi-Fi without touching the phone
wireless-adb install -f ./app-debug.apk
```

---

## 👁️ 9. Auto-Reconnect Daemon for Flaky Wi-Fi

Keep your session alive during network blips:
```bash
wireless-adb watch
```
WirelessADB will poll ADB state in the background and automatically restore your connection if Wi-Fi drops.

---

## 🩺 10. Environment Health Check

Verify ADB binary paths, permissions, and subnet routing:
```bash
wireless-adb doctor
```
