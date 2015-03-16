#This file analyses anonymized data provided by "loadAnonymiseSaveData.R" in exp-specific directory
#Working directory is set hopefully by Rproj file to directory that it's in.
setwd(
"/Users/alexh/Documents/attention_tempresltn/multiple object tracking/newTraj/newTraj_repo/analysis"
)
dataDir="../dataAnonymized/"
expName="offCenter"
anonDataFilename = paste(dataDir,expName,".Rdata",sep="") 
load(anonDataFilename,verbose=TRUE)  #returns dat

offCenter = dat
iv= 'speed'
#need to add offsetXYeachRing to factors analysed
source('analyzeMakeReadyForPlot.R') #returns fitParms, psychometrics, and function calcPctCorrThisSpeed
source('plotIndividDataWithPsychometricCurves.R')

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
