========================================
How to use Channel, Stimulus, and ArduinoController classes
========================================

# Directory structure example
# ├── channel.py
# ├── stimulus.py
# ├── arduino_controller.py
# ├── create_stimulus.py
# ├── apply_stim_from_file.py
# ├── sequential.txt
# ├── join_hold.txt
# ├── join_stay.txt

------------------------------------------------------------
1. Channel class (channel.py)
------------------------------------------------------------
Represents a single output channel (or a group of bits).

Usage:
>>> from channel import Channel

# Single-bit channel: bit 0, active for 10 ms
>>> ch1 = Channel(0, 10)

# Multi-bit channel: bits 3 and 17 active together for 10 ms
>>> ch2 = Channel([3, 17], 10)

Each Channel stores:
- number  → int or list[int], 0–31 (bit positions)
- hold_time_ms → how long the channel remains ON


------------------------------------------------------------
2. Stimulus class (stimulus.py)
------------------------------------------------------------
Creates a full timed sequence of channel activations.

Usage:
>>> from channel import Channel
>>> from stimulus import Stimulus

# Define channels
>>> ch1 = Channel(0, 10)
>>> ch2 = Channel(1, 10)
>>> ch3 = Channel(2, 10)

# Create stimulus: channels + delay between activations
>>> stim = Stimulus([ch1, ch2, ch3], delay_ms=5)

# Generate and save stimulus as Arduino commands
>>> stim.to_arduino_commands("sequential.txt", mode="sequential")
>>> stim.to_arduino_commands("join_hold.txt", mode="join_hold")
>>> stim.to_arduino_commands("join_stay.txt", mode="join_stay")

Modes:
- "sequential" → each channel turns ON/OFF one after another
- "join_hold"  → each joins after delay and holds its own ON time
- "join_stay"  → each joins after delay, all OFF together at the end

Each generated text file contains lines like:
    clearcode
    addcode:0x1/10
    addcode:0x2/10
    addcode:0x4/10
    addcode:0x0/10


------------------------------------------------------------
3. ArduinoController class (arduino_controller.py)
------------------------------------------------------------
Handles serial communication with Arduino.

Usage:
>>> from arduino_controller import ArduinoController

# Create controller instance and connect
>>> ard = ArduinoController(port="COM7", baudrate=115200)
>>> ard.connect()

# Send individual commands
>>> ard.send("clearcode")
>>> ard.send("exec")

# Send entire stimulus file
>>> ard.send_file("sequential.txt")
>>> ard.send_file_line_by_line("join_hold.txt", delay=0.01)

# Example workflow
>>> from channel import Channel
>>> from stimulus import Stimulus
>>> from arduino_controller import ArduinoController

>>> ch1 = Channel(0, 10)
>>> ch2 = Channel(1, 10)
>>> ch3 = Channel(2, 10)

>>> stim = Stimulus([ch1, ch2, ch3], delay_ms=5)
>>> stim.to_arduino_commands("join_hold.txt", mode="join_hold")

>>> ard = ArduinoController("COM7", 115200)
>>> ard.connect()
>>> ard.send_file_line_by_line("join_hold.txt", delay=0.01)
>>> ard.send("exec")

# Disconnect when done
>>> ard.disconnect()

------------------------------------------------------------
4. Notes
------------------------------------------------------------
- Each bit corresponds to one channel (0–31).
- Multi-bit channels allow simultaneous activation (e.g. [3,17]).
- Generated files are human-readable and reusable.
- The controller automatically prints Arduino responses in the background.
