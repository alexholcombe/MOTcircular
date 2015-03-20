Specific experiments
==============

## Experiment: Concentric vs. peripheral
Is the speed limit the same in the periphery, when not rotating about fixation?
- See [theory](analysis/theory.md) for uncrowded stimulus choice and prediction
- To eyetrack or not to eyetrack? Could include the flicker-revealer and appeal to past recordings of these participants.. Or ask Chris to show me his code, pay someone to go through the trials and find those that must be excluded.
- Use 2 targets, because less cognitive contamination, with different eccentricities so can have an exactly-comparable condition at fixation.
- Downside of 2 targets is that when concentric you can occasionally group them. That will make concentric look better than it should.
- We know the speed limit can't be a blur-limited limit because temporal blurring length is proportional to linear speed, not rps. So in periphery, looks really blurred yet speed limit doesn't go down much. (Ultimately temporal blurring predicts a tf limit but already shown that doesn't hit until 7 Hz, far faster than 2 rps).
- Could do it with 1 target, but then have the eye movements problem and worse blurring problem at 120 Hz. Somewhat mitigated by having both orbits present but only one with a target.
- Have to just use single ring? Although there will always be a confound between crossing hemifields and not. Speed limit could conceivably even have been one of crossing hemifields. Yes, so I'm testing that hypothesis.

3 conditions
- One trajectory, centered.  r=6
- One trajectory, a bit off center. e=5
- One trajectory, way off center. e=10 or 11
- Crossed with a second factor which puts the periphery one in each quadrant, yielding 12 conditions. Actually that's a bit too many conditions, so let's only go left and right, not up and down also.

So the centered one won't happen very often because the two others each have two versions, making a total of 5 conditions.

Seem to need more cuingTime because gotta get oneself stably fixating even when not center

## Experiment: Circular speed is the limiting factor

- Adding modulations to the trajectory has little effect, in other words rotational speed is the determinant.  
- First, blast the annoying speed limit people with a square trajectory. This finally helps answer those interested in linear speed limit
- Compare square trajectory to circular and to a big modulation.

Results
- Critical issue is speed limit of smaller-radius one when not concentric. Smaller one is always ringToQuery=0. Speed limit for me is lower by about 0.4rps.


