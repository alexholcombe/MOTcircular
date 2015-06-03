#To get the eyetracking file that this file processes,
#Chris opens the EDF file created by Eyelink in 
#He instructs the software to print out the following fields: 
#RECORDING_SESSION_LABEL 	TRIAL_LABEL	CURRENT_FIX_BLINK_AROUND	CURRENT_FIX_X
#E.g.,
#RECORDING_SESSION_LABEL	TRIAL_LABEL	CURRENT_FIX_BLINK_AROUND	CURRENT_FIX_X
#LN_20Apr2015_14-22	Trial: 1	NONE	403.80
#LN_20Apr2015_14-22	Trial: 2	AFTER	400.00

#The job of this program is to examine each fixation event designated by Eyelink and check whether
#all the fixations for each trial is within the desired fixation zone.
#It also outputs whether the subject blinked on each trial.
library(stringr)
library(dplyr)

inputFilename<-"WN_26May2015_13-44Eyetracking"# "TrackingExperimentEyetrackingLN"
inputFilenameSuffix<-".txt"
inputDir<-"./dataForTestingOfCode/"
inputFilenameWithPath<-paste0(inputDir,inputFilename,inputFilenameSuffix)
outputFilename<-paste0(inputDir,inputFilename,"_eachTrialSummary")
df <- read.table(inputFilenameWithPath, header = TRUE, sep ="\t")

#trial num should be contained in either TRIAL_LABEL or TRIAL_INDEX
if ("TRIAL_LABEL" %in% colnames(df)) {
  #TRIAL_LABEL column contents are printed as as "Trial:1", "Trial:2". Let's delete "Trial:"
  df$TRIAL_LABEL<-gsub("Trial:", "", df$TRIAL_LABEL)
  #Converts Trial number in to numeric form  
  df<-transform(df, TRIAL_LABEL=as.numeric(TRIAL_LABEL))
  names(df)[names(df) == 'TRIAL_LABEL'] <- 'trial' #rename column
} else if ("TRIAL_INDEX" %in% colnames(df)){
  names(df)[names(df) == 'TRIAL_INDEX'] <- 'trial' #rename column
} else { 
  print("Neither TRIAL_LABEL nor TRIAL_INDEX present, need one!") }

colsExpected = c("RECORDING_SESSION_LABEL","trial","CURRENT_FIX_BLINK_AROUND",
                 "CURRENT_FIX_X","CURRENT_FIX_Y")
colsExpectedNotPresent <- setdiff( colsExpected,colnames(df) )
if (length(colsExpectedNotPresent) >0) {
  if (length(colsExpectedNotPresent)==1 && colsExpectedNotPresent[1]=="CURRENT_FIX_Y") {
    print("Chris early output did not include CURRENT_FIX_Y, that's ok for now")
  } else {
    stop( paste0("The file ",inputFilename," does not have the expected columns  :",colsExpectedNotPresent) )
  }
}
colsPresentNotExpected<- setdiff( colnames(df), colsExpected )
if (length(colsPresentNotExpected) >0) {
  cat("These columns are in the file",inputFilename," but were not expected:")
  print( paste(colsPresentNotExpected,collapse=',') )
}

#Calculating the exclusion zone numbers
exclusionDeg = 0.2 #if participant's eye is ever more than exclusionDeg away from fixation, Exclusion=1
widthPix = 800
heightPix = 600
monitorWidth = 39.5 #cm
viewdist = 57 #cm
widthScreenDeg =  2*(atan((monitorWidth/2)/viewdist) /pi*180)
pixelsPerDegree = widthPix / widthScreenDeg
exclusionPixels = exclusionDeg * pixelsPerDegree
leftLimitPixel = widthPix/2 - exclusionPixels
rightLimitPixel = widthPix/2 + exclusionPixels
bottomLimitPixel = heightPix/2 + exclusionPixels
topLimitPixel = heightPix/2 - exclusionPixels

#File is formatted with potentially many rows for each trial. Multiple events in each trial according to Eyelink
#Code whether a blink occurred around the time of every event
dg<-mutate(df,blink=(CURRENT_FIX_BLINK_AROUND!="NONE"))

#Go through every event for all trials and indicate whether each event falls within the designated limits
dg<-mutate(dg, outOfDesiredArea= 
             (CURRENT_FIX_X>leftLimitPixel) & (CURRENT_FIX_X<rightLimitPixel) )

if ("CURRENT_FIX_Y" %in% colnames(dg)) {
  dg<-mutate(dg, outOfDesiredArea= 
               (CURRENT_FIX_Y>=bottomLimitPixel) & (CURRENT_FIX_X<topLimitPixel) )  
}

#Change names of columns to something more readable
#colnames(mydata)<- c("Subject", "Trial", "Blink", "Position")

#Break apart by trial number, then find max deviation and whether any fell out of desired area, etc
by_trial <- group_by(dg, trial)
oneRowPerTrial <- summarise(by_trial,
                   outOfDesiredArea = max(outOfDesiredArea),
                   maxXdev = max( abs(CURRENT_FIX_X-widthPix/2) ),
                   blinks = sum( blink ),
                   meanX = mean(CURRENT_FIX_X) )

if ("CURRENT_FIX_Y" %in% colnames(dg)) {
  oneRowPerTrialExtra <- summarise(by_trial, 
                    maxYdev = max( abs(CURRENT_FIX_Y-heightPix/2) ),
                    meanY = mean(CURRENT_FIX_Y) )
  oneRowPerTrial<- merge(oneRowPerTrial, oneRowPerTrialExtra, by=c("trial"))
}
head(oneRowPerTrial)
#write.table(oneRowPerTrial, paste0(inputDir, outputFilename,".txt"), sep="\t", row.names=FALSE)