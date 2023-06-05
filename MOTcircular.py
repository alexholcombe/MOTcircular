__author__ = """Alex "O." Holcombe, Wei-Ying Chen""" ## double-quotes will be silently removed, single quotes will be left, eg, O'Connor
############################################################
###For set-up on a new machine, some variables to consider
###
### useClock
### For set-up of a new experimnet variant, variables to consider: 
### trialDurMin, trackVariableIntervMax
##############
import psychopy.info
from psychopy import sound, monitors, logging, visual, data, core
import psychopy.gui, psychopy.event
import numpy as np
import itertools #to calculate all subsets
from copy import deepcopy
from math import atan, pi, cos, sin, sqrt, ceil
import time, sys, platform, os, gc, io #io is successor to StringIO
#from EyelinkEyetrackerForPsychopySUPA3 import EyeLinkCoreGraphicsPsychopy, Tracker_EyeLink #Chris Fajou integration but try ioHub
from helpersAOH import accelerateComputer, openMyStimWindow, calcCondsPerNumTargets, LCM, gcd
eyetracking = False; eyetrackFileGetFromEyelinkMachine = False #very timeconsuming to get the file from the Windows machine over the ethernet cable, 
#usually better to get the EDF file from the Eyelink machine by hand by rebooting into Windows and going to 

quitFinder = False
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

numRings=3
radii=[2.5,9.5,15]   #Need to encode as array for those experiments wherein more than one ring presented 

respRadius=radii[0] #deg
refreshRate= 110 *1.0;  #160 #set to the framerate of the monitor
useClock = True #as opposed to using frame count, which assumes no frames are ever missed
fullscr=1; scrn=0
#Find out if screen may be Retina because of bug in psychopy for mouse coordinates (https://discourse.psychopy.org/t/mouse-coordinates-doubled-when-using-deg-units/11188/5)
has_retina_scrn = False
import subprocess
if subprocess.call("system_profiler SPDisplaysDataType | grep -i 'retina'", shell=True) == 0:
    has_retina_scrn = True #https://stackoverflow.com/questions/58349657/how-to-check-is-it-a-retina-display-in-python-or-terminal
        
# create a dialog from dictionary 
infoFirst = { 'Autopilot':autopilot, 'Check refresh etc':True, 'Screen to use':scrn, 'Fullscreen (timing errors if not)': fullscr, 'Screen refresh rate': refreshRate }
OK = psychopy.gui.DlgFromDict(dictionary=infoFirst, 
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

#trialDurMin does not include trackVariableIntervMax or trackingExtraTime, during which the cue is on. Not really part of the trial.
trialDurMin = 1
trackingExtraTime=1.0; #giving the person time to attend to the cue (secs). This gets added to trialDurMin
trackVariableIntervMax = 0.8 #Random interval that gets added to trackingExtraTime and trialDurMin
if demo:trialDurMin = 5;refreshRate = 60.; 
tokenChosenEachRing= [-999]*numRings
rampUpDur=0; #duration of speed ramp from stationary, during cue
rampDownDur=0 #duration of speedramp down up to the end of the trial

def maxTrialDur():
    return( trialDurMin+trackingExtraTime+trackVariableIntervMax)
badTimingCushion = 0.1 #Creating 100ms more of reversals than should need. Because if miss frames and using clock time instead of frames, might go longer
def maxPossibleReversals():  #need answer to know how many blank fields to print to file
    return int( ceil(      (maxTrialDur() - trackingExtraTime)  / timeTillReversalMin          ) )
def getReversalTimes():
    reversalTimesEachRing = [  [] for i in range(numRings)  ]
    for r in range(numRings): # set random reversal times
        thisReversalDur = trackingExtraTime
        while thisReversalDur< trialDurTotal+badTimingCushion:  
            thisReversalDur +=  np.random.uniform(timeTillReversalMin,timeTillReversalMax) #10000; print('WARNING thisReversalDur off') 
            reversalTimesEachRing[r].append(thisReversalDur)
    return reversalTimesEachRing
    
toTrackCueDur = rampUpDur+rampDownDur+trackingExtraTime  #giving the person time to attend to the cue (secs)
trialDurFrames=int(trialDurMin*refreshRate)+int( trackingExtraTime*refreshRate )
rampUpFrames = refreshRate*rampUpDur;   rampDownFrames = refreshRate*rampDownDur;
ShowTrackCueFrames = int( refreshRate*toTrackCueDur )
rampDownStart = trialDurFrames-rampDownFrames
ballStdDev = 1.8
mouseChoiceArea = ballStdDev*0.8 # origin =1.3
units='deg' #'cm'
timeTillReversalMin = 0.5 #0.5; 
timeTillReversalMax = 1.5# 1.3 #2.9
colors_all = np.array([[1,-1,-1]] * 20)  #colors of the blobs (all identical) in a ring. Need as many as max num objects in a ring
cueColor = np.array([1,1,1])
#monitor parameters
widthPixRequested = 800 #1440  #monitor width in pixels
heightPixRequested =600  #900 #monitor height in pixels
monitorwidth = 30; #38.5 #monitor width in centimeters
viewdist = 57.; #cm
bgColor = [-1,-1,-1] #black background
monitorname = 'testMonitor' # 'mitsubishi' #in psychopy Monitors Center
if exportImages:
    fullscr=0; scrn=0
    widthPixRequested = 600; heightPixRequested = 450
    monitorwidth = 25.0
if demo:    
    scrn=0; fullscr=0
    widthPixRequested = 800; heightPixRequested = 600
    monitorname='testMonitor'
    allowGUI = True
    monitorwidth = 23#18.0

mon = monitors.Monitor(monitorname,width=monitorwidth, distance=viewdist)#fetch the most recent calib for this monitor
mon.setSizePix( (widthPixRequested,heightPixRequested) )
myWin = openMyStimWindow(mon,widthPixRequested,heightPixRequested,bgColor,allowGUI,units,fullscr,scrn,waitBlank)
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
myDlg = psychopy.gui.Dlg(title="object tracking experiment", pos=(200,400))
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
if checkRefreshEtc and (not demo) and (myWinRes != [widthPixRequested,heightPixRequested]).any():
    msgWrongResolution = 'Instead of desired resolution of '+ str(widthPixRequested)+'x'+str(heightPixRequested)+ ' pixels, screen apparently '+ str(myWinRes[0])+ 'x'+ str(myWinRes[1])
    myDlg.addText(msgWrongResolution, color='Red')
    print(msgWrongResolution)
myDlg.addText('Note: to abort press ESC at a trials response screen') # color='DimGrey') color names stopped working along the way, for unknown reason
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
    dataFile = open(fileName+'.txt', 'w')  # sys.stdout
    import shutil
    #save a copy of the code as it was when that subject was run
    shutil.copy2(sys.argv[0], fileName+'.py') # complete target filename given
    #saveCodeCmd = 'cp \'' + sys.argv[0] + '\' '+ fileName + '.py'
    #os.system(saveCodeCmd)
    
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
msg = 'longFrameLimit=' + str(longFrameLimit) + ' Recording trials where one or more interframe interval exceeded this figure '
print(msg, file=logF)
print(msg)
if msgWrongResolution != '':
    logging.error(msgWrongResolution)

#Not a test - the final window opening
myWin = openMyStimWindow(mon,widthPixRequested,heightPixRequested,bgColor,allowGUI,units,fullscr,scrn,waitBlank)

#Just roll with whatever wrong resolution the screen is set to
widthPix = myWin.size[0]
heightPix = myWin.size[1]
pixelperdegree = widthPix / (atan(monitorwidth/viewdist) /np.pi*180)

myMouse = psychopy.event.Mouse(visible = 'true',win=myWin)
runInfo = psychopy.info.RunTimeInfo(
        win=myWin,    ## a psychopy.visual.Window() instance; None = default temp window used; False = no win, no win.flips()
        refreshTest='grating', ## None, True, or 'grating' (eye-candy to avoid a blank screen)
        verbose=True, ## True means report on everything 
        userProcsDetailed=True  ## if verbose and userProcsDetailed, return (command, process-ID) of the user's processes
        )
print('second window opening runInfo mean ms=',runInfo["windowRefreshTimeAvg_ms"],file=logF)
logging.info(runInfo)
logging.info('gammaGrid='+str(mon.getGammaGrid()))
logging.info('linearizeMethod='+str(mon.getLinearizeMethod()))
    
gaussian = visual.PatchStim(myWin, tex='none',mask='gauss',colorSpace='rgb',size=ballStdDev,autoLog=autoLogging)
gaussian2 = visual.PatchStim(myWin, tex='none',mask='gauss',colorSpace='rgb',size=ballStdDev,autoLog=autoLogging)
optionChosenCircle = visual.Circle(myWin, radius=mouseChoiceArea, edges=32, colorSpace='rgb',fillColor = (1,0,1),autoLog=autoLogging) #to outline chosen options

#Optionally show zones around objects that will count as a click for that object
clickableRegion = visual.Circle(myWin, radius=2.2, edges=32, colorSpace='rgb',fillColor=(-1,.5,-1),autoLog=autoLogging) #to show clickable zones
#Optionally show location of most recent click
clickedRegion = visual.Circle(myWin, radius=2.2, edges=32, colorSpace='rgb',lineColor=(-1,1,-1),fillColor=(-1,1,-1),autoLog=autoLogging) #to show clickable zones
clickedRegion.setColor((0,1,-1)) #show in yellow

landmarkDebug = visual.Circle(myWin, radius=2.2, edges=32, colorSpace='rgb',fillColor=(1,-1,1),autoLog=autoLogging) #to show clickable zones

circlePostCue = visual.Circle(myWin, radius=2*radii[0], edges=32, colorSpace='rgb',fillColor = (-.85,-.85,-.85),lineColor=(-1,-1,-1),autoLog=autoLogging) #visual postcue
#referenceCircle allows visualisation of trajectory, mostly for debugging
referenceCircle = visual.Circle(myWin, radius=radii[0], edges=32, colorSpace='rgb',lineColor=(-1,-1,1),autoLog=autoLogging) #visual postcue

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

#respText = visual.TextStim(myWin,pos=(0, -.5),colorSpace='rgb',color = (1,1,1),anchorHoriz='center', anchorVert='center', units='norm',autoLog=autoLogging)
NextText = visual.TextStim(myWin,pos=(0, 0),colorSpace='rgb',color = (1,1,1),anchorHoriz='center', anchorVert='center', units='norm',autoLog=autoLogging)
NextRemindPctDoneText = visual.TextStim(myWin,pos=(-.1, -.4),colorSpace='rgb',color= (1,1,1),anchorHoriz='center', anchorVert='center', units='norm',autoLog=autoLogging)
NextRemindCountText = visual.TextStim(myWin,pos=(.1, -.5),colorSpace='rgb',color = (1,1,1),anchorHoriz='center', anchorVert='center', units='norm',autoLog=autoLogging)

stimList = []
# temporalfrequency limit test
numObjsInRing =         [  2,                    8        ]
speedsEachNumObjs =  [ [1.1,1.2,1.4,1.7], [1.1,1.2,1.4,1.7] ]     #dont want to go faster than 2 because of blur problem
numTargets = np.array([2,3])  # np.array([1,2,3])
leastCommonMultipleSubsets = int( calcCondsPerNumTargets(numRings,numTargets) )
leastCommonMultipleTargetNums = int( LCM( numTargets ) )  #have to use this to choose whichToQuery. For explanation see newTrajectoryEventuallyForIdentityTracking.oo3
#print('leastCommonMultipleSubsets=',leastCommonMultipleSubsets, ' leastCommonMultipleTargetNums= ', leastCommonMultipleTargetNums)
                
for numObjs in numObjsInRing: #set up experiment design
    idx = numObjsInRing.index(numObjs)
    speeds= speedsEachNumObjs[  idx   ]
    for speed in speeds:
        ringNums = np.arange(numRings)
        for nt in numTargets: #  If 3 concentric rings involved, have to consider 3 choose 2, 3 choose 1, have to have as many conditions as the maximum
          subsetsThis = list(itertools.combinations(ringNums,nt)) #all subsets of length nt from the universe of ringNums
          numSubsetsThis = len( subsetsThis );   #print('numSubsetsThis=',numSubsetsThis)
          repsNeeded = leastCommonMultipleSubsets / numSubsetsThis #that's the number of repetitions needed to make up for number of subsets of rings
          for r in range( int(repsNeeded) ):  #for nt with largest number of subsets, need no repetitions
              for s in subsetsThis:
                  whichIsTarget = np.ones(numRings)*-999 #-999 is  value meaning no target in that ring. 1 will mean target in ring
                  for ring in s:
                     whichIsTarget[ring] = np.random.randint(0,numObjs-1,size=1) #deprecated np.random.random_integers(0, numObjs-1, size=1) #1
                  #print('numTargets=',nt,' whichIsTarget=',whichIsTarget,' and that is one of ',numSubsetsThis,' possibilities and we are doing ',repsNeeded,'repetitions')
                  for whichToQuery in range( leastCommonMultipleTargetNums ):  #for each subset, have to query one. This is dealed out to  the current subset by using modulus. It's assumed that this will result in equal total number of queried rings
                      whichSubsetEntry = whichToQuery % nt  #e.g. if nt=2 and whichToQuery can be 0,1,or2 then modulus result is 0,1,0. This implies that whichToQuery won't be totally counterbalanced with which subset, which is bad because
                                      #might give more resources to one that's queried more often. Therefore for whichToQuery need to use least common multiple.
                      ringToQuery = s[whichSubsetEntry];  #print('ringToQuery=',ringToQuery,'subset=',s)
                      for basicShape in ['circle']: #'diamond'
                        for initialDirRing0 in [-1,1]:
                                stimList.append( {'basicShape':basicShape, 'numObjectsInRing':numObjs,'speed':speed,'initialDirRing0':initialDirRing0,
                                        'numTargets':nt,'whichIsTarget':whichIsTarget,'ringToQuery':ringToQuery} )
    #set up record of proportion correct in various conditions
trialSpeeds = list() #purely to allow report at end of how many trials got right at each speed
for s in stimList: trialSpeeds.append( s['speed'] )
uniqSpeeds = set(trialSpeeds) #reduce speedsUsed list to unique members, unordered set
uniqSpeeds = sorted( list(uniqSpeeds)  )
uniqSpeeds = np.array( uniqSpeeds ) 
numRightWrongEachSpeedOrder = np.zeros([ len(uniqSpeeds), 2 ]); #summary results to print out at end
numRightWrongEachSpeedIdent = deepcopy(numRightWrongEachSpeedOrder)
#end setup of record of proportion correct in various conditions

trials = data.TrialHandler(stimList,trialsPerCondition) #constant stimuli method

timeAndDateStr = time.strftime("%d%b%Y_%H-%M", time.localtime()) 
logging.info(  str('starting exp with name: "'+'TemporalFrequencyLimit'+'" at '+timeAndDateStr)   )
logF = io.StringIO()  #kludge so I dont have to change all the print >>logF statements
msg = 'numtrials='+ str(trials.nTotal)+', trialDurMin= '+str(trialDurMin)+ ' trackVariableIntervMax= '+ str(trackVariableIntervMax) + 'refreshRate=' +str(refreshRate)     
logging.info( msg )
print(msg)
msg = 'rampUpDur=' + str(rampUpDur) + ' rampDownDur= ' + str(rampDownDur) + ' secs'
print(msg, file=logF);
logging.info( logF.getvalue() )
logging.info('task='+'track'+'   respType='+respType)
logging.info( 'ring radii=' + str(radii)   )
logging.flush()

RFcontourAmp= 0.0
RFcontourFreq = 2.0
RFcontourPhase = 0
def RFcontourCalcModulation(angle,freq,phase): 
    modulation = sin(angle*freq + phase) #radial frequency contour equation, e.g. http://www.journalofvision.org/content/14/11/12.full from Wilkinson et al. 1998
    return modulation
    
def diamondShape(constSpeedOrConstRps,angle):
    def triangleWave(period, phase):
           #triangle wave is in sine phase (starts at 0)
           y = -abs(phase % (2*period) - period) # http://stackoverflow.com/questions/1073606/is-there-a-one-line-function-that-generates-a-triangle-wave
           #y goes from -period to 0.  Need to rescale to -1 to 1 to match sine wave etc.
           y = y/period*2 + 1
           #Now goes from -1 to 1
           return y
           
    if constSpeedOrConstRps: #maintain constant rps. So, draw the blob at the prescribed theta. But change the radius to correspond to a square.
        #As a consequence, will travel faster the more the direction differs from the circle, like around the corners
        #Theta varies from 0 to 2pi. Taking its cosine, gives x coordinate on circle.
        #Instead of taking cosine, I should just make it a linear ramp of x back and forth. That is, turn it into a triangle wave
        #Want 0 to pi to be -1 to 1
        x = triangleWave(pi,angle)
        y = triangleWave(pi, (angle-pi/2)%(2*pi ))
        #This will always describe a diamond. To change the shape would have to use vector rotation formula
    else: #constant speed, so
        #take theta not as the angle wanted, but what proportion (after being divided by 2pi) along the trajectory you want to go
        angle = angle % (2*pi) #modulus
        proportnTraj = angle/(2*pi)
        if (proportnTraj < 0) or (proportnTraj>1):
            print("Unexpected angle below 0!"); logging.error("Unexpected angle below 0!")
        #how do I go from proportnTraj either to x,y or to theta?
        #Analytic method is that as increase theta deviates from 4 points that touches circle, theta change is smaller for equal change in proportnTraj
        #Brute force method is to divide into 4 segments, below.
        zeroToFour = proportnTraj*4
        if zeroToFour < 1: #headed NW up the first quadrant
            x = 1 - (zeroToFour-0)
            y = (zeroToFour-0)
        elif zeroToFour < 2: #SW
            x = - (zeroToFour - 1)
            y = 1- (zeroToFour - 1)
        elif zeroToFour < 3: #SE
            x = -1+(zeroToFour - 2)
            y = - (zeroToFour - 2)
        elif zeroToFour < 4: #NE
            x = (zeroToFour-3)
            y = -1+(zeroToFour-3)
        else: logging.error("Unexpected zeroToFour="+ str(zeroToFour))
        #Max x is 1, meaning that it will be the diamond that circumscribes the unit circle.
        #Otherwise need to adjust by calculating the average eccentricity of such a diamond and compensating, which I never did.
        return x,y

ampTemporalRadiusModulation = 0.0 # 1.0/3.0
ampModulatnEachRingTemporalPhase = np.random.rand(numRings) * 2*np.pi
def xyThisFrameThisAngle(basicShape, radiiThisTrial, numRing, angle, thisFrameN, speed):
    #period of oscillation should be in sec
    r = radiiThisTrial[numRing]
    timeSeconds = thisFrameN / refreshRate
    def waveForm(type,speed,timeSeconds,numRing):
        if speed==0 and ampTemporalRadiusModulation==0:
            return 0 #this way don't get division by zero error when speed=0
        else:
            periodOfRadiusModulation = 1.0/speed#so if speed=2 rps, radius modulation period = 0.5 s
            modulatnPhaseRadians = timeSeconds/periodOfRadiusModulation * 2*pi + ampModulatnEachRingTemporalPhase[numRing]
            if type=='sin':
                return sin(modulatnPhaseRadians)
            elif type == 'sqrWave':
                ans = np.sign( sin(modulatnPhaseRadians) ) #-1 or 1. That's great because that's also sin min and max
                if ans==0: ans = -1+ 2*round( np.random.rand(1)[0] ) #exception case is when 0, gives 0, so randomly change that to -1 or 1
                return ans
            else: print('Error! unexpected type in radiusThisFrameThisAngle')
        
    if basicShape == 'circle':
        rThis =  r + waveForm('sin',speed,timeSeconds,numRing) * r * ampTemporalRadiusModulation
        rThis += r * RFcontourAmp * RFcontourCalcModulation(angle,RFcontourFreq,RFcontourPhase)
        x = rThis*cos(angle)
        y = rThis*sin(angle)
    elif basicShape == 'diamond': #actual square-shaped trajectory. Could also add all the modulations to this, later
        x,y = diamondShape(constSpeedOrConstRps = False, angle=angle)
        x*=r
        y*=r
    else: 
        print('Unexpected basicShape: ',basicShape)
    
    return x,y

def angleChangeThisFrame(speed,initialDirectionEachRing, numRing, thisFrameN, lastFrameN):
    angleMove = initialDirectionEachRing[numRing] * speed*2*pi*(thisFrameN-lastFrameN) / refreshRate
    return angleMove

def  oneFrameOfStim(thisTrial,currFrame,clock,useClock,offsetXYeachRing,initialDirectionEachRing,currAngle,blobToCueEachRing,isReversed,reversalNumEachRing,ShowTrackCueFrames): 
#defining a function to draw each frame of stim. So can call second time for tracking task response phase
      global cueRing,ringRadial,ringRadialR, currentlyCuedBlob #makes python treat it as a local variable
      global angleIniEachRing, correctAnswers
      
      #Determine what frame we are on
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
        speed = thisTrial['speed']
        if basicShape == 'diamond':  #scale up speed so that it achieves that speed in rps even though it has farther to travel
            perimeter = radii[numRing]*4.0
            circum = 2*pi*radii[numRing]
            speed = thisTrial['speed'] * perimeter/circum #Have to go this much faster to get all the way around in same amount of time as for circle
        angleMove = angleChangeThisFrame(speed,initialDirectionEachRing, numRing, n, n-1)
        currAngle[numRing] = currAngle[numRing]+angleMove*(isReversed[numRing])
        angleObject0 = angleIniEachRing[numRing] + currAngle[numRing]
        for nobject in range(numObjects):
            if nobject==0:
                if reversalNumEachRing[numRing] <= len(reversalTimesEachRing[numRing]): #haven't exceeded reversals assigned
                    reversalNum = int(reversalNumEachRing[numRing])
                    if len( reversalTimesEachRing[numRing] ) <= reversalNum:
                        msg = 'Not enough reversal times allocated, reached ' +str(reversalNum)+ ' reversals at '+ str( round(reversalTimesEachRing[numRing][reversalNum-1],1) )
                        msg=msg+ 'and still going (only allocated the following:' + str( np.around(reversalTimesEachRing[numRing],1) )+ ' n= ' + str(round(n,1))
                        msg=msg+ ' current time ='+str( round(n/refreshRate,2) )+' asking for time of next one, will assume no more reversals'
                        logging.error(msg)
                        print(msg)
                        nextReversalTime = 9999 #didn't allocate enough, will just not reverse any more
                    else: #allocated enough reversals
                        nextReversalTime = reversalTimesEachRing[numRing][ reversalNum ]
                    if n > refreshRate * nextReversalTime: #have now exceeded time for this next reversal
                        isReversed[numRing] = -1*isReversed[numRing]
                        reversalNumEachRing[numRing] +=1
            angleThisObject = angleObject0 + (2*pi)/numObjects*nobject
            x,y = xyThisFrameThisAngle(thisTrial['basicShape'],radii, numRing,angleThisObject,n,speed)
            x += offsetXYeachRing[numRing][0]
            y += offsetXYeachRing[numRing][1]
            if n< ShowTrackCueFrames and nobject==blobToCueEachRing[numRing]: #cue in white  
                weightToTrueColor = n*1.0/ShowTrackCueFrames #compute weighted average to ramp from white to correct color
                blobColor = (1.0-weightToTrueColor)*cueColor +  weightToTrueColor*colors_all[nobject]
                blobColor *= contrast #also might want to change contrast, if everybody's contrast changing in contrast ramp
                #print('weightToTrueColor=',weightToTrueColor,' n=',n, '  blobColor=',blobColor)
            else: blobColor = colors_all[0]*contrast
            #referenceCircle.setPos(offsetXYeachRing[numRing]);  referenceCircle.draw() #debug
            gaussian.setColor( blobColor, log=autoLogging )
            gaussian.setPos([x,y])
            gaussian.draw()
      if blindspotFill:
          blindspotStim.draw()
      return angleIniEachRing,currAngle,isReversed,reversalNumEachRing   
# #######End of function that displays the stimuli #####################################
########################################################################################

showclickableRegions = True
showClickedRegion = False
def  collectResponses(thisTrial,n,responses,responsesAutopilot,offsetXYeachRing,respRadius,currAngle,expStop ):
    optionSets=numRings
   #Draw response cues
    numTimesRespSoundPlayed=0
    if numTimesRespSoundPlayed<1: #2
        respSound.setVolume(1)
        if numRings > 1:
            respSound.play()
        numTimesRespSoundPlayed +=1
    #respText.draw()

    respondedEachToken = np.zeros([numRings,numObjects])  #potentially two sets of responses, one for each ring
    optionIdexs=list();baseSeq=list();numOptionsEachSet=list();numRespsNeeded=list()
    numRespsNeeded = np.zeros(numRings) 
    for ring in range(numRings):
        optionIdexs.append([])
        noArray=list()
        for k in range(numObjects):noArray.append(colors_all[0])
        baseSeq.append(np.array(noArray))
        for i in range(numObjects):
            optionIdexs[ring].append(baseSeq[ring][i % len(baseSeq[ring])] )
        if ring == thisTrial['ringToQuery']:
            numRespsNeeded[ ring ] = 1
        else: numRespsNeeded[ ring ] = 0
        numOptionsEachSet.append(len(optionIdexs[ring]))
    respcount = 0;     tClicked = 0;       lastClickState=0;       mouse1=0
    for ring in range(optionSets): 
            responses.append( list() )
            zeros = [0]*int(numRespsNeeded[ring])
            responsesAutopilot.append( zeros )  #autopilot response is 0
    passThisTrial = False; 
    numTimesRespSoundPlayed=0
    while respcount < sum(numRespsNeeded): #collecting response
       #Draw visual response cue
       if visuallyPostCue:
            circlePostCue.setPos( offsetXYeachRing[ thisTrial['ringToQuery'] ] )
            circlePostCue.setRadius( radii[ thisTrial['ringToQuery'] ] )
            circlePostCue.draw()
                
       for optionSet in range(optionSets):  #draw this group (ring) of options
          for ncheck in range( numOptionsEachSet[optionSet] ):  #draw each available to click on in this ring
                angle =  (angleIniEachRing[optionSet]+currAngle[optionSet]) + ncheck*1.0/numOptionsEachSet[optionSet] *2.*pi
                stretchOutwardRingsFactor = 1
                x,y = xyThisFrameThisAngle(thisTrial['basicShape'],radii,optionSet,angle,n,thisTrial['speed'])
                x = x+ offsetXYeachRing[optionSet][0]
                y = y+ offsetXYeachRing[optionSet][1]
                #draw colors, and circles around selected items. Colors are drawn in order they're in in optionsIdxs
                opts=optionIdexs;
                if respondedEachToken[optionSet][ncheck]:  #draw circle around this one to indicate this option has been chosen
                       optionChosenCircle.setColor(array([1,-1,1]), log=autoLogging)
                       optionChosenCircle.setPos([x,y])
                       optionChosenCircle.draw()                
                gaussian.setColor(  colors_all[0], log=autoLogging )  #draw blob
                gaussian.setPos([x,y]);  
                gaussian.draw()
                 
       mouse1, mouse2, mouse3 = myMouse.getPressed()
       if mouse1 and lastClickState==0:  #only count this event if is a new click. Problem is that mouse clicks continue to be pressed for along time
            mouseX,mouseY = myMouse.getPos() 
            #supposedly in units of myWin, which is degrees, BUT
            mouseFactor = 1
            if (has_retina_scrn and scrn==0): #Because of a bug in Psychopy triggered by retina displays
                mouseFactor = 0.5
            mouseX = mouseX * mouseFactor 
            mouseY = mouseY * mouseFactor 
            for optionSet in range(optionSets):
              for ncheck in range( numOptionsEachSet[optionSet] ): 
                    angle =  (angleIniEachRing[optionSet]+currAngle[optionSet]) + ncheck*1.0/numOptionsEachSet[optionSet] *2.*pi #radians
                    x,y = xyThisFrameThisAngle(thisTrial['basicShape'],radii,optionSet,angle,n,thisTrial['speed'])
                    x = x+ offsetXYeachRing[optionSet][0]
                    y = y+ offsetXYeachRing[optionSet][1]
                    #check whether mouse click was close to any of the colors
                    #Colors were drawn in order they're in in optionsIdxs
                    distance = sqrt(pow((x-mouseX),2)+pow((y-mouseY),2))
                    mouseToler = mouseChoiceArea + optionSet*mouseChoiceArea/6.#deg visual angle?  origin=2
                    #landmarkDebug.setPos([8,6]); landmarkDebug.draw()
                    if showClickedRegion:
                        clickedRegion.setPos([mouseX,mouseY])
                        clickedRegion.setRadius(mouseToler) 
                        clickedRegion.draw()
                    if showclickableRegions: #revealed in green every time you click
                        clickableRegion.setPos([x,y]) 
                        clickableRegion.setRadius(mouseToler) 
                        clickableRegion.draw()
                        #print('mouseXY=',round(mouseX,2),',',round(mouseY,2),'xy=',round(x,2),',',round(y,2), ' distance=',distance, ' mouseToler=',mouseToler)
                    if distance<mouseToler:
                        c = opts[optionSet][ncheck] #idx of color that this option num corresponds to
                        if respondedEachToken[optionSet][ncheck]:  #clicked one that already clicked on
                            if lastClickState ==0: #only count this event if is a distinct click from the one that selected the blob!
                                respondedEachToken[optionSet][ncheck] =0
                                responses[optionSet].remove(c) #this redundant list also of course encodes the order
                                respcount -= 1
                                print('removed number ',ncheck, ' from clicked list')
                        else:         #clicked on new one, need to add to response    
                            numRespsAlready = len(  np.where(respondedEachToken[optionSet])[0]  )
                            #print('numRespsAlready=',numRespsAlready,' numRespsNeeded= ',numRespsNeeded,'  responses=',responses)   #debugOFF
                            if numRespsAlready >= numRespsNeeded[optionSet]:
                                pass #not allowed to select this one until de-select other
                            else:
                                respondedEachToken[optionSet][ncheck] = 1 #register this one has been clicked
                                responses[optionSet].append(c) #this redundant list also of course encodes the order
                                respcount += 1  
                                print('added  ',ncheck,'th response to clicked list')
                #print 'response=', response, '  respcount=',respcount, ' lastClickState=',lastClickState, '  after affected by click'
           #end if mouse clicked
           
       for key in psychopy.event.getKeys():       #check if pressed abort-type key
              if key in ['escape']: # ['escape','q']:
                  expStop = True
                  respcount = 1
              
       lastClickState = mouse1
       if autopilot: 
            respcount = 1
            for i in range(numRings):
                for j in range(numObjects):
                    respondedEachToken[i][j] = 1 #must set to True for tracking task with click responses, because it uses to determine which one was clicked on
       if blindspotFill:
            blindspotStim.draw()

       myWin.flip(clearBuffer=True)  
       if screenshot and ~screenshotDone:
           myWin.getMovieFrame()       
           screenshotDone = True
           myWin.saveMovieFrames('respScreen.jpg')
       #end response collection loop for non-'track' task
    #if [] in responses: responses.remove([]) #this is for case of tracking with click response, when only want one response but draw both rings. One of responses to optionset will then be blank. Need to get rid of it
    return responses,responsesAutopilot,respondedEachToken, expStop
    ####### #End of function definition that collects responses!!!! #################################################
    
print('Starting experiment of',trials.nTotal,'trials. Current trial is trial 0.')
#print header for data file
print('trialnum\tsubject\tbasicShape\tnumObjects\tspeed\tinitialDirRing0', end='\t', file=dataFile)
print('orderCorrect\ttrialDurTotal\tnumTargets', end= '\t', file=dataFile) 
for i in range(numRings):
    print('whichIsTarget',i,  sep='', end='\t', file=dataFile)
print('ringToQuery',end='\t',file=dataFile)
for i in range(numRings):dataFile.write('Direction'+str(i)+'\t')
for i in range(numRings):dataFile.write('respAdj'+str(i)+'\t')
for r in range(numRings):
    for j in range(maxPossibleReversals()):
        dataFile.write('rev'+str(r)+'_'+str(j)+'\t')  #reversal times for each ring
print('timingBlips', file=dataFile)
#end of header
trialClock = core.Clock()
stimClock = core.Clock()
trialNum=0; numTrialsOrderCorrect=0; numAllCorrectlyIdentified=0; blueMistakes=0; expStop=False; framesSaved=0;
thisTrial = trials.next()
trialDurTotal=0;
ts = list();

if eyetracking:
    eyeMoveFile=('EyeTrack_'+subject+'_'+timeAndDateStr+'.EDF')
    tracker=Tracker_EyeLink(myWin,trialClock,subject,1, 'HV5',(255,255,255),(0,0,0),False,(widthPix,heightPix))

randomStartAngleEachRing = True
randomInitialDirExceptRing0 = True
oppositeInitialDirFirstTwoRings = True

while trialNum < trials.nTotal and expStop==False:
    accelerateComputer(1,process_priority, disable_gc) #speed up
    colorRings=list();preDrawStimToGreasePipeline = list()
    isReversed= list([1]) * numRings #always takes values of -1 or 1
    reversalNumEachRing = list([0]) * numRings
    if randomStartAngleEachRing:
        angleIniEachRing = list( np.random.uniform(0,2*pi,size=[numRings]) )
    else: 
        angleIniEachRing = [0]*numRings
    currAngle = list([0]) * numRings
    if randomInitialDirExceptRing0:
        initialDirectionEachRing = list( np.random.randint(0,1,size=[numRings]) *2 -1 ) #randomise initial direction of each ring
        initialDirectionEachRing[0] = thisTrial['initialDirRing0']
        if oppositeInitialDirFirstTwoRings and numRings>1:
            initialDirectionEachRing[1] = -1*initialDirectionEachRing[0]
    else:
        initialDirectionEachRing = [ thisTrial['initialDirRing0'] ] * numRings
    trackVariableIntervDur=np.random.uniform(0,trackVariableIntervMax) #random interval tacked onto tracking to make total duration variable so cant predict final position
    trialDurTotal = maxTrialDur() - trackVariableIntervDur
    trialDurFrames= int( trialDurTotal*refreshRate )
    print('trialDurTotal=',np.around(trialDurTotal,2),' trialDurFrames=',np.around(trialDurFrames,2), 'refreshRate=',np.around(refreshRate) ) 
    xyTargets = np.zeros( [thisTrial['numTargets'], 2] ) #need this for eventual case where targets can change what ring they are in
    numDistracters = numRings*thisTrial['numObjectsInRing'] - thisTrial['numTargets']
    xyDistracters = np.zeros( [numDistracters, 2] )

    reversalTimesEachRing = getReversalTimes()
    numObjects = thisTrial['numObjectsInRing']
    centerInMiddleOfSegment =360./numObjects/2.0
    blobsToPreCue=thisTrial['whichIsTarget']
    core.wait(.1)
    myMouse.setVisible(False)      
    if eyetracking: 
        tracker.startEyeTracking(trialNum,calibTrial=True,widthPix=widthPix,heightPix=heightPix) # tell eyetracker to start recording. Does this also somehow allow it to draw on the screen for the calibration?

    fixatnPeriodFrames = int(   (np.random.rand(1)/2.+0.8)   *refreshRate)  #random interval between x and x+800ms
    for i in range(fixatnPeriodFrames):
        if i%2:
            fixation.draw()
        else: fixationBlank.draw()
        myWin.flip() #clearBuffer=True)  
    trialClock.reset()
    t0=trialClock.getTime(); t=trialClock.getTime()-t0     
    for L in range(len(ts)):
        ts.remove(ts[0]) # clear ts array, to try to avoid memory problems?
    stimClock.reset()
    print('About to start trial and trialDurFrames =',round(trialDurFrames,1))
    
    #the loop for this trial's stimulus!
    for n in range(trialDurFrames): 
        offsetXYeachRing=[ [0,0],[0,0],[0,0] ]
        (angleIni,currAngle,isReversed,reversalNumEachRing) = \
                oneFrameOfStim(thisTrial,n,stimClock,useClock,offsetXYeachRing,initialDirectionEachRing,currAngle,blobsToPreCue,isReversed,reversalNumEachRing,ShowTrackCueFrames) #da big function

        if exportImages:
            myWin.getMovieFrame(buffer='back') #for later saving
            framesSaved +=1
        myWin.flip(clearBuffer=True)
        
        #time management
        t=trialClock.getTime()-t0;
        ts.append(t);
        if useClock: #Rather than necessarily showing every frame, allowing for skipped frames by showing frame that is correct for this time.
            #But that means that n may not reach trialDurFrames until after have reached end of trial, so need to quit rather than 
            #let the stimuli keep going around and around
            if t > trialDurTotal:
                msg="Must not have kept up with some frames, breaking out of loop"; print(msg)
                break
    #End of trial stimulus loop!
    
    if eyetracking:
        tracker.stopEyeTracking() #This seems to work immediately and cause the Eyelink machine to save the EDF file to its own drive
    #clear mouse buffer in preparation for response, which may involve clicks
    psychopy.event.clearEvents(eventType='mouse')

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
                msg= 'trialnum=' + str(trialNum) + ' ' + longFramesStr
                print(msg, file=logF)
                print(msg)
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
    ringQuerySoundFileNames = [ 'innerring.wav', 'middlering.wav', 'outerring.wav' ]
    soundDir = 'sounds'
    if numRings==3:
        soundFileNum = thisTrial['ringToQuery']
    else: #eg if numRings==2:
        soundFileNum = thisTrial['ringToQuery']*2 #outer, not middle for ring==1
        
    respSoundPathAndFile= os.path.join(soundDir, ringQuerySoundFileNames[ soundFileNum ])
    respSound = sound.Sound(respSoundPathAndFile, secs=.2)
    
    #corrSoundPathAndFile= os.path.join(soundDir, 'Ding.wav')
    #corrSound = sound.Sound(corrSoundPathAndFile, secs=.2)

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
        orderCorrect=0; numColorsCorrectlyIdentified=0; blueMistake=0;respAdj=list();sCorrect=list();targetCorrect=0;
        for l in range(numRings):
                    if responses[l] !=[]: 
                       tokenChosenEachRing[l]=np.where(respondedEachToken[l])  [0][0] 
                       respAdjs= initialDirectionEachRing[l]*isReversed[l]*(tokenChosenEachRing[l]-thisTrial['whichIsTarget'][l])
                       if respAdjs> numObjects/2. : respAdjs-= numObjects  #code in terms of closest way around. So if 9 objects and 8 ahead, code as -1
                       if respAdjs < -numObjects/2. : respAdjs += numObjects
                       respAdj.append(respAdjs)
                       if tokenChosenEachRing[l]==thisTrial['whichIsTarget'][l]: 
                          sCorrects=1
                          sCorrect.append(sCorrects);
                          targetCorrect+=sCorrects
                    else:
                       respAdj.append(-999)
                       sCorrect.append(0)
        if targetCorrect==1: orderCorrect = 3
        else: orderCorrect = 0
                 
        if respType=='order':  #: this used to work without last conditional
            numColorsCorrectlyIdentified=-1
        else: 
            numColorsCorrectlyIdentified = len(   intersect1d(response,answer)   )
            if numColorsCorrectlyIdentified < 3:
                if 4 in answer and not (3 in answer): #dark blue present
                    if 3 in response: #light blue in answer
                        blueMistake =1
                elif 3 in answer and not (4 in answer): #light blue present
                    if 4 in response: #dark blue in answer
                        blueMistake =1                
        #end if statement for if not expStop
    if passThisTrial:orderCorrect = -1    #indicate for data analysis that observer opted out of this trial, because think they moved their eyes

    #header print('trialnum\tsubject\tbasicShape\tnumObjects\tspeed\tinitialDirRing0\tangleIni
    print(trialNum,subject,thisTrial['basicShape'],thisTrial['numObjectsInRing'],thisTrial['speed'],thisTrial['initialDirRing0'],sep='\t', end='\t', file=dataFile)
    print(orderCorrect,'\t',trialDurTotal,'\t',thisTrial['numTargets'],'\t', end=' ', file=dataFile) #override newline end
    for i in range(numRings):  print( thisTrial['whichIsTarget'][i], end='\t', file=dataFile  )
    print( thisTrial['ringToQuery'],end='\t',file=dataFile )
    for i in range(numRings):dataFile.write(str(round(initialDirectionEachRing[i],4))+'\t') 
    for i in range(numRings):dataFile.write(str(round(respAdj[i],4))+'\t') 
    for k in range(numRings):
        for i in range(len(reversalTimesEachRing[k])):
            print(round(reversalTimesEachRing[k][i],4),'\t', end='', file=dataFile)
        for j in range(i+1,maxPossibleReversals()):
            print('-999\t', end='', file=dataFile)
    print(numCasesInterframeLong, file=dataFile)
    numTrialsOrderCorrect += (orderCorrect >0)  #so count -1 as 0
    numAllCorrectlyIdentified += (numColorsCorrectlyIdentified==3)
    speedIdx = np.where(uniqSpeeds==thisTrial['speed'])[0][0]  #extract index, where returns a list with first element array of the indexes
    numRightWrongEachSpeedOrder[ speedIdx, (orderCorrect >0) ] +=1  #if right, add to 1th column, otherwise add to 0th column count
    numRightWrongEachSpeedIdent[ speedIdx, (numColorsCorrectlyIdentified==3) ] +=1
    blueMistakes+=blueMistake
    dataFile.flush(); logF.flush(); 
    
    if feedback and not expStop:
        if orderCorrect==3  :correct=1
        else:correct=0
        if correct:
            #corrSound.play()
            hiA = sound.Sound('A',octave=4, sampleRate=6000, secs=.8)
            hiA.setVolume(0.9)
            hiA.play()
        else: #incorrect
            lowD = sound.Sound('E',octave=3, sampleRate=6000, secs=.8)
            lowD.setVolume(0.9)
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
           for key in psychopy.event.getKeys():       #check if pressed abort-type key
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
    
print('finishing at ',timeAndDateStr, file=logF)
print('%corr order report= ', round( numTrialsOrderCorrect*1.0/trialNum*100., 2)  , '% of ',trialNum,' trials', end=' ')
print('%corr each speed: ', end=' ')
print(np.around( numRightWrongEachSpeedOrder[:,1] / ( numRightWrongEachSpeedOrder[:,0] + numRightWrongEachSpeedOrder[:,1]), 2))
print('\t\t\t\tnum trials each speed =', numRightWrongEachSpeedOrder[:,0] + numRightWrongEachSpeedOrder[:,1])
logging.flush(); dataFile.close(); logF.close()

if eyetracking:
  if eyetrackFileGetFromEyelinkMachine:
    eyetrackerFileWaitingText = visual.TextStim(myWin,pos=(-.1,0),colorSpace='rgb',color = (1,1,1),anchorHoriz='center', anchorVert='center', units='norm',autoLog=autoLogging)
    eyetrackerFileWaitingText.setText('Waiting for eyetracking file from Eyelink computer. Do not abort eyetracking machine or file will not be saved?')
    eyetrackerFileWaitingText.draw()
    myWin.flip()
    msg = tracker.closeConnectionToEyeTracker(eyeMoveFile) #this requests the data back and thus can be very time-consuming, like 20 min or more
    print(msg); print(msg,file=logF) #""Eyelink connection closed successfully" or "Eyelink not available, not closed properly"
  else: 
    print('You will have to get the Eyelink EDF file off the eyetracking machine by hand')
    
if quitFinder: #turn Finder back on
        applescript="\'tell application \"Finder\" to launch\'" #turn Finder back on
        shellCmd = 'osascript -e '+applescript
        os.system(shellCmd)
core.quit()