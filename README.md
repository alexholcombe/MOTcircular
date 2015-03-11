Multiple object tracking experiment
==============
This program is super-complicated, legacy of many different papers using tracking. I don't recommend you use it without my guidance. My other repositories, such as attentional-blink, are more user-friendly.

Want to add
- Sinusoidal modulation of radius. Radius calls function to determine its value at each time step. 
- Add waveform to the trajectory. This is something added to each object's radius as function of its angle. Set up as function call so can be arbitrary function.

How do we handle reversals? Reversals necessitate integration. So, either pre-generated trajectories or something really complicated with 
We already use incremental changes to the angle, which presently count on not missing a frame. I should probably start by functionising the position accumulation.

In the long term, want to set up exchange of objects among rings. Necessary to conduct an identity-tracking experiment. Can also push harder on speed limit that way.

issues
- line 513