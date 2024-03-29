# Flight-Control
This repository contains information and contents for flight control and is supervised by prof. Moritz Diehl as a part of academics, University of Freiburg.

Abbreviations:
- MPC - Model Predictive Control 
- CF - Crazy-Flie drone module

![image](https://user-images.githubusercontent.com/14985440/209779929-f99364ab-e37d-41b7-8ba9-7d6061df09ba.png)

The theory notes in this repository are self explanatory but requires prior knowledge of notations and exposure to control eqautions.

The optimization software library used in this repository is Rockit. It is a specialized optimization library designed specifically for model predictive control (MPC) problems. It is built on top of CasADi and provides additional functionality for handling MPC-specific constraints and dynamics. Rockit includes a variety of methods for solving MPC problems, including multiple shooting and direct collocation.
We use Multiple shooting method in this project.

![PlotWithObstacles](https://user-images.githubusercontent.com/14985440/224574973-c0256fd3-d872-4258-91a3-0e3bd1fbe8eb.png)

Plot showing simulation results, with 3 obstacles and a reference point as goal.

Discussion/Problems:
1. https://github.com/orgs/bitcraze/discussions/528#discussion-4776334
2. https://github.com/orgs/bitcraze/discussions/535#discussion-4795575

DONE:
- Simple visualization of controls on flight path but without considering exact equations. (Formulation)
- Visualize with motion equations. (Formulation)
- Implement controls with MPC. (Formulation)
- Add static obstacles to the objective function and frame the constraints related to it. (Formulation)
- Operate crazy-flie drone in pitch-roll invariant frame. (Literature)
- Tested velocity commands with Flowdeck and Multiranger. (Testing)
- Tested and callibrated positions with Lighthouse positioning system. (Testing)
- Offline drone movement with MPC generated velocities with time-delays. (Testing)
- Online drone manuever with state-estimation. (Testing) (Final reference reached is bit-inaccurate)

TODO:
- Debug why, final reference state reached is invloved with inaccuracy.
- Add dynamic obstacles to the objective function and frame the constraints related to it.
