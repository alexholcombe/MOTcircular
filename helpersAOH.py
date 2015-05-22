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



