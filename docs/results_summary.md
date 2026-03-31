# Results Summary

This document collects the main verified outcomes and showcase assets for the GitHub version of the TP3 project.

## Verified Runtime Outcomes

- the BCR arm spawns in Gazebo Sim from `robot_description`
- the real mesh-based arm renders correctly
- `joint_state_broadcaster` is active
- `joint_trajectory_controller` is active
- the arm executes the scripted motion sequence: home -> test pose -> home
- the FK node receives `/joint_states` and reports end-effector positions

## Verified AI Outcomes

- `10000` FK samples generated
- train / validation / test split: `7000 / 1500 / 1500`
- trained CPU-only PyTorch model saved
- training loss plot saved
- analytical vs learned FK comparison saved
- live ROS 2 comparison between analytical FK and MLP FK validated

## Metrics

| Metric | X | Y | Z |
|---|---:|---:|---:|
| MAE | 0.106253 | 0.112794 | 0.072709 |
| RMSE | 0.134917 | 0.140585 | 0.093391 |

Source: [`fk_mlp_metrics.json`](../bcr_ws/src/bcr_arm_gazebo/models/fk_mlp_metrics.json)

## Live Comparison Snapshot

Static home pose comparison:

- analytical FK: `(0.0600, 0.0000, 1.0250) m`
- predicted FK: `(-0.0539, 0.0484, 1.0386) m`
- delta: `(-0.1139, 0.0484, 0.0136) m`
- Euclidean error: `0.1245 m`

Motion-phase examples:

- analytical `(0.2799, 0.0608, 0.9872)` vs predicted `(0.0684, 0.1463, 1.0359)` with error `0.2332 m`
- analytical `(0.3989, 0.1473, 0.9230)` vs predicted `(0.1794, 0.2241, 0.9821)` with error `0.2400 m`
- analytical `(0.4772, 0.2527, 0.8375)` vs predicted `(0.2551, 0.3137, 0.8828)` with error `0.2347 m`

## Showcase Assets

- Gazebo screenshot: [`docs/media/gazebo_arm_render.png`](media/gazebo_arm_render.png)
- Motion video: [`moving_arm.mp4`](../moving_arm.mp4)
- Training loss plot: [`fk_mlp_loss.png`](../bcr_ws/src/bcr_arm_gazebo/plots/fk_mlp_loss.png)
- Prediction comparison CSV: [`fk_prediction_examples.csv`](../bcr_ws/src/bcr_arm_gazebo/plots/fk_prediction_examples.csv)

## Known Limitations

- Gazebo GUI rendering under WSLg may require software rendering or headless mode on some systems.
- The FK implementation uses a clean documented DH-style model aligned to the URDF dimensions and joint-axis structure, which is suitable for the assignment and report.
