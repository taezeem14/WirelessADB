# ⚡ WirelessADB Project Architecture & Specifications

### System Information
- **Package**: wireless-adb
- **Version**: 4.0.0
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
    | Connection Engine|   | Telemetry Engine |   | Media & Tools    |
    | • High-Port Gen  |   | • Battery %/Temp |   | • scrcpy (60fps) |
    | • Android 11 Pair|   | • Wi-Fi RSSI     |   | • Screenshot PNG |
    | • Auto-Reconnect |   | • Ping Latency   |   | • Screenrecord   |
    | • PID Lock Guard |   | • Subnet Guard   |   | • Push / Pull    |
    | • Favorites/Alias|   | • Hardware Specs |   | • Apps & Logcat  |
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
1. **`UI` & `Colors`**: High-performance ANSI styling engine with Windows VT100 kernel activation, ASCII banner, formatted rounded unicode boxes, and safe Unicode printing.
2. **`ADBWrapper`**: Subprocess abstraction with timeout protection, device discovery, battery/wifi telemetry extraction, mDNS detection, screencap, screenrecord, file push/pull, and logcat.
3. **`WirelessADBManager`**: Core business logic for handshakes, Android 11+ pairing wizard, profile persistence, favorites management, singleton watcher daemon, and full CLI dispatch.
4. **`pyproject.toml` & `setup.py`**: PEP 517/518 build system standardizing `pip install .` and console scripts (`wireless-adb`, `wadb`).
5. **Installers**: Native installers for Windows (`install.ps1`, `install_windows.bat`), Linux (`install_linux.sh`), and macOS (`install_macos.sh`).
