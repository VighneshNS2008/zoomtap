import os
import sys
import serial
import serial.tools.list_ports
import pyautogui
import time
from threading import Thread
import psutil
import winsound  # For beeps

class ZoomController:
    def __init__(self, com_port=None, baud_rate=115200):
        self.com_port = com_port or self.find_esp_port()
        self.baud_rate = baud_rate
        self.serial_port = None
        self.running = True
        self.hand_raised = False
        self.is_muted = False
        self.last_serial_time = time.time()

    @staticmethod
    def find_esp_port():
        ports = list(serial.tools.list_ports.comports())
        for port in ports:
            if "CP210X" in port.description.upper() or "CH340" in port.description.upper():
                return port.device
        return None

    def beep(self, frequency, duration):
        """ Play a beep sound with the given frequency and duration. """
        winsound.Beep(frequency, duration)

    def connect_serial(self):
        try:
            if self.serial_port and self.serial_port.is_open:
                self.serial_port.close()
            self.serial_port = serial.Serial(self.com_port, self.baud_rate)
            print(f"✅ Connected to {self.com_port}")
            self.beep(1000, 200)  # Short high-pitched beep for Serial connect
            self.last_serial_time = time.time()
            return True
        except serial.SerialException as e:
            print(f"❌ Serial connection error: {e}")
            return False

    def handle_command(self, command):
        if command == "MUTE":
            pyautogui.hotkey('alt', 'a')
            self.is_muted = True
            print("🔇 Muting")
            self.beep(600, 200)  # Low-pitched beep for Mute
        elif command == "UNMUTE":
            pyautogui.hotkey('alt', 'a')
            self.is_muted = False
            print("🔊 Unmuting")
            self.beep(800, 200)  # High-pitched beep for Unmute
        elif command == "HAND_RAISE":
            pyautogui.hotkey('alt', 'y')
            self.hand_raised = True
            print("✋ Hand Raised")
            self.beep(800, 100)  # Short beep
            time.sleep(0.1)
            self.beep(800, 100)  # Short beep (Double beep)
        elif command == "HAND_LOWER":
            pyautogui.hotkey('alt', 'y')
            self.hand_raised = False
            print("👇 Hand Lowered")
            self.beep(800, 100)  # Single short beep

    def monitor_serial(self):
        print("\n📡 Starting Serial Monitor...")
        start_time = time.time()
        while self.running:
            try:
                # Stop if no serial connection within 1 minute of startup
                if not self.serial_port or not self.serial_port.is_open:
                    if time.time() - start_time > 60:
                        print("❌ No Serial Connection within 1 minute. Stopping...")
                        self.stop()
                        return
                    if not self.connect_serial():
                        time.sleep(5)
                        continue
                
                # Retry for 5 seconds if Serial disconnects
                if not self.serial_port.is_open:
                    print("❌ Serial Disconnected. Retrying for 5 seconds...")
                    retry_start = time.time()
                    while time.time() - retry_start < 5:
                        if self.connect_serial():
                            print("🔌 Serial Reconnected!")
                            break
                        time.sleep(1)
                    else:
                        print("❌ Serial Not Reconnected. Stopping...")
                        self.stop()
                        return

                if self.serial_port.in_waiting:
                    command = self.serial_port.readline().decode().strip()
                    if command:
                        print(f"📨 Received command: {command}")
                        self.handle_command(command)
                        self.last_serial_time = time.time()
            except PermissionError as e:
                # Handle ClearCommError failed (PermissionError(13, 'Access is denied.', None, 5))
                if "Access is denied" in str(e):
                    print("❌ Serial Error: Access Denied. Stopping...")
                    self.stop()
                    return
            except OSError as e:
                # Handle ClearCommError failed (OSError(9, 'The handle is invalid.', None, 6))
                if "The handle is invalid" in str(e):
                    print("❌ Serial Error: Handle Invalid. Attempting to reconnect...")
                    self.serial_port.close()
                    time.sleep(1)
                    if not self.connect_serial():
                        print("❌ Failed to reconnect. Stopping...")
                        self.stop()
                else:
                    print(f"Serial error: {e}")
                    time.sleep(1)

    def start(self):
        print("\n=== Zoom Controller Starting ===")
        print(f"🔌 Serial Port: {self.com_port}")
        self.monitor_thread = Thread(target=self.monitor_serial)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()

    def stop(self):
        self.running = False
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.close()
        print("\n=== Zoom Controller Stopped ===")
        if os.path.exists("zoom_controller.pid"):
            os.remove("zoom_controller.pid")

if __name__ == "__main__":
    controller = ZoomController()
    with open("zoom_controller.pid", "w") as f:
        f.write(str(os.getpid()))
    try:
        controller.start()
        while controller.running:
            time.sleep(1)
    except KeyboardInterrupt:
        controller.stop()
    except Exception as e:
        print(f"Fatal error: {e}")
        controller.stop()
