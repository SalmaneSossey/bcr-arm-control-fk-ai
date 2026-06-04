#!/usr/bin/python3
import sys
import time
from pathlib import Path

import numpy as np
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState, PointCloud2
from trajectory_msgs.msg import JointTrajectory

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from classifier import DGCNNClassifier
from ik_solver import JOINT_NAMES, fk_position, solve_ik
from perception import pointcloud2_to_xyz_array
from segmentation import segment_objects
from trajectory import make_joint_trajectory

CAMERA_WORLD_XYZ = np.array([0.6, 0.0, 1.2], dtype=float)
CAMERA_WORLD_RPY = np.array([0.0, 1.5708, 0.0], dtype=float)
PRE_GRASP_DZ = 0.05


def rpy_to_rotation_matrix(roll: float, pitch: float, yaw: float) -> np.ndarray:
    cr, sr = np.cos(roll), np.sin(roll)
    cp, sp = np.cos(pitch), np.sin(pitch)
    cy, sy = np.cos(yaw), np.sin(yaw)

    rotation_x = np.array([[1.0, 0.0, 0.0], [0.0, cr, -sr], [0.0, sr, cr]])
    rotation_y = np.array([[cp, 0.0, sp], [0.0, 1.0, 0.0], [-sp, 0.0, cp]])
    rotation_z = np.array([[cy, -sy, 0.0], [sy, cy, 0.0], [0.0, 0.0, 1.0]])
    return rotation_z @ rotation_y @ rotation_x


CAMERA_TO_WORLD_ROTATION = rpy_to_rotation_matrix(*CAMERA_WORLD_RPY)


def camera_to_world(points: np.ndarray) -> np.ndarray:
    points = np.asarray(points, dtype=float)
    return points @ CAMERA_TO_WORLD_ROTATION.T + CAMERA_WORLD_XYZ


def is_reachable_table_object(world_centroid: np.ndarray) -> bool:
    x, y, z = world_centroid
    return 0.25 <= x <= 0.80 and -0.35 <= y <= 0.35 and 0.42 <= z <= 0.70


class PickAndPlaceNode(Node):
    def __init__(self) -> None:
        super().__init__("tp5_pick_and_place")
        self.publisher = self.create_publisher(
            JointTrajectory,
            "/joint_trajectory_controller/joint_trajectory",
            10,
        )
        self.joint_subscription = self.create_subscription(
            JointState,
            "/joint_states",
            self.joint_state_callback,
            10,
        )
        self.cloud_subscription = self.create_subscription(
            PointCloud2,
            "/camera/points",
            self.cloud_callback,
            10,
        )
        self.joint_values = np.zeros(7, dtype=float)
        self.pipeline_started = False
        self.classifier: DGCNNClassifier | None = None
        self.get_logger().info(
            "TP5 pipeline ready: PointCloud2 -> segmentation -> DGCNN -> IK -> quintic trajectory."
        )

    def joint_state_callback(self, msg: JointState) -> None:
        joint_map = {name: pos for name, pos in zip(msg.name, msg.position)}
        if all(name in joint_map for name in JOINT_NAMES):
            self.joint_values = np.array([joint_map[name] for name in JOINT_NAMES], dtype=float)

    def _classifier(self) -> DGCNNClassifier:
        if self.classifier is None:
            self.get_logger().info("Loading TP4 DGCNN classifier from /home/salmane/Tps/tp4_for_tp5.")
            self.classifier = DGCNNClassifier()
        return self.classifier

    def cloud_callback(self, msg: PointCloud2) -> None:
        if self.pipeline_started:
            return
        self.pipeline_started = True
        try:
            self.run_pipeline(msg)
        except Exception as exc:
            self.get_logger().error(f"TP5 pick-and-place failed: {exc}")

    def run_pipeline(self, msg: PointCloud2) -> None:
        points = pointcloud2_to_xyz_array(msg)
        self.get_logger().info(f"Received point cloud with {len(points)} XYZ points.")
        clusters, plane = segment_objects(points)
        self.get_logger().info(f"RANSAC plane points={len(plane)} object clusters={len(clusters)}.")
        if not clusters:
            raise RuntimeError("No object clusters found after plane removal.")

        classifier = self._classifier()
        ranked = []
        for cluster in clusters[:5]:
            label, confidence, class_index = classifier.classify(cluster.points)
            world_centroid = camera_to_world(cluster.centroid.reshape(1, 3))[0]
            ranked.append((cluster, label, confidence, class_index, world_centroid))
            self.get_logger().info(
                f"cluster={cluster.label} size={len(cluster.points)} "
                f"camera_centroid={cluster.centroid.round(4)} world_centroid={world_centroid.round(4)} "
                f"class={label} confidence={confidence:.3f}"
            )

        candidates = [entry for entry in ranked if is_reachable_table_object(entry[4])]
        if not candidates:
            raise RuntimeError("No segmented cluster landed in the reachable table-object workspace.")

        target_cluster, label, confidence, _, centroid = min(
            candidates,
            key=lambda entry: abs(float(entry[4][0]) - 0.45)
            + abs(float(entry[4][1]) - 0.10)
            + abs(float(entry[4][2]) - 0.50),
        )
        pre_grasp = centroid + np.array([0.0, 0.0, PRE_GRASP_DZ], dtype=float)
        self.get_logger().info(
            f"Selected cluster label={label} confidence={confidence:.3f}; "
            f"world_centroid={centroid.round(4)} pre_grasp={pre_grasp.round(4)}"
        )

        seed = self.joint_values.copy()
        solution, success, error = solve_ik(pre_grasp, seed=seed)
        self.get_logger().info(
            f"IK success={success} error={error:.4f} m q={np.round(solution, 4).tolist()} "
            f"fk={np.round(fk_position(solution), 4).tolist()}"
        )
        if not success:
            raise RuntimeError("IK did not reach the pre-grasp tolerance.")

        trajectory = make_joint_trajectory(seed, solution, duration=3.0, steps=45)
        self.publisher.publish(trajectory)
        self.get_logger().info("Published quintic trajectory to pre-grasp.")
        time.sleep(3.5)

        home = np.zeros(7, dtype=float)
        return_trajectory = make_joint_trajectory(solution, home, duration=3.0, steps=45)
        self.publisher.publish(return_trajectory)
        self.get_logger().info("Published return-home trajectory.")


def main() -> None:
    rclpy.init()
    node = PickAndPlaceNode()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
