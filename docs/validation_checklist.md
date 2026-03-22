# Validation Checklist

Run these commands from the repository root.

## 1. Environment

```bash
./tools/env_check.sh
```

Expected:

- Ubuntu `22.04`
- `/opt/ros/humble/setup.bash` exists
- `ROS_DISTRO=humble` after sourcing
- `python3` resolves inside `.venv/bin/python3`

## 2. Xacro Check

```bash
source ./tools/source_ros.sh
xacro bcr_ws/src/bcr_arm_description/urdf/robots/bcr_arm.urdf.xacro use_gazebo:=true use_camera:=false ros2_controllers_path:=$(pwd)/bcr_ws/src/bcr_arm_gazebo/config/ros2_controllers.yaml > /tmp/bcr_arm.urdf
check_urdf /tmp/bcr_arm.urdf
```

Expected:

- a valid URDF is produced
- `check_urdf` prints a successful parse summary

## 3. Build

```bash
./tools/build_ws.sh
```

Expected:

- `colcon build --symlink-install` completes
- `bcr_arm_description` and `bcr_arm_gazebo` are discoverable with `ros2 pkg list`

## 4. Launch Gazebo

```bash
./tools/run_gazebo.sh
```

Expected:

- Gazebo Sim starts
- the BCR arm is spawned from `robot_description`
- `joint_state_broadcaster` and `joint_trajectory_controller` are loaded

## 5. Controllers

In another sourced terminal:

```bash
source ./tools/source_ros.sh
source bcr_ws/install/setup.bash
ros2 control list_controllers
```

Expected:

- `joint_state_broadcaster` active
- `joint_trajectory_controller` active

## 6. Motion Test

```bash
./tools/run_motion_test.sh
```

Expected:

- the node publishes three motion goals
- the arm moves home -> test -> home
- the recorded demo can be saved as `moving_arm.mp4`

## 7. FK Node

```bash
./tools/run_fk.sh
```

Expected:

- joint states are received
- end-effector `(x, y, z)` values are printed
- if the FK node runs during motion, the values should change over time

## 8. AI Pipeline

```bash
./tools/run_ai_training.sh
```

Expected:

- dataset generated under `bcr_ws/src/bcr_arm_gazebo/data/`
- model saved under `bcr_ws/src/bcr_arm_gazebo/models/`
- plot saved under `bcr_ws/src/bcr_arm_gazebo/plots/`
- evaluation metrics printed
