from channel import Channel
import os

class Stimulus:
    def __init__(self, channels, delay_ms):
        """
        channels: list of Channel objects in intended activation order
        delay_ms: time between activations (stagger)
        """
        self.channels = channels
        self.delay = delay_ms

    def generate_sequence(self, mode="sequential"):
        """
        mode:
          'sequential' -> one channel after another, no overlap
          'join_stay'  -> each joins after delay, all off together at the end
          'join_hold'  -> each joins after delay, stays on for its own hold time
        """
        seq = []
        active_mask = 0

        if mode == "sequential":
            for ch in self.channels:
                seq.append((ch.mask, ch.hold_time_ms))
            seq.append((0, self.channels[-1].hold_time_ms))

        elif mode == "join_stay":
            for ch in self.channels:
                active_mask |= ch.mask
                seq.append((active_mask, self.delay))
            seq.append((0, self.channels[-1].hold_time_ms))

        elif mode == "join_hold":
            timeline = []
            for i, ch in enumerate(self.channels):
                start = i * self.delay
                end = start + ch.hold_time_ms
                timeline.append((start, ch.mask, "on"))
                timeline.append((end, ch.mask, "off"))

            timeline.sort()
            active = 0
            prev_t = 0
            for t, bitmask, action in timeline:
                if t > prev_t:
                    seq.append((active, t - prev_t))
                active = active | bitmask if action == "on" else active & ~bitmask
                prev_t = t
            seq.append((0, self.delay))
        else:
            raise ValueError("Invalid mode")

        return seq

    # write a sequence to a file in the current working directory
    def to_arduino_commands(self, file_name, mode="sequential"):
        path2file = os.path.join(os.path.join(os.getcwd(), file_name))
        seq = self.generate_sequence(mode)
        lines = ["clearcode"]
        for mask, dur in seq:
            lines.append(f"addcode:0x{mask:X}/{dur}")
        # lines.append("exec")  # optional
        content = "\n".join(lines)
        with open(path2file, "w", encoding="utf-8") as f:
            f.write(content)