from __future__ import print_function
__author__ = """Alex "O." Holcombe""" ## double-quotes will be silently removed, single quotes will be left, eg, O'Connor
import numpy as np
import itertools #to calculate all subsets
from copy import deepcopy
from math import atan, pi, cos, sin, sqrt, ceil
import time, sys, platform, os, StringIO, gc
from psychopy import visual, core

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

def accelerateComputer(slowFast, process_priority, disable_gc):
	# process_priority =  'normal' 'high' or 'realtime'
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

def openMyStimWindow(monitorSpec,widthPix,heightPix,bgColor,allowGUI,units,fullscr,scrn,waitBlank): #make it a function because have to do it several times, want to be sure is identical each time
    myWin = visual.Window(monitor=monitorSpec,size=(widthPix,heightPix),allowGUI=allowGUI,units=units,color=bgColor,colorSpace='rgb',fullscr=fullscr,screen=scrn,waitBlanking=waitBlank) #Holcombe lab monitor
    if myWin is None:
        print('ERROR: Failed to open window in openMyStimWindow!')
        core.quit()
    return myWin

def constructRingsAsGratings(numObjects,patchAngle,colors,stimColorIdxsOrder,gratingTexPix,blobToCue,ppLog):
    #Originally to construct a grating formed of the colors in order of stimColorIdxsOrder
    texEachRing=list() #texture which will draw the ring of objects via openGL texture on grating
    cueTexEachRing=list() #making a separate grating for the cue, wherein everything background color except the location of the cue
    ringsRadial=list(); #after making the rings of object, put them in this list
    cueRings=list() #after making grating for each cue, put it in this cue 
    stimColorIdxsOrder= stimColorIdxsOrder[::-1]  #reverse order of indices, because grating texture is rendered in reverse order than is blobs version
    radialMaskEachRing=[[0,0,0,1,1,] ,[0,0,0,0,0,0,1,1,],[0,0,0,0,0,0,0,0,0,0,1,1,]]
    numUniquePatches= len( max(stimColorIdxsOrder,key=len) )
    numCycles =(1.0*numObjects) / numUniquePatches
    angleSegment = 360./(numUniquePatches*numCycles)
    if gratingTexPix % numUniquePatches >0: #gratingTexPix contains numUniquePatches. numCycles will control how many total objects there are around circle
        ppLog.warn('Warning: could not exactly render a '+str(numUniquePatches)+'-segment pattern radially, will be off by '+str( (gratingTexPix%numUniquePatches)*1.0 /gratingTexPix ) )
    if numObjects % numUniquePatches >0:
        msg= 'Warning: numUniquePatches ('+str(numUniquePatches)+') not go evenly into numObjects'; ppLog.warn(msg)
    #create texture for red-green-blue-red-green-blue etc. radial grating
    for i in range(numRings):
        #myTex.append(np.zeros([gratingTexPix,gratingTexPix,3])+[1,-1,1])
        texEachRing.append( np.zeros([gratingTexPix,gratingTexPix,3])+bgColor[0] ) #start with all channels in all locs = bgColor
        cueTexEachRing.append( np.ones([gratingTexPix,gratingTexPix,3])*bgColor[0]  )
    if patchAngle > angleSegment:
        msg='Error: patchAngle requested ('+str(patchAngle)+') bigger than maximum possible ('+str(angleSegment)+') numUniquePatches='+str(numUniquePatches)+' numCycles='+str(numCycles); 
        print(msg); ppLog.error(msg)
  
    oneCycleAngle = 360./numCycles
    segmentSizeTexture = angleSegment/oneCycleAngle *gratingTexPix #I call it segment because includes spaces in between, that I'll write over subsequently
    patchSizeTexture = patchAngle/oneCycleAngle *gratingTexPix
    patchSizeTexture = round(patchSizeTexture) #best is odd number, even space on either size
    patchFlankSize = (segmentSizeTexture-patchSizeTexture)/2.
    patchAngleActual = patchSizeTexture / gratingTexPix * oneCycleAngle
    if abs(patchAngleActual - patchAngle) > .04:
        msg = 'Desired patchAngle = '+str(patchAngle)+' but closest can get with '+str(gratingTexPix)+' gratingTexPix is '+str(patchAngleActual); 
        ppLog.warn(msg)
    
    for colrI in range(numUniquePatches): #for that portion of texture, set color
        start = colrI*segmentSizeTexture
        end = start + segmentSizeTexture
        start = round(start) #don't round until after do addition, otherwise can fall short
        end = round(end)
        nColor = colrI #mimics code in drawoneframe
        ringColr=list();
        for i in range(numRings):
            ringColr.append(colors[ stimColorIdxsOrder[i][nColor] ])
        for colorChannel in range(3):
            for i in range(numRings):
                texEachRing[i][:, start:end, colorChannel] = ringColr[i][colorChannel]; 
            for cycle in range(int(round(numCycles))):
              base = cycle*gratingTexPix/numCycles
              for i in range(numRings):
                cueTexEachRing[i][:, base+start/numCycles:base+end/numCycles, colorChannel] = ringColr[1][colorChannel]
        #draw bgColor area (emptySizeEitherSideOfPatch) by overwriting first and last entries of segment 
        for i in range(numRings):
            texEachRing[i][:, start:start+patchFlankSize, :] = bgColor[0]; #one flank
            texEachRing[i][:, end-1-patchFlankSize:end, :] = bgColor[0]; #other flank
        
        for cycle in range(int(round(numCycles))): 
              base = cycle*gratingTexPix/numCycles
              for i in range(numRings):
                 cueTexEachRing[i][:,base+start/numCycles:base+(start+patchFlankSize)/numCycles,:] =bgColor[0]; 
                 cueTexEachRing[i][:,base+(end-1-patchFlankSize)/numCycles:base+end/numCycles,:] =bgColor[0]
        
    #color the segment to be cued white. First, figure out cue segment len
    segmentLen = gratingTexPix/numCycles*1/numUniquePatches
    WhiteCueSizeAdj=0 # adust the white cue marker wingAdd 20110923
    if thisTrial['numObjectsInRing']==3:WhiteCueSizeAdj=110
    elif thisTrial['numObjectsInRing']==6:WhiteCueSizeAdj=25
    elif thisTrial['numObjectsInRing']==12:WhiteCueSizeAdj=-15
    elif thisTrial['numObjectsInRing']==2:WhiteCueSizeAdj=200
    
    for i in range(numRings): #color cue position white
            if blobToCue[i] >=0: #-999 means dont cue anything
                blobToCueCorrectForRingReversal = numObjects-1 - blobToCue[i] #grating seems to be laid out in opposite direction than blobs, this fixes postCueNumBlobsAway so positive is in direction of motion
                if blobToCueCorrectForRingReversal==0 and thisTrial['numObjectsInRing']==12:   WhiteCueSizeAdj=0
                cueStartEntry = blobToCueCorrectForRingReversal*segmentLen+WhiteCueSizeAdj
                cueEndEntry = cueStartEntry + segmentLen-2*WhiteCueSizeAdj
                cueTexEachRing[i][:, cueStartEntry:cueEndEntry, :] = -1*bgColor[0]   #-1*bgColor is that what makes it white?
                blackGrains = round( .25*(cueEndEntry-cueStartEntry) )#number of "pixels" of texture at either end of cue sector to make black. Need to update this to reflect patchAngle
                cueTexEachRing[i][:, cueStartEntry:cueStartEntry+blackGrains, :] = bgColor[0];  #this one doesn't seem to do anything?
                cueTexEachRing[i][:, cueEndEntry-1-blackGrains:cueEndEntry, :] = bgColor[0];
    angRes = 100 #100 is default. I have not seen any effect. This is currently not printed to log file!
    
    for i in range(numRings):
         ringsRadial.append(visual.RadialStim(myWin, tex=texEachRing[i], color=[1,1,1],size=radii[i],#myTexInner is the actual colored pattern. radial grating used to make it an annulus 
            mask=ringRadialMask[i], # this is a 1-D mask dictating the behaviour from the centre of the stimulus to the surround.
            radialCycles=0, angularCycles=double(thisTrial['numObjectsInRing'])/numUniquePatches,
            angularRes=angRes, interpolate=antialiasGrating, autoLog=autoLogging))
         #the mask is radial and indicates that should show only .3-.4 as one moves radially, creating an annulus
    #end preparation of colored rings
    #draw cueing grating for tracking task. Have entire grating be empty except for one white sector
         cueRings.append(visual.RadialStim(myWin, tex=cueTexEachRing[i], color=[1,1,1],size=radii[i], #cueTexInner is white. Only one sector of it shown by mask
                        mask = radialMaskEachRing[i], radialCycles=0, angularCycles=1, #only one cycle because no pattern actually repeats- trying to highlight only one sector
                        angularRes=angRes, interpolate=antialiasGrating, autoLog=autoLogging) )#depth doesn't seem to work, just always makes it invisible?
    
    currentlyCuedBlob = blobToCue #this will mean that don't have to redraw 
    return ringsRadial,cueRings,currentlyCuedBlob
    ######### End constructRingAsGrating ###########################################################
