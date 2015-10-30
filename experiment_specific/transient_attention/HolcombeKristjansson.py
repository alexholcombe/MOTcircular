from __future__ import print_function
__author__ = """Alex "O." Holcombe, Wei-Ying Chen""" ## double-quotes will be silently removed, single quotes will be left, eg, O'Connor
import helpersAOH
from psychopy import *
import psychopy.info
from psychopy import sound, monitors, logging
import numpy as np
import itertools #to calculate all subsets
from copy import deepcopy
from math import atan, pi, cos, sin, sqrt, ceil
import time, sys, platform, os, StringIO, gc
eyetrackingOption = False #Because Psychopy v1.83.01 mistakenly included an old version of pylink which prevents EyelinkEyetrackerForPsychopySUPA3 stuff from importing
if eyetrackingOption:
    from EyelinkEyetrackerForPsychopySUPA3 import Tracker_EyeLink #Chris Fajou integration
from helpersAOH import accelerateComputer, openMyStimWindow, constructThickThinWedgeRingsTargetAndCue
eyetracking = False

quitFinder = True
if quitFinder:
    applescript="\'tell application \"Finder\" to quit\'" #quit Finder.
    shellCmd = 'osascript -e '+applescript
    os.system(shellCmd)
process_priority = 'realtime' # 'normal' 'high' or 'realtime'
disable_gc = True

subject='test'#'test'
autoLogging = False
demo = False
autopilot=False
if autopilot:  subject='auto'
feedback=True
exportImages= False #quits after one trial / output image
screenshot= False; screenshotDone = False;allowGUI = False;waitBlank = False
trackAllIdenticalColors = True#with tracking, can either use same colors as other task (e.g. 6 blobs but only 3 colors so have to track one of 2) or set all blobs identical color

timeAndDateStr = time.strftime("%d%b%Y_%H-%M", time.localtime()) 
respTypes=['order']; respType=respTypes[0]
bindRadiallyRingToIdentify=1 #0 is inner, 1 is outer
gratingTexPix=1024#numpy textures must be a power of 2. So, if numColorsRoundTheRing not divide without remainder into textPix, there will be some rounding so patches will not all be same size

numRings=2
radii=[25]   #Need to encode as array for those experiments wherein more than one ring presented 

respRadius=radii[0] #deg
refreshRate= 60 *1.0;  #160 #set to the framerate of the monitor
useClock = True #as opposed to using frame count, which assumes no frames are ever missed
fullscr=1; #show in small window (0) or full screen (1) 
scrn=0 #which screen to display the stimuli. 0 is home screen, 1 is second screen
# create a dialog from dictionary 
infoFirst = { 'Autopilot':autopilot, 'Check refresh etc':False, 'Screen to use':scrn, 'Fullscreen (timing errors if not)': fullscr, 'Screen refresh rate': refreshRate }
OK = gui.DlgFromDict(dictionary=infoFirst, 
    title='MOT', 
    order=['Autopilot','Check refresh etc', 'Screen to use', 'Screen refresh rate', 'Fullscreen (timing errors if not)'], 
    tip={'Check refresh etc': 'To confirm refresh rate and that can keep up, at least when drawing a grating',
            'Screen to use': '0 means primary screen, 1 means second screen'},
    )
if not OK.OK:
    print('User cancelled from dialog box'); core.quit()
autopilot = infoFirst['Autopilot']
checkRefreshEtc = infoFirst['Check refresh etc']
scrn = infoFirst['Screen to use']
print('scrn = ',scrn, ' from dialog box')
fullscr = infoFirst['Fullscreen (timing errors if not)']
refreshRate = infoFirst['Screen refresh rate']

if demo: refreshRate = 60. 
tokenChosenEachRing= [-999]*numRings
targetDur = 0.6; #duration of target     
targetDur = round(targetDur * refreshRate) / refreshRate #discretize to nearest integer number of refreshes
logging.info(  'targetDur= '+str(targetDur)   )

rampUpDur=0
rampUpFrames = refreshRate*rampUpDur
ballStdDev = 1.8
mouseChoiceArea = ballStdDev*0.8 # origin =1.3
units='deg' #'cm'
timeTillReversalMin = 0.5 #0.5; 
timeTillReversalMax = 1.5# 1.3 #2.9
colors_all = np.array([[1,-1,-1],[1,-1,-1]])
cueColor = np.array([1,1,1])
#monitor parameters
widthPix = 800 #1440  #monitor width in pixels
heightPix =600  #900 #monitor height in pixels
monitorwidth = 38.5 #28.5 #monitor width in centimeters
viewdist = 57.; #cm
pixelperdegree = widthPix/ (atan(monitorwidth/viewdist) /np.pi*180)
bgColor = [-1,-1,-1] #black background
monitorname = 'testMonitor' # 'mitsubishi' #in psychopy Monitors Center
if exportImages:
    fullscr=0; scrn=0
    widthPix = 600; heightPix = 450
    monitorwidth = 25.0
if demo:    
    scrn=0; fullscr=0
    widthPix = 800; heightPix = 600
    monitorname='testMonitor'
    allowGUI = True
    monitorwidth = 23#18.0

mon = monitors.Monitor(monitorname,width=monitorwidth, distance=viewdist)#fetch the most recent calib for this monitor
mon.setSizePix( (widthPix,heightPix) )
myWin = openMyStimWindow(mon,widthPix,heightPix,bgColor,allowGUI,units,fullscr,scrn,waitBlank)
myMouse = event.Mouse(visible = 'true',win=myWin)
myWin.setRecordFrameIntervals(False)

trialsPerCondition = 1 #default value

refreshMsg2 = ''
if not checkRefreshEtc:
    refreshMsg1 = 'REFRESH RATE WAS NOT CHECKED'
    refreshRateWrong = False
else: #checkRefreshEtc
    runInfo = psychopy.info.RunTimeInfo(
            # if you specify author and version here, it overrides the automatic detection of __author__ and __version__ in your script
            #author='<your name goes here, plus whatever you like, e.g., your lab or contact info>',
            #version="<your experiment version info>",
            win=myWin,    ## a psychopy.visual.Window() instance; None = default temp window used; False = no win, no win.flips()
            refreshTest='grating', ## None, True, or 'grating' (eye-candy to avoid a blank screen)
            verbose=True, ## True means report on everything 
            userProcsDetailed=True  ## if verbose and userProcsDetailed, return (command, process-ID) of the user's processes
            )
    print('Finished runInfo- which assesses the refresh and processes of this computer')
    refreshMsg1 = 'Median frames per second ='+ str( np.round(1000./runInfo["windowRefreshTimeMedian_ms"],1) )
    refreshRateTolerancePct = 3
    pctOff = abs( (1000./runInfo["windowRefreshTimeMedian_ms"]-refreshRate) / refreshRate)
    refreshRateWrong =  pctOff > (refreshRateTolerancePct/100.)
    if refreshRateWrong:
        refreshMsg1 += ' BUT'
        refreshMsg1 += ' program assumes ' + str(refreshRate)
        refreshMsg2 =  'which is off by more than' + str(round(refreshRateTolerancePct,0)) + '%!!'
    else:
        refreshMsg1 += ', which is close enough to desired val of ' + str( round(refreshRate,1) )
    myWinRes = myWin.size
    myWin.allowGUI =True

myWin.close() #have to close window to show dialog box
dlgLabelsOrdered = list() #new dialog box
myDlg = gui.Dlg(title="object tracking experiment", pos=(200,400))
if not autopilot:
    myDlg.addField('Subject name :', subject, tip='or subject code')
    dlgLabelsOrdered.append('subject')
myDlg.addField('Trials per condition (default=' + str(trialsPerCondition) + '):', trialsPerCondition, tip=str(trialsPerCondition))
dlgLabelsOrdered.append('trialsPerCondition')
pctCompletedBreak = 50
myDlg.addText(refreshMsg1, color='Black')
if refreshRateWrong:
    myDlg.addText(refreshMsg2, color='Red')
msgWrongResolution = ''
if checkRefreshEtc and (not demo) and (myWinRes != [widthPix,heightPix]).any():
    msgWrongResolution = 'Instead of desired resolution of '+ str(widthPix)+'x'+str(heightPix)+ ' pixels, screen apparently '+ str(myWinRes[0])+ 'x'+ str(myWinRes[1])
    myDlg.addText(msgWrongResolution, color='Red')
    print(msgWrongResolution)
myDlg.addText('Note: to abort press ESC at a trials response screen', color=[-1.,1.,-1.]) # color='DimGrey') color names stopped working along the way, for unknown reason
myDlg.show()
if myDlg.OK: #unpack information from dialogue box
   thisInfo = myDlg.data #this will be a list of data returned from each field added in order
   if not autopilot:
       name=thisInfo[dlgLabelsOrdered.index('subject')]
       if len(name) > 0: #if entered something
         subject = name #change subject default name to what user entered
       trialsPerCondition = int( thisInfo[ dlgLabelsOrdered.index('trialsPerCondition') ] ) #convert string to integer
       print('trialsPerCondition=',trialsPerCondition)
       logging.info('trialsPerCondition ='+str(trialsPerCondition))
else: 
   print('User cancelled from dialog box.')
   logging.flush()
   core.quit()

if os.path.isdir('.'+os.sep+'dataRaw'):
    dataDir='dataRaw'
else:
    print('"dataRaw" directory does not exist, so saving data in present working directory')
    dataDir='.'
expname = ''
fileNameWithPath = dataDir+'/'+subject+ '_' + expname+timeAndDateStr
if not demo and not exportImages:
    saveCodeCmd = 'cp \'' + sys.argv[0] + '\' '+ fileNameWithPath + '.py'
    os.system(saveCodeCmd)  #save a copy of the code as it was when that subject was run
    logF = logging.LogFile(fileNameWithPath+'.log', 
        filemode='w',#if you set this to 'a' it will append instead of overwriting
        level=logging.INFO)#info, data, warnings, and errors will be sent to this logfile
if demo or exportImages: 
  logging.console.setLevel(logging.ERROR)  #only show this level  messages and higher
logging.console.setLevel(logging.WARNING) #DEBUG means set the console to receive nearly all messges, INFO is for everything else, INFO, EXP, DATA, WARNING and ERROR 
if refreshRateWrong:
    logging.error(refreshMsg1+refreshMsg2)
else: logging.info(refreshMsg1+refreshMsg2)
longerThanRefreshTolerance = 0.27
longFrameLimit = round(1000./refreshRate*(1.0+longerThanRefreshTolerance),3) # round(1000/refreshRate*1.5,2)
msg = 'longFrameLimit='+ str(longFrameLimit) +' Recording trials where one or more interframe interval exceeded this figure '
logging.info(msg); print(msg)
if msgWrongResolution != '':
    logging.error(msgWrongResolution)

myWin = openMyStimWindow(mon,widthPix,heightPix,bgColor,allowGUI,units,fullscr,scrn,waitBlank)
print('Window opened')
myMouse = event.Mouse(visible = 'true',win=myWin)
print('Mouse enabled')
runInfo = psychopy.info.RunTimeInfo(
        win=myWin,    ## a psychopy.visual.Window() instance; None = default temp window used; False = no win, no win.flips()
        refreshTest='grating', ## None, True, or 'grating' (eye-candy to avoid a blank screen)
        verbose=True, ## True means report on everything 
        userProcsDetailed=True  ## if verbose and userProcsDetailed, return (command, process-ID) of the user's processes
        )
msg = 'second window opening runInfo mean ms='+ str( runInfo["windowRefreshTimeAvg_ms"] )
logging.info(msg); print(msg)
logging.info(runInfo)
logging.info('gammaGrid='+str(mon.getGammaGrid()))
logging.info('linearizeMethod='+str(mon.getLinearizeMethod()))

eyeballRadius = 5
eyeball = visual.Circle(myWin, radius=eyeballRadius, edges=32, fillColorSpace='rgb',fillColor = (1,0,1),autoLog=autoLogging) #to outline chosen options

gaussian = visual.PatchStim(myWin, tex='none',mask='gauss',colorSpace='rgb',size=ballStdDev,autoLog=autoLogging)
gaussian2 = visual.PatchStim(myWin, tex='none',mask='gauss',colorSpace='rgb',size=ballStdDev,autoLog=autoLogging)
optionChosenCircle = visual.Circle(myWin, radius=mouseChoiceArea, edges=32, fillColorSpace='rgb',fillColor = (1,0,1),autoLog=autoLogging) #to outline chosen options
clickableRegion = visual.Circle(myWin, radius=0.5, edges=32, fillColorSpace='rgb',fillColor = (-1,1,-1),autoLog=autoLogging) #to show clickable zones
circlePostCue = visual.Circle(myWin, radius=2*radii[0], edges=32, fillColorSpace='rgb',fillColor = (-.85,-.85,-.85),lineColor=(-1,-1,-1),autoLog=autoLogging) #visual postcue
#referenceCircle allows visualisation of trajectory, mostly for debugging
referenceCircle = visual.Circle(myWin, radius=radii[0], edges=32, fillColorSpace='rgb',lineColor=(-1,-1,1),autoLog=autoLogging) #visual postcue

blindspotFill = 0 #a way for people to know if they move their eyes
if blindspotFill:
    blindspotStim = visual.PatchStim(myWin, tex='none',mask='circle',size=4.8,colorSpace='rgb',color = (-1,1,-1),autoLog=autoLogging) #to outline chosen options
    blindspotStim.setPos([13.1,-2.7]) #AOH, size=4.8; pos=[13.1,-2.7] #DL: [13.3,-0.8]
fixatnNoise = True
fixSizePix = 20 #make fixation big so flicker more conspicuous
if fixatnNoise:
    numChecksAcross = fixSizePix/4
    nearestPowerOfTwo = round( sqrt(numChecksAcross) )**2 #Because textures (created on next line) must be a power of 2
    fixatnNoiseTexture = np.round( np.random.rand(nearestPowerOfTwo,nearestPowerOfTwo) ,0 )   *2.0-1 #Can counterphase flicker  noise texture to create salient flicker if you break fixation
    fixation= visual.PatchStim(myWin, tex=fixatnNoiseTexture, size=(fixSizePix,fixSizePix), units='pix', mask='circle', interpolate=False, autoLog=autoLogging)
    fixationBlank= visual.PatchStim(myWin, tex=-1*fixatnNoiseTexture, colorSpace='rgb',mask='circle',size=fixSizePix,units='pix',autoLog=autoLogging)
else:
    fixation = visual.PatchStim(myWin,tex='none',colorSpace='rgb',color=(.9,.9,.9),mask='circle',units='pix',size=fixSizePix,autoLog=autoLogging)
    fixationBlank= visual.PatchStim(myWin,tex='none',colorSpace='rgb',color=(-1,-1,-1),mask='circle',units='pix',size=fixSizePix,autoLog=autoLogging)
fixationPoint = visual.PatchStim(myWin,colorSpace='rgb',color=(1,1,1),mask='circle',units='pix',size=2,autoLog=autoLogging) #put a point in the center

#create noise post-mask
numChecksAcross = 128
nearestPowerOfTwo = round( sqrt(numChecksAcross) )**2 #Because textures (created on next line) must be a power of 2
whiteNoiseTexture = np.round( np.random.rand(nearestPowerOfTwo,nearestPowerOfTwo) ,0 )   *2.0-1 #Can counterphase flicker  noise texture to create salient flicker if you break fixation
noiseMask= visual.PatchStim(myWin, tex=whiteNoiseTexture, size=(widthPix,heightPix), units='pix', interpolate=False, autoLog=autoLogging)

respText = visual.TextStim(myWin,pos=(0, -.8),colorSpace='rgb',color = (1,1,1),alignHoriz='center', alignVert='center', units='norm',autoLog=autoLogging)
NextText = visual.TextStim(myWin,pos=(0, 0),colorSpace='rgb',color = (1,1,1),alignHoriz='center', alignVert='center', units='norm',autoLog=autoLogging)
NextRemindPctDoneText = visual.TextStim(myWin,pos=(-.1, -.4),colorSpace='rgb',color= (1,1,1),alignHoriz='center', alignVert='center', units='norm',autoLog=autoLogging)
NextRemindCountText = visual.TextStim(myWin,pos=(.1, -.5),colorSpace='rgb',color = (1,1,1),alignHoriz='center', alignVert='center', units='norm',autoLog=autoLogging)

stimList = []
speeds = np.array( [ 0.5 ]  )   #dont want to go faster than 2 because of blur problem
#Set up the factorial design (list of all conditions)
for numCuesEachRing in [ [1] ]:
 for numObjsEachRing in [ [8] ]: #First entry in each sub-list is num objects in the first ring, second entry is num objects in the second ring
  for cueLeadTime in [.160,.700]:  #How long is the cue on prior to the eyeballs appearing
      for speed in speeds:
          for direction in [1.0]: # [-1.0,1.0]:
            for targetAngleOffset in [-3,3]:
                for objToCueQuadrant in range(4):
                    stimList.append( {'numCuesEachRing':numCuesEachRing,'numObjsEachRing':numObjsEachRing,'targetAngleOffset':targetAngleOffset,
                                                'cueLeadTime':cueLeadTime,'speed':speed,'objToCueQuadrant':objToCueQuadrant,'direction':direction} )
#set up record of proportion correct in various conditions
trials = data.TrialHandler(stimList,trialsPerCondition) #constant stimuli method
                                #        extraInfo= {'subject':subject} )  #will be included in each row of dataframe and wideText. Not working in v1.82.01

numRightWrongEachSpeed = np.zeros([ len(speeds), 2 ]); #summary results to print out at end
#end setup of record of proportion correct in various conditions

timeAndDateStr = time.strftime("%d%b%Y_%H-%M", time.localtime()) 
logging.info(  str('starting exp with name: "'+'MovingCue'+'" at '+timeAndDateStr)   )
logging.info( 'numtrials='+ str(trials.nTotal)+' refreshRate='+str(refreshRate)      )

print(' numtrials=', trials.nTotal)
logging.info('rampUpDur='+str(rampUpDur)+ ' targetDur='+ str(targetDur) + ' secs')
logging.info('task='+'track'+'   respType='+respType)
logging.info(   'radii=' + str(radii)   )
logging.flush()

RFcontourAmp= 0.0
RFcontourFreq = 2.0
RFcontourPhase = 0
def RFcontourCalcModulation(angle,freq,phase): 
    modulation = sin(angle*freq + phase) #radial frequency contour equation, e.g. http://www.journalofvision.org/content/14/11/12.full from Wilkinson et al. 1998
    return modulation

ampTemporalRadiusModulation = 0.0 # 1.0/3.0
ampModulatnEachRingTemporalPhase = np.random.rand(numRings) * 2*np.pi
def xyThisFrameThisAngle(basicShape, radiiThisTrial, numRing, angle, thisFrameN, speed):
    #period of oscillation should be in sec
    periodOfRadiusModulation = 1.0/speed#so if speed=2 rps, radius modulation period = 0.5 s
    r = radiiThisTrial[numRing]
    timeSeconds = thisFrameN / refreshRate
    modulatnPhaseRadians = timeSeconds/periodOfRadiusModulation * 2*pi + ampModulatnEachRingTemporalPhase[numRing]
    def waveForm(phase,type):
        if type=='sin':
            return sin(modulatnPhaseRadians)
        elif type == 'sqrWave':
            ans = np.sign( sin(modulatnPhaseRadians) ) #-1 or 1. That's great because that's also sin min and max
            if ans==0: ans = -1+ 2*round( np.random.rand(1)[0] ) #exception case is when 0, gives 0, so randomly change that to -1 or 1
            return ans
        else: print('Error! unexpected type in radiusThisFrameThisAngle')
        
    if basicShape == 'circle':
        rThis =  r + waveForm(modulatnPhaseRadians,'sin') * r * ampTemporalRadiusModulation
        rThis += r * RFcontourAmp * RFcontourCalcModulation(angle,RFcontourFreq,RFcontourPhase)
        x = rThis*cos(angle)
        y = rThis*sin(angle)
    elif basicShape == 'square': #actual square-shaped trajectory. Could also add all the modulations to this, later
            #Theta varies from 0 to 2pi. Instead of taking its cosine, I should just pretend it is linear. Map it to 0->1 with triangle wave
            #Want 0 to pi to be -1 to 1
            def triangleWave(period, phase):
                   #triangle wave is in sine phase (starts at 0)
                   y = -abs(phase % (2*period) - period) # http://stackoverflow.com/questions/1073606/is-there-a-one-line-function-that-generates-a-triangle-wave
                   #y goes from -period to 0.  Need to rescale to -1 to 1 to match sine wave etc.
                   y = y/period*2 + 1
                   #Now goes from -1 to 1
                   return y
            x = r * triangleWave(pi,angle)
            y = r * triangleWave(pi, (angle-pi/2)%(2*pi ))
            #This will always describe a diamond. To change the shape would have to use vector rotation formula
    else: print('Unexpected basicShape ',basicShape)
    return x,y

def angleChangeThisFrame(thisTrial, moveDirection, numRing, thisFrameN, lastFrameN):
    angleMove = moveDirection[numRing]*thisTrial['direction']*thisTrial['speed']*2*pi*(thisFrameN-lastFrameN)/refreshRate
    return angleMove

def oneFrameOfStim(thisTrial,currFrame,maskBegin,cues,stimRings,target,clock,useClock,offsetXYeachRing):
#defining a function to draw each frame of stim. So can call second time for tracking task response phase
          if useClock: #Don't count on not missing frames. Use actual time.
            t = clock.getTime()
            n = round(t*refreshRate)
          else:
            n = currFrame
          
          if n<rampUpFrames:
                contrast = cos( -pi+ pi* n/rampUpFrames  ) /2. +.5 #starting from -pi trough of cos, and scale into 0->1 range
          else: contrast = 1
          if n%2:
            fixation.draw()#flicker fixation on and off at framerate to see when skip frame
          else:
            fixationBlank.draw()
          fixationPoint.draw()
          #draw cue
          for numRing in range(len(cues)):
            if n< thisTrial['cueLeadTime']*refreshRate: #keep cue moving
                angleMove = angleChangeThisFrame(thisTrial, moveDirection, numRing, n, n-1)
                cues[numRing].setOri(angleMove,operation='+',log=autoLogging)
            else: pass #Time for target, cue will now be stationary
            cueCurrAngle = cues[numRing].ori
            cue.draw()
          #draw eyeballs
          if n >= thisTrial['cueLeadTime']*refreshRate: #also draw rings
               for numRing in range(len(stimRings)):
#                angleMove = angleChangeThisFrame(thisTrial, moveDirection, numRing, n, n-1)
#                stimAngleEachRing[numRing] += angleMove*(isReversed[numRing])
#                angleObject0 = angleIniEachRing[numRing] + eyeballsCurrAngleEachRing[numRing]
                #    print('angleMove=',np.round(angleMove,2)*180/pi, ' angleObject0=',np.round(angleObject0,2)*180/pi)
                #stimRings[numRing].setOri(stimAngle,log=autoLogging)
                stimRings[numRing].draw()
                #target.setOri(angleMove,operation='+',log=autoLogging)
                
               target.draw()
#                if reversalNumEachRing[numRing] <= len(reversalTimesEachRing[numRing]): #haven't exceeded  reversals assigned
#                    reversalNum = int(reversalNumEachRing[numRing])
#                    if len( reversalTimesEachRing[numRing] ) <= reversalNum:
#                        msg = 'You failed to allocate enough reversal times, reached ' +str(reversalNum)+ ' reversals at '+ str(reversalTimesEachRing[numRing][reversalNum-1]) + \
#                                  'and still going, current time ='+str(n/refreshRate)+' asking for time of next one, will assume no more reversals'
#                        logging.error(msg)
#                        print(msg)
#                        nextReversalTime = 9999 #didn't allocate enough, will just not reverse any more
#                    else: #allocated enough reversals
#                        nextReversalTime = reversalTimesEachRing[numRing][ reversalNum ]
#                    if n > refreshRate * nextReversalTime: #have now exceeded time for this next reversal
#                        isReversed[numRing] = -1*isReversed[numRing]
#                        reversalNumEachRing[numRing] +=1
#                        
#                    x,y = xyThisFrameThisAngle('circle',radii, numRing,angleThisObject,n,thisTrial['speed']) ########################################################
#                    x += offsetXYeachRing[numRing][0]
#                    y += offsetXYeachRing[numRing][1]
          if n >= maskBegin*refreshRate:
            noiseMask.draw()
            
          if blindspotFill:
              blindspotStim.draw()
          return cueCurrAngle
# #######End of function definition that displays the stimuli!!!! #####################################

respPromptText = visual.TextStim(myWin,height=0.09, pos=(0, -.8),colorSpace='rgb',color = (1,1,1),alignHoriz='center', alignVert='center', units='norm',autoLog=autoLogging)
respPromptText.setText('Press A if the thin wedge is offset anticlockwise, or L if clockwise')

def collectResponses(expStop): #Kristjansson&Holcombe cuing experiment
    #draw the possible stimuli
    #eyeball left, eyeball right, eyeball down, eyeball up
    #draw something that represents clockwise 
    responsesNeeded = 1
    responsesAutopilot = list(['A'])
    for r in range(responsesNeeded):
        responsesAutopilot.append('A')
    respcount =0
    
    while respcount <responsesNeeded:
        respPromptText.draw()
        myWin.flip()
        for key in event.getKeys():       #check if pressed abort-type key
              key = key.upper()
              if key in ['ESCAPE','Q']:
                  expStop = True
                  respcount += 1
                  responses.append('X') #dummy response so dont' get error when try to record in datafile before quitting
              elif key.upper() in ['A','L']: #A for anticlockwise, L for clockwise
                   responses.append( key.upper() )
                   respcount += 1
              else: #flicker response prompt to indicate invalid response
                for f in range(2):
                    myWin.flip(); myWin.flip()
                    respPromptText.draw()
                    myWin.flip()
        if autopilot:
           respCount = responsesNeeded
           break
           
    return responses,responsesAutopilot, expStop

trialNum=0; numTrialsCorrect=0; expStop=False; framesSaved=0;
print('Starting experiment of',trials.nTotal,'trials. Current trial is trial ',trialNum)
NextRemindCountText.setText( str(trialNum) + ' of ' + str(trials.nTotal)     )
NextRemindCountText.draw()
myWin.flip()
#end of header
trialClock = core.Clock()
stimClock = core.Clock()
thisTrial = trials.next()
ts = list();

if eyetracking:
    eyeMoveFile=('EyeTrack_'+subject+'_'+timeAndDateStr+'.EDF')
    tracker=Tracker_EyeLink(myWin,trialClock,subject,1, 'HV5',(255,255,255),(0,0,0),False,(widthPix,heightPix))

while trialNum < trials.nTotal and expStop==False:
    accelerateComputer(1,process_priority, disable_gc) #speed up
    
    numObjects = thisTrial['numObjsEachRing'][0] #haven't implemented additional rings yet
    objsPerQuadrant = numObjects / 4
    if numObjects % 4 != 0:
        msg = 'numObjects not evenly divisible by 4, therefore cannot randomise quadrant. Therefore picking object to cue completely randomly'
        logging.error(msg); print(msg)
        objToCue = np.random.random_integers(0, numObjects-1, size=1)
    else:
        quadrantObjectToCue =  np.random.random_integers(0, objsPerQuadrant-1, size=1)
        objToCue = thisTrial['objToCueQuadrant']*objsPerQuadrant + quadrantObjectToCue
    #print('objToCue=',objToCue)
    colorRings=list();
    preDrawStimToGreasePipeline = list()
    isReversed= list([1]) * numRings #always takes values of -1 or 1
    reversalNumEachRing = list([0]) * numRings
    angleIniEachRing = list( np.random.uniform(0,2*pi,size=[numRings]) )
    cueCurrAngleEachRing = list([0]) * numRings
    moveDirection = list( np.random.random_integers(0,1,size=[numRings]) *2 -1 ) #randomise initial direction
    maskBegin = thisTrial['cueLeadTime'] + targetDur
    maskDur = 0.25
    trialDurTotal = maskBegin + maskDur
    trialDurFrames= int( trialDurTotal*refreshRate )
    
    #Task will be to judge which thick wedge has the thin wedge offset within it
    #Set up parameters to construct the thick,thin wedges, target, and cue
    gratingTexPix= 1024
    radius = 25
    visibleWedge = [0,360]
    patchAngleThickWedges = 360/numObjects/2
    thickWedgeColor = [0,-1,-1]
    thinWedgeColor=[0,0,1]
    cueColor=[1,1,1]
    radialMask =   np.array( [0,0,0,0,0,0,0,1,0,0,0] )
    wedgeRadiusFraction = np.where(radialMask)[0][0]*1.0 / len(radialMask)
    #print('wedgeRadiusFraction = ',wedgeRadiusFraction)
    wedgeThicknessFraction = len( np.where(radialMask)[0] )*1.0 / len(radialMask)
    #print('wedgeThickness = ',wedgeThicknessFraction*radius)
    wedgeCenterFraction = wedgeRadiusFraction + wedgeThicknessFraction/2.
    desiredArcDistanceFractionRadius = .23
    cueInnerArcDesiredFraction = wedgeCenterFraction - desiredArcDistanceFractionRadius
    cueOuterArcDesiredFraction = wedgeCenterFraction + desiredArcDistanceFractionRadius
    if cueOuterArcDesiredFraction > 1:
        msg='Can"t start outer arc at fraction='+str(cueOuterArcDesiredFraction)
        logging.error(msg); print(msg)
    fractionResolution = .02     #Quantisation of possible positions of cue arc
    binsNeeded = 1.0 / fractionResolution
    cueRadialMask = np.zeros( binsNeeded )
    #For the cueRadialMask, want everything zero except just inside and outside of the wedges.
    innerArcCenterPos = round( binsNeeded*cueInnerArcDesiredFraction )
    outerArcCenterPos = round( binsNeeded*cueOuterArcDesiredFraction )
    cueRadialMask[ innerArcCenterPos ] = 1
    cueRadialMask[ outerArcCenterPos ] = 1
    thinWedgesAngleSubtend = 2
    innerArcActualFraction = innerArcCenterPos*1.0/len(cueRadialMask)
    outerArcActualFraction = outerArcCenterPos*1.0/len(cueRadialMask)
    closeEnough = .01
    if abs(cueInnerArcDesiredFraction - innerArcActualFraction) > closeEnough:
        print('cueInnerArcDesiredFraction of object radius = ',cueInnerArcDesiredFraction, ' actual = ', innerArcActualFraction, ' exceeding tolerance of ',closeEnough )
    if abs(cueOuterArcDesiredFraction - outerArcActualFraction) > closeEnough:
        print('cueOuterArcDesiredFraction of object radius = ',cueOuterArcDesiredFraction, ' actual = ', outerArcActualFraction, ' exceeding tolerance of ',closeEnough)
    thickThinWedgesRing, target, cue =  \
            constructThickThinWedgeRingsTargetAndCue(myWin,radii[0],radialMask,cueRadialMask,visibleWedge,numObjects,patchAngleThickWedges,
                            thinWedgesAngleSubtend,bgColor,thickWedgeColor,thinWedgeColor,thisTrial['targetAngleOffset'],gratingTexPix,cueColor,objToCue,ppLog=logging)
    core.wait(.1)
    myMouse.setVisible(False)
    if eyetracking: 
        tracker.startEyeTracking(trialNum,True,widthPix,heightPix) #start recording with eyetracker

    fixatnPeriodFrames = int(   (np.random.rand(1)/2.+0.8)   *refreshRate)  #random interval between x and x+800ms
    for i in range(fixatnPeriodFrames):
        if i%2:
            fixation.draw()
        else: fixationBlank.draw()
        myWin.flip() #clearBuffer=True)  
    trialClock.reset()
    t0=trialClock.getTime(); t=trialClock.getTime()-t0
    ts = list()
    stimClock.reset()
    for n in range(trialDurFrames): #this is the loop for this trial's stimulus!
            offsetXYeachRing=[[0,0],[0,0]]
            cueAngle = \
                        oneFrameOfStim(thisTrial,n,maskBegin,[cue],[thickThinWedgesRing],target,stimClock,useClock,offsetXYeachRing) #actual drawing of stimuli
            if exportImages:
                myWin.getMovieFrame(buffer='back') #for later saving
                framesSaved +=1
            myWin.flip(clearBuffer=True)
            t=trialClock.getTime()-t0; ts.append(t);
    #event.waitKeys(maxWait=2, keyList=['SPACE'], timeStamped=False) #debugOFF
    myWin.flip()
    event.clearEvents(eventType='mouse')
    if eyetracking:
        tracker.stopEyeTracking()

    #end of big stimulus loop
    accelerateComputer(0,process_priority, disable_gc) #turn off stuff that sped everything up
    #check for timing problems
    interframeIntervs = np.diff(ts)*1000 #difference in time between successive frames, in ms
    idxsInterframeLong = np.where( interframeIntervs > longFrameLimit ) [0] #frames that exceeded longerThanRefreshTolerance of expected duration
    numCasesInterframeLong = len( idxsInterframeLong )
    if numCasesInterframeLong >0:
       longFramesStr =  'ERROR,'+str(numCasesInterframeLong)+' frames were longer than '+str(longFrameLimit)+' ms'
       if demo: 
         longFramesStr += 'not printing them all because in demo mode'
       else:
           longFramesStr += ' apparently screen refreshes skipped, interframe durs were:'+\
                    str( np.around(  interframeIntervs[idxsInterframeLong] ,1  ) )+ ' and was these frames: '+ str(idxsInterframeLong)
       if longFramesStr != None:
                msg = 'trialnum=' + str(trialNum) +  longFramesStr
                print(msg);  logging.info(msg)
                if not demo:
                    flankingAlso=list()
                    for idx in idxsInterframeLong: #also print timing of one before and one after long frame
                        if idx-1>=0:  flankingAlso.append(idx-1)
                        else: flankingAlso.append(np.NaN)
                        flankingAlso.append(idx)
                        if idx+1<len(interframeIntervs):  flankingAlso.append(idx+1)
                        else: flankingAlso.append(np.NaN)
                    if np.NaN in flankingAlso: #was the first or last frame
                        logging.info('was first or last frame')
                    else:
                        logging.info( 'flankers also=' + str( np.around(interframeIntervs[flankingAlso],1) ))
            #end timing check
    myMouse.setVisible(True)
    passThisTrial=False
    
    # ####### set up and collect responses
    responses = list();  responsesAutopilot = list()
    responses,responsesAutopilot, expStop =  \
            collectResponses(expStop)  #collect responses!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!#####
    core.wait(.1)
    if exportImages:  #maybe catch one frame of response
        myWin.saveMovieFrames('exportedImages/frame.png')    
        expStop=True
    #Handle response, calculate whether correct, ########################################
    if autopilot:
        responses = responsesAutopilot
    #score response
    if thisTrial['targetAngleOffset'] >0:
        answer = 'L'
    else:
        answer = 'A'
    if responses[0] == answer:
        correct = 1
    else: correct = 0            
    if passThisTrial: 
        correct = -1    #indicate for data analysis that observer opted out of this trial, because think they moved their eyes
    
    #header print('trialnum\tsubject\tbasicShape\tnumObjects\tspeed\tdirection\tangleIni
    trials.data.add('subject', subject) #because extraInfo not working
    trials.data.add('objToCueRing0', objToCue[0])
    trials.data.add('numObjsRing0', numObjsEachRing[0])
    trials.data.add('numCuesRing0', numCuesEachRing[0])
    trials.data.add('response', responses[0]) #switching to using psychopy-native ways of storing, saving data 
    trials.data.add('correct', correct) #switching to using psychopy-native ways of storing, saving data 
    trials.data.add('timingBlips', numCasesInterframeLong)
    numTrialsCorrect += (correct >0)  #so count -1 as 0
    speedIdxs = np.where(thisTrial['speed']==speeds)[0]
    if len(speedIdxs) ==0:
        print('Apparently current speed= ',thisTrial['speed'],' is not in list of speeds=',speeds, '. Please make sure speeds is a numpy array')
    else: speedIdx = speedIdxs[0]  #extract index, where returns a list with first element array of the indexes
    numRightWrongEachSpeed[ speedIdx, (correct >0) ] +=1  #if right, add to 1th column, otherwise add to 0th column count
    
    if feedback and not expStop:
        if correct:
            highA = sound.Sound('G',octave=5, sampleRate=6000, secs=.8, bits=8)
            highA.setVolume(0.8)
            highA.play()
        else: #incorrect
            lowD = sound.Sound('E',octave=3, sampleRate=6000, secs=.8, bits=8)
            lowD.setVolume(0.8)
            lowD.play()
    trialNum+=1
    waitForKeyPressBetweenTrials = False
    if trialNum< trials.nTotal:
        if trialNum%( max(trials.nTotal/4,1) ) ==0:  #have to enforce at least 1, otherwise will modulus by 0 when #trials is less than 4
            pctDone = round(    (1.0*trialNum) / (1.0*trials.nTotal)*100,  0  )
            NextRemindPctDoneText.setText( str(pctDone) + '% complete' )
            NextRemindCountText.setText( str(trialNum) + ' of ' + str(trials.nTotal)     )
            for i in range(5):
                myWin.flip(clearBuffer=True)
                NextRemindPctDoneText.draw()
                NextRemindCountText.draw()
        waitingForKeypress = False
        if waitForKeyPressBetweenTrials:
            waitingForKeypress=True
            NextText.setText('Press "SPACE" to continue')
            NextText.draw()
            NextRemindCountText.draw()
            NextRemindText.draw()
            myWin.flip(clearBuffer=True) 
        else: core.wait(0.15)
        while waitingForKeypress:
           if autopilot:
                waitingForKeypress=False
           elif expStop == True:
                waitingForKeypress=False
           for key in event.getKeys():       #check if pressed abort-type key
                 if key in ['space']: 
                    waitingForKeypress=False
                 if key in ['escape','q']:
                    expStop = True
                    waitingForKeypress=False
        myWin.clearBuffer()
        thisTrial = trials.next()
    core.wait(.1); time.sleep(.1)
    #end trials loop  ###########################################################
if expStop == True:
    msg = 'user aborted experiment on keypress with trials trialNum=' + str(trialNum)
    logging.info(msg);  print(msg)
else: 
    print("Experiment finished")
if  trialNum >0:
    fileNamePP = fileNameWithPath + '.txt'
    dfFromPP = trials.saveAsWideText(fileNamePP)
    print("Psychopy wideText has been saved as", fileNamePP)
    fileNamePickle = fileNameWithPath #.psydat will automatically be appended
    trials.saveAsPickle(fileNamePickle) #.psydat
    print("Most Psychopy-ic method: trials trialHandler has been saved as", fileNamePickle+'.psydat', " and should include copy of code")
    #see analysis/analyzeTest.py
    df = dfFromPP[:trialNum] #delete trials for which don't have response etc. yet, as that will otherwise cause error when averaging, plotting
    if trialNum < trials.nTotal: #When you abort early, correct and other columns are not numeric because have value of "-"
        #converting to numeric
        df = df.convert_objects(convert_numeric=True)
        print('df.dtypes=', df.dtypes) #df.dtypes in my case are  "objects". you can't take the mean
        print('dfFromPP =', df)
if eyetracking:
    tracker.closeConnectionToEyeTracker(eyeMoveFile)
logging.info('finishing at '+timeAndDateStr)
#print('%corr = ', round( correct*1.0/trialNum*100., 2)  , '% of ',trialNum,' trials', end=' ')
print('%corr each speed: ', end=' ')
print(np.around( numRightWrongEachSpeed[:,1] / ( numRightWrongEachSpeed[:,0] + numRightWrongEachSpeed[:,1]), 2))
print('\t\t\t\tnum trials each speed =', numRightWrongEachSpeed[:,0] + numRightWrongEachSpeed[:,1])
logging.flush()
myWin.close()
if quitFinder:
        applescript="\'tell application \"Finder\" to launch\'" #turn Finder back on
        shellCmd = 'osascript -e '+applescript
        os.system(shellCmd)

#Fit and plot data
plotData = False
if trialNum >0 and plotData:
    import plotHelpers
    fig = plotHelpers.plotDataAndPsychometricCurve(df, dataFileName=None)
    figName = 'pythonFig'
    figFnameWithPath = os.path.join('analysis/figs/', figName + '.png')
    import pylab
    pylab.savefig( figFnameWithPath ) #, bbox_inches='tight')
    print('The plot has been saved, as', figFnameWithPath)
    pylab.show() #pauses until window manually closed. Have to save before calling this, because closing the window loses the figure
