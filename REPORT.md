# TP3 Report

## Title

Simulation, Forward Kinematics, and Neural Network Approximation for the 7-DOF BCR Arm in ROS 2 Humble

## 1. Introduction

This project implements a complete ROS 2 Humble simulation workflow for the 7-degree-of-freedom Black Coffee Robotics arm. The work reuses the provided `bcr_arm_description` package and adds the missing simulation, control, forward kinematics, and AI approximation layers required by the assignment.

The final system is able to:

- launch the BCR arm in Gazebo Sim
- configure `ros2_control` for the seven revolute joints
- drive the arm through a scripted trajectory
- compute the analytical forward kinematics from live joint states
- train a neural network to approximate the analytical FK mapping
- compare analytical and learned FK online during execution

## 2. Objectives

The main objectives of this TP were:

1. verify the ROS 2 Humble environment in WSL Ubuntu
2. reuse the supplied robot description instead of recreating the arm model
3. create the missing `bcr_arm_gazebo` package
4. connect the robot to Gazebo Sim and `ros2_control`
5. configure the joint state broadcaster and trajectory controller
6. implement a Python motion test node
7. implement a forward kinematics node based on DH matrices
8. implement an AI extension using a neural network
9. validate the whole workspace and prepare deliverable documentation

## 3. Software Environment

The project was validated in the following environment:

- Ubuntu `22.04.5 LTS (Jammy)` under WSL2
- ROS 2 `Humble`
- Gazebo Sim via `ros_gz_sim`
- Python `3.10`
- repo-local virtual environment `.venv`
- CPU-only PyTorch

## 4. Workspace Structure

The workspace is organized as follows:

```text
tp3_robotics/
├── README.md
├── REPORT.md
├── INSTALL_WSL_UBUNTU.md
├── docs/
├── tools/
├── .vscode/
└── bcr_ws/
    └── src/
        ├── bcr_arm_description/
        └── bcr_arm_gazebo/
```

The role of each package is:

- `bcr_arm_description`: provided robot model, URDF/Xacro, meshes, and `ros2_control` hooks
- `bcr_arm_gazebo`: Gazebo launch, controller configuration, FK scripts, and AI scripts

## 5. Robot Description Reuse

The provided `bcr_arm_description` package already contained the main robot description:

- meshes for the BCR arm
- Xacro/URDF robot structure
- `ros2_control` integration files
- launch and RViz assets

This package was reused directly as required by the assignment. Only the missing simulation-and-validation layer was added around it.

## 6. Gazebo and ros2_control Integration

The missing package `bcr_arm_gazebo` was created as an `ament_cmake` package.

Its main components are:

- `launch/bcr_arm.gazebo.launch.py`
- `config/ros2_controllers.yaml`
- `scripts/test_arm_movement.py`
- `scripts/forward_kinematics.py`
- `scripts/predict_fk_mlp.py`
- `scripts/compare_fk_streams.py`

The Gazebo launch file performs the following sequence:

1. process the main robot Xacro file
2. publish the `robot_description`
3. start `robot_state_publisher`
4. launch Gazebo Sim
5. spawn the robot into the world
6. load and activate `joint_state_broadcaster`
7. load and activate `joint_trajectory_controller`

The controller configuration uses:

- `joint_state_broadcaster`
- `joint_trajectory_controller`

for the seven joints:

- `joint1`
- `joint2`
- `joint3`
- `joint4`
- `joint5`
- `joint6`
- `joint7`

The command interface is `position`, while the exported state interfaces are `position` and `velocity`.

## 7. Motion Test Node

The motion validation script publishes a `trajectory_msgs/JointTrajectory` message on:

`/joint_trajectory_controller/joint_trajectory`

It sends three consecutive targets:

1. home pose: `[0, 0, 0, 0, 0, 0, 0]`
2. test pose: `[0.5, -0.5, 0.3, -0.7, 0.2, 0.4, 0.1]`
3. return to home

Each motion is executed over approximately 3 seconds.

### Motion Test Terminal Evidence

```text
[INFO] [test_arm_movement]: Ready to publish home -> test -> home trajectory goals.
[INFO] [test_arm_movement]: Published home goal with 3.0 s duration: [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
[INFO] [test_arm_movement]: Published test goal with 3.0 s duration: [0.5, -0.5, 0.3, -0.7, 0.2, 0.4, 0.1]
[INFO] [test_arm_movement]: Published home goal with 3.0 s duration: [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
[INFO] [test_arm_movement]: Motion test complete.
```

This confirms that the controller accepted and executed the command sequence.

## 8. Forward Kinematics

The analytical FK node subscribes to `/joint_states` and computes the end-effector position using Denavit-Hartenberg matrices.

The implemented standard DH transform is:

```text
A_i = RotZ(theta_i) * TransZ(d_i) * TransX(a_i) * RotX(alpha_i)
```

### Geometric Parameters Used

- `L1 = 0.200`
- `L2_offset = 0.065`
- `L3 = 0.410`
- `L4_offset = -0.065`
- `L5 = 0.310`
- `L6_offset = 0.060`
- `L7 = 0.105`

### Functional Behavior

The node now performs three actions:

1. subscribes to `/joint_states`
2. republishes the ordered 7-joint vector on `/bcr_arm/joint_vector`
3. publishes the analytical end-effector position on `/bcr_arm/fk/analytical`

### FK Terminal Evidence

During motion, the end-effector position changed as expected. For example:

```text
[INFO] [forward_kinematics]: End-effector position -> x=0.1735 m, y=0.0189 m, z=1.0153 m
[INFO] [forward_kinematics]: End-effector position -> x=0.3229 m, y=0.0860 m, z=0.9691 m
[INFO] [forward_kinematics]: End-effector position -> x=0.4269 m, y=0.1778 m, z=0.8991 m
[INFO] [forward_kinematics]: End-effector position -> x=0.4961 m, y=0.2952 m, z=0.8006 m
```

This confirms that the FK node was reading live joint states and computing the current Cartesian position of the end-effector.

## 9. AI Extension: Neural Network for Kinematic Approximation

The chosen AI option is:

`Neural networks for kinematic approximation`

More precisely, the project uses a multilayer perceptron to approximate the mapping:

```text
[q1, q2, q3, q4, q5, q6, q7] -> [x, y, z]
```

### 9.1 Dataset Generation

The dataset generation script:

- samples random valid joint configurations
- computes the analytical FK target for each sample
- stores the result in CSV format

The generated dataset contains:

- `10000` samples
- `7000` train samples
- `1500` validation samples
- `1500` test samples

### 9.2 MLP Architecture

The neural network architecture is:

- input layer: `7`
- hidden layer 1: `64` neurons + ReLU
- hidden layer 2: `128` neurons + ReLU
- hidden layer 3: `64` neurons + ReLU
- output layer: `3`

The network predicts:

- `x`
- `y`
- `z`

### 9.3 Training Configuration

- optimizer: Adam
- loss: MSE
- epochs: `150`
- batch size: `128`
- CPU-only PyTorch

### 9.4 Saved Artifacts

- trained model: `bcr_ws/src/bcr_arm_gazebo/models/fk_mlp.pt`
- metrics file: `bcr_ws/src/bcr_arm_gazebo/models/fk_mlp_metrics.json`
- training plot: `bcr_ws/src/bcr_arm_gazebo/plots/fk_mlp_loss.png`
- comparison examples: `bcr_ws/src/bcr_arm_gazebo/plots/fk_prediction_examples.csv`

## 10. AI Results

The current measured test metrics are:

| Metric | X | Y | Z |
|---|---:|---:|---:|
| MAE | 0.106253 | 0.112794 | 0.072709 |
| RMSE | 0.134917 | 0.140585 | 0.093391 |

These results show that the neural network is able to approximate the analytical FK reasonably well, while still exhibiting visible error, especially during motion and off-center poses.

## 11. Live Analytical vs Predicted FK Comparison

To strengthen the AI validation, the project was extended with two live ROS 2 nodes:

- `predict_fk_mlp.py`
- `compare_fk_streams.py`

### Online Predictor

The predictor node:

- loads the trained model once at startup
- subscribes to `/bcr_arm/joint_vector`
- publishes predicted end-effector position on `/bcr_arm/fk/predicted`

### Comparison Node

The comparison node:

- subscribes to `/bcr_arm/fk/analytical`
- subscribes to `/bcr_arm/fk/predicted`
- reports the coordinate-wise delta and Euclidean error

### Terminal Evidence: Static Pose

At the home pose, the comparison output was:

```text
analytical=(0.0600, 0.0000, 1.0250) m
predicted=(-0.0539, 0.0484, 1.0386) m
delta=(-0.1139, 0.0484, 0.0136) m
euclidean_error=0.1245 m
```

### Terminal Evidence: Motion Phase

During the movement toward the commanded test pose, the comparison node reported for example:

```text
analytical=(0.2799, 0.0608, 0.9872) m | predicted=(0.0684, 0.1463, 1.0359) m | euclidean_error=0.2332 m
analytical=(0.3989, 0.1473, 0.9230) m | predicted=(0.1794, 0.2241, 0.9821) m | euclidean_error=0.2400 m
analytical=(0.4772, 0.2527, 0.8375) m | predicted=(0.2551, 0.3137, 0.8828) m | euclidean_error=0.2347 m
```

This demonstrates that the network follows the global motion trend but still differs from the analytical FK by a noticeable margin. That behavior is acceptable in this project because the AI objective is approximation rather than exact symbolic computation.

## 12. Gazebo Validation

The Gazebo launch output confirmed that:

- the robot was spawned successfully from `robot_description`
- all seven joints were loaded by `gz_ros2_control`
- the hardware interface was configured and activated
- `joint_state_broadcaster` was loaded and activated
- `joint_trajectory_controller` was loaded and activated

Example evidence from the Gazebo terminal:

```text
[spawn_bcr_arm]: OK creation of entity.
[controller_manager]: Loading controller 'joint_state_broadcaster'
[spawner_joint_state_broadcaster]: Configured and activated joint_state_broadcaster
[controller_manager]: Loading controller 'joint_trajectory_controller'
[spawner_joint_trajectory_controller]: Configured and activated joint_trajectory_controller
```

This confirms that the simulation-control pipeline is operational.

## 13. Discussion

The project successfully meets the core educational goals:

- reuse of the given robot description
- Gazebo integration
- controller configuration
- joint-space command execution
- analytical FK computation
- AI-based approximation of FK

The analytical FK remains the reference method because it is derived from the mathematical model of the manipulator. The neural network is valuable as a learned approximation that can infer end-effector coordinates quickly after training, but it is naturally less precise than the analytical model.

The live comparison module makes this trade-off visible in a very clear way.

## 14. Limitations

- Gazebo GUI under WSLg can produce rendering warnings depending on the graphics stack.
- The DH model is an educational DH-style approximation aligned with the URDF dimensions and joint-axis layout.
- The MLP predicts only end-effector position `(x, y, z)`, not full orientation.
- The prediction error remains significant for some poses, especially while the arm is moving through more complex configurations.

## 15. Conclusion

This TP3 project delivers a complete ROS 2 Humble simulation workflow for the 7-DOF BCR arm. The system launches successfully in Gazebo, executes commanded joint trajectories, computes analytical forward kinematics online, and includes a working AI extension based on a multilayer perceptron trained on analytically generated FK data.

The added live comparison between analytical FK and learned FK strengthens the project by showing both the usefulness and the limitations of neural approximation in robotics.

## 16. Submission Assets

The following files can be referenced directly in the final submission:

- project overview: `README.md`
- installation notes: `INSTALL_WSL_UBUNTU.md`
- report scaffold: `REPORT.md`
- DH notes: `docs/dh_notes.md`
- validation summary: `docs/results_summary.md`
- Gazebo screenshot: `docs/media/gazebo_arm_render.png`
- motion video: `moving_arm.mp4`
- MLP metrics: `bcr_ws/src/bcr_arm_gazebo/models/fk_mlp_metrics.json`
- loss plot: `bcr_ws/src/bcr_arm_gazebo/plots/fk_mlp_loss.png`
- prediction examples: `bcr_ws/src/bcr_arm_gazebo/plots/fk_prediction_examples.csv`
