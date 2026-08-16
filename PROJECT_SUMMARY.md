# ⚡ WirelessADB Project Architecture & Specifications

### System Information
- **Package**: WirelessADB
- **Version**: 3.2.0
- **License**: MIT
- **Repository**: https://github.com/taezeem14/WirelessADB

---

## 🏛️ Architecture Overview

```
                      +-----------------------------+
                      |   CLI & Interactive TUI     |
                      +--------------+--------------+
                                     |
              +----------------------+----------------------+
              |                      |                      |
    +---------v--------+   +---------v--------+   +---------v--------+
    | Connection Engine|   | Telemetry Engine |   |  Tool Integrator |
    | • High-Port Gen  |   | • Battery %/Temp |   | • scrcpy (60fps) |
    | • Android 11 Pair|   | • Wi-Fi RSSI     |   | • Wireless Shell |
    | • Auto-Reconnect |   | • Ping Latency   |   | • APK Installer  |
    +---------+--------+   +---------+--------+   +---------+--------+
              |                      |                      |
              +----------------------+----------------------+
                                     |
                      +--------------v--------------+
                      |    ADB Low-Level Wrapper    |
                      +--------------+--------------+
                                     |
                      +--------------v--------------+
                      | Physical & Wireless Devices |
                      +-----------------------------+
```

---

## 🛠️ Modules Breakdown
1. **`UI` & `Colors`**: High-performance ANSI styling engine with Windows VT100 kernel activation, ASCII banner, formatted rounded unicode boxes, and badges.
2. **`ADBWrapper`**: Subprocess abstraction with timeout protection, device discovery, battery/wifi telemetry extraction, and mDNS detection.
3. **`WirelessADBManager`**: Core business logic for handshakes, Android 11+ pairing wizard, profile persistence, and auto-reconnect watcher.
4. **`pyproject.toml` & `setup.py`**: PEP 517/518 build system standardizing `pip install .` and console scripts (`wireless-adb`, `wadb`).
5. **Installers**: Native scripts for Windows (`install_windows.bat`), Linux (`install_linux.sh`), and macOS (`install_macos.sh`).
