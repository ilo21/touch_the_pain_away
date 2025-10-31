class Channel:
    def __init__(self, numbers, hold_time_ms):
        """
        numbers: int or list[int] — bit positions to activate simultaneously
        hold_time_ms: duration this channel (or bit group) stays active
        """
        if isinstance(numbers, int):
            self.numbers = [numbers]
        else:
            self.numbers = list(numbers)
        self.hold_time_ms = hold_time_ms

    @property
    def mask(self):
        """Return combined bitmask for all bits in this channel."""
        m = 0
        for n in self.numbers:
            m |= (1 << n)
        return m
