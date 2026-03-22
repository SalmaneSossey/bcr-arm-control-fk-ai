# Report TODO

## Required Checklist

- [ ] Confirm the final DH table
- [ ] Show the transform matrix derivation step by step
- [x] Include at least one Gazebo screenshot with the full robot visible
- [ ] Include controller validation evidence
- [x] Include motion test evidence
- [ ] Include FK console output or captured results
- [x] Include AI dataset size and train/validation/test split
- [x] Include AI MAE and RMSE
- [x] Include the saved loss plot
- [ ] List the final code files used in the TP
- [x] Prepare the demo / screen recording checklist

## Evidence Already In The Repository

- Gazebo screenshot: [`docs/media/gazebo_arm_render.png`](media/gazebo_arm_render.png)
- Motion demo video: [`moving_arm.mp4`](../moving_arm.mp4)
- AI metrics: [`fk_mlp_metrics.json`](../bcr_ws/src/bcr_arm_gazebo/models/fk_mlp_metrics.json)
- AI loss plot: [`fk_mlp_loss.png`](../bcr_ws/src/bcr_arm_gazebo/plots/fk_mlp_loss.png)
- AI comparison table source: [`fk_prediction_examples.csv`](../bcr_ws/src/bcr_arm_gazebo/plots/fk_prediction_examples.csv)

## Suggested Report Sections

1. Environment and software stack
2. Robot description reuse and package structure
3. ROS 2 control and Gazebo integration
4. Motion command test
5. Forward kinematics and DH formulation
6. AI extension with MLP regression
7. Results, limitations, and next steps
