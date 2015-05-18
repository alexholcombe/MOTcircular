Circular speed the limiting factor?
==============

## Experiment: Square vs. circle

- Adding modulations to the trajectory has little effect, in other words rotational speed is the determinant.  
- First, blast the annoying speed limit people with a square trajectory. This finally helps answer those interested in linear speed limit
- Compare square trajectory to circular at two eccentricities. Got some data for me with 1 target, but then remembered I'd like to use two targets whenever on center to avoid being blur-limited.

Results
- Critical issue is speed limit of smaller-radius one when not concentric. Smaller one is always ringToQuery=0. Speed limit for me is lower by about 0.4rps.


## Experiment: Modulate radius

- Modulation of radius as function of time. Radius calls function to determine its value at each time.
- Spatial modulation of radius, yielding a radial frequency pattern. This is something added to radius, is function of angle.

Should also be a function of time? But if the idea is to know/determine individual objects' trajectories, then reversals will mess it up.
Is it about individual object paths or not?