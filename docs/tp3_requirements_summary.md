# TP3 Requirements Summary

TP3 expects a complete ROS 2 simulation and validation workflow for the 7-DOF BCR Arm.

## Core Deliverables

- reuse the supplied robot description and meshes
- provide a valid 7-DOF URDF/Xacro description
- expose ROS 2 control interfaces
- integrate the arm with Gazebo Sim
- configure a controller manager, joint state broadcaster, and trajectory controller
- launch the robot cleanly in simulation
- command the arm from Python
- compute forward kinematics from joint states

## AI Extension

Option A is implemented here:

- generate an FK dataset from random 7-joint samples
- train an MLP regressor from joint values to end-effector `(x, y, z)`
- evaluate MAE and RMSE
- save the trained model and training plot
- compare analytical FK against neural predictions

## Report Expectations

- DH table
- transform matrix derivation notes
- Gazebo screenshots
- controller / motion validation
- AI training and evaluation results
- file inventory and demo checklist
