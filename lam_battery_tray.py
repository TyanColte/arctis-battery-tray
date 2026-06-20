import sys
import os
import json
import subprocess
import traceback
import datetime
from PyQt6.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QColorDialog
from PyQt6.QtGui import QIcon, QPainter, QColor, QFont, QPixmap, QPen
from PyQt6.QtCore import QTimer, Qt

def get_battery_info():
    try:
        clean_env = os.environ.copy()
        clean_env.pop("LD_LIBRARY_PATH", None)

        result = subprocess.run(
            ["busctl", "--user", "call", "name.giacomofurlan.ArctisManager.Next",
             "/name/giacomofurlan/ArctisManager/Next/Status",
             "name.giacomofurlan.ArctisManager.Next.Status", "GetStatus"],
            capture_output=True, text=True, check=True, env=clean_env
        )
        output = result.stdout.strip()
        if output.startswith('s "'):
            json_str = output[3:-1].encode('utf-8').decode('unicode_escape')
            data = json.loads(json_str)
            if "headset" in data and "headset_battery_charge" in data["headset"]:
                return int(data["headset"]["headset_battery_charge"]["value"])
    except Exception as e:
        return None
    return None

class BatteryTrayApp:
    def __init__(self):
        # Suppress the invalid style override warning from PyInstaller
        os.environ.pop("QT_STYLE_OVERRIDE", None)
        
        self.app = QApplication(sys.argv)
        self.app.setQuitOnLastWindowClosed(False)

        self.config_file = os.path.expanduser("~/.config/arctis-battery-tray.json")
        self.config = {
            "meter_color": "dynamic",
            "text_color": "#ffffff",
            "show_text": True
        }
        self.load_config()

        self.tray = QSystemTrayIcon()
        self.tray.setToolTip("Arctis Battery: Waiting...")

        self.menu = QMenu()
        
        self.action_show_text = self.menu.addAction("Show Percentage Text")
        self.action_show_text.setCheckable(True)
        self.action_show_text.setChecked(self.config["show_text"])
        self.action_show_text.triggered.connect(self.toggle_text)

        self.action_meter_color = self.menu.addAction("Pick Meter Color...")
        self.action_meter_color.triggered.connect(self.pick_meter_color)

        self.action_reset_meter = self.menu.addAction("Reset Meter to Dynamic Colors")
        self.action_reset_meter.triggered.connect(self.reset_meter_color)

        self.action_text_color = self.menu.addAction("Pick Text Color...")
        self.action_text_color.triggered.connect(self.pick_text_color)

        self.menu.addSeparator()

        quit_action = self.menu.addAction("Quit")
        quit_action.triggered.connect(self.app.quit)
        self.tray.setContextMenu(self.menu)

        # Generate the initial icon BEFORE showing the tray to avoid "No Icon set" warning
        self.update_battery()
        self.tray.show()

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_battery)
        self.timer.start(5000)

    def load_config(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r") as f:
                    data = json.load(f)
                    self.config.update(data)
            except Exception:
                pass

    def save_config(self):
        try:
            with open(self.config_file, "w") as f:
                json.dump(self.config, f)
        except Exception:
            pass

    def toggle_text(self, checked):
        self.config["show_text"] = checked
        self.save_config()
        self.update_battery()

    def pick_meter_color(self):
        current_color = Qt.GlobalColor.green if self.config["meter_color"] == "dynamic" else QColor(self.config["meter_color"])
        color = QColorDialog.getColor(current_color)
        if color.isValid():
            self.config["meter_color"] = color.name()
            self.save_config()
            self.update_battery()

    def reset_meter_color(self):
        self.config["meter_color"] = "dynamic"
        self.save_config()
        self.update_battery()

    def pick_text_color(self):
        color = QColorDialog.getColor(QColor(self.config["text_color"]))
        if color.isValid():
            self.config["text_color"] = color.name()
            self.save_config()
            self.update_battery()

    def generate_icon(self, battery_level):
        pixmap = QPixmap(64, 64)
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Draw battery outline with a thicker pen
        pen = QPen(Qt.GlobalColor.white)
        pen.setWidth(4)
        painter.setPen(pen)
        painter.drawRect(2, 16, 54, 32)
        painter.drawRect(56, 24, 6, 16) # Battery Tip

        if battery_level is not None:
            if self.config["meter_color"] == "dynamic":
                if battery_level > 50:
                    color = QColor(0, 255, 0)
                elif battery_level > 20:
                    color = QColor(255, 165, 0)
                else:
                    color = QColor(255, 0, 0)
            else:
                color = QColor(self.config["meter_color"])
            
            # Fill logic
            # The border inner bounds are roughly X:4 to 54, Y:18 to 46.
            # Adding 2px padding gives X=6, Y=20, Max Width=46, Height=24
            width = int(46 * (battery_level / 100.0))
            if width > 0:
                painter.fillRect(6, 20, width, 24, color)
            
            if self.config["show_text"]:
                painter.setPen(QColor(self.config["text_color"]))
                font = QFont("Arial", 20)
                font.setBold(True)
                painter.setFont(font)
                painter.drawText(0, 0, 58, 64, Qt.AlignmentFlag.AlignCenter, f"{battery_level}")
        else:
            painter.setPen(Qt.GlobalColor.red)
            font = QFont("Arial", 24)
            font.setBold(True)
            painter.setFont(font)
            painter.drawText(0, 0, 64, 64, Qt.AlignmentFlag.AlignCenter, "?")

        painter.end()
        return QIcon(pixmap)

    def update_battery(self):
        level = get_battery_info()
        icon = self.generate_icon(level)
        self.tray.setIcon(icon)
        if level is not None:
            self.tray.setToolTip(f"Arctis Battery: {level}%")
        else:
            self.tray.setToolTip("Arctis Battery: Headset Off / Unavailable")

    def run(self):
        sys.exit(self.app.exec())

if __name__ == "__main__":
    app = BatteryTrayApp()
    app.run()
