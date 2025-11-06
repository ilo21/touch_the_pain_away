class Channel:
    def __init__(self, ids, *args, **kwargs):
        """
        Two valid constructors:

        Constructor 1:
            Channel(ids, is_on=1, hold_time_ms=500)
              - ids: int or list[int]
              - is_on: 1 or 0 (default 1)
              - hold_time_ms: duration in ms

        Constructor 1:
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

