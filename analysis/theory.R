#This
setwd(
  "/Users/alexh/Documents/attention_tempresltn/multiple object tracking/newTraj/newTraj_repo/analysis"
)
library(ggplot2)

calcMeanEccentricityOfCircle <- function(radius,eccentricity,epsilonTheta) {
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
  
calcMeanEccentricityOfCircle(5, 0, .01)  #Should equal 5

calcMeanEccentricityOfCircle(3, 10, .001)  #Should equal 10, but get 10.22621. Maybe that's the right answer!

calcMeanEccentricityOfCircle(2.5, 2, .001)  #2.92
calcMeanEccentricityOfCircle(3.5, 3, .001)  #4.18
calcMeanEccentricityOfCircle(6, 5, .001)  #7.1 That's 

calcMeanEccentricityOfCircle(6, 5, .001) / 6 #1.18   An 18% boost in speed limit predicted.





# calcMeanEccentricityOfCircle <- function(radius,eccentricity,epsilonTheta) {
#   #numerically integrate as at https://github.com/alexholcombe/MOTcircular/blob/master/analysis/theory.md
#   #for each theta of the circle, calculate distance from origin to that point
#   r = radius
#   e = eccentricity
#   thetas = seq(from=0,to=2*pi-epsilonTheta,by=epsilonTheta)
#   avg = 0
#   for (i in 1:length(thetas)) {
#     ecc = sqrt( (e + r*cos(thetas[i]))^2 + (r*sin(thetas[i]))^2 )
#     avg = avg + ecc / length(thetas)
#   }
# 
#   return (avg)
# }
# 
# calcMeanEccentricityOfCircle(3, 10, .001)  #Should equal 10
# 
