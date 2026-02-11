from psychopy import visual, core, gui, data, event
import numpy, random, os, pygame
from math import *

# -- DISPLAY TEXT --

displayTextDictionary = {
            'en': {'waitMessage':'Please wait.',
                    'interStimMessage':'...',
                    'finishedMessage':'Session finished.',
                    'intensityQuestion':'How intense was the last stimulation on your skin?',
                    'intensityMin':'not at all',
                    # 'intensityMid':'barely',
                    'intensityMax':'very intense',
                    'pleasantnessQuestion':'How pleasant was the last stimulation on your skin?',
                    'pleasantnessMin':'not at all',
                    'pleasantnessMax':'extremely pleasant',
                    },
                    
            'sv': {'waitMessage':'Please wait.',
                    'interStimMessage':'...',
                    'finishedMessage':'Session finished.',
                    'intensityQuestion':'How painful was the last stimulation on your skin?',
                    'intensityMin':'not at all',
                    # 'intensityMid':'barely',
                    'intensityMax':'very intense',
                    'pleasantnessQuestion':'How much did it feel like "pricking"?',
                    'pleasantnessMin':'not at all',
                    'pleasantnessMax':'extremely pleasant',
                    } 
            }

# --


# -- GET INPUT FROM THE EXPERIMENTER --

exptInfo = {'01. Participant Code':'P00', 
            '02. Condition':('practice','baseline','post-stim'), 
            '03. Number of repeats':20, 
            '04. Laser threshold':0.0, 
            '05. Stimulation site':'dorsal left hand',
            '08. Participant language':('en','sv'),
            '09. Folder for saving data':'data'}
exptInfo['10. Date and time']= data.getDateStr(format='%Y-%m-%d_%H-%M-%S') ##add the current time

dlg = gui.DlgFromDict(exptInfo, title='Experiment details', fixed=['10. Date and time'])
if dlg.OK:
    pass ## continue
else:
    core.quit() ## the user hit cancel so exit


## select dictionary according to participant language
displayText = displayTextDictionary[exptInfo['08. Participant language']]

# --


# -- MAKE FOLDER/FILES TO SAVE DATA --

dataFolder = './'+exptInfo['09. Folder for saving data']+'/'
if not os.path.exists(dataFolder):
    os.makedirs(dataFolder)

if not exptInfo['02. Condition'] == 'practice':
    fileName = dataFolder + exptInfo['10. Date and time'] + '_' + exptInfo['01. Participant Code']
    infoFile = open(fileName+'_info.csv', 'w') 
    # for k,v in exptInfo.iteritems(): infoFile.write(k + ',' + str(v) + '\n')
    for k,v in exptInfo.items(): infoFile.write(k + ',' + str(v) + '\n')
    if exptInfo['02. Condition'] == 'pleasantness':
        dataFile = open(fileName+'_pleasantness-data.csv', 'w')
        dataFile.write('stroke,rating\n')
    else:
        dataFile = open(fileName+'_vas-data.csv', 'w')
        dataFile.write('intensity-rating,pleasantness-rating\n')


# ----


# -- SETUP VISUAL ANALOG SCALES AND VISUAL PROMPTS --

## display window and mouse input
win = visual.Window(fullscr=True, screen=1, units='norm', monitor='testMonitor')
mouse = event.Mouse()

## instructions text
waitMessage = visual.TextStim(win, text=displayText['waitMessage'], units='norm')
interStimMessage = visual.TextStim(win, text=displayText['interStimMessage'], units='norm')
finishedMessage = visual.TextStim(win, text=displayText['finishedMessage'], units='norm')

barMarker = visual.TextStim(win, text='|', units='norm')
## pain VAS
intensityVAS = visual.RatingScale(win, low=-10, high=10, precision=10, 
    showValue=False, marker=barMarker, scale = displayText['intensityQuestion'],
    tickHeight=1, stretch=1.5, size=0.8, 
    # labels=[displayText['intensityMin'], '\n\n'+displayText['intensityMid'], displayText['intensityMax']],
    labels=[displayText['intensityMin'], displayText['intensityMax']],
    # tickMarks=[-10,-8,10], mouseOnly = True, pos=(0,0.70))
    tickMarks=[-10,10], mouseOnly = True, pos=(0,0.70))

## pricking VAS
pleasantnessVAS = visual.RatingScale(win, low=-10, high=10, precision=10, 
    showValue=False, marker=barMarker, scale = displayText['pleasantnessQuestion'],
    tickHeight=1, stretch=1.5, size=0.8,
    labels=[displayText['pleasantnessMin'], displayText['pleasantnessMax']],
    tickMarks=[-10,10], mouseOnly = True, pos=(0,0))

# ## heat VAS
# heatVAS = visual.RatingScale(win, low=-10, high=10, precision=10, 
#     showValue=False, marker=barMarker, scale = displayText['heatQuestion'],
#     tickHeight=1, stretch=1.5, size=0.8,
#     labels=[displayText['heatMin'], displayText['heatMax']],
#     tickMarks=[-10,10], mouseOnly = True, pos=(0,-0.7))

# --


# -- RUN THE EXPERIMENT --

## tell participant to wait (experimenter triggers experiment with keyboard)
event.clearEvents()
waitMessage.draw()
win.flip()
if 'escape' in event.waitKeys():
    if not exptInfo['02. Condition'] == 'practice': infoFile.close(); dataFile.close()
    core.quit()


# pain loop
else:
    
    ## loop through the trials
    for trialNum in range(exptInfo['03. Number of repeats']):
        intensityVAS.reset()
        pleasantnessVAS.reset()
       
        
        ## display stim message and cue experimenter
        event.clearEvents()
        interStimMessage.draw()
        win.flip()
        
        ## present VAS
        core.wait(3.0) # 3 seconds "..." interval
        event.clearEvents()
        while intensityVAS.noResponse or pleasantnessVAS.noResponse:
            intensityVAS.draw()
            pleasantnessVAS.draw()
            win.flip()
            if event.getKeys(['escape']):
                print('user aborted')
                if not exptInfo['02. Condition'] == 'practice': infoFile.close(); dataFile.close()
                core.quit()
        
        ## check rating
        intensityRating = intensityVAS.getRating()
        pleasantnessRating = pleasantnessVAS.getRating()
       
        print('Intensity, pleasantness (-10,10) = {}, {}\n' .format(intensityRating,pleasantnessRating))
        
        ## record the data if not a practice run
        if not exptInfo['02. Condition'] == 'practice':
            dataFile.write('{},{}\n' .format(intensityRating,pleasantnessRating)) 
        
        print('{} of {} trials complete\n' .format(trialNum+1, exptInfo['03. Number of repeats']))

# ----

# -- END OF EXPERIMENT --

print('\n=== EXPERIMENT FINISHED ===\n')

## save data to file
if not exptInfo['02. Condition'] == 'practice':
    infoFile.close()
    dataFile.close()
    print('Data saved {}\n\n' .format(fileName))
else:
    print('Practice only, no data saved.')
    
## prompt at the end of the experiment
event.clearEvents()
mouse.clickReset()
finishedMessage.draw()
win.flip()
while 1:
    core.wait(2)
    core.quit()
## ----