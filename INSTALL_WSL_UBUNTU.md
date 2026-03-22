# WSL Ubuntu Install Notes

## Detected Environment

- Repository path: `/home/salmane/Tps/tp3_robotics`
- Kernel: WSL2 on Linux `6.6.87.2-microsoft-standard-WSL2`
- Ubuntu release: `22.04.5 LTS`
- Ubuntu codename: `jammy`
- ROS installation present at: `/opt/ros/humble/setup.bash`

## Compatibility Decision

ROS 2 Humble apt packages are officially targeted at Ubuntu Jammy 22.04, so this WSL environment is compatible.

## Current ROS State

- ROS 2 Humble is installed.
- The shell was not sourced by default when inspected.
- `ros2` and `xacro` work after sourcing `/opt/ros/humble/setup.bash`.
- a repo-local `.venv` should be created from `/usr/bin/python3.10`
- ROS is sourced on top of that `.venv`

## Exact Install Command

Use Ubuntu `apt` only:

```bash
sudo apt-get update
sudo apt-get install -y \
  ros-humble-ros-gz-bridge \
  ros-humble-ros-gz-sim \
  ros-humble-ros-gz-image \
  ros-humble-gz-ros2-control \
  ros-humble-ros2-control \
  ros-humble-ros2-controllers \
  ros-humble-controller-manager \
  ros-humble-joint-state-broadcaster \
  ros-humble-joint-trajectory-controller \
  ros-humble-xacro \
  ros-humble-robot-state-publisher \
  ros-humble-joint-state-publisher-gui \
  ros-humble-rviz2
```

## How To Source ROS Correctly

Recommended for this repo:

```bash
./tools/setup_venv.sh
source /home/salmane/Tps/tp3_robotics/tools/source_ros.sh
```

Manual equivalent:

```bash
export PYENV_VERSION=system
source /home/salmane/Tps/tp3_robotics/.venv/bin/activate
source /opt/ros/humble/setup.bash
source /home/salmane/Tps/tp3_robotics/bcr_ws/install/setup.bash
```

If the workspace has not been built yet, omit the second `source` line.

## VS Code Remote - WSL

1. Open the folder inside WSL, not from the Windows filesystem.
2. Start a fresh WSL terminal in VS Code.
3. Run `source tools/source_ros.sh`.
4. Use the provided VS Code tasks, or run the helper scripts from that sourced terminal.

For a GitHub-clone flow, the recommended first-time sequence is:

```bash
./tools/setup_venv.sh
source tools/source_ros.sh
./tools/build_ws.sh
```

## If ROS Commands Still Fail

- Check `echo $ROS_DISTRO`; it should print `humble` after sourcing.
- Check `which python3`; for project terminals it should resolve inside `.venv/bin/python3`.
- If `ros2` works but Python nodes fail with `rclpy._rclpy_pybind11` import errors, activate the venv and source ROS again.
