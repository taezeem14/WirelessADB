from setuptools import setup

setup(
    name="wireless-adb",
    version="3.2.0",
    description="⚡ Next-Gen Secure Wireless ADB Connection & Telemetry Suite for Android",
    py_modules=["wireless_adb"],
    python_requires=">=3.7",
    entry_points={
        "console_scripts": [
            "wireless-adb=wireless_adb:main",
            "wadb=wireless_adb:main",
        ],
    },
)
