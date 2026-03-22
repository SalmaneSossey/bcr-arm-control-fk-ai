# Troubleshooting

## ROS Not Sourced

Symptoms:

- `ros2: command not found`
- `xacro: command not found`

Fix:

```bash
source /home/salmane/Tps/tp3_robotics/tools/source_ros.sh
```

## Wrong Python For ROS

Symptoms:

- `ModuleNotFoundError: No module named 'rclpy._rclpy_pybind11'`

Cause:

- the project venv is not active, or ROS was sourced before the correct Python 3.10 environment.

Fix:

```bash
./tools/setup_venv.sh
source /home/salmane/Tps/tp3_robotics/tools/source_ros.sh
```

The project venv is based on `/usr/bin/python3.10`, which matches ROS Humble on Jammy.

## Wrong Ubuntu Version

ROS 2 Humble apt packages are for Ubuntu Jammy 22.04. If your WSL distro is not Jammy, do not force-install Humble packages from `apt`. Use a Jammy WSL instance or move to a ROS distro matching your Ubuntu release.

## Missing `ros_gz` Packages

Symptoms:

- `ros_gz_sim` package not found
- Gazebo launch include fails

Fix:

Run the install command in [`INSTALL_WSL_UBUNTU.md`](/home/salmane/Tps/tp3_robotics/INSTALL_WSL_UBUNTU.md).

## Controller Not Loaded

Symptoms:

- `joint_trajectory_controller` missing from `ros2 control list_controllers`

Checks:

- confirm Gazebo launched successfully
- confirm the robot spawned before controller spawners ran
- confirm the controller YAML path passed into xacro is correct

## Robot Spawn Failure

Symptoms:

- robot missing in Gazebo
- `create` node errors in the launch terminal

Checks:

- `robot_description` exists
- `xacro` expands without error
- mesh package paths resolve
- `ros_gz_sim create` executable is available

## Gazebo GUI Crashes In WSL

Symptoms:

- Gazebo starts, the robot spawns, controllers load, then Ogre aborts
- errors mention `Ogre::UnimplementedException`

Workarounds:

```bash
BCR_HEADLESS=true ./tools/run_gazebo.sh
```

or keep the GUI path but force software rendering:

```bash
LIBGL_ALWAYS_SOFTWARE=1 ./tools/run_gazebo.sh
```

The default helper script already enables software rendering unless you override it.

## Missing Executable Permissions

Symptoms:

- shell scripts or Python scripts cannot be run directly

Fix:

```bash
chmod +x tools/*.sh bcr_ws/src/bcr_arm_gazebo/scripts/*.py
```

## AI Python Environment Issues

Symptoms:

- `torch` import fails
- matplotlib cache warnings

Fix:

```bash
./tools/setup_venv.sh
```

The helper scripts also set `MPLCONFIGDIR` and `PIP_CACHE_DIR` to writable directories inside the repo.
