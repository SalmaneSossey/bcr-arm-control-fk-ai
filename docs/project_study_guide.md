# Project Study Guide

This note is meant to help you understand the whole TP3 project quickly before an exam or oral presentation.

## 1. Project In One Minute

This project simulates a 7-DOF robot arm called the BCR arm in ROS 2 Humble and Gazebo Sim.

It does 4 main things:

1. loads the robot model from the provided `bcr_arm_description` package
2. connects the robot to `ros2_control` so controllers can command the joints
3. runs two Python nodes:
   one sends motion commands and one computes forward kinematics from `/joint_states`
4. adds an AI extension where a neural network learns to approximate forward kinematics

So the full idea is:

`robot description -> Gazebo simulation -> controllers -> motion command -> joint states -> FK computation -> AI approximation`

## 2. What Each Package Does

### `bcr_arm_description`

This package was already provided.

Its job is to describe the robot:

- meshes
- links and joints
- Xacro / URDF files
- `ros2_control` tags inside the robot description
- RViz assets

Important idea:
this package describes what the robot is.

### `bcr_arm_gazebo`

This package was created to complete the TP.

Its job is to run and control the robot:

- Gazebo launch file
- controller YAML
- motion test node
- forward kinematics node
- AI dataset / training / evaluation scripts

Important idea:
this package describes how the robot is launched, controlled, tested, and analyzed.

## 3. Main Folder Map

```text
tp3_robotics/
├── README.md
├── INSTALL_WSL_UBUNTU.md
├── docs/
│   ├── project_study_guide.md
│   ├── tp3_requirements_summary.md
│   ├── dh_notes.md
│   ├── results_summary.md
│   ├── report_todo.md
│   ├── troubleshooting.md
│   └── validation_checklist.md
├── tools/
├── bcr_ws/
│   └── src/
│       ├── bcr_arm_description/
│       └── bcr_arm_gazebo/
│           ├── launch/
│           ├── config/
│           ├── scripts/
│           ├── data/
│           ├── models/
│           └── plots/
└── moving_arm.mp4
```

## 4. Runtime Flow: What Happens When You Launch

When you run:

```bash
source tools/source_ros.sh
./tools/run_gazebo.sh
```

the launch file [`bcr_arm.gazebo.launch.py`](../bcr_ws/src/bcr_arm_gazebo/launch/bcr_arm.gazebo.launch.py) does the following:

1. processes the Xacro robot file from `bcr_arm_description`
2. builds the `robot_description` parameter
3. starts `robot_state_publisher`
4. starts Gazebo Sim
5. spawns the robot into Gazebo from `robot_description`
6. starts `joint_state_broadcaster`
7. starts `joint_trajectory_controller`

Important exam sentence:

The launch sequence is ordered deliberately. The robot must be spawned first, then the state broadcaster starts, then the trajectory controller starts.

## 5. Why `ros2_control` Matters

`ros2_control` is the bridge between the simulated robot hardware and the ROS 2 controllers.

In this project:

- Gazebo provides the simulated robot
- `gz_ros2_control` exposes the joints as controllable interfaces
- `controller_manager` loads the controllers

The controller file is:

[`ros2_controllers.yaml`](../bcr_ws/src/bcr_arm_gazebo/config/ros2_controllers.yaml)

It defines:

- `joint_state_broadcaster`
- `joint_trajectory_controller`

### Role of Each Controller

`joint_state_broadcaster`

- publishes current joint positions and velocities
- this is why `/joint_states` exists

`joint_trajectory_controller`

- receives trajectory commands
- moves `joint1` to `joint7`
- accepts position commands in this project

Important exam sentence:

The motion script does not move the robot directly. It publishes a `JointTrajectory` message to the trajectory controller, and the controller drives the joints.

## 6. Motion Test Script

The motion script is:

[`test_arm_movement.py`](../bcr_ws/src/bcr_arm_gazebo/scripts/test_arm_movement.py)

It publishes on:

`/joint_trajectory_controller/joint_trajectory`

It sends three goals:

1. home pose
2. test pose
3. home pose again

The test pose is:

```text
[0.5, -0.5, 0.3, -0.7, 0.2, 0.4, 0.1]
```

Each motion uses a duration of 3 seconds.

Important exam sentence:

This script is a simple validation node. Its goal is to prove that the robot accepts trajectory commands and that the controllers are configured correctly.

## 7. Forward Kinematics Script

The FK script is:

[`forward_kinematics.py`](../bcr_ws/src/bcr_arm_gazebo/scripts/forward_kinematics.py)

It subscribes to:

`/joint_states`

It then:

1. extracts `joint1` to `joint7`
2. builds a DH transform for each joint
3. multiplies the transforms cumulatively
4. prints the end-effector position `(x, y, z)`

### Core Function

The central mathematical function is:

`dh_matrix(theta, d, a, alpha)`

It implements the standard DH transform:

```text
A_i = RotZ(theta_i) * TransZ(d_i) * TransX(a_i) * RotX(alpha_i)
```

### Geometry Used

The script uses these dimensions:

- `L1 = 0.200`
- `L2_offset = 0.065`
- `L3 = 0.410`
- `L4_offset = -0.065`
- `L5 = 0.310`
- `L6_offset = 0.060`
- `L7 = 0.105`

These values are documented again in [`dh_notes.md`](dh_notes.md).

Important exam sentence:

The FK node uses the live joint states coming from the simulation, so it computes the end-effector position from the robot's actual current pose in Gazebo.

## 8. DH Model: What You Need To Say

The project uses a clean educational DH-style model aligned with:

- the URDF geometry
- the alternating joint-axis structure
- the dimensions visible in the Xacro files

This is important:

The FK model is a documented approximation designed to be consistent with the robot description and suitable for the assignment.

If asked why this is acceptable, a good answer is:

The assignment requires a DH-based FK implementation. The script uses a consistent DH convention with dimensions extracted from the robot description, which is enough to compute and explain the end-effector position.

## 9. AI Part: What It Does

The AI extension is Option A: MLP regression.

The goal is to learn this mapping:

```text
[q1, q2, q3, q4, q5, q6, q7] -> [x, y, z]
```

### Step 1: Dataset Generation

Script:

[`generate_fk_dataset.py`](../bcr_ws/src/bcr_arm_gazebo/scripts/generate_fk_dataset.py)

It:

- samples random joint configurations within joint limits
- computes analytical FK for each sample
- saves the result to CSV

Each row contains:

```text
q1 q2 q3 q4 q5 q6 q7 x y z
```

### Step 2: Model Training

Script:

[`train_fk_mlp.py`](../bcr_ws/src/bcr_arm_gazebo/scripts/train_fk_mlp.py)

Model architecture:

- input: 7
- hidden layer 1: 64 + ReLU
- hidden layer 2: 128 + ReLU
- hidden layer 3: 64 + ReLU
- output: 3

Other important details:

- dataset split: `70% train / 15% validation / 15% test`
- loss: MSE
- optimizer: Adam
- epochs: `150`

It also normalizes both inputs and outputs before training.

### Step 3: Evaluation

Script:

[`evaluate_fk_mlp.py`](../bcr_ws/src/bcr_arm_gazebo/scripts/evaluate_fk_mlp.py)

It:

- loads the saved model
- loads normalization statistics
- predicts end-effector positions
- compares true FK vs predicted FK
- prints MAE and RMSE for selected examples

### Why This AI Part Matters

Analytical FK is exact according to the chosen mathematical model.

The neural network is not replacing the math; it is learning an approximation of the FK function from data.

Important exam sentence:

The AI module demonstrates that a neural network can approximate the analytical forward kinematics mapping from joint space to Cartesian position.

## 10. Important Outputs

### Simulation / Control Evidence

- Gazebo screenshot: [`docs/media/gazebo_arm_render.png`](media/gazebo_arm_render.png)
- motion video: [`moving_arm.mp4`](../moving_arm.mp4)

### AI Evidence

- dataset: [`fk_dataset.csv`](../bcr_ws/src/bcr_arm_gazebo/data/fk_dataset.csv)
- model: [`fk_mlp.pt`](../bcr_ws/src/bcr_arm_gazebo/models/fk_mlp.pt)
- metrics: [`fk_mlp_metrics.json`](../bcr_ws/src/bcr_arm_gazebo/models/fk_mlp_metrics.json)
- training plot: [`fk_mlp_loss.png`](../bcr_ws/src/bcr_arm_gazebo/plots/fk_mlp_loss.png)
- comparison examples: [`fk_prediction_examples.csv`](../bcr_ws/src/bcr_arm_gazebo/plots/fk_prediction_examples.csv)

## 11. Commands You Should Remember

### Setup

```bash
cd ~/Tps/tp3_robotics
./tools/setup_venv.sh
source tools/source_ros.sh
./tools/build_ws.sh
```

### Launch Simulation

```bash
./tools/run_gazebo.sh
```

### Run FK Node

```bash
./tools/run_fk.sh
```

### Run Motion Test

```bash
./tools/run_motion_test.sh
```

### Check Controllers

```bash
ros2 control list_controllers
```

### Run AI Pipeline

```bash
./tools/run_ai_training.sh
```

## 12. What To Say During A Demo

Here is a short oral script you can use:

1. This workspace reuses the provided BCR arm description package and adds the missing Gazebo and control layer.
2. The launch file starts Gazebo, publishes `robot_description`, spawns the robot, and then loads the ROS 2 controllers.
3. The `joint_state_broadcaster` publishes `/joint_states`, while the `joint_trajectory_controller` executes trajectory commands for the seven joints.
4. The motion node sends a simple home -> test -> home sequence to validate control.
5. The FK node listens to `/joint_states` and computes the end-effector position using DH matrices.
6. Finally, the AI extension generates FK data and trains an MLP to approximate the mapping from joint angles to Cartesian position.

## 13. Likely Exam Questions And Short Answers

### What is the role of the URDF/Xacro?

It defines the robot structure: links, joints, visuals, collisions, and control tags.

### Why use `robot_state_publisher`?

It publishes the TF tree from the robot description and the joint states.

### Why do we need `joint_state_broadcaster`?

Because the system needs a standard ROS topic that publishes the current joint states.

### Why do we need `joint_trajectory_controller`?

Because it executes commanded trajectories for the robot joints in a structured way.

### What is `/joint_states` used for here?

It is the live input to the forward kinematics node.

### What is the difference between analytical FK and AI FK?

Analytical FK computes the pose from equations. AI FK learns an approximation from generated data.

### Why normalize the data in training?

Because normalized features help the neural network train more stably and converge better.

### Why is the arm static sometimes?

Because once the controller reaches the commanded pose, it holds that position until a new command arrives.

## 14. Common Confusions

### "Did the Python motion script move the robot directly?"

No. It only publishes a trajectory message. The controller performs the actual execution.

### "Is the FK node controlling the arm?"

No. It is read-only. It only listens to joint states and computes position.

### "Did the AI train on simulator images?"

No. It trained on numerical joint-angle / end-effector-position data generated from analytical FK.

### "Is the AI required to control the robot?"

No. It is an extension that approximates FK, not the main controller.

## 15. If You Only Memorize Five Things

1. `bcr_arm_description` describes the robot, `bcr_arm_gazebo` runs and tests it.
2. Gazebo + `gz_ros2_control` + `controller_manager` make the simulated joints controllable.
3. The motion script publishes a `JointTrajectory` to the trajectory controller.
4. The FK script listens to `/joint_states` and computes `(x, y, z)` with DH matrices.
5. The AI module learns the mapping from seven joint angles to end-effector position.

## 16. Best Supporting Docs

Use these if you want more detail:

- [`README.md`](../README.md)
- [`tp3_requirements_summary.md`](tp3_requirements_summary.md)
- [`dh_notes.md`](dh_notes.md)
- [`results_summary.md`](results_summary.md)
- [`validation_checklist.md`](validation_checklist.md)
- [`report_todo.md`](report_todo.md)
