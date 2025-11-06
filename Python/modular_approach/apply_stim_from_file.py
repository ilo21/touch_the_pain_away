from arduino_controller import ArduinoController
import time

"""
Example script to apply a stimulation pattern from a text file.
The text file should contain one command per line, formatted as expected by the Arduino.
Execution starts only after user confirmation.
"""

arduino = ArduinoController("COM7", 115200)
arduino.connect()
time.sleep(2)

# Load stimulation commands from file
# arduino.send_file_line_by_line("sequential_stim.txt", delay=0.01)
arduino.send_file_line_by_line("timed_stimulus.txt", delay=0.01)
time.sleep(1)

# # Wait for user to press Enter or Space before executing
# input("Pre" \
# "ss Enter or Space to start stimulation...")

arduino.exec()
time.sleep(2)
arduino.disconnect()

