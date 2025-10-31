from arduino_controller import ArduinoController
import time

'''
Example script to apply a stimulation pattern from a text file.
The text file should contain one command per line, formatted as expected by the Arduino.
'''

arduino = ArduinoController("COM7", 115200)
arduino.connect()
time.sleep(2)
# set stim from file
arduino.send_file_line_by_line("test_stimulus.txt", delay=0.01)
time.sleep(1)
# apply
arduino.exec()
time.sleep(3)
arduino.disconnect()
