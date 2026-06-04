# TP5 Pick-and-Place

This package adds the TP5 pipeline on top of the TP3 BCR Arm workspace:

- RGB-D camera on a fixed overhead support above the table
- Gazebo pick scene with a table and `target_cup`
- ROS-Gazebo bridge for `/camera/image`, `/camera/depth_image`, `/camera/points`, and `/camera/camera_info`
- PointCloud2 to NumPy conversion
- Open3D RANSAC plane removal and DBSCAN object clustering
- TP4 DGCNN classifier loaded from `/home/salmane/Tps/tp4_for_tp5`
- damped least-squares IK for the 7-DOF arm
- quintic joint trajectory publishing to `/joint_trajectory_controller/joint_trajectory`

## Dependencies

ROS 2 / Gazebo packages:

```bash
sudo apt update
sudo apt install -y \
  ros-humble-ros-gz-sim \
  ros-humble-ros-gz-bridge \
  ros-humble-gz-ros2-control \
  ros-humble-ros2-control \
  ros-humble-ros2-controllers \
  ros-humble-xacro \
  ros-humble-sensor-msgs-py \
  ros-humble-cv-bridge \
  ros-humble-vision-msgs
```

Python packages:

```bash
/usr/bin/python3 -m pip install --user open3d
/usr/bin/python3 -m pip install --user --index-url https://download.pytorch.org/whl/cpu torch
```

This workspace currently has pyenv Python ahead of system Python. ROS Humble is built for
Ubuntu's `/usr/bin/python3`, so the TP5 ROS executables use that interpreter.

The TP4 files are expected at:

```text
/home/salmane/Tps/tp4_for_tp5/dgcnn_model.py
/home/salmane/Tps/tp4_for_tp5/dgcnn_modelnet.pth
/home/salmane/Tps/tp4_for_tp5/class_names.json
```

## Build

```bash
cd /home/salmane/Tps/tp3_robotics/bcr_ws
source /opt/ros/humble/setup.bash
colcon build
source install/setup.bash
```

## Run

Terminal 1:

```bash
cd /home/salmane/Tps/tp3_robotics/bcr_ws
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 launch bcr_arm_tp5 pick_and_place.launch.py
```

Terminal 2:

```bash
cd /home/salmane/Tps/tp3_robotics/bcr_ws
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 run bcr_arm_tp5 pick_and_place.py
```

You can also start the pipeline automatically after the controllers load:

```bash
ros2 launch bcr_arm_tp5 pick_and_place.launch.py auto_start_pipeline:=true
```

For WSL without GUI:

```bash
ros2 launch bcr_arm_tp5 pick_and_place.launch.py headless:=true
```

## Debug Commands

```bash
ros2 topic list | grep -E "camera|joint"
ros2 topic hz /camera/points
ros2 topic echo /joint_states --once
python3 src/bcr_arm_tp5/scripts/ik_solver.py
```

Expected topic output includes:

```text
/camera/camera_info
/camera/depth_image
/camera/image
/camera/points
/joint_states
/joint_trajectory_controller/joint_trajectory
```

Expected IK debug output:

```text
target=[0.45 0.1  0.53] success=True error=...
joint_names=joint1,joint2,joint3,joint4,joint5,joint6,joint7
solution=[...]
fk_position=[...]
```

Expected pick-and-place log flow:

```text
Received point cloud with ... XYZ points.
RANSAC plane points=... object clusters=...
cluster=... centroid=... class=... confidence=...
IK success=True error=...
Published quintic trajectory to pre-grasp.
Published return-home trajectory.
```
