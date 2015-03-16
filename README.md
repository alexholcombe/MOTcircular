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

Experiments
- Is the speed limit the same in the periphery, when not rotating about fixation?
-- Use 2 targets, because less cognitive contamination, with different eccentricities so can have an exactly-comparable condition at fixation.
-- Run interleaved concentric versus out to side

Issues
-Fix 
%corr order report=  76.24 % of  101  trials %corr each speed:  [ 0.45  1.    0.57  0.8   1.  ]
				num trials each speed = [ 20.  20.  21.  20.  20.]
				
 79.21 % of  101  trials %corr each speed:  [ 0.55  1.    0.55  0.85  1.  ]
				num trials each speed = [ 20.  20.  20.  20.  21.]
That is wrong, actual is
1.20 1.000
2  1.40 1.000
3  1.80 0.825

-Initialise numRings lists better
4  2.00 0.550
5  2.25 0.500
