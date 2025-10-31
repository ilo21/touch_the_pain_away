import serial
import time
import threading



class ArduinoController:
    def __init__(self, port="COM7", baud=115200):
        self.port = port
        self.baud = baud
        self.ser = None
        self._print_thread = None
        self._running = False

    # --- Connection handling ---
    def connect(self):
        if self.ser and self.ser.is_open:
            self.ser.close()
        self.ser = serial.Serial(self.port, self.baud, timeout=1)
        self._running = True
        self._start_print_thread()
        print(f"Connected {self.port} @ {self.baud} baud")

    def disconnect(self):
        self._running = False
        if self.ser and self.ser.is_open:
            self.ser.close()
            print("Disconnected")

    def reconnect(self):
        self.disconnect()
        time.sleep(0.2)
        self.connect()

    # --- Background serial monitor ---
    def _start_print_thread(self):
        if self._print_thread and self._print_thread.is_alive():
            return
        self._print_thread = threading.Thread(target=self._print_loop, daemon=True)
        self._print_thread.start()

    def _print_loop(self):
        while self._running:
            try:
                if self.ser.in_waiting:
                    line = self.ser.readline().decode(errors="ignore").strip()
                    if line:
                        print("Arduino:", line)
                else:
                    time.sleep(0.05)
            except serial.SerialException:
                print("Error: Serial disconnected")
                self._running = False
            except Exception:
                time.sleep(0.1)

    # --- Command methods ---
    def send(self, command):
        if not self.ser or not self.ser.is_open:
            raise ConnectionError("Serial port not open")
        if not command.endswith("\n"):
            command += "\n"
        self.ser.write(command.encode())

    def send_file(self, filename):
        with open(filename, "r", encoding="utf-8") as f:
            content = f.read()
        self.send(content)

    def send_file_line_by_line(self, filename, delay=0.01):
        with open(filename, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip()]
        for line in lines:
            self.send(line)
            time.sleep(delay)

    def send_command(self, cmd, index=0, value=0.0):
        self.send(f"{cmd}/{index}:{value}")

    def exec(self):
        self.send("exec")

    # --- Context manager support ---
    def __enter__(self):
        self.connect()
        return self

    def __exit__(self):
        self.disconnect()
