# Flight-Control
This repository contains information and contents for flight control.

Abbreviations:
- MPC - Model Predictive Control 
- CF - Crazy-Flie drone module

![image](https://user-images.githubusercontent.com/14985440/209779929-f99364ab-e37d-41b7-8ba9-7d6061df09ba.png)

The theory notes in this repository are self explanatory but requires prior knowledge of notations and exposure to control eqautions.

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

TODO:
- Online drone manuever with state-estimation. (30% DONE) (Testing)
- Add dynamic obstacles to the objective function and frame the constraints related to it.
