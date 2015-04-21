#expecting current working directory to be top level of this git-indexed project
setwd("/Users/alexh/Documents/attention_tempresltn/multiple object tracking/newTraj/newTraj_repo")
expFoldersPrefix= "dataRaw/"
expname = "offCenter"
expFolders <- c(expname)
expFoldersPostfix = "" #"/rawdata"
destinatnDir<-"dataAnonymized/" #where the anonymized data will be exported to
anonymiseData <- TRUE

for (expi in 1:length(expFolders)) {
  thisExpFolder = paste0(expFoldersPrefix,expFolders[expi], expFoldersPostfix)
  print(paste("From exp",thisExpFolder))
  foldersThisExp <- list.dirs(path=thisExpFolder,recursive=FALSE) #each folder should be a subject
  print("Loading data from folders:"); print(foldersThisExp)
  for (i in 1:length(foldersThisExp)) {
    thisSubjectDir <- foldersThisExp[i]
    files <- dir(path=thisSubjectDir,pattern='.txt')  #find all data files in this directory
    eyetrackIdxs = grep("Eyetracking",files)
    if (length(eyetrackIdxs) ==0) {
    		eyetrackFiles = FALSE
    }
    else { 
    		eyetrackFiles = TRUE 
    		eyetrackFiles = files[eyetrackIdxs]
	}
    nonEyetrackIdxs = grep("Eyetracking",files,invert=TRUE)
    files<- files[nonEyetrackIdxs] #don't include eyetracking ones
    #allFilesStr <- paste(files,collapse=",") #print(allFilesStr)
    for (j in 1:length(files)) { #read in sessions of this subject
    	  file = files[j]
      fname = paste0(thisSubjectDir,"/",file)
      rawDataLoad=read.table(fname, sep='\t', header=TRUE )
      rawDataLoad$exp <- expFolders[expi]
      rawDataLoad$file <- file
      #Search for eyetracking file
      fileNameLen = nchar(file)
      withoutSuffix<-substr(file,1,fileNameLen-4) 
      eyetrackFileNameShouldBe<- paste0(withoutSuffix,"Eyetracking.txt")
      row <- grep(eyetrackFileNameShouldBe, eyetrackFiles)
      eyetrackFileFound = ( length(row) >0 )
      msg=""
      if (eyetrackFileFound)
      	msg=" and found Eyetracking file"
      print(paste0("Loaded file ",file,msg))
      numTrials<- length(rawDataLoad$trialnum)
      if (eyetrackFileFound) {
      	trackFname = paste0(thisSubjectDir,"/", eyetrackFileNameShouldBe)
      	eyeTrackInfo = tryCatch( 
      	    read.table(trackFname,header=TRUE), 
      	    error=function(e) { 
      	    	   msg = paste0('ERROR reading file',trackFname,":",e)
      	    	   print(msg)
           } )
      	#Eyetracker begins trials with 1, whereas python and psychopy convention is 0
      	#So to match the eyetracker file with the psychopy file, subtract one from trial num
      	eyeTrackInfo$trialnum = eyeTrackInfo$Trial-1
      	#Delete the Trial column which confusingly is one greater than trialnum
      	eyeTrackInfo$Trial <- NULL
      	eyeTrackInfo$subject <- NULL #has entire filename with date stamp
      	rawDataWithEyetrack<- merge(rawDataLoad, eyeTrackInfo, by=c("trialnum"))
      }
      #omit last trial is total trials are odd, probably a repeat      
      msg=""
      removeLastTrial = FALSE
      if (numTrials %% 2 ==1) {
      	msg=paste0(" Odd number of trials (",numTrials,"); was session incomplete, or extra trial at end?")
      	removeLastTrial = TRUE
      }      
      if (removeLastTrial) {
      	rawDataLoad<- subset(rawDataLoad, !trialnum %in% c(length(rawDataLoad$trialnum)-1))
      	cat("Removed last trial- assuming it's a repeat")
      }
      print(paste0(", now contains ",length(rawDataLoad$trialnum)," trials ",msg))
      if (expi==1 & i==1 & j==1) { #first file of the first subject
        rawData<- rawDataLoad
      } else {  #not the first file of the first subject, so combine it with previously-loaded data
        newCols <- setdiff( colnames(rawDataLoad),prevColNames )
        oldColsNotInNew <- setdiff( prevColNames,colnames(rawDataLoad) )
        if (length(newCols) >0) {
          print( paste("newCols are",newCols))
          for (n in length(newCols)) #add newCol to old data.frame with dummy value
            rawData[newCols[n]] <- -999
        }
        if (length(oldColsNotInNew)>0) 
          print( paste("oldColsNotInNew are", oldColsNotInNew, 'thisSubjectDir=',thisSubjectDir) )
        for (n in length(oldColsNotInNew)) #add old col to new data.frame that doesn't have it
          rawDataLoad[oldColsNotInNew[n]] <- -999	
        
        tryCatch( rawData<-rbind(rawData,rawDataLoad), error=function(e)
        { print ("ERROR merging")
          colnamesNew <- paste(colnames(rawDataLoad),collapse=",")
          colnamesOld <- paste(colnames(rawData),collapse=",")
          writeLines( paste('colnamesNew=',colnamesNew,'\n colnamesOld=', colnamesOld))
          writeLines( paste('difference is ', setdiff(colnamesNew,colnamesOld)) )
          QUIT
        } )
      }
      prevColNames<- colnames(rawDataLoad)
      
    }		
  }
}

rawData = subset(rawData, subject != "auto") #get rid of any autopilot data
dat <-rawData
#end data importation 

#check data counterbalancing
source("analysis/helpers/checkCounterbalancing.R")
checkCombosOccurEqually(dat, c("numObjects","numTargets") )
checkCombosOccurEqually(dat, c("numObjects","numTargets","ringToQuery") )
checkCombosOccurEqually(dat, c("condition","leftOrRight") )
checkCombosOccurEqually(dat, c("condition","leftOrRight","offsetXYring0") ) #NO?
checkCombosOccurEqually(dat, c("numObjects","numTargets","speed") )
#If instead of using raw speed, I rank the speed within each numObjects*numTargets, then from that perspective everything should
#be perfectly counterbalanced, because each numObjects*numTargets combination has the same number of speeds tested
#But the rank for a speed depends on what numObjects-numTargets condition it's in. Should be easy with ddply
ordinalSpeedAssign <- function(df) {
#df$speedRank <- rank(df$speed)  #Rank won't work, always wants to break all ties. Whereas I want to preserve ties.
  df$speedRank <- match(df$speed,unique(df$speed)) 
  df
}
library(plyr)
d<- ddply(dat,.(numObjects,numTargets),ordinalSpeedAssign)
#check whether counterbalanced with for each speed list for a particular condition, did each equally often
#Might not be if ran multiple sessions with different speeds
checkCombosOccurEqually(d, c("numObjects","numTargets","speedRank") )

dat$correct = dat$orderCorrect /3
dat$chanceRate= 1 / dat$numObjects

rotX <- function(ch,x) 
{ #rotate each letter of a string ch by x letters thru the alphabet, as long as x<=13
  old <- paste(letters, LETTERS, collapse="", sep="")
  new <- paste(substr(old, 2*x+1, 26*2), substr(old, 1, 26), sep="")
  chartr(old, new, ch)
}
if (anonymiseData) {
  keyFile = "anonymisationKey.txt"
  if ( !file.exists(keyFile) )
  {
  	stop('The file anonymisationKey.txt does not exist!')
  }
  linesFromFile= readLines(paste0(expFoldersPrefix,keyFile),warn=FALSE)
  key = as.numeric(linesFromFile[1]) #the key to encrypt the data with
  dat$subject <- rotX(dat$subject,key) #anonymise subject initials by rotating them by key characters
}
	
table(d$speedRank,d$numObjects,d$numTargets,d$subject)

#Save anonymised data for loading by doAllAnalyses.R
fname=paste(destinatnDir,expname,sep="")
save(dat, file = paste(fname,".RData",sep=""))
write.csv(dat, file = paste(fname,".csv",sep=""))
print(paste("saved data in ",fname,".RData and ",fname,".csv",sep=""))