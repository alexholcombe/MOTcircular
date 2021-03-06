#Intended to be called by doAllAnalyses.R, which 
#variables expected:
#factorsPlusSubject
#fitParms
#psychometrics
#function calcPctCorrThisIvVal
#iv
#varyLapseRate, lapseMinMax
infoMsg=paste0(iv,"-fit")

lapseMsg=""
if (!varyLapseRate)
  lapseMsg=paste("lapseRate always",unique(lapseMinMax))
#go point by point to find thresholds for each criterion for each factorsPlusSubject
worstLapseRate <- max(fitParms$lapseRate)
paste("Can't calculate threshold above criterion level of",1-worstLapseRate,"because that's the worst subject")
calcMidPointThresh<- TRUE
calcThreeQuartersThresh<- TRUE
#maxCriterion <- 1-worstLapseRate
maxCriterion <- .95
threshCriteria<- seq(from=.67,to=maxCriterion,by=.06) #high thresholds
threshCriterion = round(threshCriteria,3) #because otherwise can include invisible 10^-21 diff which will trip you up later
threshes <- data.frame()
for (numObjectsThis in unique(fitParms$numObjects)) {
  threshCriteriaThis = threshCriteria
  threshCriteriaNotes = rep("nothingSpecial",length(threshCriteriaThis))
  if (calcMidPointThresh) {
    crit <- 1/numObjectsThis + 0.5*(1-1/numObjectsThis)  #midpoint threshold
    crit<- round(crit,3)
    threshCriteriaThis= c(threshCriteriaThis,crit)
    threshCriteriaNotes = c(threshCriteriaNotes,"midpoint")
  }
  if (calcThreeQuartersThresh) {
    crit <- 1/numObjectsThis + 0.75*(1-1/numObjectsThis)
    crit<- round(crit,3)
    threshCriteriaThis= c(threshCriteriaThis,crit)
    threshCriteriaNotes = c(threshCriteriaNotes,"threeQuarters")    
  }
  for (i in 1:length(threshCriteriaThis)) {
    threshCriterion = threshCriteriaThis[i]
    cat('Extracting thresh for criterion:',threshCriterion)
    #use point by point search to find the threshold. 
    myThreshGetNumeric= makeMyThreshGetNumerically(iv,threshCriterion)
    
    psychometricTemp<- subset(psychometrics,numObjects==numObjectsThis)
    calcThreshForPredictn<- FALSE  #because tracking-two prediction for 6, 9 objects never gets that high. Anyway this is to address
    if (!calcThreshForPredictn)  
      psychometricTemp <- subset(psychometricTemp,numTargets!="2P")
    #Don't do it where criterion corresponds to below chance
    #psychometricTemp <- subset(psychometricTemp, numObjects > 1/threshCriterion) #For these numObjects conditions, chance is above the current criterion
    
    threshesThisNumeric = ddply(psychometricTemp,factorsPlusSubject,myThreshGetNumeric) 
    threshesThisNumeric$criterion <- threshCriterion
    threshesThisNumeric$criterionNote <- threshCriteriaNotes[i]
    threshesThis<- merge(threshesThisNumeric,fitParms)
    threshes<- rbind(threshes, threshesThis)
  }
}

threshes$targets<-threshes$numTargets
themeAxisTitleSpaceNoGridLinesLegendBox = theme_classic() + #Remove gridlines, show only axes, not plot enclosing lines
  theme(axis.line = element_line(size=.3, color = "grey"), 
        axis.title.y=element_text(vjust=0.24), #Move y axis label slightly away from axis
        axis.title.x=element_text(vjust=.10), #Move x axis label slightly away from axis
        legend.key = element_blank(), #don't put boxes around legend bits
        legend.background= element_rect(color="grey90"), #put big light grey box around entire legend
        panel.background = element_rect(fill = "transparent",colour = NA),
        plot.background = element_rect(fill = "transparent",colour = NA)   )
##########Plot threshes, exp*subject*numTargets*numObjects ################
tit=paste("individual_Ss_threshesSpeed_",infoMsg,"_threeQuarterThresh",sep='')
dv="speed"
quartz(title=tit,width=6,height=3) #create graph of thresholds
h<-ggplot(data=subset(threshes,criterionNote=="threeQuarters"),   #midpoint
          aes(x=numTargets,y=thresh,color=factor(numObjects)))
h<-h+facet_grid(. ~ exp)  #facet_grid(criterion ~ exp)
h<-h+themeAxisTitleSpaceNoGridLinesLegendBox #theme_bw() 
#ylim(1.4,2.5) DO NOT use this command, it will drop some data
#h<-h+ coord_cartesian( xlim=c(xLims[1],xLims[2]), ylim=yLims ) #have to use coord_cartesian here instead of naked ylim()
h<-h+ geom_point() + geom_line(aes(group=interaction(subject,numObjects))) #plot individual lines for each subject
h<-h+ylab(  paste('threshold ',iv,' (',ifelse(dv=="speed","rps","Hz"),')',sep='') )  
if (iv=="speed") { h<-h+ggtitle("Speed limits vary widely. 6,9 will converge when plot tf") 
} else h<-h+ggtitle('6,9 validate tf limit.')
show(h)
ggsave( paste('figs/',tit,'.png',sep='') )
#############################################Plot mean speed threshes against numTargets
tit<-paste0("SpeedMeanThreshAgainstTargets)",infoMsg,"_threeQuarterThresh")
quartz(title=tit,width=4,height=3) 
h<-ggplot(data=subset(threshes,criterionNote=="threeQuarters"),   #midpoint
          aes(x=numTargets,y=thresh,color=factor(numObjects)))
h<-h+facet_grid(. ~ exp)  #facet_grid(criterion ~ exp)
h<-h+themeAxisTitleSpaceNoGridLinesLegendBox
#ylim(1.4,2.5) DO NOT use this command, it will drop some data
#h<-h+ coord_cartesian( xlim=c(xLims[1],xLims[2]), ylim=yLims ) #have to use coord_cartesian here instead of naked ylim()
#h<-h+ geom_point() + geom_line(aes(group=interaction(subject,numObjects))) #plot individual lines for each subject
h<-h+ stat_summary(fun.y=mean,geom="point")
h<-h+ stat_summary(fun.y=mean,geom="line")
h<-h+stat_summary(fun.data="mean_cl_boot",geom="errorbar",width=.2,conf.int=.95) #error bar
h<-h+ylab(  paste('threshold ',iv,' (',ifelse(iv=="speed","rps","Hz"),')',sep='')  ) 
if (iv=="speed") {  h<-h+ggtitle("6,9 difft validates t.f. limit. Speed limits vary widely")
} else h<-h+ggtitle('6,9 validate tf limit.')
#h<-h+coord_cartesian(ylim=c(1.5,2.5)) #have to use coord_cartesian here instead of naked ylim() to don't lose part of threshline
h<-h+ggtitle(paste("6,9 difft validates t.f. limit. Speed limits vary widely",lapseMsg))
show(h)
ggsave( paste0('figs/E1_EpostVSStargets_',tit,'.png') )
#############################################Plot mean speed threshes against distractors
tit<-paste0('SpeedMeanThreshAgainstDistractors ',infoMsg,' threeQuarterThresh') 
quartz(title=tit,width=4,height=3) #create graph of threshes
threshes$numObjects <- as.numeric(threshes$numObjects) #Otherwise can't connect with lines
threshes$targets <- threshes$numTargets #Otherwise can't connect with lines
h<-ggplot(data=subset(threshes,criterionNote=="threeQuarters"),   #midpoint
          aes(x=numObjects-1,y=thresh)) #,color=factor(targets) #I have no idea why but this doesn't work, hence put it in facet_grid
h<-h+facet_grid(exp ~ targets)  #facet_grid(criterion ~ exp)
h<-h+themeAxisTitleSpaceNoGridLinesLegendBox
#ylim(1.4,2.5) DO NOT use this command, it will drop some data
#h<-h+ coord_cartesian( xlim=c(xLims[1],xLims[2]), ylim=yLims ) #have to use coord_cartesian here instead of naked ylim()
#h<-h+ geom_point() + geom_line(aes(group=interaction(subject,numObjects))) #plot individual lines for each subject
dodgeWidth<-.3
h<-h+ stat_summary(fun.y=mean,geom="point",position=position_dodge(width=dodgeWidth))
h<-h+ stat_summary(fun.y=mean,geom="line",position=position_dodge(width=dodgeWidth))
#h<-h+stat_summary(fun.data = mean_cl_normal, geom="errorbar", mult=1, width=.5, position=position_dodge(width=dodgeWidth))
h<-h+stat_summary(fun.data="mean_cl_boot",geom="errorbar",width=.25,conf.int=.95,position=position_dodge(width=dodgeWidth)) 
h<-h+ylab(  paste('threshold ',dv,' (',ifelse(dv=="speed","rps","Hz"),')',sep='')  )
h<-h+xlab('Distractors')
xTicks= unique(threshes$numObjects-1) #put axis ticks at actual values used
h<-h+scale_x_continuous(breaks=c( xTicks ))
h<-h+ggtitle(paste("5,8 difft validates t.f. limit. Speed limits vary widely",lapseMsg))
#h<-h+coord_cartesian(ylim=c(1.5,2.5)) #have to use coord_cartesian here instead of naked ylim() to don't lose part of threshline
show(h) #http://stackoverflow.com/questions/7455046/how-to-make-graphics-with-transparent-background-in-r-using-ggplot2?rq=1
ggsave( paste0('figs/E1_EpostVSStargets_',tit,'.png') ,bg="transparent" ) #bg option will be passed to png
########################################Temporal frequency against targets, individual Ss
threshes$tfThresh <- threshes$thresh*threshes$numObjects
#p2 <- aes(x=numObjects-1,y=temporalFreq,color=targets); h %+% p2 #quick t.f. plot
### Pattern remarkably consistent across Ss, perhaps show in paper?
tit=paste0("individualSsTemporalFreq ",infoMsg," threeQuarterThresh")
quartz(title=tit,width=6,height=3)
#Not fair to include values above the worst-observer's lapse rate. Because then the speed limit cost of second target is infinite.
h<-ggplot(data=subset(threshes,criterionNote=="threeQuarters"),   #midpoint
          aes(x=numTargets,y=tfThresh,color=factor(numObjects)))
h<-h+facet_grid(. ~ exp)  #facet_grid(criterion ~ exp)
h<-h+ylab('threshold tf (Hz)')
h<-h+themeAxisTitleSpaceNoGridLinesLegendBox
#ylim(1.4,2.5) DO NOT use this command, it will drop some data
#h<-h+ coord_cartesian( xlim=c(xLims[1],xLims[2]), ylim=yLims ) #have to use coord_cartesian here instead of naked ylim()
dodgeAmt=.3
h<-h+ geom_point(position=position_dodge(width=dodgeWidth)) 
#I don't know why have to specify the group to get the lines to work
h<-h+ geom_line(aes(group=interaction(subject,numObjects)),position=position_dodge(width=dodgeWidth)) 
#h<-h+stat_summary(fun.data = mean_cl_normal, geom="errorbar", mult=1, width=.5, position=position_dodge(width=dodgeWidth))
h<-h+ggtitle(paste(tit,lapseMsg))
show(h) #http://stackoverflow.com/questions/7455046/how-to-make-graphics-with-transparent-background-in-r-using-ggplot2?rq=1
ggsave( paste0('figs/E1_EpostVSStargets_',tit,'.png') ,bg="transparent" ) #bg option will be passed to png
h %+% subset(threshes,criterionNote=="threeQuarters")
##########################################tf mean threshes against targets
tit=paste0("tfMeanThreshAgainstTargets ",infoMsg," threeQuarterThresh")
quartz(title=tit,width=6,height=3)
#Not fair to include values above the worst-observer's lapse rate. Because then the speed limit cost of second target is infinite.
h<-ggplot(data=subset(threshes,criterionNote=="threeQuarters"),   #midpoint
          aes(x=targets,y=tfThresh,color=factor(numObjects)))
h<-h+facet_grid(. ~ exp)  #facet_grid(criterion ~ exp)
h<-h+ylab('threshold tf (Hz)')
h<-h+themeAxisTitleSpaceNoGridLinesLegendBox
#ylim(1.4,2.5) DO NOT use this command, it will drop some data
#h<-h+ coord_cartesian( xlim=c(xLims[1],xLims[2]), ylim=yLims ) #have to use coord_cartesian here instead of naked ylim()
dodgeAmt=.3
h<-h+ stat_summary(fun.y=mean,geom="point",position=position_dodge(width=dodgeWidth))
h<-h+ stat_summary(fun.y=mean,geom="line",position=position_dodge(width=dodgeWidth))
h<-h+stat_summary(fun.data="mean_cl_boot",geom="errorbar",width=.25,conf.int=.95,position=position_dodge(width=dodgeWidth)) 
h<-h+ggtitle(paste(tit,lapseMsg))
show(h) #http://stackoverflow.com/questions/7455046/how-to-make-graphics-with-transparent-background-in-r-using-ggplot2?rq=1
ggsave( paste0('figs/E1_EpostVSStargets_',tit,'.png') ,bg="transparent" ) #bg option will be passed to png
##########################################tf mean threshes against distractors
tit=paste0("tfMeanThreshAgainstDistractors ",infoMsg," threeQuarterThresh")
quartz(title=tit,width=4,height=3) 
#Not fair to include values above the worst-observer's lapse rate. Because then the speed limit cost of second target is infinite.
h<-ggplot(data=subset(threshes,criterionNote=="threeQuarters"),   #midpoint
          aes(x=numObjects-1,y=tfThresh))#,color=targets)) #color=targets gives error I don't know why
h<-h+facet_grid(exp ~ targets)  #facet_grid(criterion ~ exp)
h<-h+ylab('threshold tf (Hz)')
h<-h+themeAxisTitleSpaceNoGridLinesLegendBox
h<-h+xlab('Distractors')
xTicks= unique(threshes$numObjects-1) #put axis ticks at actual values used
h<-h+scale_x_continuous(breaks=c( xTicks ))
#h<-h+ coord_cartesian( xlim=c(xLims[1],xLims[2]), ylim=yLims ) #have to use coord_cartesian here instead of naked ylim()
dodgeAmt=.3
h<-h+ stat_summary(fun.y=mean,geom="point",position=position_dodge(width=dodgeAmt)) 
#h<-h+stat_summary(fun.data = mean_cl_normal, geom="errorbar", mult=1, width=.5, position=position_dodge(width=dodgeWidth))
h<-h+stat_summary(fun.data="mean_cl_boot",geom="errorbar",width=.25,conf.int=.95,position=position_dodge(width=dodgeAmt)) 
h<-h+ stat_summary(fun.y=mean,geom="line",position=position_dodge(width=dodgeAmt))
h<-h+ggtitle(paste("Speed-limited for few distractrs, not much flattening by 3 targets",lapseMsg))
show(h) #http://stackoverflow.com/questions/7455046/how-to-make-graphics-with-transparent-background-in-r-using-ggplot2?rq=1
ggsave( paste0('figs/E1_EpostVSStargets_',tit,'.png') ,bg="transparent" ) #bg option will be passed to png
##########################################tf individual Ss against distractors
tit=paste0("tfSsAgainstDistractors ",infoMsg," threeQuarterThresh")
quartz(title=tit,width=6,height=3) 
#Not fair to include values above the worst-observer's lapse rate. Because then the speed limit cost of second target is infinite.
h<-ggplot(data=subset(threshes,criterionNote=="threeQuarters"),   #midpoint
          aes(x=numObjects-1,y=tfThresh,color=subject)) #color=targets,
h<-h+facet_grid(exp~targets)  #facet_grid(criterion ~ exp)
h<-h+ylab('threshold tf (Hz)')
h<-h+themeAxisTitleSpaceNoGridLinesLegendBox
h<-h+xlab('Distractors')
xTicks= unique(threshes$numObjects-1) #put axis ticks at actual values used
h<-h+scale_x_continuous(breaks=c( xTicks ))
#h<-h+ coord_cartesian( xlim=c(xLims[1],xLims[2]), ylim=yLims ) #have to use coord_cartesian here instead of naked ylim()
dodgeAmt=.3
h<-h+ geom_point()
h<-h+ geom_line()
h<-h+ggtitle(paste("individ Ss all show speed-limited for few distractrs, not much flattening by 3 targets",lapseMsg))
show(h) #http://stackoverflow.com/questions/7455046/how-to-make-graphics-with-transparent-background-in-r-using-ggplot2?rq=1
ggsave( paste0('figs/E1_EpostVSStargets_',tit,'.png') ,bg="transparent" ) #bg option will be passed to png
##########################################################

cat('I give you threshes')
###################################
#plot thresholds (at only one criterion level) for all 3 experiments at same time
# quartz()
# #tt<-subset(threshes,subject=="AH");  tt<-subset(tt,numTargets=="1")
# #tt$subject<-factor(tt$subject) #in case unused levels were the problem
# #h<-ggplot(data= fake, aes(x=separatnDeg,y=thresh))
# h<-ggplot(data= subset(threshes,numTargets!="2P"), aes(x=separatnDeg,y=thresh,color=numTargets,shape=exp))
# h<-h + facet_grid(exp~., scales="free") # ~criterion
# #h<-h+stat_summary(data=threshesThisNumeric,fun.data="mean_cl_boot",geom="errorbar",conf.int=.95,position=position_dodge(width=.2)) #error bar
# h<-h+stat_summary(fun.data="mean_cl_boot",geom="errorbar",conf.int=.95,position=position_dodge(width=.2)) #error bar
# h<-h+theme_bw() + xlab("Separation (deg)")
# #ylim(1.4,2.5) DO NOT use this command, it will drop some data
# #h<-h+ coord_cartesian( xlim=c(xLims[1],xLims[2]), ylim=yLims ) #have to use coord_cartesian here instead of naked ylim()
# #h<-h+coord_cartesian(ylim=c(1.4,2.6)) #have to use coord_cartesian here instead of naked ylim() to don't lose part of threshline
# h<-h+ stat_summary(fun.y=mean,geom="point") + stat_summary(fun.y=mean,geom="line") 
# h+theme(panel.grid.minor=element_blank(),panel.grid.major=element_blank())# hide all gridlines
# h<-h+ggtitle(paste(tit,lapseMsg))
# h
