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
# Connect first phone
wireless-adb connect

# List targets in Flutter
flutter devices

# Run on wireless device
flutter run -d <device-ip:port>
```

---

## 🚀 3. Instant Screen Mirroring + Dev Shell

```bash
# Launch high-framerate wireless mirror
wireless-adb mirror

# Open interactive shell in another terminal tab
wireless-adb shell
```

---

## 📦 4. Wireless Drag-and-Drop APK Installation

```bash
# Deploy debug APK over Wi-Fi without touching the phone
wireless-adb install -f ./app-debug.apk
```

---

## 👁️ 5. Auto-Reconnect Daemon for Unstable Wi-Fi

Keep your session alive during flaky network conditions:
```bash
wireless-adb watch
```
WirelessADB will poll ADB state in the background and automatically restore your connection if Wi-Fi drops.

---

## 🩺 6. Environment Health Check

Verify ADB binary paths, permissions, and subnet routing:
```bash
wireless-adb doctor
```
