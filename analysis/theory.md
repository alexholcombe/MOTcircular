Neurons-per-unit-time theory
==============

- The speed limit is caused by a minimum time required to deselect neurons corresponding to old locations and select neurons corresponding to new locations.

- explains why the rps speed limit is approximately the same for higher eccentricity. The # of neurons one needs to select/deselect per degree of visual angle decreases by 2*pi for every unit increase in deg of visual angle. In other words, neurons at 5 deg ecc are spaced 2pi further apart than are neurons at 4 deg ecc. 
- makes a prediction for what will happen when we move a circular trajectory from being centred on fixation into the periphery. When we move something from a mean eccentricity of 2.5 to a mean eccentricity of 6.7, that's an increase of 4.2 deg. So we'd have to increase the distance traveled by 8.4pi to have the same level of performance.
- By simply shifting the whole trajectory to be more eccentric, we instead didn't increase the distance traveled at all. That means that the speed limit should now be much higher. I guess it should be 8.4pi times higher.
- Speed limit in deg/sec (e) = `4*pi*e`   which is always equal to 2 rps
- E.g. if test at e=6.7, speed limit = `4*pi*6.7deg/sec`
 - If that traj has a radius of 2.5, then its path length is 5*pi.
 - So in rps, that's `(4*pi*6.7 deg/sec) / (5*pi deg/rev) ` = 5.36 rps
 
 But there was a bit of crowding there, which cuold be blamed for the bad speed limit.

So speed limit at e=6.7 = 4*pi*6.7deg/sec.   I instead test a distance traveled of 5*pi = 1 revolution there, speed limit in revolutions per second will then be 

4*pi*6.7 deg/sec  /   5*pi deg/rev  = 5.36 rev/sec

-More specific quantitative prediction is of entire psychometric curve. Speed limit is just one point on it. But it should all shift by the same amount. Is that additive factor or multiplicative? I think it's additive because eccentricity isn't changing, distance isn't changing.

What about for the other r=8 trajectory I moved into the periphery? 
e=11
Speed limit in deg/sec (e) = 4*pi*11 = 44*pi
But I have it travelling only 2pi8 deg per revolution.

44pi deg/sec / 2pi8 deg/rev = 2.75 rev/sec

Instead I observed a speed limit a bit slower, but similar.

-Crowding. A countervailing factor to reduce the speed limit could be crowding. While that may be an issue for the smaller-radius trajectory, crowding shouldn't apply to the larger-radius trajectory.  Small radius gives bigger predicted effect, but can't increase eccentricity as much due to crowding. Write down the size of the effect as a function of r = e/2   So for every radius r, the biggest eccentricity I can use is e = r*2 .

Speed limit (deg/sec) = 4*pi*(r*2) = 8*pi*r

The distance per revolution is only 2*pi*r

8*pi*r deg/sec   /    2*pi*r deg/rev   = 4 rev/sec

So the speed limit always goes up to 4 rev per second when you move a circle to be centered on the eccentricity that is twice its radius. Or more generally, each person's speed limit should double when you shift it like that.

If we enforce a greater protection zone like .75 instead of .5 the spacing, then presumably the speed limit should go up to 1/.75 * 2 = 2.7 


-Crossing hemifields. A countervailing factor may be a cost for crossing between hemifields. I could address this by maybe moving it only partly off-center? What is the mean eccentricity for a circle at a particular eccentricity?


