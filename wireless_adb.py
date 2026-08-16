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
from pathlib import Path
from typing import Optional, Tuple, Dict, List, Any
from dataclasses import dataclass, asdict
from enum import Enum

# Version Info
__version__ = "3.2.0"
__tool_name__ = "WirelessADB"

# Ensure UTF-8 output encoding across Windows / Linux / macOS
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

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
    ITALIC = "\033[3m"
    UNDERLINE = "\033[4m"
    BLINK = "\033[5m"
    REVERSE = "\033[7m"

    # Foreground Neon Palette
    BLACK = "\033[30m"
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
    BG_RED = "\033[48;5;52m"
    BG_BLUE = "\033[48;5;17m"

    @classmethod
    def disable(cls):
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


class UI:
    """ASCII art, banners, tables, and stylized visual output"""

    @staticmethod
    def banner():
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
        width = max([len(title) + 4] + [len(re.sub(r'\033\[[0-9;]*m', '', l)) for l in lines] + [50])
        border_top = f"{color}╭─ {Colors.BOLD}{title}{Colors.RESET}{color} " + "─" * (width - len(title) - 3) + f"╮{Colors.RESET}"
        border_bot = f"{color}╰" + "─" * (width) + f"╯{Colors.RESET}"
        
        output = [border_top]
        for line in lines:
            plain_len = len(re.sub(r'\033\[[0-9;]*m', '', line))
            padding = " " * (width - plain_len - 2)
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
        search_paths = [
            os.path.expandvars(r"%LOCALAPPDATA%\Android\Sdk\platform-tools\adb.exe"),
            r"C:\platform-tools\adb.exe",
            r"C:\Android\platform-tools\adb.exe",
            os.path.expanduser("~/Library/Android/sdk/platform-tools/adb"),
            os.path.expanduser("~/Android/Sdk/platform-tools/adb"),
            "/usr/bin/adb",
            "/usr/local/bin/adb",
        ]
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
        """Execute ADB subprocess command"""
        full_cmd = [self.adb_path] + cmd
        if self.verbose:
            print(f"{Colors.DARK_GRAY}[EXEC] {' '.join(full_cmd)}{Colors.RESET}")

        try:
            result = subprocess.run(
                full_cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                check=check
            )
            if self.verbose and result.stdout.strip():
                print(f"{Colors.DARK_GRAY}[STDOUT] {result.stdout.strip()}{Colors.RESET}")
            return result
        except subprocess.TimeoutExpired:
            if self.verbose:
                print(f"{Colors.RED}[TIMEOUT] Command timed out after {timeout}s: {' '.join(full_cmd)}{Colors.RESET}")
            raise
        except subprocess.CalledProcessError as e:
            if self.verbose:
                print(f"{Colors.RED}[STDERR] {e.stderr.strip()}{Colors.RESET}")
            raise

    def get_devices(self) -> List[Dict[str, str]]:
        """Fetch all connected devices with serial, type and state"""
        res = self.run(["devices", "-l"])
        devices = []
        for line in res.stdout.strip().split("\n")[1:]:
            line = line.strip()
            if not line:
                continue
            parts = line.split()
            if len(parts) >= 2:
                serial = parts[0]
                state = parts[1]
                is_wireless = ":" in serial
                
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
        # Strategy 1: wlan0 ip addr show
        res = self.run(["-s", serial, "shell", "ip", "addr", "show", "wlan0"])
        match = re.search(r'inet\s+(\d+\.\d+\.\d+\.\d+)', res.stdout)
        if match:
            ip = match.group(1)
            if not ip.startswith("127."):
                return ip

        # Strategy 2: ip route get 8.8.8.8
        res = self.run(["-s", serial, "shell", "ip", "route", "get", "8.8.8.8"])
        match = re.search(r'src\s+(\d+\.\d+\.\d+\.\d+)', res.stdout)
        if match:
            return match.group(1)

        # Strategy 3: ifconfig wlan0
        res = self.run(["-s", serial, "shell", "ifconfig", "wlan0"])
        match = re.search(r'inet addr:(\d+\.\d+\.\d+\.\d+)', res.stdout)
        if match:
            return match.group(1)

        # Strategy 4: getprop dhcp.wlan0.ipaddress
        res = self.run(["-s", serial, "shell", "getprop", "dhcp.wlan0.ipaddress"])
        ip = res.stdout.strip()
        if re.match(r'^\d+\.\d+\.\d+\.\d+$', ip):
            return ip

        return None

    def get_device_name(self, serial: str) -> str:
        """Fetch model & manufacturer name"""
        res_m = self.run(["-s", serial, "shell", "getprop", "ro.product.manufacturer"])
        res_n = self.run(["-s", serial, "shell", "getprop", "ro.product.model"])
        man = res_m.stdout.strip().title()
        mod = res_n.stdout.strip()
        if man and mod and not mod.lower().startswith(man.lower()):
            return f"{man} {mod}"
        return mod or man or "Android Device"

    def get_android_version(self, serial: str) -> str:
        """Fetch Android OS release version"""
        res = self.run(["-s", serial, "shell", "getprop", "ro.build.version.release"])
        sdk = self.run(["-s", serial, "shell", "getprop", "ro.build.version.sdk"])
        ver = res.stdout.strip()
        sdk_ver = sdk.stdout.strip()
        if ver and sdk_ver:
            return f"Android {ver} (API {sdk_ver})"
        return ver or "Android"

    def get_battery_info(self, serial: str) -> Dict[str, Any]:
        """Fetch battery percentage, charging state, temperature"""
        res = self.run(["-s", serial, "shell", "dumpsys", "battery"])
        data = {"level": "Unknown", "status": "Unknown", "temp": "Unknown", "health": "Good"}
        for line in res.stdout.strip().split("\n"):
            line = line.strip()
            if line.startswith("level:"):
                data["level"] = f"{line.split(':')[1].strip()}%"
            elif line.startswith("status:"):
                val = line.split(':')[1].strip()
                statuses = {"1": "Unknown", "2": "Charging ⚡", "3": "Discharging 🔋", "4": "Not charging", "5": "Full 🟢"}
                data["status"] = statuses.get(val, "Active")
            elif line.startswith("temperature:"):
                try:
                    temp_c = float(line.split(':')[1].strip()) / 10.0
                    data["temp"] = f"{temp_c:.1f}°C"
                except Exception:
                    pass
        return data

    def get_wifi_telemetry(self, serial: str) -> Dict[str, str]:
        """Retrieve Wi-Fi link speed, RSSI and SSID"""
        res = self.run(["-s", serial, "shell", "dumpsys", "wifi"])
        telemetry = {"ssid": "Unknown", "link_speed": "Unknown", "rssi": "Unknown"}
        
        ssid_match = re.search(r'SSID:\s*"?([^",\n]+)"?', res.stdout)
        if ssid_match:
            telemetry["ssid"] = ssid_match.group(1)

        speed_match = re.search(r'Link speed:\s*(\d+Mbps)', res.stdout, re.IGNORECASE)
        if speed_match:
            telemetry["link_speed"] = speed_match.group(1)

        rssi_match = re.search(r'RSSI:\s*(-?\d+)', res.stdout)
        if rssi_match:
            telemetry["rssi"] = f"{rssi_match.group(1)} dBm"

        return telemetry

    def ping_device(self, ip: str, count: int = 2) -> Optional[float]:
        """Measure roundtrip network ping latency to device"""
        try:
            if sys.platform == "win32":
                cmd = ["ping", "-n", str(count), "-w", "1000", ip]
            else:
                cmd = ["ping", "-c", str(count), "-W", "1", ip]
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=3)
            # Parse average latency
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
            self.run(["-s", serial, "tcpip", str(port)], check=True)
            time.sleep(1.5)
            return True
        except subprocess.CalledProcessError:
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
                self.run(["disconnect", target], check=True)
            else:
                self.run(["disconnect"], check=True)
            return True
        except Exception:
            return False

    def usb_mode(self, serial: str) -> bool:
        """Reset device back to USB mode"""
        try:
            self.run(["-s", serial, "usb"], check=True)
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


class WirelessADBManager:
    """Core Manager Orchestrating Profiles, Connections, and CLI Workflows"""

    PORT_MIN = 30000
    PORT_MAX = 50000
    CONFIG_DIR = Path.home() / ".wireless_adb"
    CONFIG_FILE = CONFIG_DIR / "profiles.json"

    def __init__(self, verbose: bool = False, quiet: bool = False):
        self.verbose = verbose
        self.quiet = quiet
        self.log_level = LogLevel.VERBOSE if verbose else (LogLevel.QUIET if quiet else LogLevel.NORMAL)
        self.adb = ADBWrapper(verbose=verbose)
        self.CONFIG_DIR.mkdir(parents=True, exist_ok=True)

    def log(self, msg: str, level: LogLevel = LogLevel.NORMAL, color: str = Colors.WHITE):
        if self.log_level.value >= level.value:
            print(f"{color}{msg}{Colors.RESET}")

    def generate_port(self) -> int:
        return random.randint(self.PORT_MIN, self.PORT_MAX)

    def _save_profile(self, profile: DeviceProfile) -> None:
        try:
            profiles = self._load_all_profiles()
            profiles[profile.serial] = asdict(profile)
            with open(self.CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(profiles, f, indent=2)
        except Exception as e:
            if self.verbose:
                print(f"{Colors.YELLOW}[WARN] Could not save profile: {e}{Colors.RESET}")

    def _load_all_profiles(self) -> Dict[str, Any]:
        if not self.CONFIG_FILE.exists():
            return {}
        try:
            with open(self.CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

    def get_host_ip(self) -> Optional[str]:
        """Detect local host IP address"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.settimeout(0.5)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return None

    def check_subnet(self, device_ip: str) -> bool:
        host_ip = self.get_host_ip()
        if host_ip and device_ip:
            try:
                d_net = ipaddress.ip_network(f"{device_ip}/24", strict=False)
                h_net = ipaddress.ip_network(f"{host_ip}/24", strict=False)
                if d_net != h_net:
                    self.log(f"{Colors.YELLOW}⚠️  Subnet Mismatch: Device is on {device_ip} but Host is on {host_ip}!{Colors.RESET}")
                    self.log(f"   Ensure both device and host are connected to the same Wi-Fi SSID / VLAN.")
                    return False
            except Exception:
                pass
        return True

    # ─────────────────────────────────────────────────────────────
    # Command Implementations
    # ─────────────────────────────────────────────────────────────

    def connect(self, custom_port: Optional[int] = None) -> bool:
        """Automatic USB-to-Wireless handshake flow"""
        print(UI.banner())
        self.log(f"{Colors.NEON_CYAN}▶ Step 1/5:{Colors.RESET} Detecting USB-connected Android devices...")
        
        devices = [d for d in self.adb.get_devices() if not d["is_wireless"] and d["state"] == "device"]
        unauthorized = [d for d in self.adb.get_devices() if d["state"] == "unauthorized"]

        if unauthorized:
            self.log(f"\n{Colors.RED}❌ Device Unauthorized:{Colors.RESET} Check your phone screen and tap 'Always allow from this computer'.\n")
            return False

        if not devices:
            self.log(f"\n{Colors.RED}❌ No USB-Connected Android Devices Found!{Colors.RESET}")
            print(UI.box("Troubleshooting Checklist", [
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
                print(f"  [{Colors.BOLD}{idx}{Colors.RESET}] {name} ({Colors.DARK_GRAY}{d['serial']}{Colors.RESET})")
            try:
                choice = int(input(f"\n{Colors.BOLD}Select device [1-{len(devices)}]: {Colors.RESET}"))
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
            return False
        self.log(f"  {Colors.NEON_GREEN}✔ TCP/IP Mode Active{Colors.RESET}")

        # Step 5: Connect
        self.log(f"\n{Colors.NEON_CYAN}▶ Step 5/5:{Colors.RESET} Establishing wireless handshake to {device_ip}:{port}...")
        if not self.adb.connect_wireless(device_ip, port):
            self.log(f"{Colors.RED}❌ Wireless connection handshake failed.{Colors.RESET}")
            self.log(f"   Check your router's AP client isolation and PC firewall settings.")
            return False

        # Save profile
        bat = self.adb.get_battery_info(serial)
        prof = DeviceProfile(
            serial=serial,
            ip=device_ip,
            port=port,
            last_connected=time.time(),
            device_name=dev_name,
            android_version=android_ver,
            battery_level=bat.get("level", "Unknown")
        )
        self._save_profile(prof)

        # Success Card
        print("\n" + UI.box("🎉 WIRELESS ADB CONNECTED SUCCESSFULLY", [
            f"Device       : {dev_name} ({android_ver})",
            f"Target       : {device_ip}:{port}",
            f"Battery      : {bat.get('level')} ({bat.get('status')})",
            f"Status       : {UI.status_tag(True)}",
            "",
            f"✨ {Colors.BOLD}You can now UNPLUG your USB cable!{Colors.RESET}",
            f"💡 Run '{Colors.NEON_CYAN}wireless-adb status{Colors.RESET}' or '{Colors.NEON_CYAN}wireless-adb mirror{Colors.RESET}' anytime."
        ], Colors.NEON_GREEN))
        print()
        return True

    def pair(self, endpoint: Optional[str] = None, code: Optional[str] = None) -> bool:
        """Android 11+ Zero-Cable Wi-Fi Pairing Flow"""
        print(UI.banner())
        print(UI.box("📱 ANDROID 11+ WIRELESS PAIRING (NO CABLE NEEDED)", [
            "1. On phone: Go to Developer Options -> Wireless Debugging.",
            "2. Turn on 'Wireless Debugging'.",
            "3. Tap 'Pair device with pairing code'.",
            "4. Enter the Wi-Fi pairing IP:port and 6-digit code shown on screen."
        ], Colors.NEON_PURPLE))
        print()

        if not endpoint:
            endpoint = input(f"{Colors.BOLD}Enter Pairing IP & Port (e.g. 192.168.1.15:38472): {Colors.RESET}").strip()
        if not code:
            code = input(f"{Colors.BOLD}Enter 6-Digit Pairing Code: {Colors.RESET}").strip()

        if not endpoint or not code:
            self.log(f"{Colors.RED}Pairing endpoint and code are required.{Colors.RESET}")
            return False

        self.log(f"\n{Colors.NEON_CYAN}▶ Pairing with {endpoint} using code {code}...{Colors.RESET}")
        if self.adb.pair_wireless(endpoint, code):
            self.log(f"{Colors.NEON_GREEN}✔ Pairing Successful!{Colors.RESET}")
            
            # Extract IP and prompt for the actual connection port (often different in Android 11)
            ip = endpoint.split(":")[0]
            conn_port = input(f"\n{Colors.BOLD}Enter the main Wireless Debugging Port from phone screen: {Colors.RESET}").strip()
            if conn_port:
                port = int(conn_port)
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
            return True
        else:
            self.log(f"{Colors.RED}❌ Pairing failed. Ensure the 6-digit dialog is still open on phone and retry.{Colors.RESET}")
            return False

    def status(self) -> bool:
        """Rich interactive status dashboard with telemetry"""
        print(UI.banner())
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
                lines.append(f"  ⭐ {data.get('device_name', 'Android')} ({data.get('ip')}:{data.get('port')}) — Last seen {last_t}")

        print(UI.box("📊 WIRELESS ADB LIVE DASHBOARD", lines, Colors.NEON_CYAN))
        print()
        return True

    def info(self, target: Optional[str] = None) -> bool:
        """Deep hardware and network telemetry for target device"""
        devices = self.adb.get_devices()
        if not devices:
            self.log(f"{Colors.RED}No connected devices found.{Colors.RESET}")
            return False

        serial = target or devices[0]["serial"]
        dev_name = self.adb.get_device_name(serial)
        android_ver = self.adb.get_android_version(serial)
        bat = self.adb.get_battery_info(serial)
        wifi = self.adb.get_wifi_telemetry(serial)
        ip = self.adb.get_device_ip(serial) or (serial.split(":")[0] if ":" in serial else "Unknown")
        ping = self.adb.ping_device(ip) if ip != "Unknown" else None

        # Fetch extra specs
        cpu_abi = self.adb.run(["-s", serial, "shell", "getprop", "ro.product.cpu.abi"]).stdout.strip()
        screen_size = self.adb.run(["-s", serial, "shell", "wm", "size"]).stdout.strip().replace("Physical size: ", "")
        screen_density = self.adb.run(["-s", serial, "shell", "wm", "density"]).stdout.strip().replace("Physical density: ", "")

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
        print(UI.box(f"🔍 DEVICE TELEMETRY: {dev_name}", lines, Colors.NEON_GREEN))
        return True

    def reconnect(self, alias_or_serial: Optional[str] = None) -> bool:
        """Reconnect to last known profile or specific device"""
        profiles = self._load_all_profiles()
        if not profiles:
            self.log(f"{Colors.RED}❌ No saved profiles found! Connect once via USB first.{Colors.RESET}")
            return False

        if alias_or_serial and alias_or_serial in profiles:
            target_data = profiles[alias_or_serial]
        else:
            # Latest
            latest_serial = max(profiles.keys(), key=lambda k: profiles[k].get("last_connected", 0))
            target_data = profiles[latest_serial]

        dev_name = target_data.get("device_name", "Android Device")
        ip = target_data["ip"]
        port = target_data["port"]

        self.log(f"\n{Colors.NEON_CYAN}⚡ Reconnecting to {dev_name} at {ip}:{port}...{Colors.RESET}")
        if self.adb.connect_wireless(ip, port):
            self.log(f"{Colors.NEON_GREEN}✔ Reconnected successfully!{Colors.RESET}")
            target_data["last_connected"] = time.time()
            self._save_profile(DeviceProfile(**target_data))
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
        print(UI.banner())
        self.log(f"{Colors.NEON_CYAN}🔍 Scanning local network and mDNS for Android ADB services...{Colors.RESET}\n")
        
        mdns_services = self.adb.discover_mdns()
        if mdns_services:
            lines = [f"{Colors.BOLD}DISCOVERED MDNS ADB SERVICES{Colors.RESET}"]
            for s in mdns_services:
                lines.append(f"  📡 {s['name']} - {s['service']} ({s['addr']})")
            print(UI.box("MDNS Discovery Results", lines, Colors.NEON_PURPLE))
            print()
        else:
            self.log(f"  {Colors.DARK_GRAY}No mDNS ADB services broadcasting.{Colors.RESET}")

        # Quick subnet probe on common ADB ports
        host_ip = self.get_host_ip()
        if host_ip:
            base_ip = ".".join(host_ip.split(".")[:3])
            self.log(f"  Scanning local subnet {base_ip}.1/24 (timeout 0.2s)...")
            found = []
            for i in range(1, 255):
                target_ip = f"{base_ip}.{i}"
                if target_ip == host_ip:
                    continue
                # Try socket connect on 5555
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(0.04)
                if s.connect_ex((target_ip, 5555)) == 0:
                    found.append(f"{target_ip}:5555")
                s.close()

            if found:
                print(UI.box("Subnet Port 5555 Matches", [f"  🎯 Found open ADB on {addr}" for addr in found], Colors.NEON_GREEN))
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

        devices = self.adb.get_devices()
        wireless_devs = [d["serial"] for d in devices if d["is_wireless"]]
        serial = target or (wireless_devs[0] if wireless_devs else (devices[0]["serial"] if devices else None))

        if not serial:
            self.log(f"{Colors.RED}No active devices available for mirroring.{Colors.RESET}")
            return False

        self.log(f"{Colors.NEON_GREEN}🚀 Launching scrcpy mirror for {serial}...{Colors.RESET}")
        cmd = [scrcpy, "-s", serial, "--max-fps", "60", "--video-bit-rate", "8M", "--stay-awake"]
        try:
            subprocess.Popen(cmd)
            return True
        except Exception as e:
            self.log(f"{Colors.RED}Failed to launch scrcpy: {e}{Colors.RESET}")
            return False

    def interactive_shell(self, target: Optional[str] = None) -> bool:
        """Open interactive wireless shell"""
        devices = self.adb.get_devices()
        serial = target or (devices[0]["serial"] if devices else None)
        if not serial:
            self.log(f"{Colors.RED}No active device found.{Colors.RESET}")
            return False
        
        self.log(f"{Colors.NEON_GREEN}⚡ Opening interactive wireless shell on {serial}...{Colors.RESET}\n")
        subprocess.run([self.adb.adb_path, "-s", serial, "shell"])
        return True

    def install_apk(self, apk_path: str, target: Optional[str] = None) -> bool:
        """Install APK wirelessly"""
        if not os.path.exists(apk_path):
            self.log(f"{Colors.RED}❌ File not found: {apk_path}{Colors.RESET}")
            return False
        
        devices = self.adb.get_devices()
        serial = target or (devices[0]["serial"] if devices else None)
        if not serial:
            self.log(f"{Colors.RED}No active device found.{Colors.RESET}")
            return False

        self.log(f"{Colors.NEON_CYAN}📦 Installing {os.path.basename(apk_path)} on {serial}...{Colors.RESET}")
        res = self.adb.run(["-s", serial, "install", "-r", apk_path], timeout=120)
        if "Success" in res.stdout:
            self.log(f"{Colors.NEON_GREEN}✔ APK installed successfully!{Colors.RESET}")
            return True
        else:
            self.log(f"{Colors.RED}❌ Installation failed: {res.stdout.strip()}{Colors.RESET}")
            return False

    def doctor(self) -> bool:
        """Pre-flight comprehensive environment diagnostics"""
        print(UI.banner())
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
            lines.append(f"○ scrcpy Mirroring     : Not found (optional, recommended)")

        # 5. Connected Devices
        devs = self.adb.get_devices()
        lines.append(f"✔ Detected Devices     : {len(devs)} attached ({sum(1 for d in devs if d['is_wireless'])} wireless)")

        # 6. Profile Store
        profiles = self._load_all_profiles()
        lines.append(f"✔ Saved Profiles       : {len(profiles)} registered in ~/.wireless_adb/profiles.json")

        print(UI.box("🩺 SYSTEM & ENVIRONMENT DIAGNOSTICS", lines, Colors.NEON_CYAN))
        print()
        return True

    def watch_daemon(self, interval: int = 5) -> None:
        """Continuous auto-reconnect watcher daemon"""
        print(UI.banner())
        self.log(f"{Colors.NEON_CYAN}👁️ WirelessADB Watcher Daemon Started (Polling every {interval}s)...{Colors.RESET}")
        self.log(f"   Press Ctrl+C to terminate.\n")

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
                        print(f"[{t_now}] {Colors.YELLOW}⚡ Connection dropped. Attempting auto-reconnect to {p['device_name']} ({p['ip']}:{p['port']})...{Colors.RESET}")
                        if self.adb.connect_wireless(p["ip"], p["port"]):
                            print(f"[{t_now}] {Colors.NEON_GREEN}✔ Restored connection to {p['device_name']}!{Colors.RESET}")
                time.sleep(interval)
            except KeyboardInterrupt:
                self.log(f"\n{Colors.YELLOW}Watcher daemon stopped.{Colors.RESET}")
                break
            except Exception as e:
                time.sleep(interval)

    def interactive_menu(self) -> None:
        """Interactive Terminal Menu for one-touch navigation"""
        while True:
            print(UI.banner())
            devices = self.adb.get_devices()
            w_count = sum(1 for d in devices if d["is_wireless"])
            u_count = sum(1 for d in devices if not d["is_wireless"])
            
            status_summary = f"{Colors.NEON_GREEN}{w_count} Wireless{Colors.RESET} | {Colors.YELLOW}{u_count} USB{Colors.RESET}"
            
            menu_lines = [
                f"Status: {status_summary}",
                "",
                f"  [{Colors.BOLD}1{Colors.RESET}] ⚡ Connect USB Device to Wireless (Auto High-Port)",
                f"  [{Colors.BOLD}2{Colors.RESET}] 📱 Pair via Android 11+ Wi-Fi (No Cable Needed)",
                f"  [{Colors.BOLD}3{Colors.RESET}] 📊 Show Live Status Dashboard & Latency",
                f"  [{Colors.BOLD}4{Colors.RESET}] 🔄 Quick Reconnect to Last Device",
                f"  [{Colors.BOLD}5{Colors.RESET}] 🔍 Deep Device Telemetry (Battery, CPU, Wi-Fi)",
                f"  [{Colors.BOLD}6{Colors.RESET}] 🚀 Launch scrcpy Screen Mirror",
                f"  [{Colors.BOLD}7{Colors.RESET}] 💻 Open Wireless Terminal Shell",
                f"  [{Colors.BOLD}8{Colors.RESET}] 📡 Scan Network for ADB Devices",
                f"  [{Colors.BOLD}9{Colors.RESET}] 🩺 Run Doctor Health Diagnostics",
                f"  [{Colors.BOLD}0{Colors.RESET}] 🔌 Disconnect & Clean Up All Sessions",
                f"  [{Colors.BOLD}q{Colors.RESET}] 🚪 Quit"
            ]
            print(UI.box("⚡ WIRELESS ADB CONTROL CENTER", menu_lines, Colors.NEON_CYAN))
            
            choice = input(f"\n{Colors.BOLD}Select an action [0-9, q]: {Colors.RESET}").strip().lower()
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
                self.mirror()
            elif choice == '7':
                self.interactive_shell()
            elif choice == '8':
                self.scan_network()
            elif choice == '9':
                self.doctor()
            elif choice == '0':
                self.disconnect_all()
            elif choice in ('q', 'exit'):
                self.log(f"{Colors.NEON_GREEN}Stay fast. Happy debugging! 🚀{Colors.RESET}\n")
                break
            else:
                self.log(f"{Colors.RED}Invalid option.{Colors.RESET}")
            
            input(f"\n{Colors.DARK_GRAY}Press Enter to return to menu...{Colors.RESET}")


def main():
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
  wireless-adb mirror            One-click low-latency scrcpy screen mirroring
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
            "install", "doctor", "watch"
        ],
        help="Command to execute (default: interactive menu)"
    )

    parser.add_argument("-p", "--port", type=int, help="Specify custom TCP port")
    parser.add_argument("-s", "--serial", type=str, help="Target specific device serial or IP")
    parser.add_argument("-f", "--file", type=str, help="APK file path for install command")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose debug logs")
    parser.add_argument("-q", "--quiet", action="store_true", help="Suppress non-essential logs")
    parser.add_argument("--no-color", action="store_true", help="Disable ANSI color codes")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")

    args = parser.parse_args()

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
            manager.info(target=args.serial)
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
        elif cmd == "install":
            if not args.file:
                apk = input(f"{Colors.BOLD}Enter APK file path: {Colors.RESET}").strip()
            else:
                apk = args.file
            manager.install_apk(apk, target=args.serial)
        elif cmd == "doctor":
            manager.doctor()
        elif cmd == "watch":
            manager.watch_daemon()

    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}⚡ Operation aborted by user.{Colors.RESET}")
        sys.exit(130)
    except Exception as e:
        print(f"\n{Colors.RED}❌ Unexpected error: {e}{Colors.RESET}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
