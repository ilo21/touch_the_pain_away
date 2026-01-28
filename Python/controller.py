import serial
import time
import threading
import os
import csv


class Controller:
    """
    Unified controller for Arduino stimulus experiments.
    Integrates serial communication, channel management, and stimulus generation.
    """
    
    def __init__(self, port="COM7", baud=115200):
        self.port = port
        self.baud = baud
        self.ser = None
        self._print_thread = None
        self._running = False

    # =========================================================================
    # CONNECTION HANDLING
    # =========================================================================
    def connect(self):
        """Connect to Arduino via serial port."""
        if self.ser and self.ser.is_open:
            self.ser.close()
        self.ser = serial.Serial(self.port, self.baud, timeout=1)
        self._running = True
        self._start_print_thread()
        print(f"Connected {self.port} @ {self.baud} baud")

    def disconnect(self):
        """Disconnect from Arduino."""
        self._running = False
        if self.ser and self.ser.is_open:
            self.ser.close()
            print("Disconnected")

    def reconnect(self):
        """Reconnect to Arduino."""
        self.disconnect()
        time.sleep(0.2)
        self.connect()

    # =========================================================================
    # BACKGROUND SERIAL MONITOR
    # =========================================================================
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

    # =========================================================================
    # COMMAND METHODS
    # =========================================================================
    def send(self, command):
        """Send a command to Arduino."""
        if not self.ser or not self.ser.is_open:
            raise ConnectionError("Serial port not open")
        if not command.endswith("\n"):
            command += "\n"
        self.ser.write(command.encode())

    # too quick for longer files
    def send_file(self, filename):
        """Send entire file content at once."""
        with open(filename, "r", encoding="utf-8") as f:
            content = f.read()
        self.send(content)

    def send_file_line_by_line(self, filename, delay=0.01):
        """Send file line by line with delay."""
        with open(filename, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip()]
        for line in lines:
            self.send(line)
            time.sleep(delay)

    def send_command(self, cmd, index=0, value=0.0):
        self.send(f"{cmd}/{index}:{value}")

    def exec(self):
        """Execute the loaded stimulus on Arduino."""
        self.send("exec")
################################################################
# debugging (saves log of sent commands)
    def send_stimulus_from_csv(self, csv_path, col_ms=100, delay=0.01, log_path="arduino_commands.log"):
        """
        Read a binary matrix CSV and send corresponding Arduino commands directly.

        - Each row = one channel
        - First column = channel id
        - Following columns = 0/1 values (OFF/ON)
        - col_ms = time duration per column
        - delay = pause between sending lines
        - log_path = path to log file (will be overwritten each time)

        This is equivalent to generating 'stim_from_csv.txt' and then
        calling send_file_line_by_line(), but avoids creating the file.
        """
        stim = Controller.Stimulus.from_csv_matrix(csv_path, col_ms=col_ms)
        seq = stim.generate_timed_sequence()

        # Open log file in write mode (overwrites existing file)
        with open(log_path, 'w') as log_file:
            # Send clearcode
            cmd = "clearcode"
            self.send(cmd)
            log_file.write(f"{cmd}\n")
            time.sleep(delay)

            # Send addcode commands
            for mask, dur in seq:
                if dur > 0:
                    cmd = f"addcode:0x{mask:x}/{dur}"
                    self.send(cmd)
                    log_file.write(f"{cmd}\n")
                    time.sleep(delay)
    # keep one final version eventually
    def send_stimulus_from_csv_vertical(self, csv_path, col_ms=100, delay=0.01, log_path="arduino_commands.log"):
        """
        Read a binary matrix CSV and send corresponding Arduino commands directly.
        CSV:
        - First row = channel IDs as headers
        - Each subsequent row = time step (col_ms duration)
        - Cell values: 1=ON, 0=OFF

        - col_ms = time duration per column
        - delay = pause between sending lines
        - log_path = path to log file (will be overwritten each time)

        This is equivalent to generating 'stim_from_csv.txt' and then
        calling send_file_line_by_line(), but avoids creating the file.
        """
        stim = Controller.Stimulus.from_csv_matrix_vertical(csv_path, col_ms=col_ms)
        seq = stim.generate_timed_sequence()

        # Open log file in write mode (overwrites existing file)
        with open(log_path, 'w') as log_file:
            # Send clearcode
            cmd = "clearcode"
            self.send(cmd)
            log_file.write(f"{cmd}\n")
            time.sleep(delay)

            # Send addcode commands
            for mask, dur in seq:
                if dur > 0:
                    cmd = f"addcode:0x{mask:x}/{dur}"
                    self.send(cmd)
                    log_file.write(f"{cmd}\n")
                    time.sleep(delay)

##############################################################################

    # def send_stimulus_from_csv(self, csv_path, col_ms=100, delay=0.01):
    #     """
    #     Read a binary matrix CSV and send corresponding Arduino commands directly.

    #     - Each row = one channel
    #     - First column = channel id
    #     - Following columns = 0/1 values (OFF/ON)
    #     - col_ms = time duration per column
    #     - delay = pause between sending lines

    #     This is equivalent to generating 'stim_from_csv.txt' and then
    #     calling send_file_line_by_line(), but avoids creating the file.
    #     """
    #     stim = Controller.Stimulus.from_csv_matrix(csv_path, col_ms=col_ms)
    #     seq = stim.generate_timed_sequence()

    #     self.send("clearcode")
    #     time.sleep(delay)

    #     for mask, dur in seq:
    #         if dur > 0:
    #             self.send(f"addcode:0x{mask:x}/{dur}")
    #             time.sleep(delay)


    # =========================================================================
    # CONTEXT MANAGER SUPPORT
    # =========================================================================
    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, *args):
        self.disconnect()

    # =========================================================================
    # CHANNEL CLASS (nested)
    # =========================================================================
    class Channel:
        def __init__(self, ids, *args, **kwargs):
            """
            Two valid constructors:

            Constructor 1:
                Channel(ids, is_on=1, hold_time_ms=500)
                  - ids: int or list[int]
                  - is_on: 1 or 0 (default 1)
                  - hold_time_ms: duration in ms

            Constructor 2:
                Channel(ids, onset_ms=0, offset_ms=500)
                  - ids: int or list[int]
                  - onset_ms: start time
                  - offset_ms: end time
            """
            self.ids = [ids] if isinstance(ids, int) else list(ids)
            self.is_on = 1
            self.hold_time_ms = None
            self.onset_ms = None
            self.offset_ms = None

            if "onset_ms" in kwargs and "offset_ms" in kwargs:
                # Mode B: onset/offset definition
                self.onset_ms = kwargs["onset_ms"]
                self.offset_ms = kwargs["offset_ms"]
                self.hold_time_ms = self.offset_ms - self.onset_ms
            else:
                # Mode A: on/off + hold time
                self.is_on = 1 if kwargs.get("is_on", 1) else 0
                self.hold_time_ms = kwargs.get("hold_time_ms", 500)

        @property
        def mask(self):
            """Return combined bitmask for all bits in this channel."""
            m = 0
            for n in self.ids:
                m |= (1 << n)
            return m

        def __repr__(self):
            bits = ",".join(str(n) for n in self.ids)
            if self.onset_ms is not None:
                return f"<Channel bits=[{bits}] onset={self.onset_ms}ms offset={self.offset_ms}ms>"
            else:
                state = "ON" if self.is_on else "OFF"
                return f"<Channel bits=[{bits}] state={state} hold={self.hold_time_ms}ms>"

    # =========================================================================
    # STIMULUS CLASS (nested)
    # =========================================================================
    class Stimulus:
        def __init__(self, channels):
            """
            channels: list of Channel objects (either hold-based or onset/offset-based)
            """
            self.channels = channels

        @classmethod
        def from_ordered_channels(cls, channels):
            """Create a stimulus from a list of Channel objects (sequential)."""
            return cls(channels)

        @classmethod
        def from_timed_channels(cls, channels):
            """Create a stimulus from a list of Channel objects with onset/offset times."""
            return cls(channels)
        
        @classmethod
        def from_csv_matrix(cls, csv_path, col_ms=100):
            """
            Create a Stimulus from a binary matrix CSV.

            Each row = one channel, first column = channel id
            Each column after first = time step (col_ms duration)
            Cell values: 1=ON, 0=OFF

            Example:
            3   1 1 1 1 1 0 0 0 0 ...
            4   0 0 0 0 1 1 1 1 1 ...
            11  0 0 0 0 0 0 0 0 1 1 1 1 1
            """
            # Read CSV into matrix
            with open(csv_path, newline="", encoding="utf-8") as f:
                first_line = f.readline()
                delimiter = '\t' if '\t' in first_line else ','
                f.seek(0)
                reader = csv.reader(f, delimiter=delimiter)
                rows = []
                channel_ids = []
                for row in reader:
                    row = [x.strip() for x in row if x.strip() != '']
                    if not row:
                        continue
                    channel_ids.append(int(row[0]))
                    rows.append([int(x) for x in row[1:]])

            if not rows:
                return cls([])

            n_steps = len(rows[0])
            channels = []

            # Detect onset/offset per channel
            for ch_id, row in zip(channel_ids, rows):
                onset = None
                for i, val in enumerate(row):
                    if val == 1 and onset is None:
                        onset = i * col_ms
                    elif val == 0 and onset is not None:
                        offset = i * col_ms
                        channels.append(Controller.Channel(ids=ch_id,
                                                        onset_ms=onset,
                                                        offset_ms=offset))
                        onset = None
                # Channel still active at the end
                if onset is not None:
                    channels.append(Controller.Channel(ids=ch_id,
                                                    onset_ms=onset,
                                                    offset_ms=n_steps * col_ms))

            return cls(channels)
        
        @classmethod
        def from_csv_matrix_vertical(cls, csv_path, col_ms=100):
            """
            Create a Stimulus from a transposed binary matrix CSV.

            First row = channel IDs as headers
            Each subsequent row = time step (col_ms duration)
            Cell values: 1=ON, 0=OFF

            Example:
            3   4   11
            1   0   0
            1   0   0
            1   1   0
            1   1   0
            1   1   1
            0   1   1
            0   1   1
            ...
            """
            # Read CSV into matrix
            with open(csv_path, newline="", encoding="utf-8") as f:
                first_line = f.readline()
                delimiter = '\t' if '\t' in first_line else ','
                f.seek(0)
                reader = csv.reader(f, delimiter=delimiter)
                
                # Read all rows
                all_rows = []
                for row in reader:
                    row = [x.strip() for x in row if x.strip() != '']
                    if row:
                        all_rows.append(row)
                
                if not all_rows:
                    return cls([])
                
                # First row contains channel IDs
                channel_ids = [int(x) for x in all_rows[0]]
                
                # Remaining rows contain time steps
                time_steps = [[int(x) for x in row] for row in all_rows[1:]]
            
            if not time_steps:
                return cls([])
            
            n_steps = len(time_steps)
            channels = []
            
            # Process each channel (column)
            for ch_idx, ch_id in enumerate(channel_ids):
                onset = None
                for step_idx, step_row in enumerate(time_steps):
                    val = step_row[ch_idx]
                    if val == 1 and onset is None:
                        onset = step_idx * col_ms
                    elif val == 0 and onset is not None:
                        offset = step_idx * col_ms
                        channels.append(Controller.Channel(ids=ch_id,
                                                        onset_ms=onset,
                                                        offset_ms=offset))
                        onset = None
                
                # Channel still active at the end
                if onset is not None:
                    channels.append(Controller.Channel(ids=ch_id,
                                                    onset_ms=onset,
                                                    offset_ms=n_steps * col_ms))
            
            return cls(channels)

        # ---------------------------------------------------------------------
        # SEQUENTIAL MODE (ordered channels + their hold_time_ms)
        # ---------------------------------------------------------------------
        def generate_sequence(self):
            """Sequential mode: each channel activates in order with its own hold time."""
            seq = []
            for ch in self.channels:
                seq.append((ch.mask if ch.is_on else 0, ch.hold_time_ms))
            return seq

        def to_file4arduino(self, file_name):
            """Generate Arduino commands for sequential channels."""
            path2file = os.path.join(os.getcwd(), file_name)
            seq = self.generate_sequence()
            lines = ["clearcode"]
            for mask, dur in seq:
                lines.append(f"addcode:0x{mask:x}/{dur}")
            with open(path2file, "w", encoding="utf-8") as f:
                f.write("\n".join(lines))
            return path2file

        # ---------------------------------------------------------------------
        # TIMED MODE (channels with onset/offset times)
        # ---------------------------------------------------------------------
        def generate_timed_sequence(self):
            """
            Create a time-based activation sequence using channels with onset and offset times.
            """
            events = []
            for ch in self.channels:
                mask = ch.mask
                events.append((ch.onset_ms, mask, "on"))
                events.append((ch.offset_ms, mask, "off"))

            # Sort by time, with OFF events before ON events at same time
            events.sort(key=lambda x: (x[0], 0 if x[2] == "off" else 1))
            
            seq = []
            active = 0
            prev_t = 0

            for t, mask, action in events:
                if t > prev_t:
                    seq.append((active, t - prev_t))
                active = (active | mask) if action == "on" else (active & ~mask)
                prev_t = t

            # final state (off)
            seq.append((0, 0))
            return seq
# bug with sorting?
        # def generate_timed_sequence(self):
        #     """
        #     Create a time-based activation sequence using channels with onset and offset times.
        #     """
        #     events = []
        #     for ch in self.channels:
        #         mask = ch.mask
        #         events.append((ch.onset_ms, mask, "on"))
        #         events.append((ch.offset_ms, mask, "off"))

        #     # Sort by time
        #     events.sort()
        #     seq = []
        #     active = 0
        #     prev_t = 0

        #     for t, mask, action in events:
        #         if t > prev_t:
        #             seq.append((active, t - prev_t))
        #         active = (active | mask) if action == "on" else (active & ~mask)
        #         prev_t = t

        #     # final state (off)
        #     seq.append((0, 0))
        #     return seq

        def to_file4arduino_timed(self, file_name):
            """Generate Arduino commands from onset/offset timed channels."""
            path2file = os.path.join(os.getcwd(), file_name)
            seq = self.generate_timed_sequence()
            lines = ["clearcode"]
            for mask, dur in seq:
                if dur > 0:
                    lines.append(f"addcode:0x{mask:x}/{dur}")
            with open(path2file, "w", encoding="utf-8") as f:
                f.write("\n".join(lines))
            return path2file


