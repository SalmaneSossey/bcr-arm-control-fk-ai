# bcr_arm_gazebo

This package contains the missing TP3 simulation, control, FK, and AI pieces built around the supplied `bcr_arm_description` robot model.

## Package Responsibilities

- launch Gazebo Sim with the BCR arm
- load `gz_ros2_control`
- start `joint_state_broadcaster` and `joint_trajectory_controller`
- publish a scripted motion sequence for validation
- compute forward kinematics from `/joint_states`
- generate, train, and evaluate the MLP-based FK approximation

## Important Files

- `launch/bcr_arm.gazebo.launch.py`
- `config/ros2_controllers.yaml`
- `scripts/test_arm_movement.py`
- `scripts/forward_kinematics.py`
- `scripts/generate_fk_dataset.py`
- `scripts/train_fk_mlp.py`
- `scripts/evaluate_fk_mlp.py`

## Runtime Notes

- The repository uses a repo-local `.venv` based on Ubuntu Python `3.10`.
- `tools/source_ros.sh` activates the venv and then sources ROS + the workspace.
- If Gazebo GUI rendering is unstable under WSLg, use:

```bash
BCR_HEADLESS=true ./tools/run_gazebo.sh
```

## Output Locations

- datasets: `data/`
- trained models: `models/`
- plots and comparisons: `plots/`
