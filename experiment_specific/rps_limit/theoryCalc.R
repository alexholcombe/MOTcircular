#This
setwd(
  "/Users/alexh/Documents/attention_tempresltn/multiple object tracking/newTraj/newTraj_repo/analysis"
)
library(ggplot2)

calcMeanEccentricityAlongCircle <- function(radius,eccentricity,epsilonTheta) {
  #numerically integrate as at https://github.com/alexholcombe/MOTcircular/blob/master/analysis/theory.md
  #for each theta of the circle, calculate distance from origin to that point
  r = radius
  e = eccentricity
  thetas = seq(from=0,to=2*pi-epsilonTheta,by=epsilonTheta)
  
  #imagine the center is at e,0
  #For each theta, calculate the point's coordinates. Then square its x and y, square root of that
  squares = (e + r*cos(thetas))^2 + (r*sin(thetas))^2
  sumOfEccentricities = sum( sqrt(squares) )
  avgEccentricity = sumOfEccentricities / length(thetas)
    
  return (avgEccentricity)
}

#Test function
calcMeanEccentricityAlongCircle(5, 0, .01)  #Should equal 5
calcMeanEccentricityAlongCircle(3, 10, .001)  #Should equal 10, but get 10.22621. Maybe that's the right answer!
calcMeanEccentricityAlongCircle(2.5, 2, .001)  #2.92
calcMeanEccentricityAlongCircle(3.5, 3, .001)  #4.18
calcMeanEccentricityAlongCircle(6, 5, .001)  #7.1 That's 

#Calc predictions for my experiment
r=6
exp<-data.frame(ecc=c(5,10),meanAlong=NaN)
exp$meanAlong[1] = calcMeanEccentricityAlongCircle(r, eccUsedInExp[1], .001)
exp$meanAlong[2] = calcMeanEccentricityAlongCircle(r, eccUsedInExp[2], .001)
exp$predictedRatio = exp$meanAlong/r
#An 18% boost and 82% in speed limit predicted.

#Calculate in a different direction to make sure I'm right. See https://github.com/alexholcombe/MOTcircular/blob/master/experiment_specific/rps_limit/theory.md
speedLimDva <- function(x,e) {
	#x is limit in revolutions per second
	#e is eccentricity
	dvaPerSecond = 2*pi*x*e
	return (dvaPerSecond)
}

exampleRpsLimit = 1 #by using 1, the increase will show the ratio
exp$dvaPerSec = speedLimDva(exampleRpsLimit,exp$meanAlong)
exp$rps = exp$dvaPerSec / (2*pi*6)
exp

#Check that both ways of doing the calculation give the same answer
if (sum(exp$rps - exp$speedUp) < .00001) {
	cat("Both ways of calculating coincide")
} else {
	cat("The ways of calculating do not coincide")
}
