## Design the geometry for a multi-shanks probe 

In the latest version of HERBS, we provide user a flexible functionality to 
design for multi-shank probes.

A example of a multi-shanks probe is shown as follows,
<p align="center">
<img src="../../image/probe_related/multi_probe.jpg" width="45%">
</p>

For the pre-planing, the positive direction of y-stack is always 
assumed to be facing to the users who sit in front of the screen. 
That means, the positive y-stack is "Out", whereas the negative y-stack is 'In'.

For the after-surgery reconstruction, the positive of y-stack is always assumed to be "Up", as shown in the following figure,
<p align="center">
<img src="../../image/probe_related/multi_probe_man.jpg" width="45%">
</p>


### Pre-plan the probe

<p style="font-size:120%; color:red">When using the multi-shanks mode and the mult-shanks probe settings is valid, 
the <b>Site Face Direction</b> combobox will have no effect on a single probe.</p>

1. After loading the atlas and click the <b>Probe Marker</b> tool button, 
select the probe you would like to use and check the <b>Multi-shanks Switch</b> button. 
Here we use Neuropixels 1.0 probe for example.

<p align="center">
<img src="../../image/probe_related/mp1.jpg" width="100%">
</p>

2. Click the <b>Object</b> menu --> <b>Multi-Probe Planning</b> submenu, 
a designer window will pop up and an example is shown in the window.
<p align="center">
<img src="../../image/probe_related/mp2.jpg" width="40%">
</p>

3. Design the geometry for the probe, here we would like to have 5 probes/shanks, 
and 4 of them lie along the x-axis with y values to be 0. 
That means when we click the trajectories on the 2D section window, 4 lines will show up.
<p align="center">
<img src="../../image/probe_related/mp4.jpg" width="80%">
</p>

4. Click trajectories on Atlas section window.
<p align="center">
<img src="../../image/probe_related/mp5.jpg" width="80%">
</p>

5. Even though only 4 lines show up in the 2D window, when we add pieces, 5 probes will show up.
<p align="center">
<img src="../../image/probe_related/mp6.jpg" width="40%">
</p>