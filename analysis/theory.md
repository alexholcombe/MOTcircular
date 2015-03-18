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
 - That's a prediction that's easy to falsify!
 - But a radius of 2.5 at e=6.7 could be crowded, which could be blamed for the bad speed limit.

## Crowding. Design experiment to avoid shift of trajectory into periphery introducing crowding. 
- Figure 6b of Gurnsey, Roddy & Chanab 2011 shows critical separation as a function of eccentricity and how it varies. As they say in their discussion on p. 14, 0.5 is plenty. So to be safe, let's not allow spacing to go below 0.55 of eccentricity.
- r will be `0.55*e`   Therefore, e = r/0.55
- Speed limit =`4*pi*e` 
- Substitute in r/0.55 for e
- `4*pi*r/0.55` deg per second
- In rps, `4*pi*r/0.55 / (2*pi*r)` = `2/0.55` = 3.64 rps
- In other words, shifting any trajectory as peripheral as you can before running into crowding should inflate the speed limit to 3.64 rps.
- This assumes that the average eccentricity of the displaced circle is equal to the eccentricity of its center. That's true that for a circle fully away from fixation. But when *interior of circle includes fixation, it would only work if eccentricities on other side were treated as negative. But they are instead positive eccentricities. Have to integrate*

## Crossing hemifields. A countervailing factor may be a cost for crossing between hemifields. I could address this by maybe moving it only partly off-center? What is the mean eccentricity for a circle at a particular eccentricity?




