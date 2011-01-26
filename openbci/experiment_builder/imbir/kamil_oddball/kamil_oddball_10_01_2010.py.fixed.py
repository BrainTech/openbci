#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""This experiment was created using PsychoPy2 Experiment Builder
If you publish work using this script please cite the relevant PsychoPy publications
  Peirce (2007) Journal of Neuroscience Methods 162:8-1
  Peirce (2009) Frontiers in Neuroinformatics, 2: 10"""

from numpy import * #many different maths functions
from numpy.random import * #maths randomisation functions
import os #handy system and path functions
from psychopy import core, data, event, visual, gui
import psychopy.log #import like this so it doesn't interfere with numpy.log

#store info about the experiment
expName='None'#from the Builder filename that created this script
expInfo={'participant':'ID01', 'session':001}
dlg=gui.DlgFromDict(dictionary=expInfo,title=expName)
if dlg.OK==False: core.quit() #user pressed cancel
expInfo['date']=data.getDateStr()#add a simple timestamp
expInfo['expName']=expName
#setup files for saving
if not os.path.isdir('data'):
    os.makedirs('data')#if this fails (e.g. permissions) we will get error
filename= 'data/%s_%s' %(expInfo['participant'], expInfo['date'])
logFile=open(filename+'.log', 'w')
psychopy.log.console.setLevel(psychopy.log.WARNING)#this outputs to the screen, not a file

#setup the Window
win = visual.Window(size=[1280, 800], fullscr=True, screen=0, allowGUI=False,
    monitor='testMonitor', color='white', colorSpace='rgb')

#Initialise components for routine:int1
int1Clock=core.Clock()
dsf=visual.TextStim(win=win, ori=0,
    text=u'Zapraszamy do udzia\u0142u w badaniu.',
    pos=[0, 0], height=0.1,
    color=u'black', colorSpace=u'rgb')

#Initialise components for routine:int2
int2Clock=core.Clock()
uiuiyhiu=visual.TextStim(win=win, ori=0,
    text=u'Twoje zadanie b\u0119dzie polega\u0142o na\nczytaniu i ocenianiu s\u0142\xf3w\npojawiaj\u0105cych si\u0119 kolejno na ekranie.\nWci\u015bnij klawisz SPACE zawsze wtedy,\nkiedy prezentowane s\u0142owo b\u0119dzie\nzwi\u0105zane z emocjami.\nAby przej\u015b\u0107 dalej naci\u015bnij SPACE.',
    pos=[0, 0], height=0.1,
    color=u'black', colorSpace=u'rgb')
#create our own class to store info from keyboard
class KeyResponse:
    def __init__(self):
        self.keys=[]#the key(s) pressed
        self.corr=0#was the resp correct this trial? (0=no, 1=yes)
        self.rt=None#response time
        self.clock=None#we'll use this to measure the rt

#Initialise components for routine:int3
int3Clock=core.Clock()
apoidf=visual.TextStim(win=win, ori=0,
    text=u'Postaraj si\u0119 odpowiada\u0107 jak najszybciej\npotrafisz.\nWa\u017cne jest, \u017ceby usi\u0105\u015b\u0107 w wygodnej\npozycji z lekko przymru\u017conymi\noczyma.\nAby przej\u015b\u0107 dalej naci\u015bnij SPACE.',
    pos=[0, 0], height=0.1,
    color=u'black', colorSpace=u'rgb')

#Initialise components for routine:int4
int4Clock=core.Clock()
uivgtdv=visual.TextStim(win=win, ori=0,
    text=u'Skupiaj swoj\u0105 uwag\u0119 na znaku + na\n\u015brodku ekranu\n\n+\n\nstaraj si\u0119 mruga\u0107 tylko wtedy, gdy\npojawi si\u0119 taka instrukcja\nAby przej\u015b\u0107 dalej naci\u015bnij SPACE.',
    pos=[0, 0], height=0.1,
    color=u'black', colorSpace=u'rgb')

#Initialise components for routine:int5
int5Clock=core.Clock()
sodfsdlkj=visual.TextStim(win=win, ori=0,
    text=u'Wci\u015bnij klawisz SPACE zawsze wtedy,\nkiedy prezentowane s\u0142owo b\u0119dzie\nzwi\u0105zane z emocjami.\nAby przej\u015b\u0107 do sesji treningowej\nnaci\u015bnij SPACE.',
    pos=[0, 0], height=0.1,
    color=u'black', colorSpace=u'rgb')

#set up handler to look after randomisation of trials etc
trialskjhk=data.TrialHandler(nReps=1, method=u'sequential', extraInfo=expInfo, 
    trialList=data.importTrialList(u'samples.csv'))
thisTrialskjh=trialskjhk.trialList[0]#so we can initialise stimuli with some values
#abbrieviate parameter names if possible (e.g. rgb=thisTrialskjh.rgb)
if thisTrialskjh!=None:
    for paramName in thisTrialskjh.keys():
        exec(paramName+'=thisTrialskjh.'+paramName)

#Initialise components for routine:test
testClock=core.Clock()
fxxxxx=visual.TextStim(win=win, ori=0,
    text=u'+',
    pos=[0, 0], height=0.1,
    color=u'black', colorSpace=u'rgb')
lkhkkki=visual.TextStim(win=win, ori=0,
    text=word,
    pos=[0, 0], height=0.1,
    color=u'black', colorSpace=u'rgb')

#Initialise components for routine:test_b
test_bClock=core.Clock()
lkhhguyu=visual.TextStim(win=win, ori=0,
    text=u'Mrugaj teraz.\nJe\u015bli jeste\u015b gotowy naci\u015bnij SPACE.',
    pos=[0, 0], height=0.1,
    color=u'black', colorSpace=u'rgb')

#Initialise components for routine:int6
int6Clock=core.Clock()
lkhoh=visual.TextStim(win=win, ori=0,
    text=u'Aby przej\u015b\u0107 do w\u0142a\u015bciwego badania\nnaci\u015bnij SPACE.',
    pos=[0, 0], height=0.1,
    color=u'black', colorSpace=u'rgb')

#set up handler to look after randomisation of trials etc
trials=data.TrialHandler(nReps=1, method='sequential', extraInfo=expInfo, 
    trialList=data.importTrialList('words.csv'))
thisTrial=trials.trialList[0]#so we can initialise stimuli with some values
#abbrieviate parameter names if possible (e.g. rgb=thisTrial.rgb)
if thisTrial!=None:
    for paramName in thisTrial.keys():
        exec(paramName+'=thisTrial.'+paramName)

#Initialise components for routine:trial
trialClock=core.Clock()
t_fix=visual.TextStim(win=win, ori=0,
    text='+',
    pos=[0, 0], height=0.1,
    color='black', colorSpace='rgb')
t_word=visual.TextStim(win=win, ori=0,
    text=word,
    pos=[0, 0], height=0.1,
    color='black', colorSpace='rgb')
curr_time = 0
import time
import os
import kamil_consts, kamil_helper
kamil_helper.create_words_file()
trials=data.TrialHandler(nReps=1, method='sequential', extraInfo=expInfo, 
    trialList=data.importTrialList('words.csv'))

#Initialise components for routine:blink
blinkClock=core.Clock()
xxx=visual.TextStim(win=win, ori=0,
    text=u'Mrugaj teraz.\n\nJe\u015bli jeste\u015b gotowy naci\u015bnij SPACE.',
    pos=[0, 0], height=0.1,
    color=u'black', colorSpace=u'rgb')
trials_count = 1

#Initialise components for routine:bye
byeClock=core.Clock()
lksjwpepowkf=visual.TextStim(win=win, ori=0,
    text=u'Dzi\u0119kuj\u0119 za udzia\u0142 w badaniu.',
    pos=[0, 0], height=0.1,
    color=u'black', colorSpace=u'rgb')

#update component parameters for each repeat

#run the trial
continueInt1=True
t=0; int1Clock.reset()
while continueInt1 and (t<2.0000):
    #get current time
    t=int1Clock.getTime()
    
    #update/draw components on each frame
    if (0.0<= t < (0.0+2.0)):
        dsf.draw()
    
    #check for quit (the [Esc] key)
    if event.getKeys(["escape"]): core.quit()
    event.clearEvents()#so that it doesn't get clogged with other events
    #refresh the screen
    win.flip()

#end of this routine (e.g. trial)

#update component parameters for each repeat
resplkhlkljlk = KeyResponse()#create an object of type KeyResponse

#run the trial
continueInt2=True
t=0; int2Clock.reset()
while continueInt2 and (t<1000000.0000):
    #get current time
    t=int2Clock.getTime()
    
    #update/draw components on each frame
    if (0.0 <= t):
        uiuiyhiu.draw()
    if (0.0 <= t):
        theseKeys = event.getKeys(keyList=u"['space']")
        if len(theseKeys)>0:#at least one key was pressed
            resplkhlkljlk.keys=theseKeys[-1]#just the last key pressed
            #abort routine on response
            continueInt2=False
    
    #check for quit (the [Esc] key)
    if event.getKeys(["escape"]): core.quit()
    event.clearEvents()#so that it doesn't get clogged with other events
    #refresh the screen
    win.flip()

#end of this routine (e.g. trial)

#update component parameters for each repeat
khklhjpj = KeyResponse()#create an object of type KeyResponse

#run the trial
continueInt3=True
t=0; int3Clock.reset()
while continueInt3 and (t<1000000.0000):
    #get current time
    t=int3Clock.getTime()
    
    #update/draw components on each frame
    if (0.0 <= t):
        apoidf.draw()
    if (0.0 <= t):
        theseKeys = event.getKeys(keyList=u"['space']")
        if len(theseKeys)>0:#at least one key was pressed
            khklhjpj.keys=theseKeys[-1]#just the last key pressed
            #abort routine on response
            continueInt3=False
    
    #check for quit (the [Esc] key)
    if event.getKeys(["escape"]): core.quit()
    event.clearEvents()#so that it doesn't get clogged with other events
    #refresh the screen
    win.flip()

#end of this routine (e.g. trial)

#update component parameters for each repeat
respiojoi = KeyResponse()#create an object of type KeyResponse

#run the trial
continueInt4=True
t=0; int4Clock.reset()
while continueInt4 and (t<1000000.0000):
    #get current time
    t=int4Clock.getTime()
    
    #update/draw components on each frame
    if (0.0 <= t):
        uivgtdv.draw()
    if (0.0 <= t):
        theseKeys = event.getKeys(keyList=u"['space']")
        if len(theseKeys)>0:#at least one key was pressed
            respiojoi.keys=theseKeys[-1]#just the last key pressed
            #abort routine on response
            continueInt4=False
    
    #check for quit (the [Esc] key)
    if event.getKeys(["escape"]): core.quit()
    event.clearEvents()#so that it doesn't get clogged with other events
    #refresh the screen
    win.flip()

#end of this routine (e.g. trial)

#update component parameters for each repeat
resplkdsjwo = KeyResponse()#create an object of type KeyResponse

#run the trial
continueInt5=True
t=0; int5Clock.reset()
while continueInt5 and (t<1000000.0000):
    #get current time
    t=int5Clock.getTime()
    
    #update/draw components on each frame
    if (0.0 <= t):
        sodfsdlkj.draw()
    if (0.0 <= t):
        theseKeys = event.getKeys(keyList=u"['space']")
        if len(theseKeys)>0:#at least one key was pressed
            resplkdsjwo.keys=theseKeys[-1]#just the last key pressed
            #abort routine on response
            continueInt5=False
    
    #check for quit (the [Esc] key)
    if event.getKeys(["escape"]): core.quit()
    event.clearEvents()#so that it doesn't get clogged with other events
    #refresh the screen
    win.flip()

#end of this routine (e.g. trial)

for thisTrialskjh in trialskjhk:
    #abbrieviate parameter names if possible (e.g. rgb=thisTrialskjh.rgb)
    if thisTrialskjh!=None:
        for paramName in thisTrialskjh.keys():
            exec(paramName+'=thisTrialskjh.'+paramName)
    
    #update component parameters for each repeat
    lkhkkki.setText(word)
    respkljlkj = KeyResponse()#create an object of type KeyResponse
    
    #run the trial
    continueTest=True
    t=0; testClock.reset()
    while continueTest and (t<4.0000):
        #get current time
        t=testClock.getTime()
        
        #update/draw components on each frame
        if (0.0<= t < (0.0+1.0)):
            fxxxxx.draw()
        if (1.0<= t < (1.0+1.0)):
            lkhkkki.draw()
        if (1.0<= t < (1.0+3.0)):
            theseKeys = event.getKeys(keyList=u"['space']")
            if len(theseKeys)>0:#at least one key was pressed
                respkljlkj.keys=theseKeys[-1]#just the last key pressed
        
        #check for quit (the [Esc] key)
        if event.getKeys(["escape"]): core.quit()
        event.clearEvents()#so that it doesn't get clogged with other events
        #refresh the screen
        win.flip()
    
    #end of this routine (e.g. trial)
    if len(respkljlkj.keys)>0:#we had a response
        trialskjhk.addData('respkljlkj.keys',respkljlkj.keys)

#completed 1 repeats of 'trialskjhk' repeats

trialskjhk.saveAsPickle(filename+'trialskjhk')
trialskjhk.saveAsExcel(filename+'.xlsx', sheetName='trialskjhk',
    stimOut=['word', 'group', 'fix_time', ],
    dataOut=['n','all_mean','all_std', 'all_raw'])
psychopy.log.info('saved data to '+filename+'.dlm')

#update component parameters for each repeat
resposoewoewoiew = KeyResponse()#create an object of type KeyResponse

#run the trial
continueTest_b=True
t=0; test_bClock.reset()
while continueTest_b and (t<1000000.0000):
    #get current time
    t=test_bClock.getTime()
    
    #update/draw components on each frame
    if (0.0 <= t):
        lkhhguyu.draw()
    if (0.0 <= t):
        theseKeys = event.getKeys(keyList=u"['space']")
        if len(theseKeys)>0:#at least one key was pressed
            resposoewoewoiew.keys=theseKeys[-1]#just the last key pressed
            #abort routine on response
            continueTest_b=False
    
    #check for quit (the [Esc] key)
    if event.getKeys(["escape"]): core.quit()
    event.clearEvents()#so that it doesn't get clogged with other events
    #refresh the screen
    win.flip()

#end of this routine (e.g. trial)

#update component parameters for each repeat
resplkgikh = KeyResponse()#create an object of type KeyResponse

#run the trial
continueInt6=True
t=0; int6Clock.reset()
while continueInt6 and (t<1000000.0000):
    #get current time
    t=int6Clock.getTime()
    
    #update/draw components on each frame
    if (0.0 <= t):
        lkhoh.draw()
    if (0.0 <= t):
        theseKeys = event.getKeys(keyList=u"['space']")
        if len(theseKeys)>0:#at least one key was pressed
            resplkgikh.keys=theseKeys[-1]#just the last key pressed
            #abort routine on response
            continueInt6=False
    
    #check for quit (the [Esc] key)
    if event.getKeys(["escape"]): core.quit()
    event.clearEvents()#so that it doesn't get clogged with other events
    #refresh the screen
    win.flip()

#end of this routine (e.g. trial)

for thisTrial in trials:
    #abbrieviate parameter names if possible (e.g. rgb=thisTrial.rgb)
    if thisTrial!=None:
        for paramName in thisTrial.keys():
            exec(paramName+'=thisTrial.'+paramName)
    
    #update component parameters for each repeat
    t_word.setText(word)
    t_resp = KeyResponse()#create an object of type KeyResponse
    curr_time = 0
    s_st = list(kamil_consts.s_st)
    s_dur = list(kamil_consts.s_dur)
    
    #Set first variable duration time (fixation)
    s_dur[0] = float(fix_time)
    for i in range(1, kamil_consts.NUM_OF_VALS):
        s_st[i] = float(fix_time)
    
    #run the trial
    continueTrial=True
    t=0; trialClock.reset()
    while continueTrial and (t<s_dur[-1]+s_st[-1]):
        #get current time
        t=trialClock.getTime()
        
        #update/draw components on each frame
        if (s_st[0]<= t < (s_st[0]+s_dur[0])):
            t_fix.draw()
        if (s_st[1]<= t < (s_st[1]+s_dur[1])):
            t_word.draw()
        if (s_st[2]<= t < (s_st[2]+s_dur[2])):
            if t_resp.clock==None: #if we don't have one we've just started
                t_resp.clock=core.Clock()#create one (now t=0)
            theseKeys = event.getKeys(keyList="['space']")
            if len(theseKeys)>0:#at least one key was pressed
                if t_resp.keys==[]:#then this was the first keypress
                    t_resp.keys=theseKeys[0]#just the first key pressed
                    t_resp.rt = t_resp.clock.getTime()
        if (s_st[1]<= t < (s_st[1]+s_dur[1])):
            if curr_time == 0:
            #a first frame of an image
            #send trigger, save image onset data
            #expand image start time (st) so that
            #a time needed for sending a trigger will not
            #influence image duration
                before_time = time.time()
                #send trigger ...
                kamil_helper.send()
                curr_time = time.time()
                trials.addData('onset_time', repr(curr_time))
                diff_time = curr_time - before_time
                for i in range(1, kamil_consts.NUM_OF_VALS):
                    s_st[i] = s_st[i] + diff_time
                t_resp.clock=core.Clock()
        
        #check for quit (the [Esc] key)
        if event.getKeys(["escape"]): core.quit()
        event.clearEvents()#so that it doesn't get clogged with other events
        #refresh the screen
        win.flip()
    
    #end of this routine (e.g. trial)
    if len(t_resp.keys)>0:#we had a response
        trials.addData('t_resp.keys',t_resp.keys)
        trials.addData('t_resp.rt',t_resp.rt)
    if len(t_resp.keys)==0:
        trials.addData('t_resp.keys','')
        trials.addData('t_resp.rt', -1)
    
    #update component parameters for each repeat
    respkl = KeyResponse()#create an object of type KeyResponse
    trials_count += 1
    if not (trials_count % kamil_consts.BLINK == 0):
       continue
    
    #run the trial
    continueBlink=True
    t=0; blinkClock.reset()
    while continueBlink and (t<1000000.0000):
        #get current time
        t=blinkClock.getTime()
        
        #update/draw components on each frame
        if (0.0 <= t):
            xxx.draw()
        if (0.0 <= t):
            theseKeys = event.getKeys(keyList="['space']")
            if len(theseKeys)>0:#at least one key was pressed
                respkl.keys=theseKeys[-1]#just the last key pressed
                #abort routine on response
                continueBlink=False
        respkl.keys = ''
        
        #check for quit (the [Esc] key)
        if event.getKeys(["escape"]): core.quit()
        event.clearEvents()#so that it doesn't get clogged with other events
        #refresh the screen
        win.flip()
    
    #end of this routine (e.g. trial)
    if len(respkl.keys)>0:#we had a response
        trials.addData('respkl.keys',respkl.keys)
    

#completed 1 repeats of 'trials' repeats

trials.saveAsPickle(filename+'trials')
trials.saveAsExcel(filename+'.xlsx', sheetName='trials',
    stimOut=['group', 'word', 'fix_time', ],
    dataOut=['n','all_mean','all_std', 'all_raw'])
psychopy.log.info('saved data to '+filename+'.dlm')

#update component parameters for each repeat
respkjftess = KeyResponse()#create an object of type KeyResponse

#run the trial
continueBye=True
t=0; byeClock.reset()
while continueBye and (t<1000000.0000):
    #get current time
    t=byeClock.getTime()
    
    #update/draw components on each frame
    if (0.0 <= t):
        lksjwpepowkf.draw()
    if (0.0 <= t):
        theseKeys = event.getKeys(keyList=u"['space']")
        if len(theseKeys)>0:#at least one key was pressed
            respkjftess.keys=theseKeys[-1]#just the last key pressed
            #abort routine on response
            continueBye=False
    
    #check for quit (the [Esc] key)
    if event.getKeys(["escape"]): core.quit()
    event.clearEvents()#so that it doesn't get clogged with other events
    #refresh the screen
    win.flip()

#end of this routine (e.g. trial)
os.remove(filename+'.xlsx')
trials.saveAsExcel(filename+'.xlsx', sheetName='trials',
    stimOut=['word', 'group', 'fix_time', ],
    dataOut=['all_raw'] #dataOut=['n','all_mean','all_std', 'all_raw']
    )

logFile.close()
win.close()
core.quit()
