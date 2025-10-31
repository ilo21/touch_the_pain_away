========================================
How to use connection.py from IPython
========================================

1. Start IPython or Jupyter terminal.

   Example:
   >>> ipython

2. Load the script once so all functions and the serial thread start.

   >>> %run connection.py --port COM7 --baud 115200

   The script will:
   - Connect to Arduino on COM7 at 115200 baud
   - Start a background thread printing all incoming serial messages

3. Available functions
   --------------------

   # Send a single text command to Arduino
   >>> send("clearcode")

   # Send full text file content in one write
   >>> file("sequential.txt")

   # Send file line by line with 10 ms delay between each line
   >>> file_line_by_line("join_hold.txt", delay=0.01)

   # Send specific command pattern: <cmd>/<index>:<value>
   >>> send_command("Target", 0, 45)

   # Shortcut for setting temperature target
   >>> temp(0, 37)

   # Disconnect serial port
   >>> discon()

   # Reconnect serial port
   >>> recon()

4. Typical use with generated stimulus file
   ----------------------------------------

   >>> file_line_by_line("sequential.txt", delay=0.01)
   >>> send("exec")

   Arduino output will appear automatically in the terminal
   thanks to the background print thread.

5. Notes
   ------
   - Ensure Arduino is running at same baud rate.
   - COM7 is default; change with:
        %run connection.py --port COM5 --baud 9600
   - Stop printing thread by interrupting IPython (Ctrl+C).
