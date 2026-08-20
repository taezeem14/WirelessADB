#!/usr/bin/env python3
"""
⚡ WirelessADB - Next-Gen Secure Wireless ADB Connection & Telemetry Suite
A production-grade, zero-dependency CLI & TUI for effortless wireless Android debugging.

Author: Built for elite Android developers & security-conscious hackers
License: MIT
Repository: https://github.com/taezeem14/WirelessADB
"""

import sys
import os
import re
import time
import json
import socket
import random
import ipaddress
import subprocess
import argparse
import shutil
import pathlib
from pathlib import Path
from typing import Optional, Tuple, Dict, List, Any
from dataclasses import dataclass, asdict, fields
from enum import Enum
from datetime import datetime

# Python 3.7+ Enforcement
if sys.version_info < (3, 7):
    sys.exit(f"[FATAL] Python 3.7+ is required. Running on {sys.version.split()[0]}.")

# Version Info
__version__ = "4.0.0"
__tool_name__ = "WirelessADB"

# Ensure UTF-8 output encoding across Windows / Linux / macOS
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


def safe_print(*args, **kwargs) -> None:
    """Print with Unicode error fallback protection for legacy Windows consoles."""
    try:
        print(*args, **kwargs)
    except UnicodeEncodeError:
        enc = sys.stdout.encoding or "ascii" if sys.stdout else "ascii"
        text = " ".join(str(a) for a in args)
        text = text.encode(enc, errors="replace").decode(enc)
        print(text, **{k: v for k, v in kwargs.items() if k != "end"})


# Enable VT100 Escape Sequences on Windows
if sys.platform == "win32":
    try:
        import ctypes
        kernel32 = ctypes.windll.kernel32
        hOut = kernel32.GetStdHandle(-11)
        mode = ctypes.c_ulong()
        kernel32.GetConsoleMode(hOut, ctypes.byref(mode))
        kernel32.SetConsoleMode(hOut, mode.value | 0x0004)
    except Exception:
        pass


class Colors:
    """Terminal styling, ANSI palettes and UI decorations"""
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    UNDERLINE = "\033[4m"

    # Foreground Neon Palette
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"

    # Hex/256-Color Accents
    NEON_PURPLE = "\033[38;5;141m"
    NEON_PINK = "\033[38;5;207m"
    NEON_GREEN = "\033[38;5;84m"
    NEON_CYAN = "\033[38;5;51m"
    NEON_ORANGE = "\033[38;5;208m"
    DARK_GRAY = "\033[38;5;240m"
    LIGHT_GRAY = "\033[38;5;250m"

    # Backgrounds
    BG_DARK = "\033[48;5;234m"
    BG_GREEN = "\033[48;5;22m"
    BG_BLUE = "\033[48;5;17m"

    @classmethod
    def disable(cls) -> None:
        """Strip all ANSI codes for plain terminals or file pipes"""
        for attr in list(cls.__dict__.keys()):
            if not attr.startswith("__") and isinstance(getattr(cls, attr), str):
                setattr(cls, attr, "")


class LogLevel(Enum):
    QUIET = 0
    NORMAL = 1
    VERBOSE = 2


@dataclass
class DeviceProfile:
    serial: str
    ip: str
    port: int
    last_connected: float
    device_name: str = "Unknown"
    alias: str = ""
    android_version: str = "Unknown"
    battery_level: str = "Unknown"

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DeviceProfile":
        """Safely instantiate DeviceProfile ignoring extraneous keys."""
        valid_fields = {f.name for f in fields(cls)}
        filtered = {k: v for k, v in data.items() if k in valid_fields}
        return cls(**filtered)


class UI:
    """ASCII art, banners, tables, and stylized visual output"""

    @staticmethod
    def banner() -> str:
        logo = f"""{Colors.NEON_CYAN}
  ██╗    ██╗██╗██████╗ ███████╗██╗     ███████╗███████╗███████╗ █████╗ ██████╗ ██████╗ 
  ██║    ██║██║██╔══██╗██╔════╝██║     ██╔════╝██╔════╝██╔════╝██╔══██╗██╔══██╗██╔══██╗
  ██║ █╗ ██║██║██████╔╝█████╗  ██║     █████╗  ███████╗███████╗███████║██║  ██║██████╔╝
  ██║███╗██║██║██╔══██╗██╔══╝  ██║     ██╔══╝  ╚════██║╚════██║██╔══██║██║  ██║██╔══██╗
  ╚███╔███╔╝██║██║  ██║███████╗███████╗███████╗███████║███████║██║  ██║██████╔╝██████╔╝
   ╚══╝╚══╝ ╚═╝╚═╝  ╚═╝╚══════╝╚══════╝╚══════╝╚══════╝╚══════╝╚═╝  ╚═╝╚═════╝ ╚═════╝ 
{Colors.RESET}{Colors.DARK_GRAY}   ⚡ Next-Gen Wireless Android Debug Bridge • v{__version__} • Built for Speed & Security ⚡{Colors.RESET}
"""
        return logo

    @staticmethod
    def box(title: str, lines: List[str], color: str = Colors.NEON_CYAN) -> str:
        plain_title = re.sub(r'\033\[[0-9;]*m', '', title)
        plain_lens = [len(re.sub(r'\033\[[0-9;]*m', '', l)) for l in lines]
        width = max([len(plain_title) + 4] + plain_lens + [54])
        
        top_dashes = max(0, width - len(plain_title) - 3)
        border_top = f"{color}╭─ {Colors.BOLD}{title}{Colors.RESET}{color} " + ("─" * top_dashes) + f"╮{Colors.RESET}"
        border_bot = f"{color}╰" + ("─" * width) + f"╯{Colors.RESET}"
        
        output = [border_top]
        for line in lines:
            plain_len = len(re.sub(r'\033\[[0-9;]*m', '', line))
            padding = " " * max(0, width - plain_len - 2)
            output.append(f"{color}│{Colors.RESET} {line}{padding} {color}│{Colors.RESET}")
        output.append(border_bot)
        return "\n".join(output)

    @staticmethod
    def badge(text: str, bg: str = Colors.BG_BLUE, fg: str = Colors.WHITE) -> str:
        return f"{bg}{fg} {text} {Colors.RESET}"

    @staticmethod
    def status_tag(online: bool) -> str:
        if online:
            return f"{Colors.NEON_GREEN}● ONLINE{Colors.RESET}"
        return f"{Colors.DARK_GRAY}○ OFFLINE{Colors.RESET}"


class ADBWrapper:
    """Low-level robust ADB execution engine"""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.adb_path = self._locate_adb()

    def _locate_adb(self) -> str:
        """Find ADB in PATH or standard Android SDK directories"""
        adb = shutil.which("adb")
        if adb:
            return adb

        # Check standard Windows / Mac / Linux paths
        search_paths = []
        if sys.platform == "win32":
            search_paths.extend([
                os.path.expandvars(r"%LOCALAPPDATA%\Android\Sdk\platform-tools\adb.exe"),
                r"C:\platform-tools\adb.exe",
                r"C:\Android\platform-tools\adb.exe",
            ])
        elif sys.platform == "darwin":
            search_paths.extend([
                os.path.expanduser("~/Library/Android/sdk/platform-tools/adb"),
                "/opt/homebrew/bin/adb",
                "/usr/local/bin/adb",
            ])
        else:
            search_paths.extend([
                os.path.expanduser("~/Android/Sdk/platform-tools/adb"),
                "/usr/bin/adb",
                "/usr/local/bin/adb",
            ])

        for p in search_paths:
            if os.path.exists(p):
                return p
        return "adb"

    def verify(self) -> Tuple[bool, str]:
        """Check if ADB is usable and return version"""
        try:
            res = self.run(["version"], check=True)
            first_line = res.stdout.strip().split("\n")[0]
            return True, first_line
        except Exception as e:
            return False, str(e)

    def run(self, cmd: List[str], check: bool = False, timeout: int = 30) -> subprocess.CompletedProcess:
        """Execute ADB subprocess command with UTF-8 encoding"""
        full_cmd = [self.adb_path] + cmd
        if self.verbose:
            safe_print(f"{Colors.DARK_GRAY}[EXEC] {' '.join(full_cmd)}{Colors.RESET}")

        try:
            result = subprocess.run(
                full_cmd,
                capture_output=True,
                encoding='utf-8',
                errors='replace',
                timeout=timeout,
                check=check
            )
            if self.verbose and result.stdout.strip():
                safe_print(f"{Colors.DARK_GRAY}[STDOUT] {result.stdout.strip()}{Colors.RESET}")
            return result
        except subprocess.TimeoutExpired:
            if self.verbose:
                safe_print(f"{Colors.RED}[TIMEOUT] Command timed out after {timeout}s: {' '.join(full_cmd)}{Colors.RESET}")
            raise
        except subprocess.CalledProcessError as e:
            if self.verbose:
                safe_print(f"{Colors.RED}[STDERR] {e.stderr.strip()}{Colors.RESET}")
            raise

    def get_devices(self) -> List[Dict[str, Any]]:
        """Fetch all connected devices with serial, type and state"""
        try:
            res = self.run(["devices", "-l"])
        except Exception:
            return []

        devices = []
        for line in res.stdout.strip().split("\n")[1:]:
            line = line.strip()
            if not line:
                continue
            parts = line.split()
            if len(parts) >= 2:
                serial = parts[0]
                state = parts[1]
                # Robust regex detection for IP:Port wireless serial
                is_wireless = bool(re.match(r'^\d+\.\d+\.\d+\.\d+:\d+$', serial))
                
                # Extract extra properties
                model = "Android Device"
                product = "Unknown"
                for p in parts[2:]:
                    if p.startswith("model:"):
                        model = p.split(":")[1].replace("_", " ")
                    elif p.startswith("product:"):
                        product = p.split(":")[1]

                devices.append({
                    "serial": serial,
                    "state": state,
                    "is_wireless": is_wireless,
                    "model": model,
                    "product": product,
                    "raw": line
                })
        return devices

    def get_device_ip(self, serial: str) -> Optional[str]:
        """Multi-strategy Wi-Fi IP address resolution"""
        strategies = [
            ["-s", serial, "shell", "ip", "addr", "show", "wlan0"],
            ["-s", serial, "shell", "ip", "route", "get", "8.8.8.8"],
            ["-s", serial, "shell", "ifconfig", "wlan0"],
            ["-s", serial, "shell", "getprop", "dhcp.wlan0.ipaddress"],
            ["-s", serial, "shell", "ip", "-f", "inet", "addr", "show"],
        ]
        
        for cmd in strategies:
            try:
                res = self.run(cmd, timeout=5)
                matches = re.findall(r'inet\s+(\d+\.\d+\.\d+\.\d+)|src\s+(\d+\.\d+\.\d+\.\d+)|inet addr:(\d+\.\d+\.\d+\.\d+)', res.stdout)
                for group in matches:
                    for ip in group:
                        if ip and not ip.startswith("127.") and not ip.startswith("0.") and not ip.startswith("169.254."):
                            return ip
                # Direct getprop single IP match
                direct_ip = res.stdout.strip()
                if re.match(r'^\d+\.\d+\.\d+\.\d+$', direct_ip) and not direct_ip.startswith("127."):
                    return direct_ip
            except Exception:
                continue

        return None

    def get_device_name(self, serial: str) -> str:
        """Fetch model & manufacturer name"""
        try:
            res_m = self.run(["-s", serial, "shell", "getprop", "ro.product.manufacturer"], timeout=5)
            res_n = self.run(["-s", serial, "shell", "getprop", "ro.product.model"], timeout=5)
            man = res_m.stdout.strip().title()
            mod = res_n.stdout.strip()
            if man and mod and not mod.lower().startswith(man.lower()):
                return f"{man} {mod}"
            return mod or man or "Android Device"
        except Exception:
            return "Android Device"

    def get_android_version(self, serial: str) -> str:
        """Fetch Android OS release version"""
        try:
            res = self.run(["-s", serial, "shell", "getprop", "ro.build.version.release"], timeout=5)
            sdk = self.run(["-s", serial, "shell", "getprop", "ro.build.version.sdk"], timeout=5)
            ver = res.stdout.strip()
            sdk_ver = sdk.stdout.strip()
            if ver and sdk_ver:
                return f"Android {ver} (API {sdk_ver})"
            return ver or "Android"
        except Exception:
            return "Android"

    def get_battery_info(self, serial: str) -> Dict[str, Any]:
        """Fetch battery percentage, charging state, temperature"""
        data = {"level": "Unknown", "status": "Unknown", "temp": "Unknown", "health": "Good"}
        try:
            res = self.run(["-s", serial, "shell", "dumpsys", "battery"], timeout=5)
            for line in res.stdout.strip().split("\n"):
                line = line.strip()
                if line.startswith("level:"):
                    data["level"] = f"{line.split(':')[1].strip()}%"
                elif line.startswith("status:"):
                    val = line.split(':')[1].strip()
                    statuses = {"1": "Unknown", "2": "Charging", "3": "Discharging", "4": "Not charging", "5": "Full"}
                    data["status"] = statuses.get(val, "Active")
                elif line.startswith("temperature:"):
                    try:
                        temp_c = float(line.split(':')[1].strip()) / 10.0
                        data["temp"] = f"{temp_c:.1f}°C"
                    except Exception:
                        pass
        except Exception:
            pass
        return data

    def get_wifi_telemetry(self, serial: str) -> Dict[str, str]:
        """Retrieve Wi-Fi link speed, RSSI and SSID"""
        telemetry = {"ssid": "Unknown", "link_speed": "Unknown", "rssi": "Unknown"}
        try:
            res = self.run(["-s", serial, "shell", "dumpsys", "wifi"], timeout=6)
            ssid_match = re.search(r'SSID:\s*"?([^",\n]+)"?', res.stdout)
            if ssid_match:
                telemetry["ssid"] = ssid_match.group(1)

            speed_match = re.search(r'Link speed:\s*(\d+Mbps)', res.stdout, re.IGNORECASE)
            if speed_match:
                telemetry["link_speed"] = speed_match.group(1)

            rssi_match = re.search(r'RSSI:\s*(-?\d+)', res.stdout)
            if rssi_match:
                telemetry["rssi"] = f"{rssi_match.group(1)} dBm"
        except Exception:
            pass

        return telemetry

    def ping_device(self, ip: str, count: int = 2) -> Optional[float]:
        """Measure roundtrip network ping latency to device"""
        try:
            if sys.platform == "win32":
                cmd = ["ping", "-n", str(count), "-w", "1000", ip]
            else:
                cmd = ["ping", "-c", str(count), "-W", "2", ip]
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            match = re.search(r'Average = (\d+)ms|avg.*?=\s*[\d.]+/([\d.]+)/', res.stdout)
            if match:
                lat = match.group(1) or match.group(2)
                return float(lat)
        except Exception:
            pass
        return None

    def enable_tcpip(self, serial: str, port: int) -> bool:
        """Switch target device into TCP/IP listening mode"""
        try:
            self.run(["-s", serial, "tcpip", str(port)], check=True, timeout=10)
            time.sleep(1.5)
            return True
        except Exception:
            return False

    def pair_wireless(self, ip_port: str, pairing_code: str) -> bool:
        """Android 11+ zero-wire Wi-Fi pairing"""
        try:
            res = self.run(["pair", ip_port, pairing_code], timeout=15)
            return "Successfully paired" in res.stdout or "paired to" in res.stdout.lower()
        except Exception:
            return False

    def connect_wireless(self, ip: str, port: int, retries: int = 3) -> bool:
        """Connect to wireless ADB endpoint with exponential backoff"""
        target = f"{ip}:{port}"
        for attempt in range(1, retries + 1):
            try:
                res = self.run(["connect", target], timeout=10)
                out = res.stdout.lower()
                if "connected" in out and "already" not in out:
                    return True
                if "already connected" in out:
                    return True
                if attempt < retries:
                    time.sleep(1.0 * attempt)
            except Exception:
                if attempt < retries:
                    time.sleep(1.0 * attempt)
        return False

    def disconnect(self, target: Optional[str] = None) -> bool:
        """Disconnect wireless device or all wireless targets"""
        try:
            if target:
                self.run(["disconnect", target], check=True, timeout=5)
            else:
                self.run(["disconnect"], check=True, timeout=5)
            return True
        except Exception:
            return False

    def usb_mode(self, serial: str) -> bool:
        """Reset device back to USB mode"""
        try:
            self.run(["-s", serial, "usb"], check=True, timeout=5)
            return True
        except Exception:
            return False

    def discover_mdns(self) -> List[Dict[str, str]]:
        """Discover wireless ADB instances via mDNS"""
        try:
            res = self.run(["mdns", "services"], timeout=5)
            results = []
            for line in res.stdout.strip().split("\n"):
                line = line.strip()
                if line and "\t" in line:
                    parts = line.split("\t")
                    results.append({"name": parts[0], "service": parts[1] if len(parts) > 1 else "", "addr": parts[2] if len(parts) > 2 else ""})
            return results
        except Exception:
            return []

    def take_screenshot(self, serial: str, dest_path: str) -> bool:
        """Capture device screenshot and save as PNG"""
        try:
            full_cmd = [self.adb_path, "-s", serial, "exec-out", "screencap", "-p"]
            with open(dest_path, "wb") as f:
                res = subprocess.run(full_cmd, stdout=f, stderr=subprocess.PIPE, timeout=15)
                if res.returncode == 0 and os.path.exists(dest_path) and os.path.getsize(dest_path) > 0:
                    return True
        except Exception:
            pass

        # Fallback via /sdcard/
        try:
            remote_tmp = "/sdcard/wadb_screenshot.png"
            self.run(["-s", serial, "shell", "screencap", "-p", remote_tmp], check=True, timeout=10)
            self.run(["-s", serial, "pull", remote_tmp, dest_path], check=True, timeout=15)
            self.run(["-s", serial, "shell", "rm", "-f", remote_tmp], timeout=5)
            return os.path.exists(dest_path) and os.path.getsize(dest_path) > 0
        except Exception:
            return False

    def record_screen(self, serial: str, dest_path: str, duration_sec: int = 10) -> bool:
        """Record screen video and pull to host"""
        remote_tmp = "/sdcard/wadb_record.mp4"
        try:
            safe_print(f"{Colors.YELLOW}⏺ Recording screen on {serial} for {duration_sec}s...{Colors.RESET}")
            self.run(["-s", serial, "shell", "screenrecord", "--time-limit", str(duration_sec), remote_tmp], timeout=duration_sec + 10)
            time.sleep(1)
            safe_print(f"{Colors.NEON_CYAN}⬇ Pulling recording to {dest_path}...{Colors.RESET}")
            self.run(["-s", serial, "pull", remote_tmp, dest_path], check=True, timeout=30)
            self.run(["-s", serial, "shell", "rm", "-f", remote_tmp], timeout=5)
            return os.path.exists(dest_path) and os.path.getsize(dest_path) > 0
        except Exception as e:
            safe_print(f"{Colors.RED}❌ Screen record failed: {e}{Colors.RESET}")
            return False

    def push_file(self, serial: str, local_path: str, remote_path: str) -> Tuple[bool, str]:
        """Push a file to device"""
        try:
            res = self.run(["-s", serial, "push", local_path, remote_path], check=True, timeout=120)
            return True, res.stdout.strip()
        except Exception as e:
            return False, str(e)

    def pull_file(self, serial: str, remote_path: str, local_path: str) -> Tuple[bool, str]:
        """Pull a file from device"""
        try:
            res = self.run(["-s", serial, "pull", remote_path, local_path], check=True, timeout=120)
            return True, res.stdout.strip()
        except Exception as e:
            return False, str(e)

    def list_packages(self, serial: str, system: bool = False, filter_kw: Optional[str] = None) -> List[str]:
        """List installed packages with optional filtering"""
        cmd = ["-s", serial, "shell", "pm", "list", "packages"]
        if system:
            cmd.append("-s")
        else:
            cmd.append("-3")  # 3rd party user apps by default
        
        try:
            res = self.run(cmd, timeout=15)
            pkgs = []
            for line in res.stdout.strip().split("\n"):
                if line.startswith("package:"):
                    pkg = line.replace("package:", "").strip()
                    if filter_kw:
                        if filter_kw.lower() in pkg.lower():
                            pkgs.append(pkg)
                    else:
                        pkgs.append(pkg)
            return sorted(pkgs)
        except Exception:
            return []

    def reboot(self, serial: str, mode: Optional[str] = None) -> bool:
        """Reboot device (normal, bootloader, recovery)"""
        cmd = ["-s", serial, "reboot"]
        if mode:
            cmd.append(mode)
        try:
            self.run(cmd, check=True, timeout=15)
            return True
        except Exception:
            return False


class WirelessADBManager:
    """Core Manager Orchestrating Profiles, Connections, and CLI Workflows"""

    PORT_MIN = 30000
    PORT_MAX = 50000
    CONFIG_DIR = Path.home() / ".wireless_adb"
    CONFIG_FILE = CONFIG_DIR / "profiles.json"
    PID_FILE = CONFIG_DIR / "watcher.pid"

    def __init__(self, verbose: bool = False, quiet: bool = False):
        self.verbose = verbose
        self.quiet = quiet
        self.log_level = LogLevel.VERBOSE if verbose else (LogLevel.QUIET if quiet else LogLevel.NORMAL)
        self.adb = ADBWrapper(verbose=verbose)
        self.CONFIG_DIR.mkdir(parents=True, exist_ok=True)

    def log(self, msg: str, level: LogLevel = LogLevel.NORMAL, color: str = Colors.WHITE) -> None:
        if self.log_level.value >= level.value:
            safe_print(f"{color}{msg}{Colors.RESET}")

    def generate_port(self) -> int:
        """Generate an available dynamic high TCP port"""
        for _ in range(50):
            port = random.randint(self.PORT_MIN, self.PORT_MAX)
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(0.1)
                    if s.connect_ex(("127.0.0.1", port)) != 0:
                        return port
            except Exception:
                return port
        return random.randint(self.PORT_MIN, self.PORT_MAX)

    def _save_profile(self, profile: DeviceProfile) -> None:
        try:
            profiles = self._load_all_profiles()
            profiles[profile.serial] = asdict(profile)
            with open(self.CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(profiles, f, indent=2)
        except Exception as e:
            if self.verbose:
                safe_print(f"{Colors.YELLOW}[WARN] Could not save profile: {e}{Colors.RESET}")

    def _load_all_profiles(self) -> Dict[str, Any]:
        if not self.CONFIG_FILE.exists():
            return {}
        try:
            with open(self.CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

    def get_host_ip(self) -> Optional[str]:
        """Detect local host IPv4 address"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.settimeout(0.5)
                s.connect(("8.8.8.8", 80))
                return s.getsockname()[0]
        except Exception:
            try:
                host = socket.gethostname()
                ip = socket.gethostbyname(host)
                if not ip.startswith("127."):
                    return ip
            except Exception:
                pass
        return None

    def check_subnet(self, device_ip: str) -> bool:
        host_ip = self.get_host_ip()
        if host_ip and device_ip:
            try:
                d_net = ipaddress.ip_network(f"{device_ip}/24", strict=False)
                h_net = ipaddress.ip_network(f"{host_ip}/24", strict=False)
                if d_net != h_net:
                    self.log(f"{Colors.YELLOW}⚠️  Subnet Warning: Device is on {device_ip} but Host is on {host_ip}!{Colors.RESET}")
                    self.log(f"   Ensure both device and host are connected to the same Wi-Fi SSID / VLAN.")
                    return False
            except Exception:
                pass
        return True

    def _get_active_target(self, target: Optional[str] = None) -> Optional[str]:
        """Resolve target device or auto-select active wireless/USB device"""
        if target:
            return target
        devices = self.adb.get_devices()
        wireless = [d["serial"] for d in devices if d["is_wireless"] and d["state"] == "device"]
        if wireless:
            return wireless[0]
        usb = [d["serial"] for d in devices if not d["is_wireless"] and d["state"] == "device"]
        if usb:
            return usb[0]
        return None

    # ─────────────────────────────────────────────────────────────
    # Command Implementations
    # ─────────────────────────────────────────────────────────────

    def connect(self, custom_port: Optional[int] = None) -> bool:
        """Automatic USB-to-Wireless handshake flow"""
        safe_print(UI.banner())
        self.log(f"{Colors.NEON_CYAN}▶ Step 1/5:{Colors.RESET} Detecting USB-connected Android devices...")
        
        all_devs = self.adb.get_devices()
        devices = [d for d in all_devs if not d["is_wireless"] and d["state"] == "device"]
        unauthorized = [d for d in all_devs if d["state"] == "unauthorized"]

        if unauthorized:
            self.log(f"\n{Colors.RED}❌ Device Unauthorized:{Colors.RESET} Check your phone screen and tap 'Always allow from this computer'.\n")
            return False

        if not devices:
            self.log(f"\n{Colors.RED}❌ No USB-Connected Android Devices Found!{Colors.RESET}")
            safe_print(UI.box("Troubleshooting Checklist", [
                "1. Connect phone to PC using a USB data cable.",
                "2. Enable Developer Options -> USB Debugging on phone.",
                "3. Unlock phone and approve the 'Allow USB Debugging' RSA prompt.",
                "4. For zero-wire Wi-Fi pairing (Android 11+), run: wireless-adb pair",
            ], Colors.YELLOW))
            return False

        # Select Device
        if len(devices) > 1:
            self.log(f"{Colors.NEON_GREEN}Found {len(devices)} USB devices:{Colors.RESET}")
            for idx, d in enumerate(devices, 1):
                name = self.adb.get_device_name(d["serial"])
                safe_print(f"  [{Colors.BOLD}{idx}{Colors.RESET}] {name} ({Colors.DARK_GRAY}{d['serial']}{Colors.RESET})")
            try:
                choice = int(input(f"\n{Colors.BOLD}Select device [1-{len(devices)}]: {Colors.RESET}"))
                if choice < 1 or choice > len(devices):
                    safe_print(f"{Colors.RED}  Choice must be between 1 and {len(devices)}.{Colors.RESET}")
                    return False
                selected = devices[choice - 1]
            except Exception:
                self.log(f"{Colors.RED}Invalid selection. Aborted.{Colors.RESET}")
                return False
        else:
            selected = devices[0]

        serial = selected["serial"]
        dev_name = self.adb.get_device_name(serial)
        android_ver = self.adb.get_android_version(serial)
        self.log(f"  {Colors.NEON_GREEN}✔ Selected:{Colors.RESET} {Colors.BOLD}{dev_name}{Colors.RESET} ({android_ver}) [{serial}]")

        # Step 2: Get IP
        self.log(f"\n{Colors.NEON_CYAN}▶ Step 2/5:{Colors.RESET} Querying device Wi-Fi IPv4 address...")
        device_ip = self.adb.get_device_ip(serial)
        if not device_ip:
            self.log(f"{Colors.RED}❌ Could not detect Wi-Fi IP address!{Colors.RESET}")
            self.log(f"   Make sure Wi-Fi is active and connected on your Android device.")
            return False

        self.log(f"  {Colors.NEON_GREEN}✔ Device IP:{Colors.RESET} {Colors.BOLD}{device_ip}{Colors.RESET}")
        self.check_subnet(device_ip)

        # Step 3: Choose Port
        port = custom_port if custom_port else self.generate_port()
        self.log(f"\n{Colors.NEON_CYAN}▶ Step 3/5:{Colors.RESET} Assigning secure port: {Colors.NEON_PURPLE}{port}{Colors.RESET} (Range {self.PORT_MIN}-{self.PORT_MAX})")

        # Step 4: TCP/IP
        self.log(f"\n{Colors.NEON_CYAN}▶ Step 4/5:{Colors.RESET} Switching device into TCP/IP mode on port {port}...")
        if not self.adb.enable_tcpip(serial, port):
            self.log(f"{Colors.RED}❌ Failed to enable TCP/IP mode on device.{Colors.RESET}")
            self.log(f"   Ensure USB debugging remains allowed on your device.")
            return False
        self.log(f"  {Colors.NEON_GREEN}✔ TCP/IP Mode Active{Colors.RESET}")

        # Step 5: Connect
        target_endpoint = f"{device_ip}:{port}"
        self.log(f"\n{Colors.NEON_CYAN}▶ Step 5/5:{Colors.RESET} Establishing wireless handshake to {target_endpoint}...")
        if not self.adb.connect_wireless(device_ip, port):
            self.log(f"{Colors.RED}❌ Wireless connection handshake failed.{Colors.RESET}")
            self.log(f"   Check router AP client isolation and PC firewall settings.")
            return False

        # Save profile
        bat = self.adb.get_battery_info(serial)
        prof = DeviceProfile(
            serial=target_endpoint,
            ip=device_ip,
            port=port,
            last_connected=time.time(),
            device_name=dev_name,
            android_version=android_ver,
            battery_level=bat.get("level", "Unknown")
        )
        self._save_profile(prof)

        # Success Card
        safe_print("\n" + UI.box("🎉 WIRELESS ADB CONNECTED SUCCESSFULLY", [
            f"Device       : {dev_name} ({android_ver})",
            f"Target       : {target_endpoint}",
            f"Battery      : {bat.get('level')} ({bat.get('status')})",
            f"Status       : {UI.status_tag(True)}",
            "",
            f"✨ {Colors.BOLD}You can now UNPLUG your USB cable!{Colors.RESET}",
            f"💡 Run '{Colors.NEON_CYAN}wireless-adb status{Colors.RESET}' or '{Colors.NEON_CYAN}wireless-adb mirror{Colors.RESET}' anytime."
        ], Colors.NEON_GREEN))
        safe_print()
        return True

    def pair(self, endpoint: Optional[str] = None, code: Optional[str] = None) -> bool:
        """Android 11+ Zero-Cable Wi-Fi Pairing Flow"""
        safe_print(UI.banner())
        safe_print(UI.box("📱 ANDROID 11+ WIRELESS PAIRING (NO CABLE NEEDED)", [
            "1. On phone: Go to Developer Options -> Wireless Debugging.",
            "2. Turn on 'Wireless Debugging'.",
            "3. Tap 'Pair device with pairing code'.",
            "4. Enter the Wi-Fi pairing IP:port and 6-digit code shown on screen."
        ], Colors.NEON_PURPLE))
        safe_print()

        if not endpoint:
            endpoint = input(f"{Colors.BOLD}Enter Pairing IP & Port (e.g. 192.168.1.15:38472): {Colors.RESET}").strip()
        if not code:
            code = input(f"{Colors.BOLD}Enter 6-Digit Pairing Code: {Colors.RESET}").strip()

        if not endpoint or not code:
            self.log(f"{Colors.RED}Pairing endpoint and code are required.{Colors.RESET}")
            return False

        self.log(f"\n{Colors.NEON_CYAN}▶ Pairing with {endpoint}...{Colors.RESET}")
        if self.adb.pair_wireless(endpoint, code):
            self.log(f"{Colors.NEON_GREEN}✔ Pairing Successful!{Colors.RESET}")
            
            # Extract IP and prompt for the actual connection port
            ip = endpoint.split(":")[0]
            conn_port = input(f"\n{Colors.BOLD}Enter the main Wireless Debugging Port from phone screen: {Colors.RESET}").strip()
            if conn_port:
                try:
                    port = int(conn_port)
                except ValueError:
                    safe_print(f"{Colors.RED}  [ERROR] Invalid port number: {conn_port}{Colors.RESET}")
                    return False
                self.log(f"Connecting to {ip}:{port}...")
                if self.adb.connect_wireless(ip, port):
                    dev_name = self.adb.get_device_name(f"{ip}:{port}")
                    self.log(f"{Colors.NEON_GREEN}✔ Connected wirelessly to {dev_name} ({ip}:{port})!{Colors.RESET}")
                    self._save_profile(DeviceProfile(
                        serial=f"{ip}:{port}",
                        ip=ip,
                        port=port,
                        last_connected=time.time(),
                        device_name=dev_name
                    ))
                    return True
                else:
                    self.log(f"{Colors.RED}❌ Connection to {ip}:{port} failed.{Colors.RESET}")
                    return False
            return True
        else:
            self.log(f"{Colors.RED}❌ Pairing failed. Ensure the 6-digit dialog is still open on phone and retry.{Colors.RESET}")
            return False

    def status(self) -> bool:
        """Rich interactive status dashboard with telemetry"""
        safe_print(UI.banner())
        devices = self.adb.get_devices()
        
        usb_devs = [d for d in devices if not d["is_wireless"]]
        wifi_devs = [d for d in devices if d["is_wireless"]]

        lines = []
        lines.append(f"{Colors.BOLD}ACTIVE WIRELESS SESSIONS ({len(wifi_devs)}){Colors.RESET}")
        if wifi_devs:
            for d in wifi_devs:
                serial = d["serial"]
                name = self.adb.get_device_name(serial)
                bat = self.adb.get_battery_info(serial)
                ip = serial.split(":")[0] if ":" in serial else serial
                ping = self.adb.ping_device(ip)
                ping_str = f"{ping:.1f}ms latency" if ping is not None else "ping N/A"
                lines.append(f"  {Colors.NEON_GREEN}●{Colors.RESET} {Colors.BOLD}{name}{Colors.RESET} ➔ {Colors.NEON_CYAN}{serial}{Colors.RESET}")
                lines.append(f"    ├─ Battery : {bat.get('level')} ({bat.get('status')}) | Temp: {bat.get('temp')}")
                lines.append(f"    └─ Network : {ping_str} | State: {d['state']}")
        else:
            lines.append(f"  {Colors.DARK_GRAY}No wireless devices currently connected.{Colors.RESET}")

        lines.append("")
        lines.append(f"{Colors.BOLD}PHYSICAL USB DEVICES ({len(usb_devs)}){Colors.RESET}")
        if usb_devs:
            for d in usb_devs:
                name = self.adb.get_device_name(d["serial"])
                bat = self.adb.get_battery_info(d["serial"])
                lines.append(f"  {Colors.YELLOW}🔌{Colors.RESET} {Colors.BOLD}{name}{Colors.RESET} [{d['serial']}] - State: {d['state']} | Battery: {bat.get('level')}")
        else:
            lines.append(f"  {Colors.DARK_GRAY}No USB devices connected.{Colors.RESET}")

        profiles = self._load_all_profiles()
        if profiles:
            lines.append("")
            lines.append(f"{Colors.BOLD}SAVED DEVICE PROFILES ({len(profiles)}){Colors.RESET}")
            for s, data in list(profiles.items())[-4:]:
                last_t = time.strftime("%Y-%m-%d %H:%M", time.localtime(data.get("last_connected", 0)))
                alias_tag = f" [{data.get('alias')}]" if data.get("alias") else ""
                lines.append(f"  ⭐ {data.get('device_name', 'Android')}{alias_tag} ({data.get('ip')}:{data.get('port')}) — Last seen {last_t}")

        safe_print(UI.box("📊 WIRELESS ADB LIVE DASHBOARD", lines, Colors.NEON_CYAN))
        safe_print()
        return True

    def info(self, target: Optional[str] = None, json_export: bool = False) -> bool:
        """Deep hardware and network telemetry for target device"""
        devices = self.adb.get_devices()
        if not devices:
            self.log(f"{Colors.RED}No connected devices found. Run 'wireless-adb connect' first.{Colors.RESET}")
            return False

        serial = target or devices[0]["serial"]
        dev_name = self.adb.get_device_name(serial)
        android_ver = self.adb.get_android_version(serial)
        bat = self.adb.get_battery_info(serial)
        wifi = self.adb.get_wifi_telemetry(serial)
        ip = self.adb.get_device_ip(serial) or (serial.split(":")[0] if ":" in serial else "Unknown")
        ping = self.adb.ping_device(ip) if ip != "Unknown" else None

        cpu_abi = self.adb.run(["-s", serial, "shell", "getprop", "ro.product.cpu.abi"]).stdout.strip()
        screen_size = self.adb.run(["-s", serial, "shell", "wm", "size"]).stdout.strip().replace("Physical size: ", "")
        screen_density = self.adb.run(["-s", serial, "shell", "wm", "density"]).stdout.strip().replace("Physical density: ", "")

        telemetry_data = {
            "device_name": dev_name,
            "serial": serial,
            "android_version": android_ver,
            "cpu_abi": cpu_abi,
            "display": f"{screen_size} ({screen_density} dpi)",
            "battery": bat,
            "wifi": {
                "ip": ip,
                "ssid": wifi.get("ssid"),
                "link_speed": wifi.get("link_speed"),
                "rssi": wifi.get("rssi"),
                "ping_ms": ping
            }
        }

        if json_export:
            safe_print(json.dumps(telemetry_data, indent=2))
            return True

        lines = [
            f"{Colors.BOLD}HARDWARE SPECS{Colors.RESET}",
            f"  Model          : {dev_name}",
            f"  Serial/Target  : {serial}",
            f"  OS Version     : {android_ver}",
            f"  CPU ABI        : {cpu_abi}",
            f"  Display        : {screen_size} ({screen_density} dpi)",
            "",
            f"{Colors.BOLD}BATTERY & POWER{Colors.RESET}",
            f"  Charge Level   : {bat.get('level')} ({bat.get('status')})",
            f"  Temperature    : {bat.get('temp')}",
            "",
            f"{Colors.BOLD}NETWORK TELEMETRY{Colors.RESET}",
            f"  Wi-Fi IP       : {ip}",
            f"  Connected SSID : {wifi.get('ssid')}",
            f"  Link Speed     : {wifi.get('link_speed')}",
            f"  Signal RSSI    : {wifi.get('rssi')}",
            f"  Ping Latency   : {f'{ping:.1f} ms' if ping is not None else 'N/A'}",
        ]
        safe_print(UI.box(f"🔍 DEVICE TELEMETRY: {dev_name}", lines, Colors.NEON_GREEN))
        return True

    def reconnect(self, alias_or_serial: Optional[str] = None) -> bool:
        """Reconnect to last known profile or specific alias/endpoint"""
        profiles = self._load_all_profiles()
        if not profiles:
            self.log(f"{Colors.RED}❌ No saved profiles found! Connect once via USB first.{Colors.RESET}")
            return False

        target_data = None
        if alias_or_serial:
            # Check by key or alias
            for k, p in profiles.items():
                if k == alias_or_serial or p.get("alias") == alias_or_serial or p.get("ip") == alias_or_serial:
                    target_data = p
                    break

        if not target_data:
            latest_key = max(profiles.keys(), key=lambda k: profiles[k].get("last_connected", 0))
            target_data = profiles[latest_key]

        dev_name = target_data.get("device_name", "Android Device")
        ip = target_data["ip"]
        port = target_data["port"]

        self.log(f"\n{Colors.NEON_CYAN}⚡ Reconnecting to {dev_name} at {ip}:{port}...{Colors.RESET}")
        if self.adb.connect_wireless(ip, port):
            self.log(f"{Colors.NEON_GREEN}✔ Reconnected successfully!{Colors.RESET}")
            target_data["last_connected"] = time.time()
            self._save_profile(DeviceProfile.from_dict(target_data))
            return True
        else:
            self.log(f"{Colors.RED}❌ Reconnection failed.{Colors.RESET}")
            self.log(f"   Device Wi-Fi IP may have changed. Re-run '{Colors.NEON_CYAN}wireless-adb connect{Colors.RESET}' with USB.")
            return False

    def disconnect_all(self, reset_usb: bool = True) -> bool:
        """Disconnect all wireless devices safely"""
        self.log(f"\n{Colors.NEON_CYAN}🔌 Disconnecting wireless ADB sessions...{Colors.RESET}")
        devices = self.adb.get_devices()
        wireless_devs = [d["serial"] for d in devices if d["is_wireless"]]
        usb_devs = [d["serial"] for d in devices if not d["is_wireless"]]

        for target in wireless_devs:
            self.adb.disconnect(target)
            self.log(f"  {Colors.NEON_GREEN}✔ Disconnected:{Colors.RESET} {target}")

        if not wireless_devs:
            self.adb.disconnect()
            self.log(f"  {Colors.NEON_GREEN}✔ Cleared all remote endpoints.{Colors.RESET}")

        if reset_usb and usb_devs:
            for s in usb_devs:
                self.adb.usb_mode(s)
                self.log(f"  {Colors.NEON_GREEN}✔ Reset {s} back to USB mode.{Colors.RESET}")

        self.log(f"{Colors.NEON_GREEN}✨ All sessions cleaned up safely.{Colors.RESET}\n")
        return True

    def scan_network(self) -> bool:
        """Scan local mDNS and subnet for active ADB instances"""
        safe_print(UI.banner())
        self.log(f"{Colors.NEON_CYAN}🔍 Scanning local network and mDNS for Android ADB services...{Colors.RESET}\n")
        
        mdns_services = self.adb.discover_mdns()
        if mdns_services:
            lines = [f"{Colors.BOLD}DISCOVERED MDNS ADB SERVICES{Colors.RESET}"]
            for s in mdns_services:
                lines.append(f"  📡 {s['name']} - {s['service']} ({s['addr']})")
            safe_print(UI.box("MDNS Discovery Results", lines, Colors.NEON_PURPLE))
            safe_print()
        else:
            self.log(f"  {Colors.DARK_GRAY}No mDNS ADB services broadcasting.{Colors.RESET}")

        # Subnet probe on common ADB ports with proper socket closure
        host_ip = self.get_host_ip()
        if host_ip:
            base_ip = ".".join(host_ip.split(".")[:3])
            self.log(f"  Scanning local subnet {base_ip}.1/24 (timeout 0.04s per port)...")
            found = []
            for i in range(1, 255):
                target_ip = f"{base_ip}.{i}"
                if target_ip == host_ip:
                    continue
                s = None
                try:
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.settimeout(0.04)
                    if s.connect_ex((target_ip, 5555)) == 0:
                        found.append(f"{target_ip}:5555")
                except Exception:
                    pass
                finally:
                    if s:
                        s.close()

            if found:
                safe_print(UI.box("Subnet Port 5555 Matches", [f"  🎯 Found open ADB on {addr}" for addr in found], Colors.NEON_GREEN))
            else:
                self.log(f"  {Colors.NEON_GREEN}✔ No insecure port 5555 instances exposed on local subnet.{Colors.RESET}")

        return True

    def mirror(self, target: Optional[str] = None) -> bool:
        """Launch ultra-low-latency scrcpy screen mirror"""
        scrcpy = shutil.which("scrcpy")
        if not scrcpy:
            self.log(f"{Colors.RED}❌ 'scrcpy' not found in PATH!{Colors.RESET}")
            self.log(f"   Install scrcpy from https://github.com/Genymobile/scrcpy to enable mirroring.")
            return False

        serial = self._get_active_target(target)
        if not serial:
            self.log(f"{Colors.RED}No active devices available for mirroring. Run 'wireless-adb connect' first.{Colors.RESET}")
            return False

        self.log(f"{Colors.NEON_GREEN}🚀 Launching scrcpy mirror for {serial}...{Colors.RESET}")
        cmd = [scrcpy, "-s", serial, "--max-fps", "60", "--video-bit-rate", "8M", "--stay-awake"]
        try:
            creationflags = 0
            if sys.platform == "win32":
                creationflags = subprocess.CREATE_NEW_PROCESS_GROUP
            subprocess.Popen(cmd, creationflags=creationflags)
            return True
        except Exception as e:
            self.log(f"{Colors.RED}Failed to launch scrcpy: {e}{Colors.RESET}")
            return False

    def interactive_shell(self, target: Optional[str] = None) -> bool:
        """Open interactive wireless shell"""
        serial = self._get_active_target(target)
        if not serial:
            self.log(f"{Colors.RED}No active device found. Connect a device first.{Colors.RESET}")
            return False
        
        self.log(f"{Colors.NEON_GREEN}⚡ Opening interactive wireless shell on {serial}...{Colors.RESET}\n")
        subprocess.run([self.adb.adb_path, "-s", serial, "shell"])
        return True

    def install_apk(self, apk_path: str, target: Optional[str] = None) -> bool:
        """Install APK wirelessly"""
        if not os.path.exists(apk_path):
            self.log(f"{Colors.RED}❌ File not found: {apk_path}{Colors.RESET}")
            return False
        
        serial = self._get_active_target(target)
        if not serial:
            self.log(f"{Colors.RED}No active device found. Connect a device first.{Colors.RESET}")
            return False

        self.log(f"{Colors.NEON_CYAN}📦 Installing {os.path.basename(apk_path)} on {serial}...{Colors.RESET}")
        res = self.adb.run(["-s", serial, "install", "-r", apk_path], timeout=120)
        if "Success" in res.stdout:
            self.log(f"{Colors.NEON_GREEN}✔ APK installed successfully!{Colors.RESET}")
            return True
        else:
            self.log(f"{Colors.RED}❌ Installation failed: {res.stdout.strip()}{Colors.RESET}")
            return False

    # ─────────────────────────────────────────────────────────────
    # NEW V4.0 FEATURES
    # ─────────────────────────────────────────────────────────────

    def screenshot(self, output_path: Optional[str] = None, target: Optional[str] = None) -> bool:
        """📸 Capture screenshot from connected Android device"""
        serial = self._get_active_target(target)
        if not serial:
            self.log(f"{Colors.RED}❌ No active device found. Connect a device first.{Colors.RESET}")
            return False

        if not output_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"screenshot_{timestamp}.png"

        self.log(f"{Colors.NEON_CYAN}📸 Capturing screen from {serial}...{Colors.RESET}")
        if self.adb.take_screenshot(serial, output_path):
            abs_path = os.path.abspath(output_path)
            self.log(f"{Colors.NEON_GREEN}✔ Screenshot saved to: {Colors.BOLD}{abs_path}{Colors.RESET}")
            return True
        else:
            self.log(f"{Colors.RED}❌ Failed to capture screenshot.{Colors.RESET}")
            return False

    def record(self, output_path: Optional[str] = None, duration: int = 15, target: Optional[str] = None) -> bool:
        """🎥 Record screen video from device"""
        serial = self._get_active_target(target)
        if not serial:
            self.log(f"{Colors.RED}❌ No active device found.{Colors.RESET}")
            return False

        if not output_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"screenrecord_{timestamp}.mp4"

        if self.adb.record_screen(serial, output_path, duration_sec=duration):
            abs_path = os.path.abspath(output_path)
            self.log(f"{Colors.NEON_GREEN}✔ Screen recording saved to: {Colors.BOLD}{abs_path}{Colors.RESET}")
            return True
        return False

    def push(self, local_path: str, remote_path: str, target: Optional[str] = None) -> bool:
        """📂 Push file to device"""
        if not os.path.exists(local_path):
            self.log(f"{Colors.RED}❌ Local file not found: {local_path}{Colors.RESET}")
            return False

        serial = self._get_active_target(target)
        if not serial:
            self.log(f"{Colors.RED}❌ No active device found.{Colors.RESET}")
            return False

        self.log(f"{Colors.NEON_CYAN}⬆ Pushing {local_path} ➔ {remote_path}...{Colors.RESET}")
        ok, msg = self.adb.push_file(serial, local_path, remote_path)
        if ok:
            self.log(f"{Colors.NEON_GREEN}✔ File pushed successfully!{Colors.RESET}")
            return True
        else:
            self.log(f"{Colors.RED}❌ Push failed: {msg}{Colors.RESET}")
            return False

    def pull(self, remote_path: str, local_path: Optional[str] = None, target: Optional[str] = None) -> bool:
        """📂 Pull file from device"""
        if not local_path:
            local_path = os.path.basename(remote_path.rstrip("/")) or "pulled_file"

        serial = self._get_active_target(target)
        if not serial:
            self.log(f"{Colors.RED}❌ No active device found.{Colors.RESET}")
            return False

        self.log(f"{Colors.NEON_CYAN}⬇ Pulling {remote_path} ➔ {local_path}...{Colors.RESET}")
        ok, msg = self.adb.pull_file(serial, remote_path, local_path)
        if ok:
            self.log(f"{Colors.NEON_GREEN}✔ File pulled successfully to {os.path.abspath(local_path)}!{Colors.RESET}")
            return True
        else:
            self.log(f"{Colors.RED}❌ Pull failed: {msg}{Colors.RESET}")
            return False

    def apps(self, system: bool = False, filter_kw: Optional[str] = None, target: Optional[str] = None) -> bool:
        """📱 List installed applications"""
        serial = self._get_active_target(target)
        if not serial:
            self.log(f"{Colors.RED}❌ No active device found.{Colors.RESET}")
            return False

        app_type = "System & 3rd-Party" if system else "3rd-Party User"
        self.log(f"{Colors.NEON_CYAN}📱 Fetching {app_type} apps from {serial}...{Colors.RESET}")
        pkgs = self.adb.list_packages(serial, system=system, filter_kw=filter_kw)
        
        if not pkgs:
            self.log(f"{Colors.YELLOW}No packages found matching criteria.{Colors.RESET}")
            return True

        lines = [f"{Colors.BOLD}INSTALLED PACKAGES ({len(pkgs)}){Colors.RESET}"]
        for p in pkgs[:40]:
            lines.append(f"  📦 {p}")
        if len(pkgs) > 40:
            lines.append(f"  {Colors.DARK_GRAY}... and {len(pkgs) - 40} more packages.{Colors.RESET}")

        safe_print(UI.box(f"📱 APPS: {serial}", lines, Colors.NEON_CYAN))
        return True

    def logcat(self, tag: Optional[str] = None, save_file: Optional[str] = None, target: Optional[str] = None) -> bool:
        """📋 Stream live logcat logs"""
        serial = self._get_active_target(target)
        if not serial:
            self.log(f"{Colors.RED}❌ No active device found.{Colors.RESET}")
            return False

        cmd = [self.adb.adb_path, "-s", serial, "logcat", "-v", "time"]
        if tag:
            cmd.extend(["-s", f"{tag}:*"])

        self.log(f"{Colors.NEON_GREEN}📋 Streaming live logcat on {serial} (Ctrl+C to stop)...{Colors.RESET}\n")
        try:
            if save_file:
                with open(save_file, "w", encoding="utf-8") as f:
                    safe_print(f"Logging to file: {save_file}")
                    proc = subprocess.Popen(cmd, stdout=f, stderr=subprocess.STDOUT)
                    proc.wait()
            else:
                subprocess.run(cmd)
        except KeyboardInterrupt:
            safe_print(f"\n{Colors.YELLOW}Logcat stream stopped.{Colors.RESET}")
        return True

    def reboot_device(self, mode: Optional[str] = None, target: Optional[str] = None) -> bool:
        """🔄 Reboot connected device"""
        serial = self._get_active_target(target)
        if not serial:
            self.log(f"{Colors.RED}❌ No active device found.{Colors.RESET}")
            return False

        mode_str = mode if mode else "system"
        confirm = input(f"{Colors.YELLOW}Are you sure you want to reboot {serial} into '{mode_str}'? [y/N]: {Colors.RESET}").strip().lower()
        if confirm != "y":
            self.log("Reboot cancelled.")
            return False

        self.log(f"{Colors.NEON_CYAN}🔄 Rebooting {serial} ({mode_str})...{Colors.RESET}")
        if self.adb.reboot(serial, mode=mode):
            self.log(f"{Colors.NEON_GREEN}✔ Reboot signal sent successfully.{Colors.RESET}")
            return True
        else:
            self.log(f"{Colors.RED}❌ Reboot command failed.{Colors.RESET}")
            return False

    def favorites(self, alias: Optional[str] = None, target: Optional[str] = None, delete: Optional[str] = None) -> bool:
        """⭐ Manage saved profiles & aliases"""
        profiles = self._load_all_profiles()
        
        if delete:
            if delete in profiles:
                del profiles[delete]
                with open(self.CONFIG_FILE, "w", encoding="utf-8") as f:
                    json.dump(profiles, f, indent=2)
                self.log(f"{Colors.NEON_GREEN}✔ Deleted profile for {delete}{Colors.RESET}")
                return True
            else:
                self.log(f"{Colors.RED}❌ Profile {delete} not found.{Colors.RESET}")
                return False

        if alias and target:
            if target in profiles:
                profiles[target]["alias"] = alias
                with open(self.CONFIG_FILE, "w", encoding="utf-8") as f:
                    json.dump(profiles, f, indent=2)
                self.log(f"{Colors.NEON_GREEN}✔ Assigned alias '{alias}' to {target}{Colors.RESET}")
                return True
            else:
                self.log(f"{Colors.RED}❌ Target {target} not found in saved profiles.{Colors.RESET}")
                return False

        # List all favorites
        safe_print(UI.banner())
        if not profiles:
            self.log(f"{Colors.DARK_GRAY}No saved profiles. Connect a device to create one.{Colors.RESET}")
            return True

        lines = [f"{Colors.BOLD}SAVED DEVICE FAVORITES ({len(profiles)}){Colors.RESET}"]
        for key, p in profiles.items():
            alias_tag = f" [Alias: {Colors.NEON_PURPLE}{p.get('alias')}{Colors.RESET}]" if p.get("alias") else ""
            last_t = time.strftime("%Y-%m-%d %H:%M", time.localtime(p.get("last_connected", 0)))
            lines.append(f"  ⭐ {Colors.BOLD}{p.get('device_name', 'Android')}{Colors.RESET}{alias_tag}")
            lines.append(f"     └─ Endpoint: {p.get('ip')}:{p.get('port')} | Last: {last_t}")
        
        safe_print(UI.box("⭐ DEVICE PROFILES & FAVORITES", lines, Colors.NEON_PURPLE))
        return True

    def doctor(self) -> bool:
        """Pre-flight comprehensive environment diagnostics"""
        safe_print(UI.banner())
        lines = []
        
        # 1. Python Check
        py_ver = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        lines.append(f"✔ Python Version       : {py_ver} ({sys.executable})")

        # 2. ADB Check
        adb_ok, adb_msg = self.adb.verify()
        if adb_ok:
            lines.append(f"✔ ADB Binary           : {adb_msg} ({self.adb.adb_path})")
        else:
            lines.append(f"❌ ADB Binary          : NOT FOUND or FAILING ({adb_msg})")

        # 3. Host Network
        host_ip = self.get_host_ip()
        lines.append(f"✔ Host IP Address      : {host_ip or 'Offline'}")

        # 4. scrcpy check
        scrcpy = shutil.which("scrcpy")
        if scrcpy:
            lines.append(f"✔ scrcpy Mirroring     : Installed ({scrcpy})")
        else:
            lines.append(f"○ scrcpy Mirroring     : Not found (optional, recommended for screen mirror)")

        # 5. Connected Devices
        devs = self.adb.get_devices()
        lines.append(f"✔ Detected Devices     : {len(devs)} attached ({sum(1 for d in devs if d['is_wireless'])} wireless)")

        # 6. Profile Store
        profiles = self._load_all_profiles()
        lines.append(f"✔ Saved Profiles       : {len(profiles)} registered in ~/.wireless_adb/profiles.json")

        safe_print(UI.box("🩺 SYSTEM & ENVIRONMENT DIAGNOSTICS", lines, Colors.NEON_CYAN))
        safe_print()
        return True

    def watch_daemon(self, interval: int = 5) -> None:
        """Continuous auto-reconnect watcher daemon with singleton lock"""
        safe_print(UI.banner())
        
        # Singleton check
        try:
            if self.PID_FILE.exists():
                try:
                    old_pid = int(self.PID_FILE.read_text().strip())
                    if sys.platform == "win32":
                        # Windows process check
                        res = subprocess.run(["tasklist", "/FI", f"PID eq {old_pid}"], capture_output=True, text=True)
                        if str(old_pid) in res.stdout:
                            safe_print(f"{Colors.YELLOW}⚠️ Watcher daemon is already running (PID {old_pid}).{Colors.RESET}")
                            return
                    else:
                        os.kill(old_pid, 0)
                        safe_print(f"{Colors.YELLOW}⚠️ Watcher daemon is already running (PID {old_pid}).{Colors.RESET}")
                        return
                except Exception:
                    pass
            self.PID_FILE.write_text(str(os.getpid()))
        except Exception:
            pass

        self.log(f"{Colors.NEON_CYAN}👁️ WirelessADB Watcher Daemon Started (Polling every {interval}s)...{Colors.RESET}")
        self.log(f"   Press Ctrl+C to terminate.\n")

        try:
            while True:
                try:
                    devices = self.adb.get_devices()
                    wireless_active = any(d["is_wireless"] and d["state"] == "device" for d in devices)
                    
                    if not wireless_active:
                        profiles = self._load_all_profiles()
                        if profiles:
                            latest = max(profiles.keys(), key=lambda k: profiles[k].get("last_connected", 0))
                            p = profiles[latest]
                            t_now = time.strftime("%H:%M:%S")
                            safe_print(f"[{t_now}] {Colors.YELLOW}⚡ Connection dropped. Reconnecting to {p.get('device_name')} ({p['ip']}:{p['port']})...{Colors.RESET}")
                            if self.adb.connect_wireless(p["ip"], p["port"]):
                                safe_print(f"[{t_now}] {Colors.NEON_GREEN}✔ Restored connection to {p.get('device_name')}!{Colors.RESET}")
                    time.sleep(interval)
                except KeyboardInterrupt:
                    raise
                except Exception as e:
                    safe_print(f"\r  [!] Watch error: {e}", end='', flush=True)
                    time.sleep(interval)
        except KeyboardInterrupt:
            self.log(f"\n{Colors.YELLOW}Watcher daemon stopped.{Colors.RESET}")
        finally:
            try:
                if self.PID_FILE.exists():
                    self.PID_FILE.unlink()
            except Exception:
                pass

    def interactive_menu(self) -> None:
        """Interactive Terminal Menu for one-touch navigation"""
        while True:
            safe_print(UI.banner())
            devices = self.adb.get_devices()
            w_count = sum(1 for d in devices if d["is_wireless"])
            u_count = sum(1 for d in devices if not d["is_wireless"])
            
            status_summary = f"{Colors.NEON_GREEN}{w_count} Wireless{Colors.RESET} | {Colors.YELLOW}{u_count} USB{Colors.RESET}"
            
            menu_lines = [
                f"Status: {status_summary}",
                "",
                f"  [{Colors.BOLD}1{Colors.RESET}] ⚡ Connect USB Device to Wireless (Auto High-Port)",
                f"  [{Colors.BOLD}2{Colors.RESET}] 📱 Pair via Android 11+ Wi-Fi (No Cable Needed)",
                f"  [{Colors.BOLD}3{Colors.RESET}] 📊 Live Status Dashboard & Latency HUD",
                f"  [{Colors.BOLD}4{Colors.RESET}] 🔄 Quick Reconnect to Last Device",
                f"  [{Colors.BOLD}5{Colors.RESET}] 🔍 Deep Device Telemetry (Battery, CPU, Wi-Fi)",
                f"  [{Colors.BOLD}6{Colors.RESET}] 📸 Capture Device Screenshot",
                f"  [{Colors.BOLD}7{Colors.RESET}] 🎥 Record Device Screen Video",
                f"  [{Colors.BOLD}8{Colors.RESET}] 🚀 Launch scrcpy 60FPS Screen Mirror",
                f"  [{Colors.BOLD}9{Colors.RESET}] 💻 Open Wireless Terminal Shell",
                f"  [{Colors.BOLD}A{Colors.RESET}] 📦 Install APK Wireless",
                f"  [{Colors.BOLD}B{Colors.RESET}] 📂 Push / Pull File Transfer",
                f"  [{Colors.BOLD}C{Colors.RESET}] 📱 List Installed Apps & Packages",
                f"  [{Colors.BOLD}D{Colors.RESET}] 📋 Live Logcat Streamer",
                f"  [{Colors.BOLD}E{Colors.RESET}] 📡 Scan Network for ADB Devices",
                f"  [{Colors.BOLD}F{Colors.RESET}] ⭐ Manage Device Favorites & Aliases",
                f"  [{Colors.BOLD}G{Colors.RESET}] 🔄 Reboot Device (System / Bootloader / Recovery)",
                f"  [{Colors.BOLD}H{Colors.RESET}] 🩺 Run Doctor Health Diagnostics",
                f"  [{Colors.BOLD}0{Colors.RESET}] 🔌 Disconnect & Clean Up All Sessions",
                f"  [{Colors.BOLD}q{Colors.RESET}] 🚪 Quit"
            ]
            safe_print(UI.box("⚡ WIRELESS ADB CONTROL CENTER", menu_lines, Colors.NEON_CYAN))
            
            choice = input(f"\n{Colors.BOLD}Select an action [0-9, A-H, q]: {Colors.RESET}").strip().lower()
            if choice == '1':
                self.connect()
            elif choice == '2':
                self.pair()
            elif choice == '3':
                self.status()
            elif choice == '4':
                self.reconnect()
            elif choice == '5':
                self.info()
            elif choice == '6':
                self.screenshot()
            elif choice == '7':
                self.record()
            elif choice == '8':
                self.mirror()
            elif choice == '9':
                self.interactive_shell()
            elif choice == 'a':
                apk = input(f"{Colors.BOLD}Enter APK file path: {Colors.RESET}").strip()
                if apk:
                    self.install_apk(apk)
            elif choice == 'b':
                mode = input(f"{Colors.BOLD}Transfer mode - [1] Push to device, [2] Pull from device: {Colors.RESET}").strip()
                if mode == '1':
                    loc = input(f"Local file path: ").strip()
                    rem = input(f"Remote destination path (e.g. /sdcard/): ").strip()
                    if loc and rem:
                        self.push(loc, rem)
                elif mode == '2':
                    rem = input(f"Remote file path on device: ").strip()
                    loc = input(f"Local destination path (optional): ").strip()
                    if rem:
                        self.pull(rem, loc if loc else None)
            elif choice == 'c':
                kw = input(f"{Colors.BOLD}Filter by keyword (press Enter for all): {Colors.RESET}").strip()
                self.apps(filter_kw=kw if kw else None)
            elif choice == 'd':
                tag = input(f"{Colors.BOLD}Filter by tag (press Enter for all): {Colors.RESET}").strip()
                self.logcat(tag=tag if tag else None)
            elif choice == 'e':
                self.scan_network()
            elif choice == 'f':
                self.favorites()
            elif choice == 'g':
                m = input(f"{Colors.BOLD}Reboot mode - [1] Normal, [2] Bootloader, [3] Recovery: {Colors.RESET}").strip()
                mode_map = {"1": None, "2": "bootloader", "3": "recovery"}
                if m in mode_map:
                    self.reboot_device(mode=mode_map[m])
            elif choice == 'h':
                self.doctor()
            elif choice == '0':
                self.disconnect_all()
            elif choice in ('q', 'exit'):
                self.log(f"{Colors.NEON_GREEN}Stay fast. Happy debugging! 🚀{Colors.RESET}\n")
                break
            else:
                self.log(f"{Colors.RED}Invalid option.{Colors.RESET}")
            
            input(f"\n{Colors.DARK_GRAY}Press Enter to return to menu...{Colors.RESET}")


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="wireless-adb",
        description="⚡ WirelessADB - Next-Gen Secure Wireless ADB Connection & Telemetry Suite",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Quick Examples:
  wireless-adb                   Launch interactive control center menu
  wireless-adb connect           Auto-switch USB device to secure wireless port
  wireless-adb pair              Android 11+ zero-wire Wi-Fi pairing
  wireless-adb reconnect         Instantly reconnect to last active device
  wireless-adb screenshot        Capture device screenshot to PNG
  wireless-adb record            Record screen video from device
  wireless-adb mirror            One-click low-latency scrcpy screen mirroring
  wireless-adb apps              List installed user applications
  wireless-adb push <src> <dst>  Push file to device
  wireless-adb pull <src> [dst]  Pull file from device
  wireless-adb status            Display live telemetry and battery meters
  wireless-adb doctor            Run pre-flight environment checks
  wireless-adb disconnect        Safely tear down all wireless sessions
        """
    )

    parser.add_argument(
        "command",
        nargs="?",
        default="menu",
        choices=[
            "menu", "ui", "connect", "pair", "status", "info",
            "reconnect", "disconnect", "scan", "mirror", "shell",
            "install", "doctor", "watch", "screenshot", "record",
            "push", "pull", "apps", "logcat", "reboot", "favorites"
        ],
        help="Command to execute (default: interactive menu)"
    )

    # General Options
    parser.add_argument("-p", "--port", type=int, help="Specify custom TCP port")
    parser.add_argument("-s", "--serial", type=str, help="Target specific device serial or IP")
    parser.add_argument("-f", "--file", type=str, help="File path for install/screenshot/push/pull")
    parser.add_argument("-o", "--output", type=str, help="Output destination path")
    parser.add_argument("--remote", type=str, help="Remote path on device")
    parser.add_argument("--system", action="store_true", help="Include system packages in apps list")
    parser.add_argument("--filter", type=str, help="Filter keyword for apps/logcat")
    parser.add_argument("--tag", type=str, help="Logcat tag filter")
    parser.add_argument("--time", type=int, default=15, help="Duration in seconds for screen record")
    parser.add_argument("--bootloader", action="store_true", help="Reboot into bootloader")
    parser.add_argument("--recovery", action="store_true", help="Reboot into recovery")
    parser.add_argument("--alias", type=str, help="Set alias for device in favorites")
    parser.add_argument("--delete", type=str, help="Delete profile in favorites")
    parser.add_argument("--json", action="store_true", help="Export output as JSON (where supported)")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose debug logs")
    parser.add_argument("-q", "--quiet", action="store_true", help="Suppress non-essential logs")
    parser.add_argument("--no-color", action="store_true", help="Disable ANSI color codes")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")

    args, unknown = parser.parse_known_args()

    if args.no_color:
        Colors.disable()

    manager = WirelessADBManager(verbose=args.verbose, quiet=args.quiet)

    try:
        cmd = args.command
        if cmd in ("menu", "ui"):
            manager.interactive_menu()
        elif cmd == "connect":
            manager.connect(custom_port=args.port)
        elif cmd == "pair":
            manager.pair()
        elif cmd == "status":
            manager.status()
        elif cmd == "info":
            manager.info(target=args.serial, json_export=args.json)
        elif cmd == "reconnect":
            manager.reconnect(alias_or_serial=args.serial)
        elif cmd == "disconnect":
            manager.disconnect_all()
        elif cmd == "scan":
            manager.scan_network()
        elif cmd == "mirror":
            manager.mirror(target=args.serial)
        elif cmd == "shell":
            manager.interactive_shell(target=args.serial)
        elif cmd == "screenshot":
            out = args.output or args.file
            manager.screenshot(output_path=out, target=args.serial)
        elif cmd == "record":
            out = args.output or args.file
            manager.record(output_path=out, duration=args.time, target=args.serial)
        elif cmd == "push":
            src = args.file or (unknown[0] if len(unknown) > 0 else None)
            dst = args.remote or args.output or (unknown[1] if len(unknown) > 1 else None)
            if not src or not dst:
                safe_print(f"{Colors.RED}Usage: wireless-adb push <local_path> <remote_path>{Colors.RESET}")
            else:
                manager.push(src, dst, target=args.serial)
        elif cmd == "pull":
            src = args.remote or args.file or (unknown[0] if len(unknown) > 0 else None)
            dst = args.output or (unknown[1] if len(unknown) > 1 else None)
            if not src:
                safe_print(f"{Colors.RED}Usage: wireless-adb pull <remote_path> [local_path]{Colors.RESET}")
            else:
                manager.pull(src, dst, target=args.serial)
        elif cmd == "apps":
            manager.apps(system=args.system, filter_kw=args.filter, target=args.serial)
        elif cmd == "logcat":
            manager.logcat(tag=args.tag or args.filter, save_file=args.output, target=args.serial)
        elif cmd == "reboot":
            mode = "bootloader" if args.bootloader else ("recovery" if args.recovery else None)
            manager.reboot_device(mode=mode, target=args.serial)
        elif cmd == "favorites":
            manager.favorites(alias=args.alias, target=args.serial, delete=args.delete)
        elif cmd == "install":
            apk = args.file or (unknown[0] if len(unknown) > 0 else None)
            if not apk:
                apk = input(f"{Colors.BOLD}Enter APK file path: {Colors.RESET}").strip()
            manager.install_apk(apk, target=args.serial)
        elif cmd == "doctor":
            manager.doctor()
        elif cmd == "watch":
            manager.watch_daemon()

    except KeyboardInterrupt:
        safe_print(f"\n{Colors.YELLOW}⚡ Operation aborted by user.{Colors.RESET}")
        sys.exit(130)
    except Exception as e:
        safe_print(f"\n{Colors.RED}❌ Unexpected error: {e}{Colors.RESET}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
