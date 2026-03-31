#!/usr/bin/env python3
import math
import time

import numpy as np
import rclpy
from geometry_msgs.msg import PointStamped
from rclpy.node import Node
from sensor_msgs.msg import JointState

L1 = 0.200
L2_OFFSET = 0.065
L3 = 0.410
L4_OFFSET = -0.065
L5 = 0.310
L6_OFFSET = 0.060
L7 = 0.105


def dh_matrix(theta: float, d: float, a: float, alpha: float) -> np.ndarray:
    ct = math.cos(theta)
    st = math.sin(theta)
    ca = math.cos(alpha)
    sa = math.sin(alpha)
    return np.array(
        [
            [ct, -st * ca, st * sa, a * ct],
            [st, ct * ca, -ct * sa, a * st],
            [0.0, sa, ca, d],
            [0.0, 0.0, 0.0, 1.0],
        ],
        dtype=float,
    )


def compute_fk(joints: list[float]) -> np.ndarray:
    # Educational DH-style model aligned with the URDF dimensions and
    # alternating joint-axis pattern exposed by the provided robot description.
    dh_params = [
        (joints[0], L1, 0.0, math.pi / 2.0),
        (joints[1], 0.0, L2_OFFSET, -math.pi / 2.0),
        (joints[2], L3, 0.0, math.pi / 2.0),
        (joints[3], 0.0, L4_OFFSET, -math.pi / 2.0),
        (joints[4], L5, 0.0, math.pi / 2.0),
        (joints[5], 0.0, L6_OFFSET, -math.pi / 2.0),
        (joints[6], L7, 0.0, 0.0),
    ]

    transform = np.eye(4)
    for theta, d, a, alpha in dh_params:
        transform = transform @ dh_matrix(theta, d, a, alpha)
    return transform


class ForwardKinematicsNode(Node):
    def __init__(self) -> None:
        super().__init__("forward_kinematics")
        self.subscription = self.create_subscription(
            JointState, "/joint_states", self.joint_state_callback, 10
        )
        self.joint_vector_publisher = self.create_publisher(
            JointState, "/bcr_arm/joint_vector", 10
        )
        self.position_publisher = self.create_publisher(
            PointStamped, "/bcr_arm/fk/analytical", 10
        )
        self.joint_names = [f"joint{i}" for i in range(1, 8)]
        self.last_log_time = 0.0
        self.get_logger().info(
            "Listening on /joint_states and publishing /bcr_arm/joint_vector "
            "plus /bcr_arm/fk/analytical."
        )

    def joint_state_callback(self, msg: JointState) -> None:
        joint_map = {name: pos for name, pos in zip(msg.name, msg.position)}
        if not all(name in joint_map for name in self.joint_names):
            return

        joint_values = [joint_map[name] for name in self.joint_names]
        ordered_joint_msg = JointState()
        ordered_joint_msg.header = msg.header
        ordered_joint_msg.name = self.joint_names
        ordered_joint_msg.position = joint_values
        self.joint_vector_publisher.publish(ordered_joint_msg)

        transform = compute_fk(joint_values)
        x, y, z = transform[0, 3], transform[1, 3], transform[2, 3]

        point_msg = PointStamped()
        point_msg.header = msg.header
        point_msg.header.frame_id = point_msg.header.frame_id or "base_link"
        point_msg.point.x = float(x)
        point_msg.point.y = float(y)
        point_msg.point.z = float(z)
        self.position_publisher.publish(point_msg)

        now = time.monotonic()
        if now - self.last_log_time >= 1.0:
            self.get_logger().info(
                f"End-effector position -> x={x:.4f} m, y={y:.4f} m, z={z:.4f} m"
            )
            self.last_log_time = now


def main() -> None:
    rclpy.init()
    node = ForwardKinematicsNode()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()


if __name__ == "__main__":
    main()
