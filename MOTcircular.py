from __future__ import print_function
__author__ = """Alex "O." Holcombe, Wei-Ying Chen""" ## double-quotes will be silently removed, single quotes will be left, eg, O'Connor
from psychopy import *
import psychopy.info
from psychopy import sound, monitors, logging
import numpy as np
import itertools #to calculate all subsets
from copy import deepcopy
from math import atan, pi, cos, sin, sqrt
import time, colorsys, sys, platform, os, StringIO, gc
#BEGIN helper functions from primes.py
def gcd(a,b): 
   """Return greatest common divisor using Euclid's Algorithm."""
   while b:      
        a, b = b, a % b
   return a
def lcm(a,b):
   """Return lowest common multiple."""
   return (a*b)/gcd(a,b)
def LCM(terms):
   "Return lcm of a list of numbers."   
   return reduce(lambda a,b: lcm(a,b), terms)
#END helper functions from primes.py
def calcCondsPerNumTargets(numRings,numTargets):
    #numRings is number of rings, each of which can have up to one target
    #numTargets is list or array of numTarget conditions, e.g. 1,2,3 means the experiment includes 1, 2, and 3 targets
    #Each target can be placed randomly in any of the rings.
    #Want all possibilities to be covered equally often. That means each target number condition has to include all the combinations
    #     of places that number of targets can go.
    #So that some targetNum conditinos don't have more trials than others, have to scale up each targetNum condition to the worst case.
    #Actually it's worse than that. To make them fit evenly, have to use least common multiple
    #3 rings choose 2 for targets, 3 rings choose 1 for target, have to have as many conditions as the maximum.
    #To find maximum, determine length of each.
    ringNums = np.arange(numRings)
    numPossibilitiesEach = list()
    for k in numTargets:
        numPossibilitiesCouldPutKtargets = len( list(itertools.combinations(ringNums,k)) )
        #print(numPossibilitiesCouldPutKtargets)
        numPossibilitiesEach.append(  numPossibilitiesCouldPutKtargets  )
    m = max( numPossibilitiesEach )  #because the worst case (number of targets) requires this many, have to have this many for all. Actually,
    leastCommonMultiple = LCM( numPossibilitiesEach )  #to have equal number of trials per numtargets, would have to use this figure for each
    #print('biggest=',m, ' Least common multiple=', leastCommonMultiple)
    return leastCommonMultiple

quitFinder = True
if quitFinder:
    applescript="\'tell application \"Finder\" to quit\'" #quit Finder.
    shellCmd = 'osascript -e '+applescript
    os.system(shellCmd)
process_priority = 'realtime' # 'normal' 'high' or 'realtime'
disable_gc = True
def acceleratePsychopy(slowFast):
    global process_priority, disable_gc
    if slowFast:
        if process_priority == 'normal':
            pass
        elif process_priority == 'high':
            core.rush(True)
        elif process_priority == 'realtime': # Only makes a diff compared to 'high' on Windows.
            core.rush(True, realtime = True)
        else:
            print('Invalid process priority:',process_priority,"Process running at normal.")
            process_priority = 'normal'
        if disable_gc:
            gc.disable()
    if slowFast==0: #turn off the speed-up
        if disable_gc:
            gc.enable()
        core.rush(False)

subject='test'#'test'
autoLogging = False
demo = False
autopilot=False
if autopilot:  subject='auto'
feedback=True
exportImages= False #quits after one trial / output image
slitView = False  #visual barrier
screenshot= False; screenshotDone = False;showRefreshMisses=False;allowGUI = False;waitBlank = False
trackAllIdenticalColors = True#with tracking, can either use same colors as other task (e.g. 6 blobs but only 3 colors so have to track one of 2) or set all blobs identical color
Reversal =True

timeAndDateStr = time.strftime("%d%b%Y_%H-%M", time.localtime()) 
respTypes=['order']; respType=respTypes[0]
bindRadiallyRingToIdentify=1 #0 is inner, 1 is outer
trackPostcueOrClick = 1 #postcue means say yes/no postcued was a target, click means click on which you think was/were the targets

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

RANum=8 #Number of reversal tims to log to datafile for each ring
numRings=1
radii=[6] #[2.5,8,12] #[4,8,12] 
offsets = np.array([[0,0],[-5,0],[-10,0]])

respRadius=radii[0] #deg
hz= 60.0 #120 *1.0;  #set to the framerate of the monitor
useClock = True
trialDur =1.9 #3 4.8;
if demo:trialDur = 5;hz = 60.; 
tokenChosenEachRing= [-999]*numRings
rampUpDur=.3; rampDownDur=.7; trackingExtraTime=.4; #giving the person time to attend to the cue (secs)
toTrackCueDur = rampUpDur+rampDownDur+trackingExtraTime
trialDurFrames=int(trialDur*hz)+int( trackingExtraTime*hz )
rampUpFrames = hz*rampUpDur;   rampDownFrames = hz*rampDownDur;  ShowTrackCueFrames = int( hz*toTrackCueDur )
rampDownStart = trialDurFrames-rampDownFrames
ballStdDev = 1.8
mouseChoiceArea = ballStdDev*0.8 # origin =1.3
units='deg' #'cm'
if showRefreshMisses:fixSize = 2.6  #make fixation bigger so flicker more conspicuous
else: fixSize = 0.3
timeTillReversalMin = 0.25; timeTillReversalMax = 1.0 #2.9

#start definition of colors 
hues=np.arange(16)/16.
saturatns = np.array( [1]*16 )
vals= np.array( [1]*16 )
colors=list()
for i in range(16):
  if i==5 or i==6 or i==7 or i==8 or i==10 or i==11 :continue
  else: colors.append( colorsys.hsv_to_rgb(hues[i],saturatns[i],vals[i]) ) #actually colorsys is really lame!
colors = np.array(colors)  

maxlum = np.array([30.,80.,20.]); #I dunno if these are correct, they were for an old monitor of mine
gamma=np.array([2.2,2.2,2.2]);
totLums = np.array(   [0.0]*len(colors) )  #calculate luminance of each color
lums = np.zeros((len(colors),3))
for c in range( len(colors) ):
    for guni in range(3):
        lums[c][guni] = maxlum[guni] *  pow( colors[c][guni], gamma[guni] )  
        totLums[c] +=  lums[c][guni] 
minLum = min(totLums)  #apparently this is the worst-case lum for the hues we started with
colorsRescaled = colors
for i in range( len(colors) ):
  scaleFactor = minLum / totLums[i]
  desiredLums = lums[i,:] *scaleFactor #this might be fine for when one gun is 0, it preserves pairwise ratios
  for guni in range(3):
    colorsRescaled[i,guni] = pow(  desiredLums[guni]/maxlum[guni] , 1./gamma[guni] )
colorNames=['red','yellow','green','cyan','blue','fuchsia']
colors_all2 = colorsRescaled
colors_all = colors_all2  *2-1
total_colors = 6; #6 #universe of colors that nb_colors color set for this display is drawn from
nb_colors = 3; #3 #number unique colors in display. Works except answer and options doesn't take it into account. Assumes this value is 3

#monitor parameters
fullscr=0; scrn=0
widthPix = 1024 #1440  #monitor width in pixels
heightPix =768  #900 #monitor height in pixels
monitorwidth = 38.5 #28.5 #monitor width in centimeters
viewdist = 57.; #cm
pixelperdegree = widthPix/ (atan(monitorwidth/viewdist) /np.pi*180)
bgColor = [-1,-1,-1] #black background
monitorname = 'mitsubishi' #in psychopy Monitors Center
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
myWin = visual.Window(monitor=mon,size=(widthPix,heightPix),allowGUI=allowGUI,units=units,color=bgColor,colorSpace='rgb',fullscr=fullscr,screen=scrn,waitBlanking=waitBlank) #Holcombe lab monitor
myWin.setRecordFrameIntervals(False)
myMouse = event.Mouse(visible = 'true',win=myWin)
gaussian = visual.PatchStim(myWin, tex='none',mask='gauss',colorSpace='rgb',size=ballStdDev,autoLog=autoLogging)
gaussian2 = visual.PatchStim(myWin, tex='none',mask='gauss',colorSpace='rgb',size=ballStdDev,autoLog=autoLogging)
optionChosenCircle = visual.Circle(myWin, radius=mouseChoiceArea, edges=32, fillColorSpace='rgb',fillColor = (1,0,1),autoLog=autoLogging) #to outline chosen options
clickableRegion = visual.Circle(myWin, radius=0.5, edges=32, fillColorSpace='rgb',fillColor = (-1,1,-1),autoLog=autoLogging) #to show clickable zones
circlePostCue = visual.Circle(myWin, radius=2*radii[0], edges=32, fillColorSpace='rgb',fillColor = (-.85,-.85,-.85),lineColor=(-1,-1,-1),autoLog=autoLogging) #visual postcue

blindspotFill = 0 #a way for people to know if they move their eyes
if blindspotFill:
    blindspotStim = visual.PatchStim(myWin, tex='none',mask='circle',size=4.8,colorSpace='rgb',color = (-1,1,-1),autoLog=autoLogging) #to outline chosen options
    blindspotStim.setPos([13.1,-2.7]) #AOH, size=4.8; pos=[13.1,-2.7] #DL: [13.3,-0.8]
fixation = visual.PatchStim(myWin,tex='none',colorSpace='rgb',color=(1,1,1),mask='circle',size=fixSize,autoLog=autoLogging)
fixationBlank= visual.PatchStim(myWin,tex='none',colorSpace='rgb',color=(-1,-1,-1),mask='circle',size=fixSize,autoLog=autoLogging)   
respText = visual.TextStim(myWin,pos=(0, -.8),colorSpace='rgb',color = (1,1,1),alignHoriz='center', alignVert='center', units='norm',autoLog=autoLogging)
NextText = visual.TextStim(myWin,pos=(0, 0),colorSpace='rgb',color = (1,1,1),alignHoriz='center', alignVert='center', units='norm',autoLog=autoLogging)
NextRemindText = visual.TextStim(myWin,pos=(.3, -.4),colorSpace='rgb',color = (1,1,1),alignHoriz='center', alignVert='center', units='norm',autoLog=autoLogging)
NextRemindCountText = visual.TextStim(myWin,pos=(-.1, -.4),colorSpace='rgb',color= (1,1,1),alignHoriz='center', alignVert='center', units='norm',autoLog=autoLogging)

#check screen refresh is what assuming it is, hz ########################################################################
Hzs=list()
myWin.setRecordFrameIntervals(True) #otherwise myWin.fps won't work
myWin.update(); myWin.update();myWin.update();myWin.update();
for i in range(50):
	myWin.update()
	Hzs.append( myWin.fps() )  #varies wildly on successive runs!
Hzs = np.array( Hzs );     Hz= np.median(Hzs)
msPerFrame= 1000./Hz
print('psychopy is reporting that frames per second are around = ', round(Hz,3),' and your drawing calculations are being done using the figure of ',hz, end=' ') 
NY='y'
if abs( (np.median(Hzs)-hz) / hz) > .05: 
	print(' which is off by more than 5%') 
	NY ='Y' # raw_input("Do you wish to continue nonetheless? ")
if NY.upper()<>'Y':
    core.quit()
    myWin.close()
# end testing of screen refresh########################################################################
if (not demo) and (myWin.size != [widthPix,heightPix]).any():
    myDlg = gui.Dlg(title="MOT experiment", pos=(200,400))
    msgWrongResolution = 'Screen NOT the desired resolution of '+ str(widthPix)+'x'+str(heightPix)+ ' pixels!!'
    myDlg.addText(msgWrongResolution, color='Red')
    logging.warning(msgWrongResolution)
    print(msgWrongResolution)
    myDlg.addText('Note: during the experiment, press ESC at response screen to quit', color='DimGrey')
    myDlg.show()
    core.quit()
longerThanRefreshTolerance = 0.2
longFrameLimit = round(1000./hz*(1.0+longerThanRefreshTolerance),3) # round(1000/hz*1.5,2)
print('longFrameLimit=',longFrameLimit,' Recording trials where one or more interframe interval exceeded this figure ', file=logF)
print('longFrameLimit=',longFrameLimit,' Recording trials where one or more interframe interval exceeded this figure ')

# mask setting..................
maskOrbitSize = 2*(radii[numRings-1] +ballStdDev)#perhaps draw a big rectangle with a custom transparency layer (mask) in the shape of a thick ring
maskSz=512
myMask = np.ones([maskSz,maskSz]) #let everything through
blockingWidth = int( (ballStdDev+radii[0])/maskOrbitSize * maskSz )
#show the center so can see fixation point
centralShowDiam = round( fixSize/maskOrbitSize * maskSz )
for w in range(  int(maskSz/2-centralShowDiam), int(maskSz/2+centralShowDiam)  ):
    for h in range(  int(maskSz/2-centralShowDiam), int(maskSz/2+centralShowDiam)  ):
        myMask[h,w] = -1 #show (don't block)
#show a horizontal strip
blockingHeight = int(              (ballStdDev/2)/maskOrbitSize *maskSz       )
stripTop = int( maskSz /2. - blockingHeight/2 )
stripBtm = stripTop + blockingHeight
horizCoords = range( 0, blockingWidth )  #left side of rings
horizCoords = horizCoords + range(maskSz-1, maskSz-blockingWidth-1, -1) #right side of rings (to make it easier to fixate on center)
for w in horizCoords:
    for h in range( stripTop, stripBtm, 1):
        myMask[h,w] = -1 #show (don't block)
maskOrbit = visual.PatchStim(myWin,tex='none',colorSpace='rgb',color=(1,1,0),mask=myMask,size=maskOrbitSize,autoLog=autoLogging)  #depth=  , negative depth is closer
#end slit computation

stimList = []
# temporalfrequency limit test
numObjsInRing = [2]
speedsEachNumObjs = [ [1.5, 1.65, 1.8, 2.0],     #these correspond to the speeds to use for each entry of numObjsInRing
                                         [1.5, 1.65, 1.8, 2.0], 
                                         [1.5, 1.65, 1.8, 2.0]   ]
numTargets = np.array([1])  # np.array([1,2,3])
leastCommonMultipleSubsets = calcCondsPerNumTargets(numRings,numTargets)
leastCommonMultipleTargetNums = LCM( numTargets )  #have to use this to choose whichToQuery. For explanation see newTrajectoryEventuallyForIdentityTracking.oo3
print('leastCommonMultipleSubsets=',leastCommonMultipleSubsets)
                
for numObjs in numObjsInRing: #set up experiment design
    idx = numObjsInRing.index(numObjs)
    speeds= speedsEachNumObjs[  idx   ]
    for speed in speeds:
        ringNums = np.arange(numRings)
        for nt in numTargets: #  3 choose 2, 3 choose 1, have to have as many conditions as the maximum
          subsetsThis = list(itertools.combinations(ringNums,nt)) #all subsets of length nt from the universe of ringNums
          numSubsetsThis = len( subsetsThis );   print('numSubsetsThis=',numSubsetsThis)
          repsNeeded = leastCommonMultipleSubsets / numSubsetsThis #that's the number of repetitions needed to make up for number of subsets of rings
          for r in xrange(repsNeeded):  #for nt with largest number of subsets, need no repetitions
                  for s in subsetsThis:
                      whichIsTarget = np.ones(numRings)*-999 #-999 is  value meaning no target in that ring. 1 will mean target in ring
                      for ring in s:
                         whichIsTarget[ring] = np.random.random_integers(0, numObjs-1, size=1) #1
                      print('numTargets=',nt,' whichIsTarget=',whichIsTarget,' and that is one of ',numSubsetsThis,' possibilities and we are doing ',repsNeeded,'repetitions')
                      for whichToQuery in xrange( leastCommonMultipleTargetNums ):  #for each subset, have to query one. This is dealed out to  the current subset by using modulus. It's assumed that this will result in equal total number of queried rings
                              whichSubsetEntry = whichToQuery % nt  #e.g. if nt=2 and whichToQuery can be 0,1,or2 then modulus result is 0,1,0. This implies that whichToQuery won't be totally counterbalanced with which subset, which is bad because
                                              #might give more resources to one that's queried more often. Therefore for whichToQuery need to use least common multiple.
                              ringToQuery = s[whichSubsetEntry];  print('ringToQuery=',ringToQuery,'subset=',s)
                              for condition in [0,1,2]: #centered, slightly off-center, or fully off-center
                               for leftOrRight in [0,1]:
                                  offsetXYeachRing = np.array([ offsets[condition] ]) #because other experiments involve multiple rings, it's a 2-d array
                                  if condition >0:
                                         if leftOrRight: #flip to right
                                            offsetXYeachRing *= -1
                                  offsetXYeachRing = list(offsetXYeachRing) #so that when print, prints on one line
                                  for direction in [-1.0,1.0]:  
                                        stimList.append( {'numObjectsInRing':numObjs,'speed':speed, 'direction':direction,'slitView':slitView,'numTargets':nt,'whichIsTarget':whichIsTarget,
                                          'ringToQuery':ringToQuery,'condition':condition,'leftOrRight':leftOrRight,'offsetXYeachRing':offsetXYeachRing} )
#set up record of proportion correct in various conditions
trialSpeeds = list() #purely to allow report at end of how many trials got right at each speed
for s in stimList: trialSpeeds.append( s['speed'] )
uniqSpeeds = set(trialSpeeds) #reduce speedsUsed list to unique members, unordered set
uniqSpeeds = sorted( list(uniqSpeeds)  )
uniqSpeeds = np.array( uniqSpeeds ) 
numRightWrongEachSpeedOrder = np.zeros([ len(uniqSpeeds), 2 ]); #summary results to print out at end
numRightWrongEachSpeedIdent = deepcopy(numRightWrongEachSpeedOrder)
#end setup of record of proportion correct in various conditions

blockReps=1 #5
trials = data.TrialHandler(stimList,blockReps) #constant stimuli method
refreshTimingCheck = None #'grating'
try:
    runInfo = psychopy.info.RunTimeInfo(
            win=myWin,    ## a psychopy.visual.Window() instance; None = default temp window used; False = no win, no win.flips()
            refreshTest=refreshTimingCheck, ## None, True, or 'grating' (eye-candy to avoid a blank screen)
            verbose=True, ## True means report on everything 
            userProcsDetailed=True,  ## if verbose and userProcsDetailed, return (command, process-ID) of the user's processes
            )
    logging.info(runInfo)
except Exception,e: print(str(e)) #print error

timeAndDateStr = time.strftime("%d%b%Y_%H-%M", time.localtime()) 
logging.info(  str('starting exp with name: "'+'TemporalFrequencyLimit'+'" at '+timeAndDateStr)   )
logF = StringIO.StringIO()  #kludge so I dont have to change all the print >>logF statements
logging.info(    'numtrials='+ str(trials.nTotal)+' and each trialDur='+str(trialDur)+' hz='+str(hz)      )

print(' numtrials=', trials.nTotal)
print('rampUpDur=',rampUpDur, ' rampDownDur=', rampDownDur, ' secs', file=logF);  logging.info( logF.getvalue() ); logF = StringIO.StringIO() 
logging.info('task='+'track'+'   respType='+respType)
logging.info( 'colors_all='+str(colors_all)+ '\ncolorNames='+str(colorNames)+ '  trackPostcueOrClick='+str(trackPostcueOrClick)+'  trackAllIdenticalColors='+str(trackAllIdenticalColors) )
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
def radiusThisFrameThisAngle(numRing, angle, thisFrameN):
    r = radii[numRing]
    timeSeconds = thisFrameN / hz
    period = 0.5 #seconds
    phaseRadians = timeSeconds/period * 2*pi + ampModulatnEachRingTemporalPhase[numRing]
    rThis =  r + sin(phaseRadians) * r * ampTemporalRadiusModulation
    rThis += r * RFcontourAmp * RFcontourCalcModulation(angle,RFcontourFreq,RFcontourPhase)
    return rThis
    
def angleChangeThisFrame(thisTrial, moveDirection, numRing, thisFrameN, lastFrameN):
    anglemove = moveDirection[numRing]*thisTrial['direction']*thisTrial['speed']*2*pi*(thisFrameN-lastFrameN)/hz
    return anglemove

def  oneFrameOfStim(currFrame,clock,useClock,offsetXYeachRing,currAngle,blobToCueEachRing,isReversed,reversalNo,ShowTrackCueFrames): 
#defining a function to draw each frame of stim. So can call second time for tracking task response phase
          global cueRing,ringRadial,ringRadialR, currentlyCuedBlob #makes python treat it as a local variable
          global angleIni, correctAnswers
          if useClock: #Don't count on not missing frames. Use actual time.
            t = clock.getTime()
            n = round(t*hz)
          else:
            n = currFrame
          
          if n<rampUpFrames:
                contrast = cos( -pi+ pi* n/rampUpFrames  ) /2. +.5 #starting from -pi trough of cos, and scale into 0->1 range
          elif n> rampDownStart:
                contrast = cos(pi* (n-rampDownStart)/rampDownFrames ) /2.+.5 #starting from peak of cos, and scale into 0->1 range
          else: contrast = 1
          contrast = 1
          fixation.draw()
          if n%2>=1: fixation.draw()#flicker fixation on and off at framerate to see when skip frame
          else:fixationBlank.draw()         
    
          for noRing in range(numRings):
            for nobject in range(numObjects):
                nColor =nobject % nb_colors
                angleMove = angleChangeThisFrame(thisTrial, moveDirection, noRing, n, n-1)
                if nobject==0:
                    if Reversal:
                        if reversalNo[noRing] <= len(RAI[noRing]):   #When reversals times assigned, e.g. RAI. They are accumulated WHILE thisReversalDur<trialDurTotal:  line 558
                            if n > hz * RAI[noRing][ int(reversalNo[noRing]) ]:
                                isReversed[noRing] = -1*isReversed[noRing]
                                reversalNo[noRing] +=1
                    currAngle[noRing]=currAngle[noRing]+angleMove*(isReversed[noRing])
                angleObject0 = angleIni[noRing] + currAngle[noRing]
                angleThisObject = angleObject0 + (2*pi)/numObjects*nobject
                r = radiusThisFrameThisAngle(noRing,angleThisObject,n)
                x = offsetXYeachRing[noRing][0] + r*cos(angleThisObject)
                y = offsetXYeachRing[noRing][1] + r*sin(angleThisObject)
                if   n< ShowTrackCueFrames and nobject==blobToCueEachRing[noRing]: #cue in white  
                    weightToTrueColor = n*1.0/ShowTrackCueFrames #compute weighted average to ramp from white to correct color
                    blobColor = (1-weightToTrueColor)*np.array([1,1,1])  +  weightToTrueColor*colorsInInnerRingOrder[nColor] 
                    blobColor = blobColor*contrast #also might want to change contrast, if everybody's contrast changing in contrast ramp
                else: blobColor = colorsInInnerRingOrder[nColor]*contrast    
                gaussian.setColor( blobColor, log=autoLogging )
                gaussian.setPos([x,y])
                gaussian.draw()
          if blindspotFill:
              blindspotStim.draw()
          if thisTrial['slitView']: maskOrbit.draw()
          return angleIni,currAngle,isReversed,reversalNo   
# #######End of function definition that displays the stimuli!!!! #####################################

showClickableRegions = True
def  collectResponses(n,responses,responsesAutopilot,offsetXYeachRing,respRadius,currAngle,expStop ):
    optionSets=numRings;    
    
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
    for ring in xrange(numRings):
        optionIdexs.append([])
        noArray=list()
        for k in range(numObjects):noArray.append(colors_ind[0])
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
            responsesAutopilot.append( [0]*numRespsNeeded[ring] )  #autopilot response is 0
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
                        angle =  (angleIni[optionSet]+currAngle[optionSet]) + ncheck*1.0/numOptionsEachSet[optionSet] *2.*pi
                        stretchOutwardRingsFactor = 1
                        r = radiusThisFrameThisAngle(optionSet,angle,n)
                        x = offsetXYeachRing[optionSet][0]+r*cos(angle);  
                        y = offsetXYeachRing[optionSet][1]+r*sin(angle)
                        #draw colors, and circles around selected items. Colors are drawn in order they're in in optionsIdxs
                        opts=optionIdexs;
                        c = opts[optionSet][ncheck] #idx of color that this option num corresponds to. Need an extra [0] b/c list of arrays
                        if respondedEachToken[optionSet][ncheck]:  #draw circle around this one to indicate this option has been chosen
                               optionChosenCircle.setColor(array([1,-1,1]), log=autoLogging)
                               optionChosenCircle.setPos([x,y])
                               optionChosenCircle.draw()                
                        #gaussian.setRGB( colors_all[c] )  #draw blob
                        gaussian.setColor(  colors_all[0], log=autoLogging )  #draw blob
                        gaussian.setPos([x,y]);  
                        gaussian.draw()
                         
               mouse1, mouse2, mouse3 = myMouse.getPressed()
               if mouse1 and lastClickState==0:  #only count this event if is a new click. Problem is that mouse clicks continue to be pressed for along time
                    mouseX,mouseY = myMouse.getPos()
                    #print 'assumes window spans entire screen of ',monitorwidth,' cm; mouse position apparently in cm when units is set to deg = (',mouseX,',',mouseY,')'  
                    #because mouse apparently giving coordinates in cm, I need to convert it to degrees of visual angle because that's what drawing is done in terms of
                    cmperpixel = monitorwidth*1.0/widthPix
                    degpercm = 1.0/cmperpixel/pixelperdegree;  
                    mouseX = mouseX # * degpercm #mouse x location relative to center, converted to degrees
                    mouseY = mouseY #* degpercm #mouse x location relative to center, converted to degrees
                    for optionSet in range(optionSets):
                      for ncheck in range( numOptionsEachSet[optionSet] ): 
                            angle =  (angleIni[optionSet]+currAngle[optionSet]) + ncheck*1.0/numOptionsEachSet[optionSet] *2.*pi #radians
                            r = radiusThisFrameThisAngle(optionSet,angle,n)
                            x = offsetXYeachRing[optionSet][0]+r*cos(angle)
                            y = offsetXYeachRing[optionSet][1]+r*sin(angle)
                            #check whether mouse click was close to any of the colors
                            #Colors were drawn in order they're in in optionsIdxs
                            distance = sqrt(pow((x-mouseX),2)+pow((y-mouseY),2))
                            mouseToler = mouseChoiceArea + optionSet*mouseChoiceArea/6.#deg visual angle?  origin=2
                            if showClickableRegions: #revealed in green every time you click
                                clickableRegion.setPos([x,y])
                                clickableRegion.setRadius(mouseToler)
                                clickableRegion.draw()
                                #print('mouseXY=',round(mouseX,2),',',round(mouseY,2),'xy=',x,',',y, ' distance=',distance, ' mouseToler=',mouseToler)
                            if distance<mouseToler:
                                c = opts[optionSet][ncheck] #idx of color that this option num corresponds to
                                if respondedEachToken[optionSet][ncheck]:  #clicked one that already clicked on
                                    if lastClickState ==0: #only count this event if is a distinct click from the one that selected the blob!
                                        respondedEachToken[optionSet][ncheck] =0
                                        responses[optionSet].remove(c) #this redundant list also of course encodes the order
                                        respcount -= 1
                                        #print('removed number ',ncheck, ' from clicked list')
                                else:         #clicked on new one, need to add to response    
                                    numRespsAlready = len(  np.where(respondedEachToken[optionSet])[0]  )
                                    #print('numRespsAlready=',numRespsAlready,' numRespsNeeded= ',numRespsNeeded,'  responses=',responses)   #debugOFF
                                    if numRespsAlready >= numRespsNeeded[optionSet]:
                                        pass #not allowed to select this one until de-select other
                                    else:
                                        respondedEachToken[optionSet][ncheck] = 1 #register this one has been clicked
                                        responses[optionSet].append(c) #this redundant list also of course encodes the order
                                        respcount += 1  
                                        #print('added  ',ncheck,'th response to clicked list')
                        #print 'response=', response, '  respcount=',respcount, ' lastClickState=',lastClickState, '  after affected by click'
                   #end if mouse clicked
                   
               for key in event.getKeys():       #check if pressed abort-type key
                      if key in ['escape','q']:
                          expStop = True
                          respcount = nb_colors
                      
               lastClickState = mouse1
               if autopilot: 
                    respcount = nb_colors
                    for i in xrange(numRings):
                        for j in xrange(numObjects):
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
print('trialnum\tsubject\tnumObjects\tspeed\tdirection\tcondition\leftOrRight\toffsetXYeachRing\tangleIni', end='\t', file=dataFile)
print('orderCorrect\ttrialDurTotal\tnumTargets', end= '\t', file=dataFile) 
for i in range(numRings):
    print('whichIsTarget',i,     sep='', end='\t', file=dataFile)
print('ringToQuery',end='\t',file=dataFile)
for i in range(numRings):dataFile.write('Direction'+str(i)+'\t')
for i in range(numRings):dataFile.write('respAdj'+str(i)+'\t')
for i in range(numRings):
    for j in range(RANum):dataFile.write('RAV'+str(i)+'_'+str(j)+'\t')  #reversal times for each ring
print('timingBlips', file=dataFile)
#end of header
trialClock = core.Clock()
stimClock = core.Clock()
nDone=0; numTrialsOrderCorrect=0; numAllCorrectlyIdentified=0; blueMistakes=0; expStop=False; framesSaved=0;
thisTrial = trials.next()
trialDurTotal=0;
ts = list();
while nDone <= trials.nTotal and expStop==False:
    acceleratePsychopy(slowFast=1)
    angleIni=list();currAngle=list();moveDirection=list();RAI=list();isReversed=list();reversalNo=list();colors_ind=list();colorRings=list();preDrawStimToGreasePipeline = list()
    trackingVariableInterval=np.random.uniform(0,.8) #random interval taked onto tracking to make total duration variable so cant predict final position
    trialDurFrames= int( (trialDur+trackingExtraTime+trackingVariableInterval)*hz )
    trialDurTotal=trialDur+trackingExtraTime+trackingVariableInterval;
    xyTargets = np.zeros( [thisTrial['numTargets'], 2] ) #need this for eventual case where targets can change what ring they are in
    numDistracters = numRings*thisTrial['numObjectsInRing'] - thisTrial['numTargets']
    xyDistracters = np.zeros( [numDistracters, 2] )
    for ringNum in range(numRings): # initialise  parameters
         angleIni.append(np.random.uniform(0,2*pi)) #radians
         currAngle.append(0);
         moveDirection.append(-999);
         RAI.append(list());
         isReversed.append(1)
         reversalNo.append(0)
         moveDirection[ringNum] = np.random.random_integers(0,1) *2 -1 #randomise initial direction
         if ringNum==0: #set up disc colors, vestige of Current Biology paper
            colors_ind.append([0,0,0,0])
            #colors_ind.append(np.random.permutation(total_colors)[0:nb_colors]) #random subset of colors in random order
            colorRings.append(colors_all[colors_ind[ringNum]])
         else: 
            '''colors_indnext= setdiff1d(xrange(total_colors), colors_ind[Ini-1])
            np.random.shuffle(colors_indnext)
            colors_ind.append(colors_indnext)'''
            colors_ind.append([0,0,0,0])
            colorRings.append(colors_all[colors_ind[ringNum]])
    colorsInInnerRingOrder=colorsInOuterRingOrder=colors_all[[0, 0, 0]]
    stimColorIdxsOrder=[[0,0],[0,0],[0,0]]#this is used for drawing blobs during stimulus
    for r in range(numRings): # set random reversal times
        thisReversalDur = trackingExtraTime
        while thisReversalDur< trialDurTotal+.1:  #Creating 100ms more than need, in theory. Because if miss frames and using clock time instead of frames, might go longer
            thisReversalDur += np.random.uniform(timeTillReversalMin,timeTillReversalMax)
            RAI[r].append(thisReversalDur)
 
    numObjects = thisTrial['numObjectsInRing']
    centerInMiddleOfSegment =360./numObjects/2.0
    blobsToPreCue=thisTrial['whichIsTarget']
    core.wait(.1)
    myMouse.setVisible(False)      
    fixatnPeriodFrames = int(   (np.random.rand(1)/2.+0.8)   *hz)  #random interval between 800ms and 1.3s (changed when Fahed ran outer ring ident)
    for i in range(fixatnPeriodFrames):
        if thisTrial['slitView']: maskOrbit.draw()  
        fixation.draw(); myWin.flip(clearBuffer=True)  
    trialClock.reset()
    for i in range(20):
        if thisTrial['slitView']: maskOrbit.draw()  
        fixation.draw(); myWin.flip(clearBuffer=True)  
    t0=trialClock.getTime(); t=trialClock.getTime()-t0     
    for L in range(len(ts)):ts.remove(ts[0]) # clear all ts array
    stimClock.reset()
    for n in range(trialDurFrames): #this is the loop for this trial's stimulus!
            (angleIni,currAngle,isReversed,reversalNo) = \
                            oneFrameOfStim(n,stimClock,useClock,thisTrial['offsetXYeachRing'],currAngle,blobsToPreCue,isReversed,reversalNo,ShowTrackCueFrames) #da big function
            if exportImages:
                myWin.getMovieFrame(buffer='back') #for later saving
                framesSaved +=1
            myWin.flip(clearBuffer=True)
            t=trialClock.getTime()-t0; ts.append(t);
            if n==trialDurFrames-1: event.clearEvents(eventType='mouse');
    #end of big stimulus loop
    acceleratePsychopy(slowFast=0)
    #check for timing problems
    interframeIntervs = np.diff(ts)*1000 #difference in time between successive frames, in ms
    #print >>logF, 'trialnum=',nDone, '   interframe intervs were ',around(interframeIntervs,1)
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
                print('trialnum=',nDone,'  ',longFramesStr)
                print('trialnum=',nDone,'  ',longFramesStr, file=logF)
                if not demo:
                    flankingAlso=list()
                    for idx in idxsInterframeLong: #also print timing of one before and one after long frame
                        if idx-1>=0:  flankingAlso.append(idx-1)
                        else: flankingAlso.append(NaN)
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
    soundPathAndFile= os.path.join(soundDir, ringQuerySoundFileNames[ thisTrial['ringToQuery'] ])
    respSound = sound.Sound(soundPathAndFile, secs=.2)
    postCueNumBlobsAway=-999 #doesn't apply to click tracking and non-tracking task
     # ####### response set up answer
    responses = list();  responsesAutopilot = list()
    responses,responsesAutopilot,respondedEachToken,expStop = \
            collectResponses(n,responses,responsesAutopilot,thisTrial['offsetXYeachRing'],respRadius,currAngle,expStop)  #collect responses!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!#####
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
                       respAdjs= thisTrial['direction']*moveDirection[l]*isReversed[l]*(tokenChosenEachRing[l]-thisTrial['whichIsTarget'][l])
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

    #header trialnum\tsubject\tnumObjects\tspeed\tdirection\tcondition\leftOrRight\toffsetXYeachRing\tangleIni
    print(nDone,subject,thisTrial['numObjectsInRing'],thisTrial['speed'],thisTrial['direction'],sep='\t', end='\t', file=dataFile)
    print(thisTrial['condition'],thisTrial['leftOrRight'],thisTrial['offsetXYeachRing'],angleIni,sep='\t',end='\t',file=dataFile)
    print(orderCorrect,'\t',trialDurTotal,'\t',thisTrial['numTargets'],'\t', end=' ', file=dataFile) #override newline end
    for i in range(numRings):  print( thisTrial['whichIsTarget'][i], end='\t', file=dataFile  )
    print( thisTrial['ringToQuery'],end='\t',file=dataFile )
    for i in range(numRings):dataFile.write(str(round(moveDirection[i],4))+'\t') 
    for i in range(numRings):dataFile.write(str(round(respAdj[i],4))+'\t') 
    for k in range(numRings):
        for i in range(len(RAI[k])):dataFile.write(str(round(RAI[k][i],4))+'\t') 
        if int(len(RAI[k]))<int(RANum+1):
            for j in range(RANum-len(RAI[k])):dataFile.write('-999\t') 
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
            highA = sound.Sound('G',octave=5, sampleRate=6000, secs=.8, bits=8)
            highA.setVolume(0.8)
            highA.play()
        else: #incorrect
            lowD = sound.Sound('E',octave=3, sampleRate=6000, secs=.8, bits=8)
            lowD.setVolume(0.8)
            lowD.play()
    nDone+=1
    waitForKeyPressBetweenTrials = False
    if nDone< trials.nTotal:
        if nDone%( max(trials.nTotal/4,1) ) ==0:  #have to enforce at least 1, otherwise will modulus by 0 when #trials is less than 4
            NextRemindCountText.setText(  round(    (1.0*nDone) / (1.0*trials.nTotal)*100,2    )    )
            NextRemindText.setText('% complete')
            NextRemindCountText.draw()
            NextRemindText.draw()
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
    if thisTrial['slitView']:  #need to give preview so sudden appearance doesn't evoke saccade
        maskOrbit.draw()  
    core.wait(.1); time.sleep(.1)
    #end trials loop  ###########################################################
if expStop == True:
    print('user aborted experiment on keypress with trials nDone=', nDone, file=logF)
    print('user aborted experiment on keypress with trials nDone=', nDone)
print('finishing at ',timeAndDateStr, file=logF)
print('%corr order report= ', round( numTrialsOrderCorrect*1.0/nDone*100., 2)  , '% of ',nDone,' trials', end=' ')
print('%corr each speed: ', end=' ')
print(np.around( numRightWrongEachSpeedOrder[:,1] / ( numRightWrongEachSpeedOrder[:,0] + numRightWrongEachSpeedOrder[:,1]), 2))
print('\t\t\t\tnum trials each speed =', numRightWrongEachSpeedOrder[:,0] + numRightWrongEachSpeedOrder[:,1])
logging.flush(); dataFile.close(); logF.close()
if quitFinder:
        applescript="\'tell application \"Finder\" to launch\'" #turn Finder back on
        shellCmd = 'osascript -e '+applescript
        os.system(shellCmd)
core.quit()