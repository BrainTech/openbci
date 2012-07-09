#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This experiment was created using PsychoPy2 Experiment Builder (v1.74.00), pon, 9 lip 2012, 02:14:19
If you publish work using this script please cite the relevant PsychoPy publications
  Peirce, JW (2007) PsychoPy - Psychophysics software in Python. Journal of Neuroscience Methods, 162(1-2), 8-13.
  Peirce, JW (2009) Generating stimuli for neuroscience using PsychoPy. Frontiers in Neuroinformatics, 2:10. doi: 10.3389/neuro.11.010.2008
"""

from __future__ import division #so that 1/3=0.333 instead of 1/3=0
from psychopy import visual, core, data, event, logging, gui
from psychopy.constants import * #things like STARTED, FINISHED
import numpy as np  # whole numpy lib is available, prepend 'np.'
from numpy import sin, cos, tan, log, log10, pi, average, sqrt, std, deg2rad, rad2deg, linspace, asarray
from numpy.random import random, randint, normal, shuffle
import os #handy system and path functions

#store info about the experiment session
expName='None'#from the Builder filename that created this script
expInfo={}
expInfo['date']=data.getDateStr()#add a simple timestamp
expInfo['expName']=expName
#setup files for saving
if not os.path.isdir('/home/mati/obci_temp'):
    os.makedirs('/home/mati/obci_temp') #if this fails (e.g. permissions) we will get error
filename='/home/mati/obci_temp' + os.path.sep + '%s' %(expInfo['date'])
logging.console.setLevel(logging.WARNING)#this outputs to the screen, not a file

#an ExperimentHandler isn't essential but helps with data saving
thisExp = data.ExperimentHandler(name=expName, version='',
    extraInfo=expInfo, runtimeInfo=None,
    originPath=None,
    savePickle=True, saveWideText=False,
    dataFileName=filename)

#setup the Window
win = visual.Window(size=(1280, 800), fullscr=True, screen=0, allowGUI=False, allowStencil=False,
    monitor='testMonitor', color='white', colorSpace='rgb', units='norm')

#Initialise components for Routine "intro"
introClock=core.Clock()
text_7=visual.TextStim(win=win, ori=0, name='text_7',
    text='Prepare everything. Hit space to continue...',
    font='Arial',
    pos=[0, 0], height=0.1,wrapWidth=None,
    color='black', colorSpace='rgb', opacity=1,
    depth=0.0)

#Initialise components for Routine "baseline_instruction"
baseline_instructionClock=core.Clock()
text_5=visual.TextStim(win=win, ori=0, name='text_5',
    text='Now sit and relax for a moment. Just look at the screen and do nothing...',
    font='Arial',
    pos=[0, 0], height=0.1,wrapWidth=None,
    color='black', colorSpace='rgb', opacity=1,
    depth=0.0)

#Initialise components for Routine "baseline"
baselineClock=core.Clock()
text_4=visual.TextStim(win=win, ori=0, name='text_4',
    text='Now sit and relax for a moment. Just look at the screen and do nothing...',
    font='Arial',
    pos=[0, 0], height=0.1,wrapWidth=None,
    color='black', colorSpace='rgb', opacity=1,
    depth=0.0)


#Initialise components for Routine "instruct"
instructClock=core.Clock()
instrText=visual.TextStim(win=win, ori=0, name='instrText',
    text="In a moment you'll see a list of words displayed one by one at the center of the screen. Fonts will be of different colours. Your task will be to recognise font colour and to push that colour's button as fast as possible. Now - put your four fingers on buttons 7 8 9 0. Leave your hand at that position till the end of the experiment. Hit 7 to continue ...",
    font='Arial',
    pos=[0, 0], height=0.08,wrapWidth=None,
    color='black', colorSpace='rgb', opacity=1,
    depth=0.0)

#Initialise components for Routine "learn1"
learn1Clock=core.Clock()
text_8=visual.TextStim(win=win, ori=0, name='text_8',
    text='Hit 7 button (this button is assigned to GREEN colour).',
    font='Arial',
    pos=[0, 0], height=0.1,wrapWidth=None,
    color='black', colorSpace='rgb', opacity=1,
    depth=0.0)
text_9=visual.TextStim(win=win, ori=0, name='text_9',
    text=None,
    font='Arial',
    pos=[0.5, -0.8], height=0.1,wrapWidth=None,
    color='grey', colorSpace='rgb', opacity=1,
    depth=-2.0)

#Initialise components for Routine "learn2"
learn2Clock=core.Clock()
text_10=visual.TextStim(win=win, ori=0, name='text_10',
    text='Hit 8 button (this button is assigned to RED colour).',
    font='Arial',
    pos=[0, 0], height=0.1,wrapWidth=None,
    color='black', colorSpace='rgb', opacity=1,
    depth=0.0)
text_11=visual.TextStim(win=win, ori=0, name='text_11',
    text='green                         ',
    font='Arial',
    pos=[0.5, -0.8], height=0.1,wrapWidth=None,
    color='grey', colorSpace='rgb', opacity=1,
    depth=-2.0)

#Initialise components for Routine "learn3"
learn3Clock=core.Clock()
text_12=visual.TextStim(win=win, ori=0, name='text_12',
    text='Hit 9 button (this button is assigned to YELLOW colour).',
    font='Arial',
    pos=[0, 0], height=0.1,wrapWidth=None,
    color='black', colorSpace='rgb', opacity=1,
    depth=0.0)
text_13=visual.TextStim(win=win, ori=0, name='text_13',
    text='green    red                    ',
    font='Arial',
    pos=[0.5, -0.8], height=0.1,wrapWidth=None,
    color='grey', colorSpace='rgb', opacity=1,
    depth=-2.0)

#Initialise components for Routine "learn4"
learn4Clock=core.Clock()
text_14=visual.TextStim(win=win, ori=0, name='text_14',
    text='Hit 0 button (this button is assigned to BLUE colour).',
    font='Arial',
    pos=[0, 0], height=0.1,wrapWidth=None,
    color='black', colorSpace='rgb', opacity=1,
    depth=0.0)
text_15=visual.TextStim(win=win, ori=0, name='text_15',
    text='green    red    yellow        ',
    font='Arial',
    pos=[0.5, -0.8], height=0.1,wrapWidth=None,
    color='grey', colorSpace='rgb', opacity=1,
    depth=-2.0)

#Initialise components for Routine "ready_2"
ready_2Clock=core.Clock()
text_6=visual.TextStim(win=win, ori=0, name='text_6',
    text='You learned colours assigned to buttons. If ready hit 7 button to start the experiment.',
    font='Arial',
    pos=[0, 0], height=0.1,wrapWidth=None,
    color='black', colorSpace='rgb', opacity=1,
    depth=0.0)
text_16=visual.TextStim(win=win, ori=0, name='text_16',
    text='green    red    yellow    blue',
    font='Arial',
    pos=[0.5, -0.8], height=0.1,wrapWidth=None,
    color='grey', colorSpace='rgb', opacity=1,
    depth=-2.0)

#Initialise components for Routine "trial"
trialClock=core.Clock()
word=visual.TextStim(win=win, ori=0, name='word',
    text='nonsense',
    font='Arial',
    pos=[0, 0], height=0.2,wrapWidth=None,
    color=1.0, colorSpace='rgb', opacity=1,
    depth=0.0)
# defaults
CONDITIONS = ['con', 'exp']
BLOCKS_COUNT = 1
TRIALS_COUNT = 4
KEYS_MAP = {'green':'7', 'red':'8', 'yellow':'9', 'blue':'0'}
CONDITIONS_FILE='~/obci/exps/dorota2/trialTypes.csv'
BASELINE_DURATION=5

try:
    from exps import exps_helper
    from exps.dorota2 import dorota_helper
    import time, sys
    H = exps_helper.ExpsHelper(config_module=sys.modules[__name__])

    # from config 
    p = H.get_param('conditions').split(';')
    if len(p) > 0:
        CONDITIONS = p
    p = H.get_param('blocks_count')
    if len(p) > 0:
        BLOCKS_COUNT = int(p)
    p = H.get_param('trials_count')
    if len(p) > 0:
        TRIALS_COUNT = int(p)
    p = H.get_param('keys_map')
    if len(p) > 0:
        KEYS_MAP = eval(p)
    p = H.get_param('conditions_file')
    if len(p) > 0:
        CONDITIONS_FILE=p
    p = H.get_param('baseline_duration')
    if len(p) > 0:
        BASELINE_DURATION=float(p)
#generate csv file
    dorota_helper.generate_trials(CONDITIONS_FILE, CONDITIONS, BLOCKS_COUNT, TRIALS_COUNT, KEYS_MAP)

except Exception, e:
    print("No obci mode??????????????????: ")
    print(e)

#control variables
condition_index = 0
block_index = 0
trial_index = 0
fixation=visual.TextStim(win=win, ori=0, name='fixation',
    text='+',
    font='Arial',
    pos=[0, 0], height=0.1,wrapWidth=None,
    color='black', colorSpace='rgb', opacity=1,
    depth=-3.0)
hint=visual.TextStim(win=win, ori=0, name='hint',
    text='green    red    yellow    blue',
    font='Arial',
    pos=[0.5, -0.8], height=0.1,wrapWidth=None,
    color='grey', colorSpace='rgb', opacity=1,
    depth=-4.0)

#Initialise components for Routine "block_break"
block_breakClock=core.Clock()
text_2=visual.TextStim(win=win, ori=0, name='text_2',
    text='Remember - pay attention to font colours!!!',
    font='Arial',
    pos=[0, 0], height=0.1,wrapWidth=None,
    color='black', colorSpace='rgb', opacity=1,
    depth=0.0)


#Initialise components for Routine "condition_break"
condition_breakClock=core.Clock()
text_3=visual.TextStim(win=win, ori=0, name='text_3',
    text='Get some rest.. Hit one of 7 8 9 0 to continue ...',
    font='Arial',
    pos=[0, 0], height=0.1,wrapWidth=None,
    color='black', colorSpace='rgb', opacity=1,
    depth=0.0)


#Initialise components for Routine "thanks"
thanksClock=core.Clock()
thanksText=visual.TextStim(win=win, ori=0, name='thanksText',
    text='This is the end of the experiment.\n\nThanks!',
    font='arial',
    pos=[0, 0], height=0.3,wrapWidth=None,
    color=[1, 1, 1], colorSpace='rgb', opacity=1,
    depth=0.0)

# Create some handy timers
globalClock=core.Clock() #to track the time since experiment started
routineTimer=core.CountdownTimer() #to track time remaining of each (non-slip) routine 

#------Prepare to start Routine"intro"-------
t=0; introClock.reset() #clock 
frameN=-1
#update component parameters for each repeat
key_resp_3 = event.BuilderKeyResponse() #create an object of type KeyResponse
key_resp_3.status=NOT_STARTED
#keep track of which components have finished
introComponents=[]
introComponents.append(text_7)
introComponents.append(key_resp_3)
for thisComponent in introComponents:
    if hasattr(thisComponent,'status'): thisComponent.status = NOT_STARTED
#-------Start Routine "intro"-------
continueRoutine=True
while continueRoutine:
    #get current time
    t=introClock.getTime()
    frameN=frameN+1#number of completed frames (so 0 in first frame)
    #update/draw components on each frame
    
    #*text_7* updates
    if t>=0.0 and text_7.status==NOT_STARTED:
        #keep track of start time/frame for later
        text_7.tStart=t#underestimates by a little under one frame
        text_7.frameNStart=frameN#exact frame index
        text_7.setAutoDraw(True)
    
    #*key_resp_3* updates
    if t>=0.0 and key_resp_3.status==NOT_STARTED:
        #keep track of start time/frame for later
        key_resp_3.tStart=t#underestimates by a little under one frame
        key_resp_3.frameNStart=frameN#exact frame index
        key_resp_3.status=STARTED
        #keyboard checking is just starting
        key_resp_3.clock.reset() # now t=0
        event.clearEvents()
    if key_resp_3.status==STARTED:#only update if being drawn
        theseKeys = event.getKeys(keyList=['space'])
        if len(theseKeys)>0:#at least one key was pressed
            key_resp_3.keys=theseKeys[-1]#just the last key pressed
            key_resp_3.rt = key_resp_3.clock.getTime()
            #abort routine on response
            continueRoutine=False
    
    #check if all components have finished
    if not continueRoutine: #a component has requested that we end
        routineTimer.reset() #this is the new t0 for non-slip Routines
        break
    continueRoutine=False#will revert to True if at least one component still running
    for thisComponent in introComponents:
        if hasattr(thisComponent,"status") and thisComponent.status!=FINISHED:
            continueRoutine=True; break#at least one component has not yet finished
    
    #check for quit (the [Esc] key)
    if event.getKeys(["escape"]):
        core.quit()
    
    #refresh the screen
    if continueRoutine:#don't flip if this routine is over or we'll get a blank screen
        win.flip()

#End of Routine "intro"
for thisComponent in introComponents:
    if hasattr(thisComponent,"setAutoDraw"): thisComponent.setAutoDraw(False)

#------Prepare to start Routine"baseline_instruction"-------
t=0; baseline_instructionClock.reset() #clock 
frameN=-1
routineTimer.add(1.000000)
#update component parameters for each repeat
#keep track of which components have finished
baseline_instructionComponents=[]
baseline_instructionComponents.append(text_5)
for thisComponent in baseline_instructionComponents:
    if hasattr(thisComponent,'status'): thisComponent.status = NOT_STARTED
#-------Start Routine "baseline_instruction"-------
continueRoutine=True
while continueRoutine and routineTimer.getTime()>0:
    #get current time
    t=baseline_instructionClock.getTime()
    frameN=frameN+1#number of completed frames (so 0 in first frame)
    #update/draw components on each frame
    
    #*text_5* updates
    if t>=0.0 and text_5.status==NOT_STARTED:
        #keep track of start time/frame for later
        text_5.tStart=t#underestimates by a little under one frame
        text_5.frameNStart=frameN#exact frame index
        text_5.setAutoDraw(True)
    elif text_5.status==STARTED and t>=(0.0+1.0):
        text_5.setAutoDraw(False)
    
    #check if all components have finished
    if not continueRoutine: #a component has requested that we end
        routineTimer.reset() #this is the new t0 for non-slip Routines
        break
    continueRoutine=False#will revert to True if at least one component still running
    for thisComponent in baseline_instructionComponents:
        if hasattr(thisComponent,"status") and thisComponent.status!=FINISHED:
            continueRoutine=True; break#at least one component has not yet finished
    
    #check for quit (the [Esc] key)
    if event.getKeys(["escape"]):
        core.quit()
    
    #refresh the screen
    if continueRoutine:#don't flip if this routine is over or we'll get a blank screen
        win.flip()

#End of Routine "baseline_instruction"
for thisComponent in baseline_instructionComponents:
    if hasattr(thisComponent,"setAutoDraw"): thisComponent.setAutoDraw(False)

#------Prepare to start Routine"baseline"-------
t=0; baselineClock.reset() #clock 
frameN=-1
#update component parameters for each repeat
try:
    ts = time.time()
    H.send_tag(ts, ts+30, "baseline")
except Exception, e:
    print("No obci mode?: "+str(e))
#keep track of which components have finished
baselineComponents=[]
baselineComponents.append(text_4)
for thisComponent in baselineComponents:
    if hasattr(thisComponent,'status'): thisComponent.status = NOT_STARTED
#-------Start Routine "baseline"-------
continueRoutine=True
while continueRoutine:
    #get current time
    t=baselineClock.getTime()
    frameN=frameN+1#number of completed frames (so 0 in first frame)
    #update/draw components on each frame
    
    #*text_4* updates
    if t>=0.0 and text_4.status==NOT_STARTED:
        #keep track of start time/frame for later
        text_4.tStart=t#underestimates by a little under one frame
        text_4.frameNStart=frameN#exact frame index
        text_4.setAutoDraw(True)
    elif text_4.status==STARTED and t>=(0.0+BASELINE_DURATION):
        text_4.setAutoDraw(False)
    
    
    #check if all components have finished
    if not continueRoutine: #a component has requested that we end
        routineTimer.reset() #this is the new t0 for non-slip Routines
        break
    continueRoutine=False#will revert to True if at least one component still running
    for thisComponent in baselineComponents:
        if hasattr(thisComponent,"status") and thisComponent.status!=FINISHED:
            continueRoutine=True; break#at least one component has not yet finished
    
    #check for quit (the [Esc] key)
    if event.getKeys(["escape"]):
        core.quit()
    
    #refresh the screen
    if continueRoutine:#don't flip if this routine is over or we'll get a blank screen
        win.flip()

#End of Routine "baseline"
for thisComponent in baselineComponents:
    if hasattr(thisComponent,"setAutoDraw"): thisComponent.setAutoDraw(False)


#------Prepare to start Routine"instruct"-------
t=0; instructClock.reset() #clock 
frameN=-1
#update component parameters for each repeat
ready = event.BuilderKeyResponse() #create an object of type KeyResponse
ready.status=NOT_STARTED
#keep track of which components have finished
instructComponents=[]
instructComponents.append(instrText)
instructComponents.append(ready)
for thisComponent in instructComponents:
    if hasattr(thisComponent,'status'): thisComponent.status = NOT_STARTED
#-------Start Routine "instruct"-------
continueRoutine=True
while continueRoutine:
    #get current time
    t=instructClock.getTime()
    frameN=frameN+1#number of completed frames (so 0 in first frame)
    #update/draw components on each frame
    
    #*instrText* updates
    if t>=0 and instrText.status==NOT_STARTED:
        #keep track of start time/frame for later
        instrText.tStart=t#underestimates by a little under one frame
        instrText.frameNStart=frameN#exact frame index
        instrText.setAutoDraw(True)
    
    #*ready* updates
    if t>=0 and ready.status==NOT_STARTED:
        #keep track of start time/frame for later
        ready.tStart=t#underestimates by a little under one frame
        ready.frameNStart=frameN#exact frame index
        ready.status=STARTED
        #keyboard checking is just starting
        event.clearEvents()
    if ready.status==STARTED:#only update if being drawn
        theseKeys = event.getKeys()
        if len(theseKeys)>0:#at least one key was pressed
            #abort routine on response
            continueRoutine=False
    
    #check if all components have finished
    if not continueRoutine: #a component has requested that we end
        routineTimer.reset() #this is the new t0 for non-slip Routines
        break
    continueRoutine=False#will revert to True if at least one component still running
    for thisComponent in instructComponents:
        if hasattr(thisComponent,"status") and thisComponent.status!=FINISHED:
            continueRoutine=True; break#at least one component has not yet finished
    
    #check for quit (the [Esc] key)
    if event.getKeys(["escape"]):
        core.quit()
    
    #refresh the screen
    if continueRoutine:#don't flip if this routine is over or we'll get a blank screen
        win.flip()

#End of Routine "instruct"
for thisComponent in instructComponents:
    if hasattr(thisComponent,"setAutoDraw"): thisComponent.setAutoDraw(False)

#------Prepare to start Routine"learn1"-------
t=0; learn1Clock.reset() #clock 
frameN=-1
#update component parameters for each repeat
key_resp_4 = event.BuilderKeyResponse() #create an object of type KeyResponse
key_resp_4.status=NOT_STARTED
#keep track of which components have finished
learn1Components=[]
learn1Components.append(text_8)
learn1Components.append(key_resp_4)
learn1Components.append(text_9)
for thisComponent in learn1Components:
    if hasattr(thisComponent,'status'): thisComponent.status = NOT_STARTED
#-------Start Routine "learn1"-------
continueRoutine=True
while continueRoutine:
    #get current time
    t=learn1Clock.getTime()
    frameN=frameN+1#number of completed frames (so 0 in first frame)
    #update/draw components on each frame
    
    #*text_8* updates
    if t>=0.0 and text_8.status==NOT_STARTED:
        #keep track of start time/frame for later
        text_8.tStart=t#underestimates by a little under one frame
        text_8.frameNStart=frameN#exact frame index
        text_8.setAutoDraw(True)
    
    #*key_resp_4* updates
    if t>=0.0 and key_resp_4.status==NOT_STARTED:
        #keep track of start time/frame for later
        key_resp_4.tStart=t#underestimates by a little under one frame
        key_resp_4.frameNStart=frameN#exact frame index
        key_resp_4.status=STARTED
        #keyboard checking is just starting
        key_resp_4.clock.reset() # now t=0
        event.clearEvents()
    if key_resp_4.status==STARTED:#only update if being drawn
        theseKeys = event.getKeys(keyList=['7'])
        if len(theseKeys)>0:#at least one key was pressed
            key_resp_4.keys=theseKeys[-1]#just the last key pressed
            key_resp_4.rt = key_resp_4.clock.getTime()
            #abort routine on response
            continueRoutine=False
    
    #*text_9* updates
    if t>=0.0 and text_9.status==NOT_STARTED:
        #keep track of start time/frame for later
        text_9.tStart=t#underestimates by a little under one frame
        text_9.frameNStart=frameN#exact frame index
        text_9.setAutoDraw(True)
    
    #check if all components have finished
    if not continueRoutine: #a component has requested that we end
        routineTimer.reset() #this is the new t0 for non-slip Routines
        break
    continueRoutine=False#will revert to True if at least one component still running
    for thisComponent in learn1Components:
        if hasattr(thisComponent,"status") and thisComponent.status!=FINISHED:
            continueRoutine=True; break#at least one component has not yet finished
    
    #check for quit (the [Esc] key)
    if event.getKeys(["escape"]):
        core.quit()
    
    #refresh the screen
    if continueRoutine:#don't flip if this routine is over or we'll get a blank screen
        win.flip()

#End of Routine "learn1"
for thisComponent in learn1Components:
    if hasattr(thisComponent,"setAutoDraw"): thisComponent.setAutoDraw(False)

#------Prepare to start Routine"learn2"-------
t=0; learn2Clock.reset() #clock 
frameN=-1
#update component parameters for each repeat
key_resp_5 = event.BuilderKeyResponse() #create an object of type KeyResponse
key_resp_5.status=NOT_STARTED
#keep track of which components have finished
learn2Components=[]
learn2Components.append(text_10)
learn2Components.append(key_resp_5)
learn2Components.append(text_11)
for thisComponent in learn2Components:
    if hasattr(thisComponent,'status'): thisComponent.status = NOT_STARTED
#-------Start Routine "learn2"-------
continueRoutine=True
while continueRoutine:
    #get current time
    t=learn2Clock.getTime()
    frameN=frameN+1#number of completed frames (so 0 in first frame)
    #update/draw components on each frame
    
    #*text_10* updates
    if t>=0.0 and text_10.status==NOT_STARTED:
        #keep track of start time/frame for later
        text_10.tStart=t#underestimates by a little under one frame
        text_10.frameNStart=frameN#exact frame index
        text_10.setAutoDraw(True)
    
    #*key_resp_5* updates
    if t>=0.0 and key_resp_5.status==NOT_STARTED:
        #keep track of start time/frame for later
        key_resp_5.tStart=t#underestimates by a little under one frame
        key_resp_5.frameNStart=frameN#exact frame index
        key_resp_5.status=STARTED
        #keyboard checking is just starting
        key_resp_5.clock.reset() # now t=0
        event.clearEvents()
    if key_resp_5.status==STARTED:#only update if being drawn
        theseKeys = event.getKeys(keyList=['8'])
        if len(theseKeys)>0:#at least one key was pressed
            key_resp_5.keys=theseKeys[-1]#just the last key pressed
            key_resp_5.rt = key_resp_5.clock.getTime()
            #abort routine on response
            continueRoutine=False
    
    #*text_11* updates
    if t>=0.0 and text_11.status==NOT_STARTED:
        #keep track of start time/frame for later
        text_11.tStart=t#underestimates by a little under one frame
        text_11.frameNStart=frameN#exact frame index
        text_11.setAutoDraw(True)
    
    #check if all components have finished
    if not continueRoutine: #a component has requested that we end
        routineTimer.reset() #this is the new t0 for non-slip Routines
        break
    continueRoutine=False#will revert to True if at least one component still running
    for thisComponent in learn2Components:
        if hasattr(thisComponent,"status") and thisComponent.status!=FINISHED:
            continueRoutine=True; break#at least one component has not yet finished
    
    #check for quit (the [Esc] key)
    if event.getKeys(["escape"]):
        core.quit()
    
    #refresh the screen
    if continueRoutine:#don't flip if this routine is over or we'll get a blank screen
        win.flip()

#End of Routine "learn2"
for thisComponent in learn2Components:
    if hasattr(thisComponent,"setAutoDraw"): thisComponent.setAutoDraw(False)

#------Prepare to start Routine"learn3"-------
t=0; learn3Clock.reset() #clock 
frameN=-1
#update component parameters for each repeat
key_resp_6 = event.BuilderKeyResponse() #create an object of type KeyResponse
key_resp_6.status=NOT_STARTED
#keep track of which components have finished
learn3Components=[]
learn3Components.append(text_12)
learn3Components.append(key_resp_6)
learn3Components.append(text_13)
for thisComponent in learn3Components:
    if hasattr(thisComponent,'status'): thisComponent.status = NOT_STARTED
#-------Start Routine "learn3"-------
continueRoutine=True
while continueRoutine:
    #get current time
    t=learn3Clock.getTime()
    frameN=frameN+1#number of completed frames (so 0 in first frame)
    #update/draw components on each frame
    
    #*text_12* updates
    if t>=0.0 and text_12.status==NOT_STARTED:
        #keep track of start time/frame for later
        text_12.tStart=t#underestimates by a little under one frame
        text_12.frameNStart=frameN#exact frame index
        text_12.setAutoDraw(True)
    
    #*key_resp_6* updates
    if t>=0.0 and key_resp_6.status==NOT_STARTED:
        #keep track of start time/frame for later
        key_resp_6.tStart=t#underestimates by a little under one frame
        key_resp_6.frameNStart=frameN#exact frame index
        key_resp_6.status=STARTED
        #keyboard checking is just starting
        key_resp_6.clock.reset() # now t=0
        event.clearEvents()
    if key_resp_6.status==STARTED:#only update if being drawn
        theseKeys = event.getKeys(keyList=['9'])
        if len(theseKeys)>0:#at least one key was pressed
            key_resp_6.keys=theseKeys[-1]#just the last key pressed
            key_resp_6.rt = key_resp_6.clock.getTime()
            #abort routine on response
            continueRoutine=False
    
    #*text_13* updates
    if t>=0.0 and text_13.status==NOT_STARTED:
        #keep track of start time/frame for later
        text_13.tStart=t#underestimates by a little under one frame
        text_13.frameNStart=frameN#exact frame index
        text_13.setAutoDraw(True)
    
    #check if all components have finished
    if not continueRoutine: #a component has requested that we end
        routineTimer.reset() #this is the new t0 for non-slip Routines
        break
    continueRoutine=False#will revert to True if at least one component still running
    for thisComponent in learn3Components:
        if hasattr(thisComponent,"status") and thisComponent.status!=FINISHED:
            continueRoutine=True; break#at least one component has not yet finished
    
    #check for quit (the [Esc] key)
    if event.getKeys(["escape"]):
        core.quit()
    
    #refresh the screen
    if continueRoutine:#don't flip if this routine is over or we'll get a blank screen
        win.flip()

#End of Routine "learn3"
for thisComponent in learn3Components:
    if hasattr(thisComponent,"setAutoDraw"): thisComponent.setAutoDraw(False)

#------Prepare to start Routine"learn4"-------
t=0; learn4Clock.reset() #clock 
frameN=-1
#update component parameters for each repeat
key_resp_7 = event.BuilderKeyResponse() #create an object of type KeyResponse
key_resp_7.status=NOT_STARTED
#keep track of which components have finished
learn4Components=[]
learn4Components.append(text_14)
learn4Components.append(key_resp_7)
learn4Components.append(text_15)
for thisComponent in learn4Components:
    if hasattr(thisComponent,'status'): thisComponent.status = NOT_STARTED
#-------Start Routine "learn4"-------
continueRoutine=True
while continueRoutine:
    #get current time
    t=learn4Clock.getTime()
    frameN=frameN+1#number of completed frames (so 0 in first frame)
    #update/draw components on each frame
    
    #*text_14* updates
    if t>=0.0 and text_14.status==NOT_STARTED:
        #keep track of start time/frame for later
        text_14.tStart=t#underestimates by a little under one frame
        text_14.frameNStart=frameN#exact frame index
        text_14.setAutoDraw(True)
    
    #*key_resp_7* updates
    if t>=0.0 and key_resp_7.status==NOT_STARTED:
        #keep track of start time/frame for later
        key_resp_7.tStart=t#underestimates by a little under one frame
        key_resp_7.frameNStart=frameN#exact frame index
        key_resp_7.status=STARTED
        #keyboard checking is just starting
        key_resp_7.clock.reset() # now t=0
        event.clearEvents()
    if key_resp_7.status==STARTED:#only update if being drawn
        theseKeys = event.getKeys(keyList=['0'])
        if len(theseKeys)>0:#at least one key was pressed
            key_resp_7.keys=theseKeys[-1]#just the last key pressed
            key_resp_7.rt = key_resp_7.clock.getTime()
            #abort routine on response
            continueRoutine=False
    
    #*text_15* updates
    if t>=0.0 and text_15.status==NOT_STARTED:
        #keep track of start time/frame for later
        text_15.tStart=t#underestimates by a little under one frame
        text_15.frameNStart=frameN#exact frame index
        text_15.setAutoDraw(True)
    
    #check if all components have finished
    if not continueRoutine: #a component has requested that we end
        routineTimer.reset() #this is the new t0 for non-slip Routines
        break
    continueRoutine=False#will revert to True if at least one component still running
    for thisComponent in learn4Components:
        if hasattr(thisComponent,"status") and thisComponent.status!=FINISHED:
            continueRoutine=True; break#at least one component has not yet finished
    
    #check for quit (the [Esc] key)
    if event.getKeys(["escape"]):
        core.quit()
    
    #refresh the screen
    if continueRoutine:#don't flip if this routine is over or we'll get a blank screen
        win.flip()

#End of Routine "learn4"
for thisComponent in learn4Components:
    if hasattr(thisComponent,"setAutoDraw"): thisComponent.setAutoDraw(False)

#------Prepare to start Routine"ready_2"-------
t=0; ready_2Clock.reset() #clock 
frameN=-1
#update component parameters for each repeat
key_resp_2 = event.BuilderKeyResponse() #create an object of type KeyResponse
key_resp_2.status=NOT_STARTED
#keep track of which components have finished
ready_2Components=[]
ready_2Components.append(text_6)
ready_2Components.append(key_resp_2)
ready_2Components.append(text_16)
for thisComponent in ready_2Components:
    if hasattr(thisComponent,'status'): thisComponent.status = NOT_STARTED
#-------Start Routine "ready_2"-------
continueRoutine=True
while continueRoutine:
    #get current time
    t=ready_2Clock.getTime()
    frameN=frameN+1#number of completed frames (so 0 in first frame)
    #update/draw components on each frame
    
    #*text_6* updates
    if t>=0.0 and text_6.status==NOT_STARTED:
        #keep track of start time/frame for later
        text_6.tStart=t#underestimates by a little under one frame
        text_6.frameNStart=frameN#exact frame index
        text_6.setAutoDraw(True)
    
    #*key_resp_2* updates
    if t>=0.0 and key_resp_2.status==NOT_STARTED:
        #keep track of start time/frame for later
        key_resp_2.tStart=t#underestimates by a little under one frame
        key_resp_2.frameNStart=frameN#exact frame index
        key_resp_2.status=STARTED
        #keyboard checking is just starting
        key_resp_2.clock.reset() # now t=0
        event.clearEvents()
    if key_resp_2.status==STARTED:#only update if being drawn
        theseKeys = event.getKeys(keyList=['7'])
        if len(theseKeys)>0:#at least one key was pressed
            key_resp_2.keys=theseKeys[-1]#just the last key pressed
            key_resp_2.rt = key_resp_2.clock.getTime()
            #abort routine on response
            continueRoutine=False
    
    #*text_16* updates
    if t>=0.0 and text_16.status==NOT_STARTED:
        #keep track of start time/frame for later
        text_16.tStart=t#underestimates by a little under one frame
        text_16.frameNStart=frameN#exact frame index
        text_16.setAutoDraw(True)
    
    #check if all components have finished
    if not continueRoutine: #a component has requested that we end
        routineTimer.reset() #this is the new t0 for non-slip Routines
        break
    continueRoutine=False#will revert to True if at least one component still running
    for thisComponent in ready_2Components:
        if hasattr(thisComponent,"status") and thisComponent.status!=FINISHED:
            continueRoutine=True; break#at least one component has not yet finished
    
    #check for quit (the [Esc] key)
    if event.getKeys(["escape"]):
        core.quit()
    
    #refresh the screen
    if continueRoutine:#don't flip if this routine is over or we'll get a blank screen
        win.flip()

#End of Routine "ready_2"
for thisComponent in ready_2Components:
    if hasattr(thisComponent,"setAutoDraw"): thisComponent.setAutoDraw(False)

#set up handler to look after randomisation of conditions etc
trials=data.TrialHandler(nReps=1.0, method='sequential', 
    extraInfo=expInfo, originPath=None,
    trialList=data.importConditions(CONDITIONS_FILE),
    seed=None, name='trials')
thisExp.addLoop(trials)#add the loop to the experiment
thisTrial=trials.trialList[0]#so we can initialise stimuli with some values
#abbreviate parameter names if possible (e.g. rgb=thisTrial.rgb)
if thisTrial!=None:
    for paramName in thisTrial.keys():
        exec(paramName+'=thisTrial.'+paramName)

for thisTrial in trials:
    currentLoop = trials
    #abbrieviate parameter names if possible (e.g. rgb=thisTrial.rgb)
    if thisTrial!=None:
        for paramName in thisTrial.keys():
            exec(paramName+'=thisTrial.'+paramName)
    
    #------Prepare to start Routine"trial"-------
    t=0; trialClock.reset() #clock 
    frameN=-1
    #update component parameters for each repeat
    word.setColor(letterColor, colorSpace='rgb')
    word.setText(text)
    try:
        ts = time.time() - trialClock.getTime()
        H.send_tag(time.time(), time.time(), "trial")
    except Exception, e:
        print("No obci mode?: "+str(e))
    resp = event.BuilderKeyResponse() #create an object of type KeyResponse
    resp.status=NOT_STARTED
    #keep track of which components have finished
    trialComponents=[]
    trialComponents.append(word)
    trialComponents.append(resp)
    trialComponents.append(fixation)
    trialComponents.append(hint)
    for thisComponent in trialComponents:
        if hasattr(thisComponent,'status'): thisComponent.status = NOT_STARTED
    #-------Start Routine "trial"-------
    continueRoutine=True
    while continueRoutine:
        #get current time
        t=trialClock.getTime()
        frameN=frameN+1#number of completed frames (so 0 in first frame)
        #update/draw components on each frame
        
        #*word* updates
        if t>=1.0 and word.status==NOT_STARTED:
            #keep track of start time/frame for later
            word.tStart=t#underestimates by a little under one frame
            word.frameNStart=frameN#exact frame index
            word.setAutoDraw(True)
        
        
        #*resp* updates
        if t>=1.0 and resp.status==NOT_STARTED:
            #keep track of start time/frame for later
            resp.tStart=t#underestimates by a little under one frame
            resp.frameNStart=frameN#exact frame index
            resp.status=STARTED
            #keyboard checking is just starting
            resp.clock.reset() # now t=0
            event.clearEvents()
        if resp.status==STARTED:#only update if being drawn
            theseKeys = event.getKeys(keyList=['7', '8', '9', '0'])
            if len(theseKeys)>0:#at least one key was pressed
                resp.keys=theseKeys[-1]#just the last key pressed
                resp.rt = resp.clock.getTime()
                #was this 'correct'?
                if (resp.keys==str(corrAns)): resp.corr=1
                else: resp.corr=0
                #abort routine on response
                continueRoutine=False
        
        #*fixation* updates
        if t>=0.3 and fixation.status==NOT_STARTED:
            #keep track of start time/frame for later
            fixation.tStart=t#underestimates by a little under one frame
            fixation.frameNStart=frameN#exact frame index
            fixation.setAutoDraw(True)
        elif fixation.status==STARTED and t>=(0.3+0.7):
            fixation.setAutoDraw(False)
        
        #*hint* updates
        if t>=0.0 and hint.status==NOT_STARTED:
            #keep track of start time/frame for later
            hint.tStart=t#underestimates by a little under one frame
            hint.frameNStart=frameN#exact frame index
            hint.setAutoDraw(True)
        
        #check if all components have finished
        if not continueRoutine: #a component has requested that we end
            routineTimer.reset() #this is the new t0 for non-slip Routines
            break
        continueRoutine=False#will revert to True if at least one component still running
        for thisComponent in trialComponents:
            if hasattr(thisComponent,"status") and thisComponent.status!=FINISHED:
                continueRoutine=True; break#at least one component has not yet finished
        
        #check for quit (the [Esc] key)
        if event.getKeys(["escape"]):
            core.quit()
        
        #refresh the screen
        if continueRoutine:#don't flip if this routine is over or we'll get a blank screen
            win.flip()
    
    #End of Routine "trial"
    for thisComponent in trialComponents:
        if hasattr(thisComponent,"setAutoDraw"): thisComponent.setAutoDraw(False)
    try:
        ts = ts +word.tStart
        H.send_tag(ts, time.time(), "word",
        {'keys':str(resp.keys),
        'corr':str(resp.corr),
        'rt':str(resp.rt),
        'text':str(text),
       'color':str(letterColor),
       'condition':str(CONDITIONS[condition_index]),
       'block_index':str(block_index),
       'trial_index':str(trial_index),
        })
    except Exception, e:
        print("No obci mode?: "+str(e))
    
    block_changed = False
    condition_changed = False
    trial_index += 1
    if trial_index % TRIALS_COUNT == 0:
        block_index += 1
        block_changed = True
        if block_index % BLOCKS_COUNT == 0:
            condition_index += 1
            condition_changed = True
    #print("trials: "+str(trial_index)+" blocks: "+str(block_index)+ "conds: "+str(condition_index))
    #print("Block changed: "+str(block_changed))
    #print("cond changed: "+str(condition_changed))
    #check responses
    if len(resp.keys)==0: #No response was made
       resp.keys=None
       #was no response the correct answer?!
       if str(corrAns).lower()=='none':resp.corr=1 #correct non-response
       else: resp.corr=0 #failed to respond (incorrectly)
    #store data for trials (TrialHandler)
    trials.addData('resp.keys',resp.keys)
    trials.addData('resp.corr',resp.corr)
    if resp.keys != None:#we had a response
        trials.addData('resp.rt',resp.rt)
    
    #------Prepare to start Routine"block_break"-------
    t=0; block_breakClock.reset() #clock 
    frameN=-1
    routineTimer.add(2.000000)
    #update component parameters for each repeat
    if not block_changed:
        continue
    #keep track of which components have finished
    block_breakComponents=[]
    block_breakComponents.append(text_2)
    for thisComponent in block_breakComponents:
        if hasattr(thisComponent,'status'): thisComponent.status = NOT_STARTED
    #-------Start Routine "block_break"-------
    continueRoutine=True
    while continueRoutine and routineTimer.getTime()>0:
        #get current time
        t=block_breakClock.getTime()
        frameN=frameN+1#number of completed frames (so 0 in first frame)
        #update/draw components on each frame
        
        #*text_2* updates
        if t>=0.0 and text_2.status==NOT_STARTED:
            #keep track of start time/frame for later
            text_2.tStart=t#underestimates by a little under one frame
            text_2.frameNStart=frameN#exact frame index
            text_2.setAutoDraw(True)
        elif text_2.status==STARTED and t>=(0.0+2.0):
            text_2.setAutoDraw(False)
        
        
        #check if all components have finished
        if not continueRoutine: #a component has requested that we end
            routineTimer.reset() #this is the new t0 for non-slip Routines
            break
        continueRoutine=False#will revert to True if at least one component still running
        for thisComponent in block_breakComponents:
            if hasattr(thisComponent,"status") and thisComponent.status!=FINISHED:
                continueRoutine=True; break#at least one component has not yet finished
        
        #check for quit (the [Esc] key)
        if event.getKeys(["escape"]):
            core.quit()
        
        #refresh the screen
        if continueRoutine:#don't flip if this routine is over or we'll get a blank screen
            win.flip()
    
    #End of Routine "block_break"
    for thisComponent in block_breakComponents:
        if hasattr(thisComponent,"setAutoDraw"): thisComponent.setAutoDraw(False)
    
    
    #------Prepare to start Routine"condition_break"-------
    t=0; condition_breakClock.reset() #clock 
    frameN=-1
    #update component parameters for each repeat
    key_resp = event.BuilderKeyResponse() #create an object of type KeyResponse
    key_resp.status=NOT_STARTED
    if not condition_changed:
        continue
    #keep track of which components have finished
    condition_breakComponents=[]
    condition_breakComponents.append(text_3)
    condition_breakComponents.append(key_resp)
    for thisComponent in condition_breakComponents:
        if hasattr(thisComponent,'status'): thisComponent.status = NOT_STARTED
    #-------Start Routine "condition_break"-------
    continueRoutine=True
    while continueRoutine:
        #get current time
        t=condition_breakClock.getTime()
        frameN=frameN+1#number of completed frames (so 0 in first frame)
        #update/draw components on each frame
        
        #*text_3* updates
        if t>=0.0 and text_3.status==NOT_STARTED:
            #keep track of start time/frame for later
            text_3.tStart=t#underestimates by a little under one frame
            text_3.frameNStart=frameN#exact frame index
            text_3.setAutoDraw(True)
        
        #*key_resp* updates
        if t>=0.0 and key_resp.status==NOT_STARTED:
            #keep track of start time/frame for later
            key_resp.tStart=t#underestimates by a little under one frame
            key_resp.frameNStart=frameN#exact frame index
            key_resp.status=STARTED
            #keyboard checking is just starting
            key_resp.clock.reset() # now t=0
            event.clearEvents()
        if key_resp.status==STARTED:#only update if being drawn
            theseKeys = event.getKeys(keyList=['7', '8', '9', '0'])
            if len(theseKeys)>0:#at least one key was pressed
                key_resp.keys=theseKeys[-1]#just the last key pressed
                key_resp.rt = key_resp.clock.getTime()
                #abort routine on response
                continueRoutine=False
        
        
        #check if all components have finished
        if not continueRoutine: #a component has requested that we end
            routineTimer.reset() #this is the new t0 for non-slip Routines
            break
        continueRoutine=False#will revert to True if at least one component still running
        for thisComponent in condition_breakComponents:
            if hasattr(thisComponent,"status") and thisComponent.status!=FINISHED:
                continueRoutine=True; break#at least one component has not yet finished
        
        #check for quit (the [Esc] key)
        if event.getKeys(["escape"]):
            core.quit()
        
        #refresh the screen
        if continueRoutine:#don't flip if this routine is over or we'll get a blank screen
            win.flip()
    
    #End of Routine "condition_break"
    for thisComponent in condition_breakComponents:
        if hasattr(thisComponent,"setAutoDraw"): thisComponent.setAutoDraw(False)
    #check responses
    if len(key_resp.keys)==0: #No response was made
       key_resp.keys=None
    #store data for trials (TrialHandler)
    trials.addData('key_resp.keys',key_resp.keys)
    if key_resp.keys != None:#we had a response
        trials.addData('key_resp.rt',key_resp.rt)
    
    thisExp.nextEntry()

#completed 1.0 repeats of 'trials'

#get names of stimulus parameters
if trials.trialList in ([], [None], None):  params=[]
else:  params = trials.trialList[0].keys()
#save data for this loop
trials.saveAsPickle(filename+'trials', fileCollisionMethod='rename')
trials.saveAsText(filename+'trials.csv', delim=',',
    stimOut=params,
    dataOut=['n','all_mean','all_std', 'all_raw'])

#------Prepare to start Routine"thanks"-------
t=0; thanksClock.reset() #clock 
frameN=-1
routineTimer.add(2.000000)
#update component parameters for each repeat
#keep track of which components have finished
thanksComponents=[]
thanksComponents.append(thanksText)
for thisComponent in thanksComponents:
    if hasattr(thisComponent,'status'): thisComponent.status = NOT_STARTED
#-------Start Routine "thanks"-------
continueRoutine=True
while continueRoutine and routineTimer.getTime()>0:
    #get current time
    t=thanksClock.getTime()
    frameN=frameN+1#number of completed frames (so 0 in first frame)
    #update/draw components on each frame
    
    #*thanksText* updates
    if t>=0.0 and thanksText.status==NOT_STARTED:
        #keep track of start time/frame for later
        thanksText.tStart=t#underestimates by a little under one frame
        thanksText.frameNStart=frameN#exact frame index
        thanksText.setAutoDraw(True)
    elif thanksText.status==STARTED and t>=(0.0+2.0):
        thanksText.setAutoDraw(False)
    
    #check if all components have finished
    if not continueRoutine: #a component has requested that we end
        routineTimer.reset() #this is the new t0 for non-slip Routines
        break
    continueRoutine=False#will revert to True if at least one component still running
    for thisComponent in thanksComponents:
        if hasattr(thisComponent,"status") and thisComponent.status!=FINISHED:
            continueRoutine=True; break#at least one component has not yet finished
    
    #check for quit (the [Esc] key)
    if event.getKeys(["escape"]):
        core.quit()
    
    #refresh the screen
    if continueRoutine:#don't flip if this routine is over or we'll get a blank screen
        win.flip()

#End of Routine "thanks"
for thisComponent in thanksComponents:
    if hasattr(thisComponent,"setAutoDraw"): thisComponent.setAutoDraw(False)

try:
    H.finish_saving()
except Exception, e:
    print("No obci mode?: "+str(e))



#Shutting down:
win.close()
core.quit()
