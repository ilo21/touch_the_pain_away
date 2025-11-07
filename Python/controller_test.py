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


# ############################################################
# # Examples of creating stimulus files with arduino commands
# ############################################################
# # Sequential stimulus
# print("=== Create stimulus from ordered channels ===")
    
# # Create channels (define id, on/off state, and hold time)
# channels = [
#         Controller.Channel(ids=3, is_on=1, hold_time_ms=500),
#         Controller.Channel(ids=4, is_on=1, hold_time_ms=500),
#         Controller.Channel(ids=11, is_on=1, hold_time_ms=500),
# ]
    
# # Create stimulus from ordered channels and upload
# stim1 = Controller.Stimulus.from_ordered_channels(channels)
# stim1.to_file4arduino(os.path.join(stim_dir, "stim_from_ordered_channels.txt"))
    
# ###########################################################  
# # Timed stimulus
# print("\n=== Create stimulus from timed channels ===")

# # Create channels (define id, onset and offset time)
# channels_timed = [
#             Controller.Channel(ids=3, onset_ms=0, offset_ms=100),
#             Controller.Channel(ids=4, onset_ms=100, offset_ms=150),
#             Controller.Channel(ids=11, onset_ms=100, offset_ms=300),
# ]
        
# stim2 = Controller.Stimulus.from_timed_channels(channels_timed)
# stim2.to_file4arduino_timed(os.path.join(stim_dir,"stim_from_timed_channels.txt"))
  
# ###########################################################  
# # CSV matrix stimulus
# print("\n=== Create stimulus from csv ===\n")

# stim3 = Controller.Stimulus.from_csv_matrix(os.path.join(stim_dir,"motion_stim.csv"), col_ms=100)
# stim3.to_file4arduino_timed(os.path.join(stim_dir, "stim_from_csv.txt"))
  

# controller = Controller(port="COM7")
# controller.connect()
# time.sleep(2)
# controller.send_file_line_by_line(os.path.join(stim_dir,"stim_from_timed_channels.txt"), delay=0.01)
# time.sleep(1)
# controller.exec()
# time.sleep(1)
# controller.disconnect()

