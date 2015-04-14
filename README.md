Multiple object tracking experiment
==============
This program is super-complicated, legacy of many different papers using tracking. I don't recommend you use it without my guidance. My other repositories, such as attentional-blink, are more user-friendly.

New
- Modulation of radius as function of time. Radius calls function to determine its value at each time.
- Spatial modulation of radius, yielding a radial frequency pattern. This is something added to radius, is function of angle.

Should also be a function of time? But if the idea is to know/determine individual objects' trajectories, then reversals will mess it up.
Is it about individual object paths or not?

In the long term, want to set up exchange of objects among rings. Necessary to conduct an identity-tracking experiment. Can also push harder on speed limit that way.

Issues
-Look for eyetracking files (as created by Jedi Fajou) and exclude those trials
-So that github can track the loadRawDataFile, have it pull a code from an untracked file.
