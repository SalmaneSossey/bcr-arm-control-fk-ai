#!/usr/bin/env python3
import argparse
import os
import time
from pathlib import Path

import numpy as np
import rclpy
import torch
from ament_index_python.packages import PackageNotFoundError, get_package_share_directory
from geometry_msgs.msg import PointStamped
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from sensor_msgs.msg import JointState
from torch import nn


class FKMLP(nn.Module):
    def __init__(self) -> None:
        super().__init__()
        self.network = nn.Sequential(
            nn.Linear(7, 64),
            nn.ReLU(),
            nn.Linear(64, 128),
            nn.ReLU(),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Linear(64, 3),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.network(x)


def resolve_default_model_path() -> Path:
    candidates: list[Path] = []

    repo_root = os.environ.get("BCR_TP3_ROOT")
    if repo_root:
        candidates.append(
            Path(repo_root) / "bcr_ws" / "src" / "bcr_arm_gazebo" / "models" / "fk_mlp.pt"
        )

    try:
        share_root = Path(get_package_share_directory("bcr_arm_gazebo"))
        candidates.append(share_root / "models" / "fk_mlp.pt")
    except PackageNotFoundError:
        pass

    for candidate in candidates:
        if candidate.exists():
            return candidate

    search_list = "\n".join(f"- {candidate}" for candidate in candidates) or "- none"
    raise FileNotFoundError(
        "Could not find the trained FK MLP model. Checked:\n" + search_list
    )


class FKMLPPredictorNode(Node):
    def __init__(self, model_path: Path) -> None:
        super().__init__("predict_fk_mlp")
        checkpoint = torch.load(model_path, map_location="cpu")

        self.model = FKMLP()
        self.model.load_state_dict(checkpoint["model_state_dict"])
        self.model.eval()

        self.x_mean = checkpoint["x_mean"].numpy()
        self.x_std = checkpoint["x_std"].numpy()
        self.y_mean = checkpoint["y_mean"].numpy()
        self.y_std = checkpoint["y_std"].numpy()
        self.last_log_time = 0.0
        self.joint_names = [f"joint{i}" for i in range(1, 8)]

        self.subscription = self.create_subscription(
            JointState, "/bcr_arm/joint_vector", self.joint_state_callback, 10
        )
        self.publisher = self.create_publisher(
            PointStamped, "/bcr_arm/fk/predicted", 10
        )

        self.get_logger().info(
            f"Loaded FK MLP from {model_path} and listening on /bcr_arm/joint_vector."
        )

    def joint_state_callback(self, msg: JointState) -> None:
        joint_map = {name: pos for name, pos in zip(msg.name, msg.position)}
        if not all(name in joint_map for name in self.joint_names):
            return

        joints = np.array([joint_map[name] for name in self.joint_names], dtype=np.float32)
        joints_n = (joints - self.x_mean) / self.x_std

        with torch.no_grad():
            prediction_n = self.model(torch.from_numpy(joints_n[None, :])).numpy()[0]
        prediction = prediction_n * self.y_std + self.y_mean

        point_msg = PointStamped()
        point_msg.header = msg.header
        point_msg.header.frame_id = point_msg.header.frame_id or "base_link"
        point_msg.point.x = float(prediction[0])
        point_msg.point.y = float(prediction[1])
        point_msg.point.z = float(prediction[2])
        self.publisher.publish(point_msg)

        now = time.monotonic()
        if now - self.last_log_time >= 1.0:
            self.get_logger().info(
                "MLP FK prediction -> "
                f"x={prediction[0]:.4f} m, y={prediction[1]:.4f} m, z={prediction[2]:.4f} m"
            )
            self.last_log_time = now


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Load the trained FK MLP once and predict end-effector position continuously."
    )
    parser.add_argument(
        "--model",
        type=Path,
        default=resolve_default_model_path(),
        help="Path to fk_mlp.pt",
    )
    args, _ = parser.parse_known_args()

    rclpy.init()
    node = FKMLPPredictorNode(args.model)
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        node.destroy_node()


if __name__ == "__main__":
    main()
