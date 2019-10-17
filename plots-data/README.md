## Plots & Data
Inside this folder are the output from many of the scripts in this repository. The three subfolders are:

- data_FCS:	analysis for engineering data
- star_drift:	analysis for drift tracking for the stars
- slit_drift:	analysis for drift tracking for the entire mask
- seeing:	analysis for seeing tracking for the stars

The key thing to note here is that if MOSFIRE has an internal FCS issue, this could be seen in this data if both the star and slit are showing drift over time.  If only the star is showing a drift over time, then it's likely a guider flexure issue (with possible complications due to differential atmospheric refraction, or DAR).
