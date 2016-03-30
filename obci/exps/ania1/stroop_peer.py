#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time, os.path
from multiplexer.multiplexer_constants import peers, types
from obci.control.peer.configured_client import ConfiguredClient
from obci.configs import settings
from obci.utils import tags_helper
from obci.acquisition import acquisition_helper
from obci.utils.openbci_logging import log_crash

class ObciClient(ConfiguredClient):
    """A class for creating a manifest file with metadata."""
    @log_crash
    def __init__(self, addresses):
        super(ObciClient, self).__init__(addresses=addresses,
                                          type=peers.TAGS_SENDER)
        self.ready()
TAGGER = ObciClient(settings.MULTIPLEXER_ADDRESSES)


"""
This experiment was created using PsychoPy2 Experiment Builder (v1.73.02), March 23, 2012, at 14:36
If you publish work using this script please cite the relevant PsychoPy publications
  Peirce, JW (2007) PsychoPy - Psychophysics software in Python. Journal of Neuroscience Methods, 162(1-2), 8-13.
  Peirce, JW (2009) Generating stimuli for neuroscience using PsychoPy. Frontiers in Neuroinformatics, 2:10. doi: 10.3389/neuro.11.010.2008
"""
import numpy as np  # whole numpy lib is available, pre-pend 'np.'
from numpy import sin, cos, tan, log, log10, pi, average, sqrt, std, deg2rad, rad2deg, linspace, asarray
from numpy.random import random, randint, normal, shuffle
import os #handy system and path functions
from psychopy import core, data, event, logging, visual, gui
from psychopy.constants import *

experimentClock = core.Clock()

#store info about the experiment session
expName='None'#from the Builder filename that created this script
expInfo={'participant':'', 'session':'01'}
dlg=gui.DlgFromDict(dictionary=expInfo,title=expName)
if dlg.OK==False: core.quit() #user pressed cancel
expInfo['date']=data.getDateStr()#add a simple timestamp
expInfo['expName']=expName
#setup files for saving
if not os.path.isdir('data'):
    os.makedirs('data') #if this fails (e.g. permissions) we will get error
filename='data' + os.path.sep + '%s_%s' %(expInfo['participant'], expInfo['date'])
logFile=logging.LogFile(filename+'.log', level=logging.INFO)
logging.console.setLevel(logging.WARNING)#this outputs to the screen, not a file
logging.setDefaultClock(experimentClock)
#setup the Window
win = visual.Window(size=(1920, 1080), fullscr=True, screen=0, allowGUI=False, allowStencil=False,
    monitor='testMonitor', color='black', colorSpace='rgb', units='norm')

errorCircle = visual.Circle(win, radius=0.5, edges=100)
errorCircle.setAutoDraw(True)
errorCircle.setFillColor("black", colorSpace="rgb")
errorCircle.setLineColor("black", colorSpace="rgb")
errorCircle.setPos([0.015, 0.015])

#Initialise components for routine:instruct
instructClock=core.Clock()
instrText=visual.TextStim(win=win, ori=0, name='instrText',
    text='OK. Ready for the real thing?\n\nRemember, ignore the word itself; press:\nLeft for red LETTERS\nDown for green LETTERS\nRight for blue LETTERS\n(Esc will quit)\n\nPress any key to continue',
    font='Arial',
    pos=[0, 0], height=0.1,wrapWidth=None,
    color=[1, 1, 1], colorSpace='rgb', opacity=1,
    depth=0.0)

#Initialise components for routine:trial
trialClock=core.Clock()
word=visual.TextStim(win=win, ori=0, name='word',
    text='nonsense',
    font='Arial',
    pos=[0, 0], height=0.2,wrapWidth=None,
    color=1.0, colorSpace='rgb', opacity=1,
    depth=0.0)

#Initialise components for routine:thanks
thanksClock=core.Clock()
thanksText=visual.TextStim(win=win, ori=0, name='thanksText',
    text='This is the end of the experiment.\n\nThanks!',
    font='arial',
    pos=[0, 0], height=0.3,wrapWidth=None,
    color=[1, 1, 1], colorSpace='rgb', opacity=1,
    depth=0.0)

#Start of routine instruct
t=0; instructClock.reset()
frameN=-1

#update component parameters for each repeat
ready = event.BuilderKeyResponse() #create an object of type KeyResponse
ready.status=NOT_STARTED
#keep track of which have finished
instructComponents=[]#to keep track of which have finished
instructComponents.append(instrText)
instructComponents.append(ready)
for thisComponent in instructComponents:
    if hasattr(thisComponent,'status'): thisComponent.status = NOT_STARTED
#start the Routine
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
    if not continueRoutine:
        break # lets a component forceEndRoutine
    continueRoutine=False#will revert to True if at least one component still running
    for thisComponent in instructComponents:
        if hasattr(thisComponent,"status") and thisComponent.status!=FINISHED:
            continueRoutine=True; break#at least one component has not yet finished
    
    #check for quit (the [Esc] key)
    if event.getKeys(["escape"]): core.quit()
    #refresh the screen
    if continueRoutine:#don't flip if this routine is over or we'll get a blank screen
        win.flip()

#end of routine instruct
for thisComponent in instructComponents:
    if hasattr(thisComponent,"setAutoDraw"): thisComponent.setAutoDraw(False)

#set up handler to look after randomisation of conditions etc
trials=data.TrialHandler(nReps=1000.0, method='random', 
    extraInfo=expInfo, originPath=None,
    trialList=data.importConditions(os.path.join(settings.module_abs_path(), 'trialTypes.xlsx')),
    seed=None)
thisTrial=trials.trialList[0]#so we can initialise stimuli with some values
#abbreviate parameter names if possible (e.g. rgb=thisTrial.rgb)
if thisTrial!=None:
    for paramName in thisTrial.keys():
        exec(paramName+'=thisTrial.'+paramName)
#PK-b
#PK: totalCorrect, totalIncorrect counts number of correct/incorrect decisions
#PK: treshold - required number of correct (incorrect) deciosion
#PK: maxTime - time that user is given to answer
totalCorrect = 0;
totalIncorrect = 0;
treshold = 40;
maxTime = 2
#experimentClock.reset()
#beginnings = []
#answers = []
#coherences = []
#correctness = []
#experimentStartTime = None
#PK-e
first = False
for thisTrial in trials:
    #PK-b
    #PK: test for endiing condition
    if totalCorrect >= treshold and totalIncorrect >= treshold:
        break
    if ((totalIncorrect > 0 and totalCorrect/totalIncorrect > 1.2) or (totalIncorrect == 0 and totalCorrect > 10)) and maxTime > 0.7:
        maxTime -= 0.05
    if ((totalCorrect > 0 and totalIncorrect/totalCorrect > 1.2) or (totalIncorrect > 10 and totalCorrect == 0)) and maxTime < 2:
        maxTime += 0.05
    #PK-e
    currentLoop = trials
    #abbrieviate parameter names if possible (e.g. rgb=thisTrial.rgb)
    if thisTrial!=None:
        for paramName in thisTrial.keys():
            exec(paramName+'=thisTrial.'+paramName)
    
    #Start of routine trial
    t=0; trialClock.reset()
    t_start = time.time()
    frameN=-1
    
    #update component parameters for each repeat
    word.setColor(letterColor, colorSpace='rgb')
    word.setText(text)
    if first:
        experimentClock.reset()
        first = False
    #coherences.append(text == letterColor)
    #PK-b
    #currentTime = experimentClock.getTime()
    #if experimentStartTime == None:
    #    experimentStartTime = currentTime
    #beginnings.append(currentTime - experimentStartTime)
    #PK-e
    resp = event.BuilderKeyResponse() #create an object of type KeyResponse
    resp.status=NOT_STARTED
    #keep track of which have finished
    trialComponents=[]#to keep track of which have finished
    trialComponents.append(word)
    trialComponents.append(resp)
    for thisComponent in trialComponents:
        if hasattr(thisComponent,'status'): thisComponent.status = NOT_STARTED
    #start the Routine
    continueRoutine=True
    firstTime = None
    while continueRoutine:
        #get current time
        t=trialClock.getTime()
        #PK-b
        if firstTime == None:
            firstTime = t
        elif t - firstTime > maxTime:
            continueRoutine = False
            #correctness.append(-1)
            #answers.append(-1)
            break
        #PK-e
        frameN=frameN+1#number of completed frames (so 0 in first frame)
        #update/draw components on each frame
        
        #*word* updates
        if t>=0 and word.status==NOT_STARTED:
            #keep track of start time/frame for later
            word.tStart=t#underestimates by a little under one frame
            word.frameNStart=frameN#exact frame index
            word.setAutoDraw(True)
            first = True
        
        #*resp* updates
        if t>=0 and resp.status==NOT_STARTED:
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
                #PK: changed to first key pressed
                resp.keys=theseKeys[0]#just the last key pressed 
                resp.rt = resp.clock.getTime()
                #answers.append(resp.rt)
                #was this 'correct'?
                if (resp.keys==str(corrAns)):
                    #correctness.append(1)
                    resp.corr=1
                    totalCorrect += 1
                else: 
                    #correctness.append(0)
                    resp.corr=0
                    totalIncorrect += 1
                    errorCircle.setFillColor("white", colorSpace="rgb")
                    win.flip()
                    core.wait(1)
                    errorCircle.setFillColor("black", colorSpace="rgb")
                    win.flip()
                #abort routine on response
                continueRoutine=False
        
        #check if all components have finished
        if not continueRoutine:
            break # lets a component forceEndRoutine
        continueRoutine=False#will revert to True if at least one component still running
        for thisComponent in trialComponents:
            if hasattr(thisComponent,"status") and thisComponent.status!=FINISHED:
                continueRoutine=True; break#at least one component has not yet finished
        
        #check for quit (the [Esc] key)
        if event.getKeys(["escape"]): core.quit()
        #refresh the screen
        if continueRoutine:#don't flip if this routine is over or we'll get a blank screen
            win.flip()
    
    #end of routine trial
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
    t = t_start+word.tStart
    tags_helper.send_tag(
        TAGGER.conn, t, t, 
        "trial",
        {'keys':str(resp.keys),
         'corr':str(resp.corr),
         'rt':str(resp.rt),
         'text':str(text),
         'color':str(letterColor)
         }
        )


#completed 5.0 repeats of 'trials'

acquisition_helper.send_finish_saving(TAGGER.conn)
trials.saveAsPickle(filename+'trials')
trials.saveAsExcel(filename+'.xlsx', sheetName='trials',
    stimOut=trials.trialList[0].keys(),
    dataOut=['n','all_mean','all_std', 'all_raw'])


#Start of routine thanks
t=0; thanksClock.reset()
frameN=-1

#update component parameters for each repeat
#keep track of which have finished
thanksComponents=[]#to keep track of which have finished
thanksComponents.append(thanksText)
for thisComponent in thanksComponents:
    if hasattr(thisComponent,'status'): thisComponent.status = NOT_STARTED
#start the Routine
continueRoutine=True
while continueRoutine:
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
    if not continueRoutine:
        break # lets a component forceEndRoutine
    continueRoutine=False#will revert to True if at least one component still running
    for thisComponent in thanksComponents:
        if hasattr(thisComponent,"status") and thisComponent.status!=FINISHED:
            continueRoutine=True; break#at least one component has not yet finished
    
    #check for quit (the [Esc] key)
    if event.getKeys(["escape"]): core.quit()
    #refresh the screen
    if continueRoutine:#don't flip if this routine is over or we'll get a blank screen
        win.flip()
#print(beginnings)
#print(answers)
#print(coherences)
#print(correctness)
#end of routine thanks
for thisComponent in thanksComponents:
    if hasattr(thisComponent,"setAutoDraw"): thisComponent.setAutoDraw(False)

#Shutting down:
win.close()
core.quit()
