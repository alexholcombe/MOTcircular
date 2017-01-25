dfThis<- read.table(file="../dataRaw/EC_Newtask_17Jan2017_15-12.txt",header=TRUE)
df<-dfThis
dfThis<-read.table(file="../dataRaw/AH_17Jan2017_15-59.txt",header=TRUE)
df<-rbind(df,dfThis)
dfThis<-read.table(file="../dataRaw/AHtest_18Jan2017_11-05.txt",header=TRUE) #lines task
df<-rbind(df,dfThis)
dfThis<-read.table(file="../dataRaw/AHtest2_18Jan2017_15-48.txt",header=TRUE)
df<-rbind(df,dfThis)
dfThis<-read.table(file="../dataRaw/AHbright_18Jan2017_16-51.txt",header=TRUE)
df<-rbind(df,dfThis)
dfThis<-read.table(file="../dataRaw/EC_012001_20Jan2017_09-28.txt",header=TRUE)  #same as alex brightness
df<-rbind(df,dfThis)
dfThis<-read.table(file="../dataRaw/EC_022001_20Jan2017_09-49.txt",header=TRUE) #radius doubled
df<-rbind(df,dfThis)
dfThis<-read.table(file="../dataRaw/EC_032001_20Jan2017_16-58.txt",header=TRUE) #linearised monitor, went back to original radius, upgraded Psychopy to 1.84.2
df<-rbind(df,dfThis)
dfThis<-read.table(file="../dataRaw/IvT13_23Jan2017_15-29.txt",header=TRUE) #brightness task, large radius. 
df<-rbind(df,dfThis)

df$targetLocation<-"onset"
df$durMotion<-0
dfThis<-read.table(file="../dataRaw/IvTv21_23Jan2017_15-58.txt",header=TRUE) #With long motion and super-large radius
dfThis$targetLocation<-"finalCuePos"
df<-rbind(df,dfThis)
dfThis<-read.table(file="../dataRaw/EC_V2003_23Jan2017_16-42.txt",header=TRUE) #With long motion and small radius
dfThis$targetLocation<-"finalCuePos"
df<-rbind(df,dfThis)
dfThis<-read.table(file="../dataRaw/AHtest_25Jan2017_11-21.txt",header=TRUE) #brightness task, large radius. 
dfThis$targetLocation<-"finalCuePos"
df<-rbind(df,dfThis)

table(df$subject,df$timingBlips)
library(ggplot2)
g<-ggplot(df,aes(x=cueLeadTime,y=correct,color=factor(speed))) + stat_summary(fun.y=mean,geom="point",alpha=1)
g<-g+ stat_summary(fun.y=mean,geom="line")
g<-g+facet_grid(subject~targetLocation)  #, scales="free_y")
show(g)
ggsave('../figs/IncludingLast.png')
