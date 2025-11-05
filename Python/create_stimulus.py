from channel import Channel
from stimulus import Stimulus

'''
Example script to create a stimulation pattern and save it to a text file.
The generated text file can then be used with apply_stim_from_file.py to apply the stimulation.
'''

# Define channels and their hold times
ch1 = Channel(1, 50)             # single bit
ch2 = Channel([1, 20], 50)       # multi-bit channel
ch3 = Channel(20, 50)            # single bit

# Create a pattern for the stimulus (ordered list of channels)
"""
    mode:
        'sequential' -> one channel after another, no overlap (delay is not used)
        'join_stay'  -> each joins after delay, all off together at the end
        'join_hold'  -> each joins after delay, stays on for its own hold time
"""
# since each hold is 500 ms and I want 1s gap of no stim, delay is 1500 ms
# Define delay between activations
stim = Stimulus([ch1, ch2, ch3], delay_ms=10)
stim.to_arduino_commands("test_b.txt", mode="join_hold")
print("Done")