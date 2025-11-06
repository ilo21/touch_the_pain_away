from controller import Controller
import time
import os

stim_dir = "stim_files"

# Example 1: Sequential stimulus
print("=== Create stimulus from ordered channels ===")
    
# Create channels
channels = [
        Controller.Channel(ids=3, is_on=1, hold_time_ms=500),
        Controller.Channel(ids=4, is_on=1, hold_time_ms=500),
        Controller.Channel(ids=11, is_on=1, hold_time_ms=500),
]
    
# Create stimulus from ordered channels and upload
stim1 = Controller.Stimulus.from_ordered_channels(channels)
stim1.to_file4arduino(os.path.join(stim_dir, "stim_from_ordered_channels.txt"))
    
    
# Example 2: Timed stimulus
print("\n=== Create stimulus from timed channels ===")

channels_timed = [
            Controller.Channel(ids=3, onset_ms=0, offset_ms=500),
            Controller.Channel(ids=4, onset_ms=400, offset_ms=900),
            Controller.Channel(ids=11, onset_ms=800, offset_ms=1300),
]
        
stim2 = Controller.Stimulus.from_timed_channels(channels_timed)
stim2.to_file4arduino_timed(os.path.join(stim_dir,"stim_from_timed_channels.txt"))
  
    
# Example 3: CSV matrix stimulus
print("\n=== Create stimulus from csv ===\n")

stim3 = Controller.Stimulus.from_csv_matrix(os.path.join(stim_dir,"motion_stim.csv"), col_ms=100)
stim3.to_file4arduino_timed(os.path.join(stim_dir, "stim_from_csv.txt"))
  

controller = Controller(port="COM7")
controller.connect()
time.sleep(2)
controller.send_file_line_by_line(os.path.join(stim_dir,"stim_from_ordered_channels.txt"), delay=0.01)
time.sleep(1)
controller.exec()
time.sleep(1)
controller.disconnect()