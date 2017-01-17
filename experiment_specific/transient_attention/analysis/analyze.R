df<- read.table(file="../dataRaw/EC_Newtask_17Jan2017_15-12.txt",header=TRUE)
df2<-read.table(file="../dataRaw/AH_17Jan2017_15-59.txt",header=TRUE)
df<-rbind(df,df2)
library(ggplot2)
g<-ggplot(df,aes(x=cueLeadTime,y=correct,color=factor(speed))) + stat_summary(fun.y=mean,geom="point",alpha=1)
g<-g+ stat_summary(fun.y=mean,geom="line")
g<-g+facet_grid(subject~., scales="free_y")
g