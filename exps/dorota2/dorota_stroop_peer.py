#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This experiment was created using PsychoPy2 Experiment Builder (v1.74.00), nie, 8 lip 2012, 12:02:18
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
if not os.path.isdir('/home/mati/temp'):
    os.makedirs('/home/mati/temp') #if this fails (e.g. permissions) we will get error
filename='/home/mati/temp' + os.path.sep + '%s' %(expInfo['date'])
logging.console.setLevel(logging.WARNING)#this outputs to the screen, not a file

#an ExperimentHandler isn't essential but helps with data saving
thisExp = data.ExperimentHandler(name=expName, version='',
    extraInfo=expInfo, runtimeInfo=None,
    originPath=None,
    savePickle=True, saveWideText=False,
    dataFileName=filename)

#setup the Window
win = visual.Window(size=(1280, 800), fullscr=True, screen=0, allowGUI=False, allowStencil=False,
    monitor=u'testMonitor', color=u'black', colorSpace=u'rgb', units=u'norm')

#Initialise components for Routine "instruct"
instructClock=core.Clock()
instrText=visual.TextStim(win=win, ori=0, name='instrText',
    text='OK. Ready for the real thing?\n\nRemember, ignore the word itself; press:\nLeft for red LETTERS\nDown for green LETTERS\nRight for blue LETTERS\n(Esc will quit)\n\nPress any key to continue',
    font='Arial',
    pos=[0, 0], height=0.1,wrapWidth=None,
    color=[1, 1, 1], colorSpace='rgb', opacity=1,
    depth=0.0)

#Initialise components for Routine "trial"
trialClock=core.Clock()
word=visual.TextStim(win=win, ori=0, name='word',
    text='nonsense',
    font=u'Arial',
    pos=[0, 0], height=0.2,wrapWidth=None,
    color=1.0, colorSpace=u'rgb', opacity=1,
    depth=0.0)
CONDITIONS = ['CON', 'EXP']
CONDITIONS_COUNT = len(CONDITIONS)
BLOCKS_COUNT = 2
TRIALS_COUNT = 4
KEYS_MAP = {'green':'7', 'red':'8', 'yellow':'9', 'blue':'0'}
CONDITIONS_FILE='/home/mati/obci/exps/dorota2/alTypesCongruent.csv'


condition_index = 0
block_index = 0
trial_index = 0


#gen. trials()

fixation=visual.TextStim(win=win, ori=0, name='fixation',
    text=u'+',
    font=u'Arial',
    pos=[0, 0], height=0.1,wrapWidth=None,
    color=u'white', colorSpace=u'rgb', opacity=1,
    depth=-3.0)

#Initialise components for Routine "block_break"
block_breakClock=core.Clock()
text_2=visual.TextStim(win=win, ori=0, name='text_2',
    text=u'Remember - pay attention to colours!!!',
    font=u'Arial',
    pos=[0, 0], height=0.1,wrapWidth=None,
    color=u'white', colorSpace=u'rgb', opacity=1,
    depth=0.0)


#Initialise components for Routine "condition_break"
condition_breakClock=core.Clock()
text_3=visual.TextStim(win=win, ori=0, name='text_3',
    text=u'A little wrest... Hit space to continue',
    font=u'Arial',
    pos=[0, 0], height=0.1,wrapWidth=None,
    color=u'white', colorSpace=u'rgb', opacity=1,
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

#set up handler to look after randomisation of conditions etc
trials=data.TrialHandler(nReps=asarray(BLOCKS_COUNT*CONDITIONS_COUNT), method=u'sequential', 
    extraInfo=expInfo, originPath=None,
    trialList=data.importConditions(u'/home/mati/obci/exps/dorota2/trialTypesCongruent.csv'),
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
    word.setColor(letterColor, colorSpace=u'rgb')
    word.setText(text)
    
    resp = event.BuilderKeyResponse() #create an object of type KeyResponse
    resp.status=NOT_STARTED
    #keep track of which components have finished
    trialComponents=[]
    trialComponents.append(word)
    trialComponents.append(resp)
    trialComponents.append(fixation)
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
    #ts = ts +word.tStart
    #H.send_tag(ts, time.time(), "word",
    #    {'keys':str(resp.keys),
    #    'corr':str(resp.corr),
    #    'rt':str(resp.rt),
    #    'text':str(text),
    #   'color':str(letterColor),
    #   'condition':str(CONDITIONS[condition_index]),
    #   'block_index':str(block_index),
    #   'trial_index':str(trial_index),
    #    })
    block_changed = False
    condition_changed = False
    trial_index += 1
    if trial_index % TRIALS_COUNT == 0:
        block_index += 1
        block_changed = True
        if block_index % BLOCKS_COUNT == 0:
            condition_index += 1
            condition_changed = True
    print("trials: "+str(trial_index)+" blocks: "+str(block_index)+ "conds: "+str(condition_index))
    print("Block changed: "+str(block_changed))
    print("cond changed: "+str(condition_changed))
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
    routineTimer.add(1.000000)
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
        elif text_2.status==STARTED and t>=(0.0+1.0):
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
            theseKeys = event.getKeys(keyList=['space'])
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

#completed asarray(BLOCKS_COUNT*CONDITIONS_COUNT) repeats of 'trials'

#get names of stimulus parameters
if trials.trialList in ([], [None], None):  params=[]
else:  params = trials.trialList[0].keys()
#save data for this loop
#trials.saveAsPickle(filename+'trials', fileCollisionMethod='rename')
#trials.saveAsText(filename+'trials.csv', delim=',',
#    stimOut=params,
#    dataOut=['n','all_mean','all_std', 'all_raw'])

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




#Shutting down:
win.close()
core.quit()
