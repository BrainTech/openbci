#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
This experiment was created using PsychoPy2 Experiment Builder (v1.80.00), Fri 17 Jul 2015 07:05:30 PM CEST
If you publish work using this script please cite the relevant PsychoPy publications
  Peirce, JW (2007) PsychoPy - Psychophysics software in Python. Journal of Neuroscience Methods, 162(1-2), 8-13.
  Peirce, JW (2009) Generating stimuli for neuroscience using PsychoPy. Frontiers in Neuroinformatics, 2:10. doi: 10.3389/neuro.11.010.2008
"""

from __future__ import division  # so that 1/3=0.333 instead of 1/3=0
from psychopy import visual, core, data, event, logging, sound, gui
from psychopy.constants import *  # things like STARTED, FINISHED
import numpy as np  # whole numpy lib is available, prepend 'np.'
from numpy import sin, cos, tan, log, log10, pi, average, sqrt, std, deg2rad, rad2deg, linspace, asarray
from numpy.random import random, randint, normal, shuffle
import os  # handy system and path functions
from StringIO import StringIO
import base64

from obci.analysis.obci_signal_processing.tags.tags_file_writer import TagsFileWriter
import json, sys
# Store info about the experiment session
expName = 'stroop_psych'  # from the Builder filename that created this script
expInfo = {u'session': u'001', u'participant': u''}
externalExpInfo = json.loads(sys.argv[1])
expInfo.update(externalExpInfo)
if 'date' not in expInfo:
    expInfo['date'] = data.getDateStr()
expInfo['expName'] = expName

# Setup files for saving
filename = '~/ventures_experiment_data' + os.path.sep +'%s_%s_%s' %(expInfo['participant'], 'ventures_test_dual', expInfo['date'])
filename = os.path.expanduser(filename)
dataSavingDir = os.path.split(filename)[0]
if not os.path.isdir(dataSavingDir):
    os.makedirs(dataSavingDir)  # if this fails (e.g. permissions) we will get error

# An ExperimentHandler isn't essential but helps with data saving
thisExp = data.ExperimentHandler(name=expName, version='',
    extraInfo=expInfo, runtimeInfo=None,
    originPath='/home/ania/obci_mati/exps/ventures/dual_task_stroop/stroop_ventures_dual_3.psyexp',
    savePickle=True, saveWideText=False,
    dataFileName=filename)
logging.console.setLevel(logging.WARNING)  # this outputs to the screen, not a file

endExpNow = False  # flag for 'escape' or other condition => quit the exp
thisExp.sendTags = False
thisExp.saveTags = True
thisExp.tagList = []

#### Embedded resource definitions start ####
resources = {
    "nie_zgodne.csv":
    StringIO(base64.decodestring("""em5hY3plbmllLGN6Y2lvbmthCmN6ZXJ3b255LGdyZWVuCmN6ZXJ3b255LHllbGxvdwpjemVyd29u
eSxibHVlCsW8w7PFgnR5LHJlZArFvMOzxYJ0eSxncmVlbgrFvMOzxYJ0eSxibHVlCm5pZWJpZXNr
aSx5ZWxsb3cKbmllYmllc2tpLGdyZWVuCm5pZWJpZXNraSxyZWQKemllbG9ueSx5ZWxsb3cKemll
bG9ueSxyZWQKemllbG9ueSxibHVlCg==
"""))    ,
    "zgodne.csv":
    StringIO(base64.decodestring("""em5hY3plbmllLGN6Y2lvbmthCmN6ZXJ3b255LHJlZArFvMOzxYJ0eSx5ZWxsb3cKemllbG9ueSxn
cmVlbgpuaWViaWVza2ksYmx1ZQo=
"""))    ,
    "trening.csv":
    StringIO(base64.decodestring("""em5hY3plbmllLGN6Y2lvbmthLHBvcHJhd25hX29kcApjemVyd29ueSxncmVlbiw6IDgKY3plcndv
bnkseWVsbG93LDogOApjemVyd29ueSxibHVlLDogOArFvMOzxYJ0eSxyZWQsOiA5CsW8w7PFgnR5
LGdyZWVuLDogOQrFvMOzxYJ0eSxibHVlLDogOQpuaWViaWVza2kseWVsbG93LDogNwpuaWViaWVz
a2ksZ3JlZW4sOiA3Cm5pZWJpZXNraSxyZWQsOiA3CnppZWxvbnkseWVsbG93LDogMAp6aWVsb255
LHJlZCw6IDAKemllbG9ueSxibHVlLDogMApjemVyd29ueSxyZWQsOiA4CsW8w7PFgnR5LHllbGxv
dyw6IDkKemllbG9ueSxncmVlbiw6IDAKbmllYmllc2tpLGJsdWUsOiA3Cg==
"""))    ,
    "blok.csv":
    StringIO(base64.decodestring("""Ymxvawp6Z29kbnkKemdvZG55Cnpnb2RueQp6Z29kbnkKemdvZG55Cm5pZXpnb2RueQpuaWV6Z29k
bnkKbmllemdvZG55Cm5pZXpnb2RueQpuaWV6Z29kbnkK
"""))    }
#### Embedded resource definitions end ####


# Start Code - component code to be run before the window creation
import psychopy.contrib.obci
import psychopy.contrib as contrib
import psychopy.contrib.obci
import psychopy.contrib as contrib
import psychopy.contrib.obci
import psychopy.contrib as contrib
import psychopy.contrib.obci
import psychopy.contrib as contrib
import psychopy.contrib.obci
import psychopy.contrib as contrib

# Setup the Window
import psychopy.contrib.obci
import psychopy.contrib as contrib
win = contrib.obci.Window(None, size=(1366, 768), fullscr=True, screen=0, allowGUI=False, allowStencil=False,
    monitor='testMonitor', color=[0,0,0], colorSpace='rgb',
    blendMode='avg', useFBO=True,
    )
# store frame rate of monitor if we can measure it successfully
expInfo['frameRate']=win.getActualFrameRate()
if expInfo['frameRate']!=None:
    frameDur = 1.0/round(expInfo['frameRate'])
else:
    frameDur = 1.0/60.0 # couldn't get a reliable measure so guess

# Initialize components for Routine "instrukcja_2"
instrukcja_2Clock = core.Clock()
import time
text_8 = visual.TextStim(win=win, ori=0, name='text_8',
    text=u'INSTRUKCJA\n\n\n(wci\u015bnij spacj\u0119, \u017ceby przej\u015b\u0107 dalej)',    font='Arial',
    pos=[0, 0], height=0.08, wrapWidth=None,
    color='white', colorSpace='rgb', opacity=1,
    depth=-1.0)
tagger_5 = contrib.obci.TagOnFlip(
        window=win,
        tagName="timestamp", tagDescription={},        doSignal=False,
        sendTags=thisExp.sendTags, saveTags=thisExp.saveTags)
tagger_5.setTagDescription({'value':time.time()})
tagger_5.setTagName('timestamp')

# Initialize components for Routine "trening"
treningClock = core.Clock()
text_17 = visual.TextStim(win=win, ori=0, name='text_17',
    text='default text',    font='Arial',
    pos=[0, 0], height=0.2, wrapWidth=None,
    color=1.0, colorSpace='rgb', opacity=1,
    depth=0.0)
text_3 = visual.TextStim(win=win, ori=0, name='text_3',
    text='TRENING',    font='Arial',
    pos=[0, 0.5], height=0.1, wrapWidth=None,
    color='white', colorSpace='rgb', opacity=1,
    depth=-1.0)
image = visual.ImageStim(win=win, name='image',
    image=None, mask=None,
    ori=0, pos=[0, 0], size=[3.0, 3.0],
    color=[1,1,1], colorSpace='rgb', opacity=0,
    flipHoriz=False, flipVert=False,
    texRes=128, interpolate=True, depth=-2.0)
mouse = event.Mouse(win=win)
x, y = [None, None]

# Initialize components for Routine "instrukcja"
instrukcjaClock = core.Clock()
text_7 = visual.TextStim(win=win, ori=0, name='text_7',
    text=u'(wci\u015bnij spacj\u0119 aby przej\u015b\u0107 dalej)',    font='Arial',
    pos=[0, 0], height=0.08, wrapWidth=None,
    color='white', colorSpace='rgb', opacity=1,
    depth=0.0)

# Initialize components for Routine "poczatek_posturo"
poczatek_posturoClock = core.Clock()
text_5 = visual.TextStim(win=win, ori=0, name='text_5',
    text=None,    font='Arial',
    pos=[0, 0], height=0.1, wrapWidth=None,
    color='white', colorSpace='rgb', opacity=1,
    depth=0.0)
tagger_8 = contrib.obci.TagOnFlip(
        window=win,
        tagName="'{}_{}'.format($postural_task, 'start')", tagDescription={},        doSignal=False,
        sendTags=thisExp.sendTags, saveTags=thisExp.saveTags)

# Initialize components for Routine "zgodne"
zgodneClock = core.Clock()
text = visual.TextStim(win=win, ori=0, name='text',
    text='default text',    font='Arial',
    pos=[0, 0], height=0.2, wrapWidth=None,
    color=1.0, colorSpace='rgb', opacity=1,
    depth=0.0)
blok = 'zgodny'
mouse_2 = event.Mouse(win=win)
x, y = [None, None]
image_2 = visual.ImageStim(win=win, name='image_2',
    image=None, mask=None,
    ori=0, pos=[0, 0], size=[3.0, 3.0],
    color=[1,1,1], colorSpace='rgb', opacity=0,
    flipHoriz=False, flipVert=False,
    texRes=128, interpolate=True, depth=-3.0)
tagger = contrib.obci.TagOnFlip(
        window=win,
        tagName="$blok", tagDescription={},        doSignal=False,
        sendTags=thisExp.sendTags, saveTags=thisExp.saveTags)

# Initialize components for Routine "nie_zgodne"
nie_zgodneClock = core.Clock()
text_2 = visual.TextStim(win=win, ori=0, name='text_2',
    text='default text',    font='Arial',
    pos=[0, 0], height=0.2, wrapWidth=None,
    color=1.0, colorSpace='rgb', opacity=1,
    depth=0.0)

mouse_3 = event.Mouse(win=win)
x, y = [None, None]
image_3 = visual.ImageStim(win=win, name='image_3',
    image=None, mask=None,
    ori=0, pos=[0, 0], size=[3.0, 3.0],
    color=[1,1,1], colorSpace='rgb', opacity=0,
    flipHoriz=False, flipVert=False,
    texRes=128, interpolate=True, depth=-3.0)
tagger_2 = contrib.obci.TagOnFlip(
        window=win,
        tagName="$blok", tagDescription={},        doSignal=False,
        sendTags=thisExp.sendTags, saveTags=thisExp.saveTags)

# Initialize components for Routine "koniec_posturo"
koniec_posturoClock = core.Clock()
text_4 = visual.TextStim(win=win, ori=0, name='text_4',
    text=None,    font='Arial',
    pos=[0, 0], height=0.1, wrapWidth=None,
    color='white', colorSpace='rgb', opacity=1,
    depth=0.0)
tagger_7 = contrib.obci.TagOnFlip(
        window=win,
        tagName="'{}_{}'.format($postural_task, 'stop')", tagDescription={},        doSignal=False,
        sendTags=thisExp.sendTags, saveTags=thisExp.saveTags)

# Initialize components for Routine "papa"
papaClock = core.Clock()
text_10 = visual.TextStim(win=win, ori=0, name='text_10',
    text=u'Dzi\u0119kujemy za po\u015bwi\u0119cony czas.',    font='Arial',
    pos=[0, 0], height=0.1, wrapWidth=None,
    color='white', colorSpace='rgb', opacity=1,
    depth=0.0)

# Create some handy timers
globalClock = core.Clock()  # to track the time since experiment started
routineTimer = core.CountdownTimer()  # to track time remaining of each (non-slip) routine 

#------Prepare to start Routine "instrukcja_2"-------
t = 0
instrukcja_2Clock.reset()  # clock 
frameN = -1
# update component parameters for each repeat

key_resp_6 = event.BuilderKeyResponse()  # create an object of type KeyResponse
key_resp_6.status = NOT_STARTED
# keep track of which components have finished
instrukcja_2Components = []
instrukcja_2Components.append(text_8)
instrukcja_2Components.append(key_resp_6)
instrukcja_2Components.append(tagger_5)
for thisComponent in instrukcja_2Components:
    if hasattr(thisComponent, 'status'):
        thisComponent.status = NOT_STARTED

#-------Start Routine "instrukcja_2"-------
continueRoutine = True
while continueRoutine:
    # get current time
    t = instrukcja_2Clock.getTime()
    frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
    # update/draw components on each frame
    
    
    # *text_8* updates
    if t >= 0.0 and text_8.status == NOT_STARTED:
        # keep track of start time/frame for later
        text_8.tStart = t  # underestimates by a little under one frame
        text_8.frameNStart = frameN  # exact frame index
        text_8.setAutoDraw(True)
    
    # *key_resp_6* updates
    if t >= 0.0 and key_resp_6.status == NOT_STARTED:
        # keep track of start time/frame for later
        key_resp_6.tStart = t  # underestimates by a little under one frame
        key_resp_6.frameNStart = frameN  # exact frame index
        key_resp_6.status = STARTED
        # keyboard checking is just starting
        key_resp_6.clock.reset()  # now t=0
        event.clearEvents(eventType='keyboard')
    if key_resp_6.status == STARTED:
        theseKeys = event.getKeys(keyList=['space'])
        
        # check for quit:
        if "escape" in theseKeys:
            endExpNow = True
        if len(theseKeys) > 0:  # at least one key was pressed
            if key_resp_6.keys == []:  # then this was the first keypress
                key_resp_6.keys = theseKeys[0]  # just the first key pressed
                key_resp_6.rt = key_resp_6.clock.getTime()
                # a response ends the routine
                continueRoutine = False
    if t >= 0.0 and tagger_5.status == NOT_STARTED:
        # keep track of start time/frame for later
        tagger_5.tStart = t  # underestimates by a little under one frame
        tagger_5.frameNStart = frameN  # exact frame index
        tagger_5.scheduleStart()
        tagger_5.status = STARTED
    elif tagger_5.status == STARTED and frameN >= (tagger_5.frameNStart + 1):
        tagger_5.scheduleStop()
        tagger_5.status = FINISHED
    
    # check if all components have finished
    if not continueRoutine:  # a component has requested a forced-end of Routine
        routineTimer.reset()  # if we abort early the non-slip timer needs reset
        break
    continueRoutine = False  # will revert to True if at least one component still running
    for thisComponent in instrukcja_2Components:
        if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
            continueRoutine = True
            break  # at least one component has not yet finished
    
    # check for quit (the Esc key)
    if endExpNow or event.getKeys(keyList=["escape"]):
        core.quit()
    
    # refresh the screen
    if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
        win.flip()
    else:  # this Routine was not non-slip safe so reset non-slip timer
        routineTimer.reset()

#-------Ending Routine "instrukcja_2"-------
for thisComponent in instrukcja_2Components:
    if hasattr(thisComponent, "setAutoDraw"):
        thisComponent.setAutoDraw(False)


# set up handler to look after randomisation of conditions etc
trenujemy = data.TrialHandler(nReps=1, method='no-repeat random', 
    extraInfo=expInfo, originPath='/home/ania/obci_mati/exps/ventures/dual_task_stroop/stroop_ventures_dual_3.psyexp',
    trialList=data.importConditions('./trening.pkl'),
    seed=None, name='trenujemy')
thisExp.addLoop(trenujemy)  # add the loop to the experiment
thisTrenujemy = trenujemy.trialList[0]  # so we can initialise stimuli with some values
# abbreviate parameter names if possible (e.g. rgb=thisTrenujemy.rgb)
if thisTrenujemy != None:
    for paramName in thisTrenujemy.keys():
        exec(paramName + '= thisTrenujemy.' + paramName)

for thisTrenujemy in trenujemy:
    currentLoop = trenujemy
    # abbreviate parameter names if possible (e.g. rgb = thisTrenujemy.rgb)
    if thisTrenujemy != None:
        for paramName in thisTrenujemy.keys():
            exec(paramName + '= thisTrenujemy.' + paramName)
    
    #------Prepare to start Routine "trening"-------
    t = 0
    treningClock.reset()  # clock 
    frameN = -1
    # update component parameters for each repeat
    text_17.setColor(czcionka, colorSpace='rgb')
    text_17.setText(znaczenie)
    # setup some python lists for storing info about the mouse
    mouse.x = []
    mouse.y = []
    mouse.leftButton = []
    mouse.midButton = []
    mouse.rightButton = []
    mouse.time = []
    mouse.selection = []
    # keep track of which components have finished
    treningComponents = []
    treningComponents.append(text_17)
    treningComponents.append(text_3)
    treningComponents.append(image)
    treningComponents.append(mouse)
    for thisComponent in treningComponents:
        if hasattr(thisComponent, 'status'):
            thisComponent.status = NOT_STARTED
    
    #-------Start Routine "trening"-------
    continueRoutine = True
    while continueRoutine:
        # get current time
        t = treningClock.getTime()
        frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
        # update/draw components on each frame
        
        # *text_17* updates
        if t >= 0.0 and text_17.status == NOT_STARTED:
            # keep track of start time/frame for later
            text_17.tStart = t  # underestimates by a little under one frame
            text_17.frameNStart = frameN  # exact frame index
            text_17.setAutoDraw(True)
        
        # *text_3* updates
        if t >= 0.0 and text_3.status == NOT_STARTED:
            # keep track of start time/frame for later
            text_3.tStart = t  # underestimates by a little under one frame
            text_3.frameNStart = frameN  # exact frame index
            text_3.setAutoDraw(True)
        
        # *image* updates
        if t >= 0.0 and image.status == NOT_STARTED:
            # keep track of start time/frame for later
            image.tStart = t  # underestimates by a little under one frame
            image.frameNStart = frameN  # exact frame index
            image.setAutoDraw(True)
        # *mouse* updates
        if t >= 0.0 and mouse.status == NOT_STARTED:
            # keep track of start time/frame for later
            mouse.tStart = t  # underestimates by a little under one frame
            mouse.frameNStart = frameN  # exact frame index
            mouse.status = STARTED
            event.mouseButtons = [0, 0, 0]  # reset mouse buttons to be 'up'
        if mouse.status == STARTED:  # only update if started and not stopped!
            buttons = mouse.getPressed()
            if sum(buttons) > 0:  # ie if any button is pressed
                acceptClick = False
                for mask in [image]:
                    if mask.contains(mouse):
                        mouse.selection.append(mask.name)
                        acceptClick = True
                        break
                if acceptClick:
                    x, y = mouse.getPos()
                    mouse.x.append(x)
                    mouse.y.append(y)
                    mouse.leftButton.append(buttons[0])
                    mouse.midButton.append(buttons[1])
                    mouse.rightButton.append(buttons[2])
                    mouse.time.append(treningClock.getTime())
                    # abort routine on response
                    continueRoutine = False
        
        # check if all components have finished
        if not continueRoutine:  # a component has requested a forced-end of Routine
            routineTimer.reset()  # if we abort early the non-slip timer needs reset
            break
        continueRoutine = False  # will revert to True if at least one component still running
        for thisComponent in treningComponents:
            if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                continueRoutine = True
                break  # at least one component has not yet finished
        
        # check for quit (the Esc key)
        if endExpNow or event.getKeys(keyList=["escape"]):
            core.quit()
        
        # refresh the screen
        if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
            win.flip()
        else:  # this Routine was not non-slip safe so reset non-slip timer
            routineTimer.reset()
    
    #-------Ending Routine "trening"-------
    for thisComponent in treningComponents:
        if hasattr(thisComponent, "setAutoDraw"):
            thisComponent.setAutoDraw(False)
    # save mouse data
    trenujemy.addData('mouse.x', mouse.x[0])
    trenujemy.addData('mouse.y', mouse.y[0])
    trenujemy.addData('mouse.leftButton', mouse.leftButton[0])
    trenujemy.addData('mouse.midButton', mouse.midButton[0])
    trenujemy.addData('mouse.rightButton', mouse.rightButton[0])
    trenujemy.addData('mouse.time', mouse.time[0])
    trenujemy.addData('mouse.selection', mouse.selection[0])
    thisExp.nextEntry()
    
# completed 1 repeats of 'trenujemy'


# set up handler to look after randomisation of conditions etc
posturo = data.TrialHandler(nReps=1, method='sequential', 
    extraInfo=expInfo, originPath='/home/ania/obci_mati/exps/ventures/dual_task_stroop/stroop_ventures_dual_3.psyexp',
    trialList=data.importConditions('./postural_tasks.pkl'),
    seed=None, name='posturo')
thisExp.addLoop(posturo)  # add the loop to the experiment
thisPosturo = posturo.trialList[0]  # so we can initialise stimuli with some values
# abbreviate parameter names if possible (e.g. rgb=thisPosturo.rgb)
if thisPosturo != None:
    for paramName in thisPosturo.keys():
        exec(paramName + '= thisPosturo.' + paramName)

for thisPosturo in posturo:
    currentLoop = posturo
    # abbreviate parameter names if possible (e.g. rgb = thisPosturo.rgb)
    if thisPosturo != None:
        for paramName in thisPosturo.keys():
            exec(paramName + '= thisPosturo.' + paramName)
    
    #------Prepare to start Routine "instrukcja"-------
    t = 0
    instrukcjaClock.reset()  # clock 
    frameN = -1
    # update component parameters for each repeat
    key_resp_5 = event.BuilderKeyResponse()  # create an object of type KeyResponse
    key_resp_5.status = NOT_STARTED
    # keep track of which components have finished
    instrukcjaComponents = []
    instrukcjaComponents.append(text_7)
    instrukcjaComponents.append(key_resp_5)
    for thisComponent in instrukcjaComponents:
        if hasattr(thisComponent, 'status'):
            thisComponent.status = NOT_STARTED
    
    #-------Start Routine "instrukcja"-------
    continueRoutine = True
    while continueRoutine:
        # get current time
        t = instrukcjaClock.getTime()
        frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
        # update/draw components on each frame
        
        # *text_7* updates
        if t >= 0.0 and text_7.status == NOT_STARTED:
            # keep track of start time/frame for later
            text_7.tStart = t  # underestimates by a little under one frame
            text_7.frameNStart = frameN  # exact frame index
            text_7.setAutoDraw(True)
        
        # *key_resp_5* updates
        if t >= 0.0 and key_resp_5.status == NOT_STARTED:
            # keep track of start time/frame for later
            key_resp_5.tStart = t  # underestimates by a little under one frame
            key_resp_5.frameNStart = frameN  # exact frame index
            key_resp_5.status = STARTED
            # keyboard checking is just starting
            key_resp_5.clock.reset()  # now t=0
            event.clearEvents(eventType='keyboard')
        if key_resp_5.status == STARTED:
            theseKeys = event.getKeys(keyList=['space'])
            
            # check for quit:
            if "escape" in theseKeys:
                endExpNow = True
            if len(theseKeys) > 0:  # at least one key was pressed
                if key_resp_5.keys == []:  # then this was the first keypress
                    key_resp_5.keys = theseKeys[0]  # just the first key pressed
                    key_resp_5.rt = key_resp_5.clock.getTime()
                    # a response ends the routine
                    continueRoutine = False
        
        # check if all components have finished
        if not continueRoutine:  # a component has requested a forced-end of Routine
            routineTimer.reset()  # if we abort early the non-slip timer needs reset
            break
        continueRoutine = False  # will revert to True if at least one component still running
        for thisComponent in instrukcjaComponents:
            if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                continueRoutine = True
                break  # at least one component has not yet finished
        
        # check for quit (the Esc key)
        if endExpNow or event.getKeys(keyList=["escape"]):
            core.quit()
        
        # refresh the screen
        if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
            win.flip()
        else:  # this Routine was not non-slip safe so reset non-slip timer
            routineTimer.reset()
    
    #-------Ending Routine "instrukcja"-------
    for thisComponent in instrukcjaComponents:
        if hasattr(thisComponent, "setAutoDraw"):
            thisComponent.setAutoDraw(False)
    # check responses
    if key_resp_5.keys in ['', [], None]:  # No response was made
       key_resp_5.keys=None
    # store data for posturo (TrialHandler)
    posturo.addData('key_resp_5.keys',key_resp_5.keys)
    if key_resp_5.keys != None:  # we had a response
        posturo.addData('key_resp_5.rt', key_resp_5.rt)
    
    #------Prepare to start Routine "poczatek_posturo"-------
    t = 0
    poczatek_posturoClock.reset()  # clock 
    frameN = -1
    # update component parameters for each repeat
    tagger_8.setTagDescription({})
    tagger_8.setTagName('{}_{}'.format(postural_task, 'start'))
    # keep track of which components have finished
    poczatek_posturoComponents = []
    poczatek_posturoComponents.append(text_5)
    poczatek_posturoComponents.append(tagger_8)
    for thisComponent in poczatek_posturoComponents:
        if hasattr(thisComponent, 'status'):
            thisComponent.status = NOT_STARTED
    
    #-------Start Routine "poczatek_posturo"-------
    continueRoutine = True
    while continueRoutine:
        # get current time
        t = poczatek_posturoClock.getTime()
        frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
        # update/draw components on each frame
        
        # *text_5* updates
        if t >= 0.0 and text_5.status == NOT_STARTED:
            # keep track of start time/frame for later
            text_5.tStart = t  # underestimates by a little under one frame
            text_5.frameNStart = frameN  # exact frame index
            text_5.setAutoDraw(True)
        elif text_5.status == STARTED and t >= (0.0 + (0.1-win.monitorFramePeriod*0.75)):
            text_5.setAutoDraw(False)
        if t >= 0.0 and tagger_8.status == NOT_STARTED:
            # keep track of start time/frame for later
            tagger_8.tStart = t  # underestimates by a little under one frame
            tagger_8.frameNStart = frameN  # exact frame index
            tagger_8.scheduleStart()
            tagger_8.status = STARTED
        elif tagger_8.status == STARTED and frameN >= (tagger_8.frameNStart + 1):
            tagger_8.scheduleStop()
            tagger_8.status = FINISHED
        
        # check if all components have finished
        if not continueRoutine:  # a component has requested a forced-end of Routine
            routineTimer.reset()  # if we abort early the non-slip timer needs reset
            break
        continueRoutine = False  # will revert to True if at least one component still running
        for thisComponent in poczatek_posturoComponents:
            if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                continueRoutine = True
                break  # at least one component has not yet finished
        
        # check for quit (the Esc key)
        if endExpNow or event.getKeys(keyList=["escape"]):
            core.quit()
        
        # refresh the screen
        if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
            win.flip()
        else:  # this Routine was not non-slip safe so reset non-slip timer
            routineTimer.reset()
    
    #-------Ending Routine "poczatek_posturo"-------
    for thisComponent in poczatek_posturoComponents:
        if hasattr(thisComponent, "setAutoDraw"):
            thisComponent.setAutoDraw(False)
    
    # set up handler to look after randomisation of conditions etc
    losowanko = data.TrialHandler(nReps=1, method='sequential', 
        extraInfo=expInfo, originPath='/home/ania/obci_mati/exps/ventures/dual_task_stroop/stroop_ventures_dual_3.psyexp',
        trialList=data.importConditions('./bloki.pkl'),
        seed=None, name='losowanko')
    thisExp.addLoop(losowanko)  # add the loop to the experiment
    thisLosowanko = losowanko.trialList[0]  # so we can initialise stimuli with some values
    # abbreviate parameter names if possible (e.g. rgb=thisLosowanko.rgb)
    if thisLosowanko != None:
        for paramName in thisLosowanko.keys():
            exec(paramName + '= thisLosowanko.' + paramName)
    
    for thisLosowanko in losowanko:
        currentLoop = losowanko
        # abbreviate parameter names if possible (e.g. rgb = thisLosowanko.rgb)
        if thisLosowanko != None:
            for paramName in thisLosowanko.keys():
                exec(paramName + '= thisLosowanko.' + paramName)
        
        # set up handler to look after randomisation of conditions etc
        zgod = data.TrialHandler(nReps=3, method='no-repeat random', 
            extraInfo=expInfo, originPath='/home/ania/obci_mati/exps/ventures/dual_task_stroop/stroop_ventures_dual_3.psyexp',
            trialList=data.importConditions('./zgodne.pkl'),
            seed=None, name='zgod')
        thisExp.addLoop(zgod)  # add the loop to the experiment
        thisZgod = zgod.trialList[0]  # so we can initialise stimuli with some values
        # abbreviate parameter names if possible (e.g. rgb=thisZgod.rgb)
        if thisZgod != None:
            for paramName in thisZgod.keys():
                exec(paramName + '= thisZgod.' + paramName)
        
        for thisZgod in zgod:
            currentLoop = zgod
            # abbreviate parameter names if possible (e.g. rgb = thisZgod.rgb)
            if thisZgod != None:
                for paramName in thisZgod.keys():
                    exec(paramName + '= thisZgod.' + paramName)
            
            #------Prepare to start Routine "zgodne"-------
            t = 0
            zgodneClock.reset()  # clock 
            frameN = -1
            # update component parameters for each repeat
            text.setColor(czcionka, colorSpace='rgb')
            text.setText(znaczenie)
            if blok == 'niezgodny':
                break
            # setup some python lists for storing info about the mouse_2
            mouse_2.x = []
            mouse_2.y = []
            mouse_2.leftButton = []
            mouse_2.midButton = []
            mouse_2.rightButton = []
            mouse_2.time = []
            mouse_2.selection = []
            tagger.setTagDescription({'czcionka':czcionka, 'znaczenie':znaczenie})
            tagger.setTagName(blok)
            # keep track of which components have finished
            zgodneComponents = []
            zgodneComponents.append(text)
            zgodneComponents.append(mouse_2)
            zgodneComponents.append(image_2)
            zgodneComponents.append(tagger)
            for thisComponent in zgodneComponents:
                if hasattr(thisComponent, 'status'):
                    thisComponent.status = NOT_STARTED
            
            #-------Start Routine "zgodne"-------
            continueRoutine = True
            while continueRoutine:
                # get current time
                t = zgodneClock.getTime()
                frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
                # update/draw components on each frame
                
                # *text* updates
                if t >= 0.0 and text.status == NOT_STARTED:
                    # keep track of start time/frame for later
                    text.tStart = t  # underestimates by a little under one frame
                    text.frameNStart = frameN  # exact frame index
                    text.setAutoDraw(True)
                
                # *mouse_2* updates
                if t >= 0.0 and mouse_2.status == NOT_STARTED:
                    # keep track of start time/frame for later
                    mouse_2.tStart = t  # underestimates by a little under one frame
                    mouse_2.frameNStart = frameN  # exact frame index
                    mouse_2.status = STARTED
                    event.mouseButtons = [0, 0, 0]  # reset mouse buttons to be 'up'
                if mouse_2.status == STARTED:  # only update if started and not stopped!
                    buttons = mouse_2.getPressed()
                    if sum(buttons) > 0:  # ie if any button is pressed
                        acceptClick = False
                        for mask in [image_2]:
                            if mask.contains(mouse_2):
                                mouse_2.selection.append(mask.name)
                                acceptClick = True
                                break
                        if acceptClick:
                            x, y = mouse_2.getPos()
                            mouse_2.x.append(x)
                            mouse_2.y.append(y)
                            mouse_2.leftButton.append(buttons[0])
                            mouse_2.midButton.append(buttons[1])
                            mouse_2.rightButton.append(buttons[2])
                            mouse_2.time.append(zgodneClock.getTime())
                            # abort routine on response
                            continueRoutine = False
                
                # *image_2* updates
                if t >= 0.0 and image_2.status == NOT_STARTED:
                    # keep track of start time/frame for later
                    image_2.tStart = t  # underestimates by a little under one frame
                    image_2.frameNStart = frameN  # exact frame index
                    image_2.setAutoDraw(True)
                if t >= 0.0 and tagger.status == NOT_STARTED:
                    # keep track of start time/frame for later
                    tagger.tStart = t  # underestimates by a little under one frame
                    tagger.frameNStart = frameN  # exact frame index
                    tagger.scheduleStart()
                    tagger.status = STARTED
                elif tagger.status == STARTED and frameN >= (tagger.frameNStart + 1):
                    tagger.scheduleStop()
                    tagger.status = FINISHED
                
                # check if all components have finished
                if not continueRoutine:  # a component has requested a forced-end of Routine
                    routineTimer.reset()  # if we abort early the non-slip timer needs reset
                    break
                continueRoutine = False  # will revert to True if at least one component still running
                for thisComponent in zgodneComponents:
                    if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                        continueRoutine = True
                        break  # at least one component has not yet finished
                
                # check for quit (the Esc key)
                if endExpNow or event.getKeys(keyList=["escape"]):
                    core.quit()
                
                # refresh the screen
                if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
                    win.flip()
                else:  # this Routine was not non-slip safe so reset non-slip timer
                    routineTimer.reset()
            
            #-------Ending Routine "zgodne"-------
            for thisComponent in zgodneComponents:
                if hasattr(thisComponent, "setAutoDraw"):
                    thisComponent.setAutoDraw(False)
            
            # save mouse_2 data
            zgod.addData('mouse_2.x', mouse_2.x[0])
            zgod.addData('mouse_2.y', mouse_2.y[0])
            zgod.addData('mouse_2.leftButton', mouse_2.leftButton[0])
            zgod.addData('mouse_2.midButton', mouse_2.midButton[0])
            zgod.addData('mouse_2.rightButton', mouse_2.rightButton[0])
            zgod.addData('mouse_2.time', mouse_2.time[0])
            zgod.addData('mouse_2.selection', mouse_2.selection[0])
            thisExp.nextEntry()
            
        # completed 3 repeats of 'zgod'
        
        
        # set up handler to look after randomisation of conditions etc
        nie_zgod = data.TrialHandler(nReps=1, method='no-repeat random', 
            extraInfo=expInfo, originPath='/home/ania/obci_mati/exps/ventures/dual_task_stroop/stroop_ventures_dual_3.psyexp',
            trialList=data.importConditions('./nie_zgodne.pkl'),
            seed=None, name='nie_zgod')
        thisExp.addLoop(nie_zgod)  # add the loop to the experiment
        thisNie_zgod = nie_zgod.trialList[0]  # so we can initialise stimuli with some values
        # abbreviate parameter names if possible (e.g. rgb=thisNie_zgod.rgb)
        if thisNie_zgod != None:
            for paramName in thisNie_zgod.keys():
                exec(paramName + '= thisNie_zgod.' + paramName)
        
        for thisNie_zgod in nie_zgod:
            currentLoop = nie_zgod
            # abbreviate parameter names if possible (e.g. rgb = thisNie_zgod.rgb)
            if thisNie_zgod != None:
                for paramName in thisNie_zgod.keys():
                    exec(paramName + '= thisNie_zgod.' + paramName)
            
            #------Prepare to start Routine "nie_zgodne"-------
            t = 0
            nie_zgodneClock.reset()  # clock 
            frameN = -1
            # update component parameters for each repeat
            text_2.setColor(czcionka, colorSpace='rgb')
            text_2.setText(znaczenie)
            if blok == 'zgodny':
                break
            # setup some python lists for storing info about the mouse_3
            mouse_3.x = []
            mouse_3.y = []
            mouse_3.leftButton = []
            mouse_3.midButton = []
            mouse_3.rightButton = []
            mouse_3.time = []
            mouse_3.selection = []
            tagger_2.setTagDescription({'czcionka':czcionka, 'znaczenie':znaczenie})
            tagger_2.setTagName(blok)
            # keep track of which components have finished
            nie_zgodneComponents = []
            nie_zgodneComponents.append(text_2)
            nie_zgodneComponents.append(mouse_3)
            nie_zgodneComponents.append(image_3)
            nie_zgodneComponents.append(tagger_2)
            for thisComponent in nie_zgodneComponents:
                if hasattr(thisComponent, 'status'):
                    thisComponent.status = NOT_STARTED
            
            #-------Start Routine "nie_zgodne"-------
            continueRoutine = True
            while continueRoutine:
                # get current time
                t = nie_zgodneClock.getTime()
                frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
                # update/draw components on each frame
                
                # *text_2* updates
                if t >= 0.0 and text_2.status == NOT_STARTED:
                    # keep track of start time/frame for later
                    text_2.tStart = t  # underestimates by a little under one frame
                    text_2.frameNStart = frameN  # exact frame index
                    text_2.setAutoDraw(True)
                
                # *mouse_3* updates
                if t >= 0.0 and mouse_3.status == NOT_STARTED:
                    # keep track of start time/frame for later
                    mouse_3.tStart = t  # underestimates by a little under one frame
                    mouse_3.frameNStart = frameN  # exact frame index
                    mouse_3.status = STARTED
                    event.mouseButtons = [0, 0, 0]  # reset mouse buttons to be 'up'
                if mouse_3.status == STARTED:  # only update if started and not stopped!
                    buttons = mouse_3.getPressed()
                    if sum(buttons) > 0:  # ie if any button is pressed
                        acceptClick = False
                        for mask in [image_3]:
                            if mask.contains(mouse_3):
                                mouse_3.selection.append(mask.name)
                                acceptClick = True
                                break
                        if acceptClick:
                            x, y = mouse_3.getPos()
                            mouse_3.x.append(x)
                            mouse_3.y.append(y)
                            mouse_3.leftButton.append(buttons[0])
                            mouse_3.midButton.append(buttons[1])
                            mouse_3.rightButton.append(buttons[2])
                            mouse_3.time.append(nie_zgodneClock.getTime())
                            # abort routine on response
                            continueRoutine = False
                
                # *image_3* updates
                if t >= 0.0 and image_3.status == NOT_STARTED:
                    # keep track of start time/frame for later
                    image_3.tStart = t  # underestimates by a little under one frame
                    image_3.frameNStart = frameN  # exact frame index
                    image_3.setAutoDraw(True)
                if t >= 0.0 and tagger_2.status == NOT_STARTED:
                    # keep track of start time/frame for later
                    tagger_2.tStart = t  # underestimates by a little under one frame
                    tagger_2.frameNStart = frameN  # exact frame index
                    tagger_2.scheduleStart()
                    tagger_2.status = STARTED
                elif tagger_2.status == STARTED and frameN >= (tagger_2.frameNStart + 1):
                    tagger_2.scheduleStop()
                    tagger_2.status = FINISHED
                
                # check if all components have finished
                if not continueRoutine:  # a component has requested a forced-end of Routine
                    routineTimer.reset()  # if we abort early the non-slip timer needs reset
                    break
                continueRoutine = False  # will revert to True if at least one component still running
                for thisComponent in nie_zgodneComponents:
                    if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                        continueRoutine = True
                        break  # at least one component has not yet finished
                
                # check for quit (the Esc key)
                if endExpNow or event.getKeys(keyList=["escape"]):
                    core.quit()
                
                # refresh the screen
                if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
                    win.flip()
                else:  # this Routine was not non-slip safe so reset non-slip timer
                    routineTimer.reset()
            
            #-------Ending Routine "nie_zgodne"-------
            for thisComponent in nie_zgodneComponents:
                if hasattr(thisComponent, "setAutoDraw"):
                    thisComponent.setAutoDraw(False)
            
            # save mouse_3 data
            nie_zgod.addData('mouse_3.x', mouse_3.x[0])
            nie_zgod.addData('mouse_3.y', mouse_3.y[0])
            nie_zgod.addData('mouse_3.leftButton', mouse_3.leftButton[0])
            nie_zgod.addData('mouse_3.midButton', mouse_3.midButton[0])
            nie_zgod.addData('mouse_3.rightButton', mouse_3.rightButton[0])
            nie_zgod.addData('mouse_3.time', mouse_3.time[0])
            nie_zgod.addData('mouse_3.selection', mouse_3.selection[0])
            thisExp.nextEntry()
            
        # completed 1 repeats of 'nie_zgod'
        
        thisExp.nextEntry()
        
    # completed 1 repeats of 'losowanko'
    
    
    #------Prepare to start Routine "koniec_posturo"-------
    t = 0
    koniec_posturoClock.reset()  # clock 
    frameN = -1
    # update component parameters for each repeat
    tagger_7.setTagDescription({})
    tagger_7.setTagName('{}_{}'.format(postural_task, 'stop'))
    # keep track of which components have finished
    koniec_posturoComponents = []
    koniec_posturoComponents.append(text_4)
    koniec_posturoComponents.append(tagger_7)
    for thisComponent in koniec_posturoComponents:
        if hasattr(thisComponent, 'status'):
            thisComponent.status = NOT_STARTED
    
    #-------Start Routine "koniec_posturo"-------
    continueRoutine = True
    while continueRoutine:
        # get current time
        t = koniec_posturoClock.getTime()
        frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
        # update/draw components on each frame
        
        # *text_4* updates
        if t >= 0.0 and text_4.status == NOT_STARTED:
            # keep track of start time/frame for later
            text_4.tStart = t  # underestimates by a little under one frame
            text_4.frameNStart = frameN  # exact frame index
            text_4.setAutoDraw(True)
        elif text_4.status == STARTED and t >= (0.0 + (0.2-win.monitorFramePeriod*0.75)):
            text_4.setAutoDraw(False)
        if t >= 0.0 and tagger_7.status == NOT_STARTED:
            # keep track of start time/frame for later
            tagger_7.tStart = t  # underestimates by a little under one frame
            tagger_7.frameNStart = frameN  # exact frame index
            tagger_7.scheduleStart()
            tagger_7.status = STARTED
        elif tagger_7.status == STARTED and frameN >= (tagger_7.frameNStart + 1):
            tagger_7.scheduleStop()
            tagger_7.status = FINISHED
        
        # check if all components have finished
        if not continueRoutine:  # a component has requested a forced-end of Routine
            routineTimer.reset()  # if we abort early the non-slip timer needs reset
            break
        continueRoutine = False  # will revert to True if at least one component still running
        for thisComponent in koniec_posturoComponents:
            if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                continueRoutine = True
                break  # at least one component has not yet finished
        
        # check for quit (the Esc key)
        if endExpNow or event.getKeys(keyList=["escape"]):
            core.quit()
        
        # refresh the screen
        if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
            win.flip()
        else:  # this Routine was not non-slip safe so reset non-slip timer
            routineTimer.reset()
    
    #-------Ending Routine "koniec_posturo"-------
    for thisComponent in koniec_posturoComponents:
        if hasattr(thisComponent, "setAutoDraw"):
            thisComponent.setAutoDraw(False)
    thisExp.nextEntry()
    
# completed 1 repeats of 'posturo'


#------Prepare to start Routine "papa"-------
t = 0
papaClock.reset()  # clock 
frameN = -1
routineTimer.add(10.000000)
# update component parameters for each repeat
# keep track of which components have finished
papaComponents = []
papaComponents.append(text_10)
for thisComponent in papaComponents:
    if hasattr(thisComponent, 'status'):
        thisComponent.status = NOT_STARTED

#-------Start Routine "papa"-------
continueRoutine = True
while continueRoutine and routineTimer.getTime() > 0:
    # get current time
    t = papaClock.getTime()
    frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
    # update/draw components on each frame
    
    # *text_10* updates
    if t >= 0.0 and text_10.status == NOT_STARTED:
        # keep track of start time/frame for later
        text_10.tStart = t  # underestimates by a little under one frame
        text_10.frameNStart = frameN  # exact frame index
        text_10.setAutoDraw(True)
    elif text_10.status == STARTED and t >= (0.0 + (10-win.monitorFramePeriod*0.75)):
        text_10.setAutoDraw(False)
    
    # check if all components have finished
    if not continueRoutine:  # a component has requested a forced-end of Routine
        routineTimer.reset()  # if we abort early the non-slip timer needs reset
        break
    continueRoutine = False  # will revert to True if at least one component still running
    for thisComponent in papaComponents:
        if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
            continueRoutine = True
            break  # at least one component has not yet finished
    
    # check for quit (the Esc key)
    if endExpNow or event.getKeys(keyList=["escape"]):
        core.quit()
    
    # refresh the screen
    if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
        win.flip()

#-------Ending Routine "papa"-------
for thisComponent in papaComponents:
    if hasattr(thisComponent, "setAutoDraw"):
        thisComponent.setAutoDraw(False)



tagWriter = TagsFileWriter(filename + ".psychopy.tag")
for tag in contrib.obci.TagOnFlip.tags:
    tagWriter.tag_received(tag)
tagWriter.finish_saving(logging.defaultClock.getLastResetTime())

win.close()
core.quit()
