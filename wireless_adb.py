#!/usr/bin/env python3
"""
WirelessADB - Secure Wireless ADB Connection Manager
A production-grade tool for managing wireless ADB connections with enhanced security.

Author: Built for ethical Android development
License: MIT
"""

import subprocess
import sys
import re
import random
import time
import ipaddress
import json
import os
from pathlib import Path
from typing import Optional, Tuple, Dict, List
from dataclasses import dataclass
from enum import Enum

# Color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

    @staticmethod
    def disable_colors():
        """Disable colors for Windows CMD compatibility"""
        Colors.HEADER = ''
        Colors.OKBLUE = ''
        Colors.OKCYAN = ''
        Colors.OKGREEN = ''
        Colors.WARNING = ''
        Colors.FAIL = ''
        Colors.ENDC = ''
        Colors.BOLD = ''
        Colors.UNDERLINE = ''


class LogLevel(Enum):
    QUIET = 0
    NORMAL = 1
    VERBOSE = 2


@dataclass
class DeviceProfile:
    """Stores device connection information"""
    serial: str
    ip: str
    port: int
    last_connected: float
    device_name: str = "Unknown"


class ADBWrapper:
    """Low-level ADB command wrapper with error handling"""
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self._verify_adb()
    
    def _verify_adb(self) -> None:
        """Verify ADB is installed and accessible"""
        try:
            result = self.run_command(['adb', 'version'], check=True)
            if self.verbose:
                print(f"{Colors.OKCYAN}[DEBUG] ADB Version: {result.stdout.strip()}{Colors.ENDC}")
        except FileNotFoundError:
            print(f"{Colors.FAIL}[ERROR] ADB not found in PATH{Colors.ENDC}")
            print(f"{Colors.WARNING}Install ADB from: https://developer.android.com/studio/releases/platform-tools{Colors.ENDC}")
            sys.exit(1)
        except subprocess.CalledProcessError as e:
            print(f"{Colors.FAIL}[ERROR] ADB verification failed: {e}{Colors.ENDC}")
            sys.exit(1)
    
    def run_command(self, cmd: List[str], check: bool = False, timeout: int = 30) -> subprocess.CompletedProcess:
        """Execute ADB command with error handling"""
        if self.verbose:
            print(f"{Colors.OKCYAN}[DEBUG] Running: {' '.join(cmd)}{Colors.ENDC}")
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                check=check
            )
            
            if self.verbose and result.stdout:
                print(f"{Colors.OKCYAN}[DEBUG] Output: {result.stdout.strip()}{Colors.ENDC}")
            
            return result
        
        except subprocess.TimeoutExpired:
            print(f"{Colors.FAIL}[ERROR] Command timed out after {timeout}s{Colors.ENDC}")
            raise
        except subprocess.CalledProcessError as e:
            if self.verbose:
                print(f"{Colors.FAIL}[DEBUG] Command failed: {e.stderr}{Colors.ENDC}")
            raise
    
    def get_devices(self) -> List[str]:
        """Get list of connected USB devices"""
        result = self.run_command(['adb', 'devices'])
        devices = []
        
        for line in result.stdout.strip().split('\n')[1:]:  # Skip header
            if line.strip() and 'device' in line:
                serial = line.split()[0]
                # Filter out wireless connections
                if ':' not in serial:
                    devices.append(serial)
        
        return devices
    
    def get_device_ip(self, serial: str) -> Optional[str]:
        """Get Wi-Fi IP address of device"""
        result = self.run_command(['adb', '-s', serial, 'shell', 'ip', 'addr', 'show', 'wlan0'])
        
        # Parse IP from inet line
        ip_match = re.search(r'inet\s+(\d+\.\d+\.\d+\.\d+)', result.stdout)
        if ip_match:
            return ip_match.group(1)
        
        return None
    
    def get_device_name(self, serial: str) -> str:
        """Get device model name"""
        result = self.run_command(['adb', '-s', serial, 'shell', 'getprop', 'ro.product.model'])
        return result.stdout.strip() or "Unknown Device"
    
    def enable_tcpip(self, serial: str, port: int) -> bool:
        """Enable TCP/IP mode on device"""
        try:
            self.run_command(['adb', '-s', serial, 'tcpip', str(port)], check=True)
            time.sleep(2)  # Give device time to switch modes
            return True
        except subprocess.CalledProcessError:
            return False
    
    def connect_wireless(self, ip: str, port: int, retries: int = 3) -> bool:
        """Connect to device wirelessly with retry logic"""
        target = f"{ip}:{port}"
        
        for attempt in range(retries):
            try:
                result = self.run_command(['adb', 'connect', target], timeout=10)
                
                if 'connected' in result.stdout.lower():
                    return True
                
                if attempt < retries - 1:
                    print(f"{Colors.WARNING}[RETRY] Attempt {attempt + 1}/{retries} failed, retrying...{Colors.ENDC}")
                    time.sleep(1)
            
            except subprocess.TimeoutExpired:
                if attempt < retries - 1:
                    print(f"{Colors.WARNING}[RETRY] Connection timeout, retrying...{Colors.ENDC}")
                continue
        
        return False
    
    def disconnect(self, target: str) -> bool:
        """Disconnect from wireless device"""
        try:
            self.run_command(['adb', 'disconnect', target], check=True)
            return True
        except subprocess.CalledProcessError:
            return False
    
    def usb_mode(self, serial: str) -> bool:
        """Switch device back to USB mode"""
        try:
            self.run_command(['adb', '-s', serial, 'usb'], check=True)
            return True
        except subprocess.CalledProcessError:
            return False


class WirelessADBManager:
    """High-level wireless ADB connection manager"""
    
    PORT_MIN = 30000
    PORT_MAX = 50000
    CONFIG_FILE = Path.home() / '.wireless_adb' / 'profiles.json'
    
    def __init__(self, verbose: bool = False, quiet: bool = False):
        self.adb = ADBWrapper(verbose=verbose)
        self.verbose = verbose
        self.quiet = quiet
        self.log_level = LogLevel.VERBOSE if verbose else (LogLevel.QUIET if quiet else LogLevel.NORMAL)
        
        # Create config directory
        self.CONFIG_FILE.parent.mkdir(exist_ok=True)
    
    def log(self, message: str, level: LogLevel = LogLevel.NORMAL, color: str = Colors.OKBLUE):
        """Conditional logging based on verbosity"""
        if self.log_level.value >= level.value:
            print(f"{color}{message}{Colors.ENDC}")
    
    def _generate_random_port(self) -> int:
        """Generate random high port for ADB"""
        return random.randint(self.PORT_MIN, self.PORT_MAX)
    
    def _check_network_security(self, device_ip: str) -> None:
        """Warn user about network security concerns"""
        try:
            # Get host IP (basic check)
            host_ip = self._get_host_ip()
            
            if host_ip and device_ip:
                device_network = ipaddress.ip_network(f"{device_ip}/24", strict=False)
                host_network = ipaddress.ip_network(f"{host_ip}/24", strict=False)
                
                if device_network != host_network:
                    self.log(
                        f"[WARNING] Device and host appear to be on different subnets!",
                        LogLevel.NORMAL,
                        Colors.WARNING
                    )
                    self.log(
                        f"          Device: {device_ip} | Host: {host_ip}",
                        LogLevel.NORMAL,
                        Colors.WARNING
                    )
        except Exception:
            pass  # Network detection is best-effort
        
        # Always warn about network security
        self.log(
            "\n[SECURITY] Wireless ADB is INSECURE on untrusted networks!",
            LogLevel.NORMAL,
            Colors.WARNING
        )
        self.log(
            "           • Anyone on the network can access your device",
            LogLevel.NORMAL,
            Colors.WARNING
        )
        self.log(
            "           • Use only on trusted private networks",
            LogLevel.NORMAL,
            Colors.WARNING
        )
        self.log(
            "           • Random ports reduce (but don't eliminate) risk\n",
            LogLevel.NORMAL,
            Colors.WARNING
        )
    
    def _get_host_ip(self) -> Optional[str]:
        """Get host machine's local IP (best effort)"""
        try:
            if sys.platform == 'win32':
                result = subprocess.run(
                    ['ipconfig'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                match = re.search(r'IPv4 Address[.\s]*:\s*(\d+\.\d+\.\d+\.\d+)', result.stdout)
                if match:
                    return match.group(1)
            else:
                result = subprocess.run(
                    ['ip', 'addr', 'show'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                match = re.search(r'inet\s+(\d+\.\d+\.\d+\.\d+).*scope global', result.stdout)
                if match:
                    return match.group(1)
        except Exception:
            pass
        return None
    
    def _save_profile(self, profile: DeviceProfile) -> None:
        """Save device profile to config file"""
        try:
            profiles = {}
            if self.CONFIG_FILE.exists():
                with open(self.CONFIG_FILE, 'r') as f:
                    profiles = json.load(f)
            
            profiles[profile.serial] = {
                'ip': profile.ip,
                'port': profile.port,
                'last_connected': profile.last_connected,
                'device_name': profile.device_name
            }
            
            with open(self.CONFIG_FILE, 'w') as f:
                json.dump(profiles, f, indent=2)
            
            self.log(f"[SAVED] Device profile saved", LogLevel.VERBOSE, Colors.OKCYAN)
        
        except Exception as e:
            self.log(f"[WARNING] Could not save profile: {e}", LogLevel.VERBOSE, Colors.WARNING)
    
    def _load_profile(self, serial: str) -> Optional[DeviceProfile]:
        """Load device profile from config file"""
        try:
            if self.CONFIG_FILE.exists():
                with open(self.CONFIG_FILE, 'r') as f:
                    profiles = json.load(f)
                
                if serial in profiles:
                    data = profiles[serial]
                    return DeviceProfile(
                        serial=serial,
                        ip=data['ip'],
                        port=data['port'],
                        last_connected=data['last_connected'],
                        device_name=data.get('device_name', 'Unknown')
                    )
        except Exception as e:
            self.log(f"[DEBUG] Could not load profile: {e}", LogLevel.VERBOSE, Colors.OKCYAN)
        
        return None
    
    def connect(self, reconnect: bool = False) -> bool:
        """Main connection flow"""
        self.log("\n" + "="*60, LogLevel.NORMAL, Colors.HEADER)
        self.log("  WirelessADB - Secure Wireless ADB Connection Manager", LogLevel.NORMAL, Colors.HEADER)
        self.log("="*60 + "\n", LogLevel.NORMAL, Colors.HEADER)
        
        # Step 1: Detect USB devices
        self.log("[1/5] Detecting USB-connected Android devices...", LogLevel.NORMAL, Colors.OKBLUE)
        devices = self.adb.get_devices()
        
        if not devices:
            self.log("[ERROR] No USB devices found!", LogLevel.NORMAL, Colors.FAIL)
            self.log("        • Connect device via USB", LogLevel.NORMAL, Colors.WARNING)
            self.log("        • Enable USB debugging in Developer Options", LogLevel.NORMAL, Colors.WARNING)
            self.log("        • Authorize computer on device screen", LogLevel.NORMAL, Colors.WARNING)
            return False
        
        # Handle multiple devices
        if len(devices) > 1:
            self.log(f"[FOUND] {len(devices)} devices connected:", LogLevel.NORMAL, Colors.OKGREEN)
            for idx, serial in enumerate(devices, 1):
                name = self.adb.get_device_name(serial)
                self.log(f"        [{idx}] {name} ({serial})", LogLevel.NORMAL, Colors.OKCYAN)
            
            try:
                choice = int(input(f"{Colors.BOLD}Select device [1-{len(devices)}]: {Colors.ENDC}"))
                if 1 <= choice <= len(devices):
                    serial = devices[choice - 1]
                else:
                    self.log("[ERROR] Invalid selection", LogLevel.NORMAL, Colors.FAIL)
                    return False
            except (ValueError, KeyboardInterrupt):
                self.log("\n[ABORT] Operation cancelled", LogLevel.NORMAL, Colors.WARNING)
                return False
        else:
            serial = devices[0]
        
        device_name = self.adb.get_device_name(serial)
        self.log(f"[OK] Selected: {device_name} ({serial})", LogLevel.NORMAL, Colors.OKGREEN)
        
        # Step 2: Get Wi-Fi IP
        self.log("\n[2/5] Retrieving device Wi-Fi IP address...", LogLevel.NORMAL, Colors.OKBLUE)
        device_ip = self.adb.get_device_ip(serial)
        
        if not device_ip:
            self.log("[ERROR] Could not get Wi-Fi IP!", LogLevel.NORMAL, Colors.FAIL)
            self.log("        • Ensure device is connected to Wi-Fi", LogLevel.NORMAL, Colors.WARNING)
            self.log("        • Check Wi-Fi is enabled", LogLevel.NORMAL, Colors.WARNING)
            return False
        
        self.log(f"[OK] Device IP: {device_ip}", LogLevel.NORMAL, Colors.OKGREEN)
        
        # Step 3: Generate random port
        self.log("\n[3/5] Generating secure random port...", LogLevel.NORMAL, Colors.OKBLUE)
        port = self._generate_random_port()
        self.log(f"[OK] Using port: {port}", LogLevel.NORMAL, Colors.OKGREEN)
        self.log(f"     (Random port range: {self.PORT_MIN}-{self.PORT_MAX})", LogLevel.VERBOSE, Colors.OKCYAN)
        
        # Step 4: Enable TCP/IP mode
        self.log("\n[4/5] Switching device to TCP/IP mode...", LogLevel.NORMAL, Colors.OKBLUE)
        if not self.adb.enable_tcpip(serial, port):
            self.log("[ERROR] Failed to enable TCP/IP mode", LogLevel.NORMAL, Colors.FAIL)
            return False
        
        self.log(f"[OK] TCP/IP mode enabled on port {port}", LogLevel.NORMAL, Colors.OKGREEN)
        
        # Step 5: Connect wirelessly
        self.log("\n[5/5] Connecting to device wirelessly...", LogLevel.NORMAL, Colors.OKBLUE)
        if not self.adb.connect_wireless(device_ip, port):
            self.log("[ERROR] Wireless connection failed", LogLevel.NORMAL, Colors.FAIL)
            self.log("        • Ensure device and host are on same network", LogLevel.NORMAL, Colors.WARNING)
            self.log("        • Check firewall settings", LogLevel.NORMAL, Colors.WARNING)
            return False
        
        self.log(f"[OK] Connected wirelessly to {device_ip}:{port}", LogLevel.NORMAL, Colors.OKGREEN)
        
        # Save profile
        profile = DeviceProfile(
            serial=serial,
            ip=device_ip,
            port=port,
            last_connected=time.time(),
            device_name=device_name
        )
        self._save_profile(profile)
        
        # Security warnings
        self._check_network_security(device_ip)
        
        # Success summary
        self.log("\n" + "="*60, LogLevel.NORMAL, Colors.OKGREEN)
        self.log(f"  ✓ CONNECTED SUCCESSFULLY", LogLevel.NORMAL, Colors.OKGREEN)
        self.log("="*60, LogLevel.NORMAL, Colors.OKGREEN)
        self.log(f"  Device: {device_name}", LogLevel.NORMAL, Colors.OKGREEN)
        self.log(f"  Target: {device_ip}:{port}", LogLevel.NORMAL, Colors.OKGREEN)
        self.log(f"\n  You can now disconnect the USB cable.", LogLevel.NORMAL, Colors.BOLD)
        self.log(f"  Run 'wireless-adb disconnect' to cleanup when done.\n", LogLevel.NORMAL, Colors.BOLD)
        
        return True
    
    def disconnect(self, reset_usb: bool = True) -> bool:
        """Disconnect wireless ADB and optionally reset to USB mode"""
        self.log("\n[DISCONNECT] Cleaning up wireless connections...", LogLevel.NORMAL, Colors.OKBLUE)
        
        # Get all connected devices
        result = self.adb.run_command(['adb', 'devices'])
        wireless_devices = []
        
        for line in result.stdout.strip().split('\n')[1:]:
            if line.strip() and 'device' in line:
                target = line.split()[0]
                if ':' in target:  # Wireless connection
                    wireless_devices.append(target)
        
        if not wireless_devices:
            self.log("[INFO] No wireless connections found", LogLevel.NORMAL, Colors.WARNING)
            return True
        
        # Disconnect all wireless devices
        for target in wireless_devices:
            self.log(f"[DISCONNECTING] {target}...", LogLevel.NORMAL, Colors.OKBLUE)
            self.adb.disconnect(target)
        
        self.log(f"[OK] Disconnected {len(wireless_devices)} wireless connection(s)", LogLevel.NORMAL, Colors.OKGREEN)
        
        # Optionally reset to USB mode
        if reset_usb:
            usb_devices = self.adb.get_devices()
            if usb_devices:
                for serial in usb_devices:
                    self.log(f"[RESETTING] Switching {serial} back to USB mode...", LogLevel.NORMAL, Colors.OKBLUE)
                    self.adb.usb_mode(serial)
                self.log("[OK] Devices reset to USB mode", LogLevel.NORMAL, Colors.OKGREEN)
        
        return True
    
    def status(self) -> bool:
        """Show current ADB connection status"""
        self.log("\n" + "="*60, LogLevel.NORMAL, Colors.HEADER)
        self.log("  WirelessADB - Connection Status", LogLevel.NORMAL, Colors.HEADER)
        self.log("="*60 + "\n", LogLevel.NORMAL, Colors.HEADER)
        
        result = self.adb.run_command(['adb', 'devices', '-l'])
        
        usb_devices = []
        wireless_devices = []
        
        for line in result.stdout.strip().split('\n')[1:]:
            if line.strip() and 'device' in line:
                target = line.split()[0]
                if ':' in target:
                    wireless_devices.append(line)
                else:
                    usb_devices.append(line)
        
        # USB devices
        if usb_devices:
            self.log(f"USB Devices ({len(usb_devices)}):", LogLevel.NORMAL, Colors.OKGREEN)
            for device in usb_devices:
                self.log(f"  • {device}", LogLevel.NORMAL, Colors.OKCYAN)
        else:
            self.log("USB Devices: None", LogLevel.NORMAL, Colors.WARNING)
        
        print()
        
        # Wireless devices
        if wireless_devices:
            self.log(f"Wireless Devices ({len(wireless_devices)}):", LogLevel.NORMAL, Colors.OKGREEN)
            for device in wireless_devices:
                self.log(f"  • {device}", LogLevel.NORMAL, Colors.OKCYAN)
        else:
            self.log("Wireless Devices: None", LogLevel.NORMAL, Colors.WARNING)
        
        print()
        
        # Saved profiles
        if self.CONFIG_FILE.exists():
            try:
                with open(self.CONFIG_FILE, 'r') as f:
                    profiles = json.load(f)
                
                if profiles:
                    self.log(f"Saved Profiles ({len(profiles)}):", LogLevel.NORMAL, Colors.OKBLUE)
                    for serial, data in profiles.items():
                        last_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(data['last_connected']))
                        self.log(
                            f"  • {data.get('device_name', 'Unknown')} ({serial})",
                            LogLevel.NORMAL,
                            Colors.OKCYAN
                        )
                        self.log(
                            f"    Last: {data['ip']}:{data['port']} @ {last_time}",
                            LogLevel.NORMAL,
                            Colors.OKCYAN
                        )
            except Exception:
                pass
        
        print()
        return True
    
    def reconnect(self) -> bool:
        """Reconnect to last known device"""
        self.log("\n[RECONNECT] Attempting to reconnect to last device...", LogLevel.NORMAL, Colors.OKBLUE)
        
        if not self.CONFIG_FILE.exists():
            self.log("[ERROR] No saved profiles found", LogLevel.NORMAL, Colors.FAIL)
            self.log("        Connect at least once before using reconnect", LogLevel.NORMAL, Colors.WARNING)
            return False
        
        try:
            with open(self.CONFIG_FILE, 'r') as f:
                profiles = json.load(f)
            
            if not profiles:
                self.log("[ERROR] No saved profiles found", LogLevel.NORMAL, Colors.FAIL)
                return False
            
            # Get most recent profile
            latest = max(profiles.items(), key=lambda x: x[1]['last_connected'])
            serial, data = latest
            
            self.log(f"[FOUND] Last device: {data.get('device_name', 'Unknown')}", LogLevel.NORMAL, Colors.OKGREEN)
            self.log(f"        Target: {data['ip']}:{data['port']}", LogLevel.NORMAL, Colors.OKCYAN)
            
            # Try to reconnect
            if self.adb.connect_wireless(data['ip'], data['port']):
                self.log(f"[OK] Reconnected successfully!", LogLevel.NORMAL, Colors.OKGREEN)
                
                # Update timestamp
                profile = DeviceProfile(
                    serial=serial,
                    ip=data['ip'],
                    port=data['port'],
                    last_connected=time.time(),
                    device_name=data.get('device_name', 'Unknown')
                )
                self._save_profile(profile)
                
                return True
            else:
                self.log("[ERROR] Reconnection failed", LogLevel.NORMAL, Colors.FAIL)
                self.log("        • Device may be offline", LogLevel.NORMAL, Colors.WARNING)
                self.log("        • IP address may have changed", LogLevel.NORMAL, Colors.WARNING)
                self.log("        • Try 'wireless-adb connect' instead", LogLevel.NORMAL, Colors.WARNING)
                return False
        
        except Exception as e:
            self.log(f"[ERROR] Reconnection failed: {e}", LogLevel.NORMAL, Colors.FAIL)
            return False


def main():
    """CLI entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='WirelessADB - Secure Wireless ADB Connection Manager',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  wireless-adb connect              Connect to USB device wirelessly
  wireless-adb disconnect           Disconnect and cleanup
  wireless-adb status               Show connection status
  wireless-adb reconnect            Reconnect to last device
  
Security Notes:
  • Random ports (30000-50000) used instead of default 5555
  • Reduces risk of port scanning attacks
  • Still vulnerable on untrusted networks - use with caution
  • Always disconnect when done to minimize exposure
        """
    )
    
    parser.add_argument(
        'command',
        choices=['connect', 'disconnect', 'status', 'reconnect'],
        help='Command to execute'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose debug output'
    )
    
    parser.add_argument(
        '-q', '--quiet',
        action='store_true',
        help='Minimal output mode'
    )
    
    parser.add_argument(
        '--no-reset',
        action='store_true',
        help='Don\'t reset to USB mode on disconnect'
    )
    
    parser.add_argument(
        '--no-color',
        action='store_true',
        help='Disable colored output (for Windows CMD)'
    )
    
    args = parser.parse_args()
    
    # Disable colors if requested or on Windows CMD
    if args.no_color or (sys.platform == 'win32' and os.environ.get('TERM') != 'xterm'):
        Colors.disable_colors()
    
    # Create manager
    manager = WirelessADBManager(verbose=args.verbose, quiet=args.quiet)
    
    # Execute command
    try:
        if args.command == 'connect':
            success = manager.connect()
        elif args.command == 'disconnect':
            success = manager.disconnect(reset_usb=not args.no_reset)
        elif args.command == 'status':
            success = manager.status()
        elif args.command == 'reconnect':
            success = manager.reconnect()
        
        sys.exit(0 if success else 1)
    
    except KeyboardInterrupt:
        print(f"\n{Colors.WARNING}[ABORT] Operation cancelled by user{Colors.ENDC}")
        sys.exit(130)
    except Exception as e:
        print(f"\n{Colors.FAIL}[FATAL] Unexpected error: {e}{Colors.ENDC}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
