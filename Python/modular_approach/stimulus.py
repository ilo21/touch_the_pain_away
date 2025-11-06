from channel import Channel
import os
import csv

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
                        channels.append(Channel(ids=ch_id,
                                                        onset_ms=onset,
                                                        offset_ms=offset))
                        onset = None
                # Channel still active at the end
                if onset is not None:
                    channels.append(Channel(ids=ch_id,
                                                    onset_ms=onset,
                                                    offset_ms=n_steps * col_ms))

            return cls(channels)

    # -------------------------------------------------------------------------
    # SEQUENTIAL MODE (hold_time_ms)
    # -------------------------------------------------------------------------
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
            lines.append(f"addcode:0x{mask:X}/{dur}")
        with open(path2file, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

    # -------------------------------------------------------------------------
    # TIMED MODE (onset/offset)
    # -------------------------------------------------------------------------
    def generate_timed_sequence(self):
        """
        Create a time-based activation sequence using channels with onset and offset times.
        Each Channel must define:
          - ids (int or list[int])
          - onset_ms
          - offset_ms
          - is_on (optional)
        """
        events = []
        for ch in self.channels:
            mask = ch.mask
            events.append((ch.onset_ms, mask, "on"))
            events.append((ch.offset_ms, mask, "off"))

        # Sort by time
        events.sort()
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

    def to_file4arduino_timed(self, file_name):
        """Generate Arduino commands from onset/offset timed channels."""
        path2file = os.path.join(os.getcwd(), file_name)
        seq = self.generate_timed_sequence()
        lines = ["clearcode"]
        for mask, dur in seq:
            if dur > 0:
                lines.append(f"addcode:0x{mask:X}/{dur}")
        with open(path2file, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))



