from setuptools import setup

setup(
    name="wireless-adb",
    version="4.0.0",
    description="⚡ Next-Gen Secure Wireless ADB Connection, File Management, Telemetry & Mirroring Suite for Android",
    py_modules=["wireless_adb"],
    python_requires=">=3.7",
    entry_points={
        "console_scripts": [
            "wireless-adb=wireless_adb:main",
            "wadb=wireless_adb:main",
        ],
    },
)
