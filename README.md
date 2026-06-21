# Arctis Battery Tray

A lightweight, highly customizable PyQt6 system tray utility that provides a live battery indicator for SteelSeries Arctis headsets (like the Arctis Nova 7) on Linux.

## Features
- **Live Battery Status:** Automatically polls the headset's battery level via D-Bus.
- **Dynamic Icon:** A custom-drawn tray icon that visually represents the charge level and shifts colors (Green/Orange/Red) as it drops.
- **Extensive Customization:** Right-click the tray icon to:
  - Toggle the percentage text visibility.
  - Pick custom hex colors for both the text and the battery meter fill using native color pickers.
  - Reset to dynamic threshold colors.
- **Persistent Settings:** Your preferences are automatically saved to `~/.config/arctis-battery-tray.json` and applied across reboots.

## Requirements
This is a frontend UI built exclusively for the phenomenal `linux-arctis-manager` backend daemon. It uses standard D-Bus calls (`busctl`) to read the battery status, which bypasses many of the chatmix lockups and hardware polling issues found in older tools.

* Python 3
* PyQt6 (install via `pip install -r requirements.txt` or your package manager)
* [linux-arctis-manager](https://github.com/elegos/Linux-Arctis-Manager) daemon running on the user session bus.

## Installation & Autostart (Linux)

You can easily run this on startup using the provided systemd service file:

1. Clone the repository to `~/git/lam_battery_tray`.
2. Install the required dependencies: `pip install -r requirements.txt` (or install `python-pyqt6` via your system package manager).
3. Copy the service file to your user systemd directory:
   ```bash
   mkdir -p ~/.config/systemd/user/
   cp lam-battery-tray.service ~/.config/systemd/user/
   ```
4. Reload systemd and enable the service:
   ```bash
   systemctl --user daemon-reload
   systemctl --user enable --now lam-battery-tray.service
   ```

## Acknowledgements
A massive thank you and callout to [Giacomo Furlan (giacomofurlan)](https://github.com/giacomofurlan) for creating the [linux-arctis-manager](https://github.com/giacomofurlan/linux-arctis-manager) backend. Without that fantastic daemon providing clean, stable D-Bus endpoints for the hardware, this frontend wouldn't be possible!
