from channel import Channel
from stimulus import Stimulus
import os

stim_dir = "stim_files"

# sequential channels
channels_ordered = [
    Channel(3, hold_time_ms=10000),
    Channel(4, hold_time_ms=10000),
    Channel(11, hold_time_ms=10000)
]
# Create stimulus from ordered channels
stim1 = Stimulus.from_ordered_channels(channels_ordered)
stim1.to_file4arduino(os.path.join(stim_dir,"sequential_stim.txt"))

# timed channels
ch_annels_timed = [
    Channel(3, onset_ms=0, offset_ms=10000),
    Channel(4, onset_ms=10000, offset_ms=20000),
    Channel(11, onset_ms=20000, offset_ms=30000),
    Channel(12, onset_ms=0, offset_ms=30000)
]
# Create stimulus from timed channels
stim2 = Stimulus.from_timed_channels(ch_annels_timed)
stim2.to_file4arduino_timed(os.path.join(stim_dir,"timed_stimulus.txt"))

# Load stimulus from CSV matrix, define column duration as i.e. 1000ms
stim3 = Stimulus.from_csv_matrix(os.path.join(stim_dir,"motion_stim.csv"), col_ms=1000)
stim3.to_file4arduino_timed(os.path.join(stim_dir,"stim_from_csv.txt"))


print("Done")