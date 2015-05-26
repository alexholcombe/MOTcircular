#This file analyses anonymized data provided by "loadAnonymiseSaveData.R" in exp-specific directory
#Working directory is set hopefully by Rproj file to directory that it's in.
setwd(
"/Users/alexh/Documents/attention_tempresltn/multiple object tracking/newTraj/newTraj_repo/analysis"
)
dataDir="../dataAnonymized/"
expName="offCenterAndShape"
anonDataFilename = paste(dataDir,expName,".Rdata",sep="") 
load(anonDataFilename,verbose=TRUE)  #returns dat
excludeFixationViolations = FALSE #TRUE
tryQuickpsy = TRUE
if (tryQuickpsy) {
  library('quickpsy')
}
datWithFixatnViolations = dat
if (excludeFixationViolations) {
  datNoFixatnViolatn = dat[ dat$Exclusion!=1, ] #sessions not eyetracked are -999
  dat<-datNoFixatnViolatn
}
iv= 'speed'
#need to add offsetXYeachRing to factors analysed
assignCondName <- function(df) {
  df$condName='nothing'
  whichSquareExp = df$exp=='circleOrSquare_twoTargets'
  df$condName[ whichSquareExp ] = df$basicShape[whichSquareExp]
  df$condName[ df$offsetXYring0=='[-10, 0]' ] = "far"
  df$condName[ df$offsetXYring0=='[10, 0]' ] = "far"
  df$condName[ df$offsetXYring0=='[-5, 0]' ] = "near"
  df$condName[ df$offsetXYring0=='[5, 0]' ] = "near"
  df$condName[ df$offsetXYring0=='[0, 0]' ] = "centered"
  df$condName[ df$offsetXYring0=='[0, 0]' ] = "centered"
  return (df)
}
dat<-assignCondName(dat)
table(dat$exp,dat$condName)
factorsEachExpForBreakdown<- list(  list(colorF='condName',colF='subject',rowF='leftOrRight'),
                                    list(colorF='condName',colF='subject',rowF='ringToQuery') ) 
#how specific to break down the data before fitting
expThis = "offCenter" #"circleOrSquare_twoTargets"
factorsForBreakdownForAnalysis <- factorsEachExpForBreakdown[[1]]
datThis<-subset(dat,exp==expThis)
datAnalyze<-datThis
#factorsForBreakdownForAnalysis[ length(factorsForBreakdownForAnalysis)+1 ]<- "exp"
source('analyzeMakeReadyForPlot.R') #returns fitParms, psychometrics, and function calcPctCorrThisSpeed
table(psychometrics$condName)
source('plotIndividDataWithPsychometricCurves.R')
plotIndividDataAndCurves(expThis,datThis,psychometrics,factorsEachExpForBreakdown[[1]]) 
if (tryQuickpsy) {
  datDani<-datThis; datDani$speed = -1*datDani$speed
  factors= as.character(factorsEachExpForBreakdown[[1]])
  factors = c("condName","subject","leftOrRight")
  fit <- quickpsy(datDani, speed, correct, grouping=c("condName","subject","leftOrRight"), bootstrap='none',
                  xmin=-4,xmax=-1, guess=0.5) #WORKS
  fit <- quickpsy(datDani, speed, correct, grouping=factors, bootstrap='none',
                  xmin=-4,xmax=-1, guess=0.5) #DOESNT WORK. Only uses first element
  fit <- quickpsy_(datDani, 'speed', 'correct', grouping=factors, bootstrap='none'.
                   xmin=-4,xmax=-1,guess=0.5) #guessing parameter doesn't work
#  fit <- quickpsy(datDani, speed, correct, grouping=factors, bootstrap='none',
#                  xmin=-4,xmax=-1, guess=0.5) #seems to be no way to use a variable for the grouping
#  fit <- quickpsy(datDani, speed, correct, grouping=c(factors), bootstrap='none',
#                  xmin=-4,xmax=-1, guess=0.5) 

  plot1 <- plotcurves(fit)
  plot1<-plot1+coord_cartesian(xlim=c(-4,-1))
  quartz(); show(plot1)
}
########
expThis = "circleOrSquare_twoTargets" ###################
datThis<-subset(dat,exp==expThis)
factorsForBreakdownForAnalysis <- factorsEachExpForBreakdown[[2]]
datAnalyze<-datThis
source('analyzeMakeReadyForPlot.R') #returns fitParms, psychometrics, and function calcPctCorrThisSpeed
plotIndividDataAndCurves(expThis,datThis,psychometrics,factorsEachExpForBreakdown[[2]],xmin=1,xmax=2.5) 
if (tryQuickpsy) {
  datDani<-datThis; datDani$speed = -1*datDani$speed
  fit <- quickpsy(datDani, speed, correct, grouping=.(condName,subject,ringToQuery), bootstrap='none',
                  xmin=-2.5,xmax=-1, guess=0.5) #doesn't work with these data, thresholds very close to zero
  plot1 <- plotcurves(fit)
  quartz(); show(plot1)
}

  
table(psychometrics$condName) #print proportion trials excluded each condition
if (!excludeFixationViolations) {
  eyeTracked<- dat[dat$Exclusion!=-999,]
  ddply(eyeTracked,.(subject,condName),summarize, pctExcluded = mean(Exclusion))
}

source("extractThreshesAndPlot.R") #provides threshes, thresh plots


#MAYBE TO BE USED IN FUTURE, BUT PRESENTLY OFF-CENTER EXPERIMENT ANALYZED BY
#PRE-REPOSITORY R FILES
# expName="postVSS_13targets2349objects" 
# anonDataFname= paste(dataDir,expName,".Rdata",sep="") #data/postVSS_13targets2349objects.RData
# load(anonDataFname,verbose=TRUE) #returns dat
# dat$expName = expName
# colsNotInE1 = setdiff(colnames(dat),colnames(datE1))
# datE1[,colsNotInE1] = -999 #dummy value
# colsNotInThisOne = setdiff(colnames(datE1),colnames(dat))
# dat[,colsNotInThisOne] = -999 #dummy value
# dat = rbind(dat,datE1)
# 
# dat$tf = dat$speed*dat$numObjects
# for (iv in c("speed","tf")) {
#   cat('Fitting data, extracting threshes, plotting with iv=',iv)
#   source('analyzeMakeReadyForPlot.R') #returns fitParms, psychometrics, and function calcPctCorrThisSpeed
#   if (iv=="speed") { #if not, don't bother
#     source('plotIndividDataWithPsychometricCurves.R')
#   }
#   #should also do it normalizing by subjects' speed limits
#   source("extractThreshesAndPlot.R") #provides threshes, thresh plots
# 
#   varName=paste("threshes_",iv,"_",expName,sep='') #combine threshes
#   assign(varName,threshes)
#   save(list=varName,file=paste(dataDir,varName,".Rdata",sep='')) #e.g. threshes_tf_123targets269objects.Rdata
# }
# 
# #CRT_spinzter experiment#######################################################################
# load( paste0(dataDir,"E2_CRT_spinzter.RData"),verbose=TRUE) #E2
# E2<-dat
# #For CRT data, I need to take mean across trials. Spinzter already is
# meanThreshold<-function(df) {  
#   thresh<-mean(df$thresh)
#   df= data.frame(thresh)
#   return(df)
# }  
# factorsPlusSubject=c("numObjects","subject","direction","ecc","device") 
# 
# E2threshes<- ddply(E2, factorsPlusSubject,meanThreshold) #average over trialnum,startSpeed
# 
# #then plot
# tit<-"E2threshesSpeed"
# quartz(title=tit,width=2.8,height=2.9) #create graph of thresholds
# g=ggplot(E2threshes, aes(x=numObjects-1, y=thresh, color=device, shape=factor(ecc)))
# g<-g + xlab('Distractors')+ylab('threshold speed (rps)')
# dodgeAmt=0.35
# SEerrorbar<-function(x){ SEM <- sd(x) / (sqrt(length(x))); data.frame( y=mean(x), ymin=mean(x)-SEM, ymax=mean(x)+SEM ) }
# g<-g+ stat_summary(fun.data="SEerrorbar",geom="point",size=2.5,position=position_dodge(width=dodgeAmt))
# #g<-g+ stat_summary(fun.y=mean,geom="point",size=2.5,position=position_dodge(width=dodgeAmt))
# g<-g+stat_summary(fun.data="SEerrorbar",geom="errorbar",width=.25,position=position_dodge(width=dodgeAmt)) 
# g=g+theme_bw() #+ facet_wrap(~direction)
# g<-g+ coord_cartesian( ylim=c(1.0,2.5), xlim=c(0.6,2.4))
# g<-g+ scale_x_continuous(breaks=c(1,2))
# g<-g+ theme(axis.title.y=element_text(vjust=0.22))
# g<-g+theme(panel.grid.minor=element_blank(),panel.grid.major=element_blank())# hide all gridlines.
# show(g)
# ggsave( paste('figs/',tit,'.png',sep='') )
# 
# #source ( model limits) ??
# #source analyseSlopes?
# 
