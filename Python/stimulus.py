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
    
    # @classmethod
    # def from_csv(cls, csv_path):
    #     """
    #     Create a stimulus by reading a CSV file.

    #     CSV columns (example):
    #     channel_numbers,hold_time_ms,is_on
    #     0,10,1
    #     1,10,1
    #     2,10,1
    #     3|17,10,1   # use '|' to separate multiple bits for a group
    #     """
    #     channels = []
    #     with open(csv_path, newline='', encoding="utf-8") as f:
    #         reader = csv.DictReader(f)
    #         for row in reader:
    #             # parse multi-bit channels
    #             nums = [int(x) for x in row["channel_numbers"].split("|")]
    #             hold = int(row["hold_time_ms"])
    #             is_on = int(row.get("is_on", 1))
    #             channels.append(Channel(nums, hold, is_on))
    #     return cls(channels)

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



