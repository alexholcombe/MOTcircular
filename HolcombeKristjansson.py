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
from EyelinkEyetrackerForPsychopySUPA3 import EyeLinkCoreGraphicsPsychopy, Tracker_EyeLink #Chris Fajou integration
from helpersAOH import accelerateComputer, openMyStimWindow
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
trackPostcueOrClick = 1 #postcue means say yes/no postcued was a target, click means click on which you think was/were the targets

numRings=2
radii=[2.5,9.5]   #Need to encode as array for those experiments wherein more than one ring presented 
offsets = np.array([[0,0],[-5,0],[-10,0]])

respRadius=radii[0] #deg
refreshRate= 60 *1.0;  #160 #set to the framerate of the monitor
useClock = True #as opposed to using frame count, which assumes no frames are ever missed
fullscr=0; scrn=0
# create a dialog from dictionary 
infoFirst = { 'Autopilot':autopilot, 'Check refresh etc':True, 'Screen to use':scrn, 'Fullscreen (timing errors if not)': fullscr, 'Screen refresh rate': refreshRate }
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

#trialDur does not include trackingExtraTime, during which the cue is on. Not really part of the trial.
trialDur = 3.3
if demo:trialDur = 5;refreshRate = 60.; 
tokenChosenEachRing= [-999]*numRings
rampUpDur=0; rampDownDur=0
trialDurFrames=int(trialDur*refreshRate)+int( trackingExtraTime*refreshRate )
rampUpFrames = refreshRate*rampUpDur;   rampDownFrames = refreshRate*rampDownDur;
ShowTrackCueFrames = int( refreshRate*toTrackCueDur )
rampDownStart = trialDurFrames-rampDownFrames
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

trialsPerCondition = 2 #default value

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
       logging.info('trialsPerCondition =',trialsPerCondition)
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
fileName = dataDir+'/'+subject+ '_' + expname+timeAndDateStr
if not demo and not exportImages:
    dataFile = open(fileName+'.txt', 'w')  # sys.stdout  #StringIO.StringIO() 
    saveCodeCmd = 'cp \'' + sys.argv[0] + '\' '+ fileName + '.py'
    os.system(saveCodeCmd)  #save a copy of the code as it was when that subject was run
    logF = logging.LogFile(fileName+'.log', 
        filemode='w',#if you set this to 'a' it will append instead of overwriting
        level=logging.INFO)#errors, data and warnings will be sent to this logfile
if demo or exportImages: 
  dataFile = sys.stdout
  logging.console.setLevel(logging.ERROR)  #only show this level  messages and higher
logging.console.setLevel(logging.WARNING) #DEBUG means set the console to receive nearly all messges, INFO is for everything else, INFO, EXP, DATA, WARNING and ERROR 
if refreshRateWrong:
    logging.error(refreshMsg1+refreshMsg2)
else: logging.info(refreshMsg1+refreshMsg2)
longerThanRefreshTolerance = 0.27
longFrameLimit = round(1000./refreshRate*(1.0+longerThanRefreshTolerance),3) # round(1000/refreshRate*1.5,2)
print('longFrameLimit=',longFrameLimit,' Recording trials where one or more interframe interval exceeded this figure ', file=logF)
print('longFrameLimit=',longFrameLimit,' Recording trials where one or more interframe interval exceeded this figure ')
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
print('second window opening runInfo mean ms=',runInfo["windowRefreshTimeAvg_ms"],file=logF)
print('second window opening runInfo mean ms=',runInfo["windowRefreshTimeAvg_ms"])
logging.info(runInfo)
logging.info('gammaGrid='+str(mon.getGammaGrid()))
logging.info('linearizeMethod='+str(mon.getLinearizeMethod()))
    
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
    checkSizeOfFixatnTexture = fixSizePix/4
    nearestPowerOfTwo = round( sqrt(checkSizeOfFixatnTexture) )**2 #Because textures (created on next line) must be a power of 2
    fixatnNoiseTexture = np.round( np.random.rand(nearestPowerOfTwo,nearestPowerOfTwo) ,0 )   *2.0-1 #Can counterphase flicker  noise texture to create salient flicker if you break fixation
    fixation= visual.PatchStim(myWin, tex=fixatnNoiseTexture, size=(fixSizePix,fixSizePix), units='pix', mask='circle', interpolate=False, autoLog=autoLogging)
    fixationBlank= visual.PatchStim(myWin, tex=-1*fixatnNoiseTexture, colorSpace='rgb',mask='circle',size=fixSizePix,units='pix',autoLog=autoLogging)
else:
    fixation = visual.PatchStim(myWin,tex='none',colorSpace='rgb',color=(.9,.9,.9),mask='circle',units='pix',size=fixSizePix,autoLog=autoLogging)
    fixationBlank= visual.PatchStim(myWin,tex='none',colorSpace='rgb',color=(-1,-1,-1),mask='circle',units='pix',size=fixSizePix,autoLog=autoLogging)
fixationPoint = visual.PatchStim(myWin,colorSpace='rgb',color=(1,1,1),mask='circle',units='pix',size=2,autoLog=autoLogging) #put a point in the center

respText = visual.TextStim(myWin,pos=(0, -.8),colorSpace='rgb',color = (1,1,1),alignHoriz='center', alignVert='center', units='norm',autoLog=autoLogging)
NextText = visual.TextStim(myWin,pos=(0, 0),colorSpace='rgb',color = (1,1,1),alignHoriz='center', alignVert='center', units='norm',autoLog=autoLogging)
NextRemindPctDoneText = visual.TextStim(myWin,pos=(-.1, -.4),colorSpace='rgb',color= (1,1,1),alignHoriz='center', alignVert='center', units='norm',autoLog=autoLogging)
NextRemindCountText = visual.TextStim(myWin,pos=(.1, -.5),colorSpace='rgb',color = (1,1,1),alignHoriz='center', alignVert='center', units='norm',autoLog=autoLogging)

stimList = []
numObjsInRings = [[1,8]] #First entry in each sub-list is num cues in the cue ring. Second entry is num objects in the objects ring
speeds =  [ 0.5 ]     #dont want to go faster than 2 because of blur problem
#Set up the factorial design (list of all conditions)
for numCues in [1]:
 for numObjs in [4]:
  for cueLeadTime in [.160, .700]:  #How long is the cue on prior to the eyeballs appearing
      for speed in speeds:
              for direction in [-1.0,1.0]:  
                    stimList.append( {'numCues':numCues,'numObjs':numObjs,'cueLeadTime':cueLeadTime,'speed':speed, 'direction':direction} )
#set up record of proportion correct in various conditions
trials = data.TrialHandler(stimList,trialsPerCondition, #constant stimuli method
                                        extraInfo= {'subject':subject} )  #will be included in each row of dataframe and wideText

numRightWrongEachSpeedOrder = np.zeros([ len(speeds), 2 ]); #summary results to print out at end
numRightWrongEachSpeedIdent = deepcopy(numRightWrongEachSpeedOrder)
#end setup of record of proportion correct in various conditions

timeAndDateStr = time.strftime("%d%b%Y_%H-%M", time.localtime()) 
logging.info(  str('starting exp with name: "'+'MovingCue'+'" at '+timeAndDateStr)   )
logF = StringIO.StringIO()  #kludge so I dont have to change all the print >>logF statements
logging.info(    'numtrials='+ str(trials.nTotal)+' and each trialDur='+str(trialDur)+' refreshRate='+str(refreshRate)      )

print(' numtrials=', trials.nTotal)
print('rampUpDur=',rampUpDur, ' rampDownDur=', rampDownDur, ' secs', file=logF);  logging.info( logF.getvalue() ); logF = StringIO.StringIO() 
logging.info('task='+'track'+'   respType='+respType)
logging.info( 'colors_all='+str(colors_all)+ '  trackPostcueOrClick='+str(trackPostcueOrClick)  )
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

def  oneFrameOfStim(thisTrial,currFrame,clock,useClock,offsetXYeachRing,currAngle,isReversed,reversalNumEachRing,ShowTrackCueFrames): 
#defining a function to draw each frame of stim. So can call second time for tracking task response phase
          global cueRing,ringRadial,ringRadialR, currentlyCuedBlob #makes python treat it as a local variable
          global angleIniEachRing, correctAnswers
          if useClock: #Don't count on not missing frames. Use actual time.
            t = clock.getTime()
            n = round(t*refreshRate)
          else:
            n = currFrame
          
          if n<rampUpFrames:
                contrast = cos( -pi+ pi* n/rampUpFrames  ) /2. +.5 #starting from -pi trough of cos, and scale into 0->1 range
          elif rampDownFrames>0 and n > rampDownStart:
                contrast = cos(pi* (n-rampDownStart)/rampDownFrames ) /2.+.5 #starting from peak of cos, and scale into 0->1 range
          else: contrast = 1
          if n%2:
            fixation.draw()#flicker fixation on and off at framerate to see when skip frame
          else:
            fixationBlank.draw()
          fixationPoint.draw()
          
          for numRing in range(numRings):
            angleMove = angleChangeThisFrame(thisTrial, moveDirection, numRing, n, n-1)
            currAngle[numRing] = currAngle[numRing]+angleMove*(isReversed[numRing])
            angleObject0 = angleIniEachRing[numRing] + currAngle[numRing]
            #if numRing==0:
            #    print('angleMove=',np.round(angleMove,2)*180/pi, ' angleObject0=',np.round(angleObject0,2)*180/pi)
            for nobject in range(thisTrial['numObjs']):
                if nobject==0:
                        if reversalNumEachRing[numRing] <= len(reversalTimesEachRing[numRing]): #haven't exceeded  reversals assigned
                            reversalNum = int(reversalNumEachRing[numRing])
                            if len( reversalTimesEachRing[numRing] ) <= reversalNum:
                                msg = 'You failed to allocate enough reversal times, reached ' +str(reversalNum)+ ' reversals at '+ str(reversalTimesEachRing[numRing][reversalNum-1]) + \
                                          'and still going, current time ='+str(n/refreshRate)+' asking for time of next one, will assume no more reversals'
                                logging.error(msg)
                                print(msg)
                                nextReversalTime = 9999 #didn't allocate enough, will just not reverse any more
                            else: #allocated enough reversals
                                nextReversalTime = reversalTimesEachRing[numRing][ reversalNum ]
                            if n > refreshRate * nextReversalTime: #have now exceeded time for this next reversal
                                isReversed[numRing] = -1*isReversed[numRing]
                                reversalNumEachRing[numRing] +=1
                angleThisObject = angleObject0 + (2*pi)/thisTrial['numObjs']*nobject
                x,y = xyThisFrameThisAngle('circle',radii, numRing,angleThisObject,n,thisTrial['speed']) ########################################################
                x += offsetXYeachRing[numRing][0]
                y += offsetXYeachRing[numRing][1]
                blobColor = colors_all[0]*contrast
                #referenceCircle.setPos(offsetXYeachRing[numRing]);  referenceCircle.draw() #debug
                gaussian.setColor( blobColor, log=autoLogging )
                gaussian.setPos([x,y])
                gaussian.draw()
          if blindspotFill:
              blindspotStim.draw()
          return angleIniEachRing,currAngle,isReversed,reversalNumEachRing   
# #######End of function definition that displays the stimuli!!!! #####################################

def collectResponseKH( expStop): #Kristjansson&Holcombe cuing experiment
    #draw the possible stimuli
    #eyeball left, eyeball right, eyeball down, eyeball up
    ys = np.linspace(-.6,.6,4)
    offsetsNSEW = np.array([ [0,1], [0,-1], [1,0], [-1,0]])
    x = 0
    for i in len(ys): #draw each option for how the iris in the eyeball might have been offset
        ringKH.setPos([x,ys[i]])
        ringKH.draw()
        iris.setPos( np.array([x,y]) + offsetsNSEW[i])
        iris.draw()
    respcount =0
    while respcount <1:
        for key in event.getKeys():       #check if pressed abort-type key
              if key in ['escape','q']:
                  expStop = True
                  respcount = 1
              else: #key in [
                print('key =', key)
                STOP
    return responses,responsesAutopilot,respondedEachToken, expStop

    
print('Starting experiment of',trials.nTotal,'trials. Current trial is trial 0.')

for r in range(numRings):
    for j in range(maxPossibleReversals()):
        dataFile.write('rev'+str(r)+'_'+str(j)+'\t')  #reversal times for each ring
print('timingBlips', file=dataFile)
#end of header
trialClock = core.Clock()
stimClock = core.Clock()
trialNum=0; numTrialsCorrect=0; expStop=False; framesSaved=0;
thisTrial = trials.next()
trialDurTotal=0;
ts = list();

if eyetracking:
    eyeMoveFile=('EyeTrack_'+subject+'_'+timeAndDateStr+'.EDF')
    tracker=Tracker_EyeLink(myWin,trialClock,subject,1, 'HV5',(255,255,255),(0,0,0),False,(widthPix,heightPix))

while trialNum < trials.nTotal and expStop==False:
    accelerateComputer(1,process_priority, disable_gc) #speed up
    colorRings=list();
    preDrawStimToGreasePipeline = list()
    isReversed= list([1]) * numRings #always takes values of -1 or 1
    reversalNumEachRing = list([0]) * numRings
    angleIniEachRing = list( np.random.uniform(0,2*pi,size=[numRings]) )
    currAngle = list([0]) * numRings
    moveDirection = list( np.random.random_integers(0,1,size=[numRings]) *2 -1 ) #randomise initial direction
    trialDurTotal = maxTrialDur()  #thisTrial['cueLeadTime'] + targetDur + maskDur
    trialDurFrames= int( trialDurTotal*refreshRate )
    #xyTargets = np.zeros( [thisTrial['numTargets'], 2] ) #need this for eventual case where targets can change what ring they are in
    #numDistracters = numRings*thisTrial['numObjectsInRing'] - thisTrial['numTargets']
    #xyDistracters = np.zeros( [numDistracters, 2] )

    reversalTimesEachRing = getReversalTimes()
    #print('reversalTimesEachRing=',np.around(np.array(reversalTimesEachRing),2),' maxPossibleReversals=',maxPossibleReversals()) #debugOFF
    core.wait(.1)
    myMouse.setVisible(False)
    if eyetracking: 
        tracker.startEyeTracking(trialNum,True,widthPix,heightPix) # CF is awesome! - start recording with eyetracker

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
            (angleIni,currAngle,isReversed,reversalNumEachRing) = \
                            oneFrameOfStim(thisTrial,n,stimClock,useClock,offsetXYeachRing,currAngle,isReversed,reversalNumEachRing,ShowTrackCueFrames) #da big function
            if exportImages:
                myWin.getMovieFrame(buffer='back') #for later saving
                framesSaved +=1
            myWin.flip(clearBuffer=True)
            t=trialClock.getTime()-t0; ts.append(t);
            if n==trialDurFrames-1: event.clearEvents(eventType='mouse');
    if eyetracking:
        tracker.stopEyeTracking()

    #end of big stimulus loop
    accelerateComputer(0,process_priority, disable_gc) #turn off stuff that sped everything up
    #check for timing problems
    interframeIntervs = np.diff(ts)*1000 #difference in time between successive frames, in ms
    #print >>logF, 'trialnum=',trialNum, '   interframe intervs were ',around(interframeIntervs,1)
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
                print('trialnum=',trialNum,'  ',longFramesStr)
                print('trialnum=',trialNum,'  ',longFramesStr, file=logF)
                if not demo:
                    flankingAlso=list()
                    for idx in idxsInterframeLong: #also print timing of one before and one after long frame
                        if idx-1>=0:  flankingAlso.append(idx-1)
                        else: flankingAlso.append(np.NaN)
                        flankingAlso.append(idx)
                        if idx+1<len(interframeIntervs):  flankingAlso.append(idx+1)
                        else: flankingAlso.append(np.NaN)
                    #print >>logF, 'flankers also='+str( np.around( interframeIntervs[flankingAlso], 1) )
            #end timing check
    myMouse.setVisible(True)
    #ansIter=(answer).reshape(1,-1)[0]; ln=len(ansIter) #in case it's two dimensions like in bindRadially
    #print 'answer=',answer,' or ', [colorNames[ int(ansIter[i]) ] for i in range( ln )], ' it is type ',type(answer), ' and shape ', np.shape(answer)  
    #shuffledAns = deepcopy(answer);  #just to use for options, to ensure they are in a different order
    #if numObjects == 2:
    #     shuffledAns = shuffledAns[0:2]  #kludge. Really this should be controlled by nb_colors but that would require fancy array indexing where I currently have 0,2,1 etc above
   # np.random.shuffle(shuffledAns)  
    #if len(np.shape(answer)) >1: #more than one dimension, because bindRadiallyTask
    #     np.random.shuffle(shuffledAns[:,0]) #unfortunately for bindRadially task, previous shuffling shuffled pairs, not individuals
    #print 'answer after shuffling=',shuffledAns 
    passThisTrial=False
    #Create postcues
    visuallyPostCue = True
    postCueNumBlobsAway=-999 #doesn't apply to click tracking and non-tracking task
     # ####### response set up answer
    responses = list();  responsesAutopilot = list()
    responses,responsesAutopilot,respondedEachToken,expStop = \
            collectResponses(thisTrial,n,responses,responsesAutopilot,offsetXYeachRing,respRadius,currAngle,expStop)  #collect responses!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!#####
    #print("responses=",responses,";respondedEachToken=",respondedEachToken,"expStop=",expStop) #debugOFF
    core.wait(.1)
    if exportImages:  #maybe catch one frame of response
        myWin.saveMovieFrames('exported/frame.png')    
        expStop=True        
    #Handle response, calculate whether correct, ########################################
    if autopilot:responses = responsesAutopilot
    if True: #not expStop: #if short on responses, too hard to write code to handle it so don't even try
        correct=-99;  #FIX
        for l in range(numRings):
            correct = -99
            
        #end if statement for if not expStop
    if passThisTrial: correct = -1    #indicate for data analysis that observer opted out of this trial, because think they moved their eyes

    #header print('trialnum\tsubject\tbasicShape\tnumObjects\tspeed\tdirection\tangleIni
    trials.data.add('trialDurTotal', trialDurTotal)
    trials.data.add('correct', correct) #switching to using psychopy-native ways of storing, saving data 
    trials.data.add('timingBlips', numCasesInterframeLong)
    
    numTrialsCorrect += (correct >0)  #so count -1 as 0
    speedIdx = np.where(speeds==thisTrial['speed'])[0][0]  #extract index, where returns a list with first element array of the indexes
    numRightWrongEachSpeedOrder[ speedIdx, (correct >0) ] +=1  #if right, add to 1th column, otherwise add to 0th column count
    dataFile.flush(); logF.flush(); 
    
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
    print('user aborted experiment on keypress with trials trialNum=', trialNum, file=logF)
    print('user aborted experiment on keypress with trials trialNum=', trialNum)
else: 
    print("Experiment finished")
if  nDone >0:
    print("Data was saved on each trial to", fileNameWithPath+'MANUAL.txt')
    fileNamePP = fileNameWithPath
    dfFromPP = trials.saveAsWideText(fileNamePP)
    print("Psychopy's wideText has been saved as", fileNamePP)
    #dfFromPP.to_pickle(fileNameWithPath+"_DataFrame.pickle") #doing this to have a dataframe to test plotDataAndPsychometricCurve with in analyzeData.py
    fileNamePickle = fileNameWithPath #.psydat will automatically be appended
    trials.saveAsPickle(fileNamePickle)
    print("Most Psychopy-ic method: trials trialHandler has been saved as", fileNamePickle, "should include copy of code")
                      
    #df.dtypes in my case are  "objects". you can't take the mean
    df = dfFromPP
    print('df.dtypes=\n',df.dtypes)
   

if eyetracking:
    tracker.closeConnectionToEyeTracker(eyeMoveFile)
print('finishing at ',timeAndDateStr, file=logF)
print('%corr order report= ', round( correct*1.0/trialNum*100., 2)  , '% of ',trialNum,' trials', end=' ')
print('%corr each speed: ', end=' ')
print(np.around( numRightWrongEachSpeedOrder[:,1] / ( numRightWrongEachSpeedOrder[:,0] + numRightWrongEachSpeedOrder[:,1]), 2))
print('\t\t\t\tnum trials each speed =', numRightWrongEachSpeedOrder[:,0] + numRightWrongEachSpeedOrder[:,1])
logging.flush(); dataFile.close(); logF.close()
if quitFinder:
        applescript="\'tell application \"Finder\" to launch\'" #turn Finder back on
        shellCmd = 'osascript -e '+applescript
        os.system(shellCmd)
core.quit()