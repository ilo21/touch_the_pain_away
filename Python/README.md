# Arduino Stimulus Controller

Unified Python interface for generating and uploading digital stimulation patterns to an Arduino device.  
Supports sequential, time-based, and matrix (CSV-defined) stimuli.

---

### `Easiest Usage Example`

```python
from controller import Controller
import time
import os

stim_dir = "stim_files"

"""
        The easiest way to create and run the stumulus is to prepare a CSV file
        Example binary matrix CSV 
        3   1 1 1 1 1 0 0 0 0 0 0 0 0 0
        4   0 0 0 0 0 1 1 1 1 1 0 0 0 0
        11  0 0 0 0 0 0 0 0 0 1 1 1 1 1

        Each row corresponds to one channel, with the first column being the channel id,
        and the following columns being 0/1 values indicating OFF/ON states.
        The time duration per column is specified when uploading the stimulus.
"""

print("=== Connect to the controller ===")
controller = Controller(port="COM7")
controller.connect()
time.sleep(2)
print("\n=== Upload stimulus from csv to the controller ===")
# select the desired time duration per column (col_ms)
controller.send_stimulus_from_csv(os.path.join(stim_dir,"motion_stim.csv"), col_ms=10)
time.sleep(1)
print("\n=== Run ===")
controller.exec()
time.sleep(1)
controller.disconnect()
```

## Overview

This module provides:
- **Serial communication** with an Arduino (`Controller` class)  
- **Flexible stimulus generation** via nested classes:
  - `Controller.Channel` – defines a single channel (bit ID + timing)
  - `Controller.Stimulus` – builds and exports multi-channel patterns

Stimuli are exported as text command files (e.g. `stim_from_csv.txt`) and sent to Arduino over serial.

---

## Class Structure

### `Controller`
Handles serial connection and file transfer.

**Key methods**
- `connect()` / `disconnect()` – open/close serial port  
- `send(command)` – send a single line  
- `send_file_line_by_line(filename, delay=0.01)` – send text file commands line by line  
- `send_stimulus_from_csv(self, csv_path, col_ms=100, delay=0.01)` – send stimulus defined in CSV format
- `exec()` – tell Arduino to execute the uploaded sequence  

---

### `Controller.Channel`
Represents one digital output line.

**Two initialization modes**

**Sequential mode, with the duration defined**
```python
Controller.Channel(ids=3, is_on=1, hold_time_ms=500)
```
**Timed mode, with on and off times defined**
```python
Controller.Channel(ids=3, onset_ms=0, offset_ms=500)
```

### `Controller.Stimulus`
Combines channels into executable sequences.

**Constructors**
- Stimulus.from_ordered_channels(channels)

- Stimulus.from_timed_channels(channels)

- Stimulus.from_csv_matrix(csv_path, col_ms=100)<br>
CSV format: first column with channel ids, other columns = time step, each row = channel states (0=off, 1=on)
```
3   1 1 1 1 1 0 0 0 0 0 0 0 0 0
4   0 0 0 0 0 1 1 1 1 1 0 0 0 0
11  0 0 0 0 0 0 0 0 0 1 1 1 1 1
```



**Export to txt file with commands for Arduino**
- to_file4arduino(filename) – if the stimulus was created using ordered channels

- to_file4arduino_timed(filename) – if the stimulus was created using timed channels or CSV matrix

---

### `More Usage Examples`

```python
from controller import Controller
import os, time

stim_dir = "stim_files"

# Sequential stimulus
channels = [
    Controller.Channel(ids=3, hold_time_ms=500),
    Controller.Channel(ids=4, hold_time_ms=500),
    Controller.Channel(ids=11, hold_time_ms=500),
]
stim1 = Controller.Stimulus.from_ordered_channels(channels)
stim1.to_file4arduino(os.path.join(stim_dir, "stim_from_ordered_channels.txt"))

# Timed stimulus
channels_timed = [
    Controller.Channel(ids=3, onset_ms=0, offset_ms=500),
    Controller.Channel(ids=4, onset_ms=400, offset_ms=900),
    Controller.Channel(ids=11, onset_ms=800, offset_ms=1300),
]
stim2 = Controller.Stimulus.from_timed_channels(channels_timed)
stim2.to_file4arduino_timed(os.path.join(stim_dir, "stim_from_timed_channels.txt"))

# CSV-based stimulus
stim3 = Controller.Stimulus.from_csv_matrix(os.path.join(stim_dir, "motion_stim.csv"), col_ms=100)
stim3.to_file4arduino_timed(os.path.join(stim_dir, "stim_from_csv.txt"))

# Upload and execute
controller = Controller(port="COM7")
controller.connect()
time.sleep(2)
controller.send_file_line_by_line(os.path.join(stim_dir, "stim_from_ordered_channels.txt"), delay=0.01)
controller.exec()
controller.disconnect()
```

# TODO
- more tests!
