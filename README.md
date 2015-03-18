Multiple object tracking experiment
==============
This program is super-complicated, legacy of many different papers using tracking. I don't recommend you use it without my guidance. My other repositories, such as attentional-blink, are more user-friendly.

New
- Modulation of radius as function of time. Radius calls function to determine its value at each time.
- Spatial modulation of radius, yielding a radial frequency pattern. This is something added to radius, is function of angle.

Should also be a function of time? But if the idea is to know/determine individual objects' trajectories, then reversals will mess it up.
Is it about individual object paths or not?

How do we handle reversals? Reversals necessitate integration. So, either pre-generated trajectories or current system of incremental changes to the angle, which presently count on not missing a frame. I should probably start by functionising the position accumulation.

In the long term, want to set up exchange of objects among rings. Necessary to conduct an identity-tracking experiment. Can also push harder on speed limit that way.

## Experiment: Concentric vs. peripheral
Is the speed limit the same in the periphery, when not rotating about fixation?
- Use 2 targets, because less cognitive contamination, with different eccentricities so can have an exactly-comparable condition at fixation.
- Downside of 2 targets is that when concentric you can occasionally group them. That will make concentric look better than it should.
- We know the speed limit can't be a blur-limited limit because temporal blurring length is proportional to linear speed, not rps. So in periphery, looks really blurred yet speed limit doesn't go down much. (Ultimately temporal blurring predicts a tf limit but already shown that doesn't hit until 7 Hz, far faster than 2 rps).
- Could do it with 1 target, but then have the eye movements problem and worse blurring problem at 120 Hz. Somewhat mitigated by having both orbits present but only one with a target.
- Have to just use single ring? Although there will always be a confound between crossing hemifields and not. Speed limit could conceivably even have been one of crossing hemifields. Yes, so I'm testing that hypothesis.

Theory
- Neurons-per-unit-time theory is that the speed limit is caused by an amount of time required to deselect neurons corresponding to old locations and select neurons corresponding to new locations.
-- On this theory, the reason speed limit is approximately the same for higher eccentricity is that # of neurons one needs to select/deselect per degree of visual angle decreases by 2*pi for every unit increase in deg of visual angle. 
-- In other words, neurons at 5 deg ecc are spaced 2pi further apart than are neurons at 4 deg ecc. 
-- This makes a prediction for what will happen when we move a trajectory into the periphery. When we move something from a mean eccentricity of 2.5 to a mean eccentricity of 6.7, that's an increase of 4.2 deg. So we'd have to increase the distance traveled by 8.4pi to have the same level of performance.
Instead, we didn't increase the distance traveled at all. That means that the speed limit should now be much higher. I guess it should be 8.4pi times higher.

-Crowding. A countervailing factor to reduce the speed limit could be crowding. While that may be an issue for the smaller-radius trajectory, crowding shouldn't apply to the larger-radius trajectory.
Speed limit in deg/sec (e) = 2*pi*e
So speed limit at e=6.7 = 2*pi*6.7deg/sec.   I instead test a distance traveled of 5*pi there, where 2 rps will  To reach speed

   x=pi
Speed l

I should be able to write down a function that relates eccentricity to speed limit per deg traveled.

- Went from mean eccentricity of 2.5 to centered on -6,3 which has eccentricity of 6.7. Mean eccentricity of that circle is then what?  Anyway, speed limit should go down by a factor of 2 according to the number of neurons crossed theory? 
According to 

Results
- Critical issue is speed limit of smaller-radius one when not concentric. Smaller one is always ringToQuery=0. Speed limit for me is lower by about 0.4rps.



Issues
- How do I recursively change n-dimensional array into a list
- Still not seeing progress message.
- Add dialog box, for Arni
- Initialise numRings lists better
