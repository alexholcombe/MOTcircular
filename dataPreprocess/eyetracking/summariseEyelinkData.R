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
inputFilename<-"TrackingExperimentEyetrackingLN"
inputFilenameSuffix<-".txt"
inputDir<-"./"
inputFilenameWithPath<-paste0(inputDir,inputFilename,inputFilenameSuffix)
outputFilename<-paste0(inputFilename,"_eachTrialSummary")
mydata <- read.table(inputFilenameWithPath, header = TRUE, sep ="\t")

#Change names of columns to something more readable
colnames(mydata)<- c("Subject", "Trial", "Blink", "Position")

#Eyelink spits out this column contents as "Trial:1", "Trial:2". Let's delete "Trial:"
#removes the word Trial from that column
mydata$Trial<-gsub("Trial:", "", mydata$Trial)

#Converts Trial number in to numeric form  
mydata<-transform(mydata, Trial=as.numeric(Trial))

#Calculating the exclusion zone numbers
exclusionDeg = 0.2 #if participant's eye is ever more than exclusionDeg away from fixation, Exclusion=1
widthPix = 800
heightPix = 600
monitorWidth = 39.5 #cm
viewdist = 57 #cm
widthScreenDeg =  2*(atan((monitorWidth/2)/viewdist) /pi*180)
pixelsPerDegree = widthPix / widthScreenDeg
exclusionPixels = exclusionDeg * pixelsPerDegree
leftThresholdPixel = widthPix/2 - exclusionPixels
rightThresholdPixel = widthPix/2 + exclusionPixels

#Go through every fixation event for all trials and check whether each fixation is within the designated limit
#Also check for any blinks during all trials
for(i in 1:nrow(mydata)){
	withinRange = (mydata$Position[i]>=leftThresholdPixel) & (mydata$Position[i]<= rightThresholdPixel)
	blinked = (mydata$Blink[i] != "NONE")
	mydata$eyeOutOfFixationArea[i] = !withinRange
	mydata$blink[i] = blinked
}

#Find the highest value in the Trial Column (the number of trials)
highestValue = max(mydata$Trial)

#Loop through all the trials, to check each trial individually
trialsCollapsed<-NULL
for(i in 1:highestValue){
	thisTrial <-NULL
	thisTrial$Trial<-i
	#Get only the data for this trial 
	sub<-subset(mydata, Trial==i)
	thisTrial$meanPosition<-mean(sub$Position)
	deviationFromCentre = sub$Position-widthPix/2
	indexOfMax<-which.max( abs(deviationFromCentre) )
	thisTrial$maxDeviation = deviationFromCentre[indexOfMax]
	thisTrial$eyeOutOfFixationArea<-max(sub$eyeOutOfFixationArea) #if any fixation events fell outside zone, 1 else 0
	thisTrial$blink<- max(sub$blink) #TRUE if any TRUE 
	trialsCollapsed <-rbind(trialsCollapsed, thisTrial)
}

write.table(trialsCollapsed, paste0(inputDir, outputFilename,".txt"), sep="\t", row.names=FALSE)