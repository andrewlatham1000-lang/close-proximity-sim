# Close Proximity Orbital Dynamics Simulator

A physics engine modelling relative motion of close proximity objects in orbit with a graphical interface.


## Description

This project uses the equations for close proximity relative motion to model a series of objects relative to a target orbit. This simulation includes both rotational and translational dynamics, with the ability to model complex geometries, thrusters, and fuel consumption.


## Getting Started

### Dependencies

* Python libraries

  * NumPy
  * PyOpenGL
  * PyQt5


### Installing

* Just download everything 


### Executing Program

* In main.py, set mission\_path to the location of your chosen mission setup file
* Run main.py, this will start the GUI and load your mission
* The top bar of the GUI contains your time controls: play, pause, reset, warp up, warp down. These hopefully do not require much explanation. The top bar also shows the current time in the simulation
* The left dock of the GUI shows all the commands given in the mission setup, the highlighted command is next to be executed, while completed commands are greyed out
* The right dock allows you to view the real-time information of any object in your mission via a drop-down menu
* The centre of the GUI is the renderer showing the real-time position and rotation of all the Bodies in your mission


#### Missions

The "test\_mission.json" file contains and example mission to show how to set up bodies, shapes, fuel tanks, and thrusters, as well as construct a mission timeline. The commands available are currently limited to "add" and "burn", support for "set" and "solve" is planned".



### Terms \& Definitions

This section will define some of the terms used when describing how to build missions

* Shape - A shape is a simple geometric object which contains information about its position, rotation, mass, and inertia.
* Fuel tank - A composite object which contains both a shell shape of constant mass, and a solid object of "fuel" which decreases in mass when it is used up.
* Thruster - A point from which a thrust vector can be applied, thrusters are connected to a fuel tank, and stop working if that tank runs out of fuel.
* Body - A body is a composite object containing any number of shapes, fuel tanks, and thrusters. The equations of motion described below are applied to bodies.



### Reference Frames

The global reference frame for this simulation is the Local Vertical Local Horizontal (LVLH) frame. This is the frame shown by the GUI. However, Bodies within the simulation hold information in the body-fixed frame, as well as their position and rotation in the global frame to allow for conversion to the LVLH frame. Similarly, Shapes and other objects which make up the Body are defined in their own body-fixed frame, but hold their position and rotation relative to the body-fixed frame of the Body.


This setup allows for bodies to be more easily defined, and reduces the accumulation of error during simulation integration. The centre of mass and vertices for each shape in the LVLH frame are calculated as follows, including terms for camera zoom, position, and rotation:


### Equations of Motion

$$ 
1 + 1 = 2 
$$

Bodies observe translational motion by integrating relative motion equations, with the target parameters being given in the mission setup:
<img width="781" height="306" alt="image" src="https://github.com/user-attachments/assets/d91d5aee-8f38-413f-adf0-bec28e791672" />


This integration uses the Euler predictor-corrector method and is capable of retaining a high level of accuracy over an orbital period.

The equations for rotational motion are calculated from quarternions:



These equations update the position and rotation matrix of each body in the LVLH frame.



