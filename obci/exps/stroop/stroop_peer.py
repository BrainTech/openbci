#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This experiment was created using PsychoPy2 Experiment Builder (v1.74.00), pią, 6 lip 2012, 21:58:49
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
if not os.path.isdir('./temp'):
    os.makedirs('./temp') #if this fails (e.g. permissions) we will get error
filename='./temp' + os.path.sep + '%s' %(expInfo['date'])
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
    font='Arial',
    pos=[0, 0], height=0.2,wrapWidth=None,
    color=1.0, colorSpace='rgb', opacity=1,
    depth=0.0)
from obci.exps import exps_helper
import time
H = exps_helper.ExpsHelper()

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
trials=data.TrialHandler(nReps=1.0, method='random', 
    extraInfo=expInfo, originPath=None,
    trialList=data.importConditions('trialTypes.xlsx'),
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
    resp = event.BuilderKeyResponse() #create an object of type KeyResponse
    resp.status=NOT_STARTED
    ts = time.time() - trialClock.getTime()
    H.send_tag(time.time(), time.time(), "trial")
    #keep track of which components have finished
    trialComponents=[]
    trialComponents.append(word)
    trialComponents.append(resp)
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
        if t>=0.5 and word.status==NOT_STARTED:
            #keep track of start time/frame for later
            word.tStart=t#underestimates by a little under one frame
            word.frameNStart=frameN#exact frame index
            word.setAutoDraw(True)
        
        #*resp* updates
        if t>=0.5 and resp.status==NOT_STARTED:
            #keep track of start time/frame for later
            resp.tStart=t#underestimates by a little under one frame
            resp.frameNStart=frameN#exact frame index
            resp.status=STARTED
            #keyboard checking is just starting
            resp.clock.reset() # now t=0
            event.clearEvents()
        if resp.status==STARTED:#only update if being drawn
            theseKeys = event.getKeys(keyList=['left', 'down', 'right'])
            if len(theseKeys)>0:#at least one key was pressed
                resp.keys=theseKeys[-1]#just the last key pressed
                resp.rt = resp.clock.getTime()
                #was this 'correct'?
                if (resp.keys==str(corrAns)): resp.corr=1
                else: resp.corr=0
                #abort routine on response
                continueRoutine=False
        
        
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
    ts = ts + word.tStart
    H.send_tag(ts, time.time(), "word",
        {'keys':str(resp.keys),
        'corr':str(resp.corr),
        'rt':str(resp.rt),
        'text':str(text),
        'color':str(letterColor)
        })
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
H.finish_saving()

#Shutting down:
win.close()
core.quit()
