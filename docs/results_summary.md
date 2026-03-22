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

## Metrics

| Metric | X | Y | Z |
|---|---:|---:|---:|
| MAE | 0.115953 | 0.118293 | 0.076190 |
| RMSE | 0.144932 | 0.148845 | 0.095406 |

Source: [`fk_mlp_metrics.json`](../bcr_ws/src/bcr_arm_gazebo/models/fk_mlp_metrics.json)

## Showcase Assets

- Gazebo screenshot: [`docs/media/gazebo_arm_render.png`](media/gazebo_arm_render.png)
- Motion video: [`moving_arm.mp4`](../moving_arm.mp4)
- Training loss plot: [`fk_mlp_loss.png`](../bcr_ws/src/bcr_arm_gazebo/plots/fk_mlp_loss.png)
- Prediction comparison CSV: [`fk_prediction_examples.csv`](../bcr_ws/src/bcr_arm_gazebo/plots/fk_prediction_examples.csv)

## Known Limitations

- Gazebo GUI rendering under WSLg may require software rendering or headless mode on some systems.
- The FK implementation uses a clean documented DH-style model aligned to the URDF dimensions and joint-axis structure, which is suitable for the assignment and report.
