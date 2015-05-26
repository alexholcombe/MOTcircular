Eyetracking
==============

# Communication from Psychopy to Eyelink

Call functions in `EyelinkEyetrackerForPsychopySUPA3.py` to open communication with eyetracker, to generate the calibration display and calibrate, to close the eyetracker and retrieve the eyetracking file from the Eyelink machine

# Preprocessing of the Eyelink (EDF) file

To get the eyetracking file that this file processes,
Chris opens the EDF file created by Eyelink in the DataViewer(?) software
He instructs the software to print out the following fields: 
RECORDING_SESSION_LABEL 	TRIAL_LABEL	CURRENT_FIX_BLINK_AROUND	CURRENT_FIX_X

This results in something like:
`
RECORDING_SESSION_LABEL	TRIAL_LABEL	CURRENT_FIX_BLINK_AROUND	CURRENT_FIX_X
LN_20Apr2015_14-22	Trial: 1	NONE	403.80
LN_20Apr2015_14-22	Trial: 2	AFTER	400.00
`

# Juno processing pipeline with EDF file
- his C program takes the output of edf2asc.exe (with certain flags, Juno will let us know when he gets additional data)
 (asc2msg) reads the first word on each line and use that as an indicator of what's on that line, basically the XY
- messages carry the stimulus information
- Split it into two files, one for eye position and one for stimulus information. Each file has one row for every 0.5 ms.

- Then, Juno has R program that reads in the two files output from asc2msg, then it looks for certain events which denote the time interval of interest.

EDF2ASC can do at least two different things. Split out different things.

- Meet with Tamara

-- Order with which the EDF files are saved. The event markers were appearing after the data. Please ensure that the events are written in before the start. Ask Tamara about that.
