# Touch The Pain Away
Multichannel hugger<br><br>
This repo is a work in progress to share the code between the groups.

In windows search field, start typing miniconda. That will open a miniconda terminal with:

(base) C:\Users\username>

activate the ttpa_psychopy environment that has all libraries necessary to run the code:

conda activate ttpa_psychopy

Navigate to the folder where the script is:

cd C:\LAB\TTPA\touch_the_pain_away-main\Python

Github version (use):
cd C:\Users\username\Documents\touch_the_pain_away\Python

Now you can run the script:
	
python controller_test.py


This will execute the pattern from stim_files/motion_stim_vertical.csv where the headers are channel numbes (don't change), and each row is 100ms either on(1) or off(0)

To change the pattern file name or time, edit the following line in the code (controller_test.py):

controller.send_stimulus_from_csv_vertical(os.path.join(stim_dir,"motion_stim_vertical.csv"), col_ms=100)