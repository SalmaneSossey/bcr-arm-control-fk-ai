#!/usr/bin/env python3
import math

import rclpy
from geometry_msgs.msg import PointStamped
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node


class FKComparisonNode(Node):
    def __init__(self) -> None:
        super().__init__("compare_fk_streams")
        self.analytical_position: tuple[float, float, float] | None = None
        self.predicted_position: tuple[float, float, float] | None = None

        self.create_subscription(
            PointStamped,
            "/bcr_arm/fk/analytical",
            self.analytical_callback,
            10,
        )
        self.create_subscription(
            PointStamped,
            "/bcr_arm/fk/predicted",
            self.predicted_callback,
            10,
        )
        self.timer = self.create_timer(1.0, self.report_difference)
        self.get_logger().info(
            "Comparing /bcr_arm/fk/analytical against /bcr_arm/fk/predicted."
        )

    def analytical_callback(self, msg: PointStamped) -> None:
        self.analytical_position = (msg.point.x, msg.point.y, msg.point.z)

    def predicted_callback(self, msg: PointStamped) -> None:
        self.predicted_position = (msg.point.x, msg.point.y, msg.point.z)

    def report_difference(self) -> None:
        if self.analytical_position is None or self.predicted_position is None:
            return

        ax, ay, az = self.analytical_position
        px, py, pz = self.predicted_position
        dx = px - ax
        dy = py - ay
        dz = pz - az
        distance_error = math.sqrt(dx * dx + dy * dy + dz * dz)

        self.get_logger().info(
            "FK comparison -> "
            f"analytical=({ax:.4f}, {ay:.4f}, {az:.4f}) m | "
            f"predicted=({px:.4f}, {py:.4f}, {pz:.4f}) m | "
            f"delta=({dx:.4f}, {dy:.4f}, {dz:.4f}) m | "
            f"euclidean_error={distance_error:.4f} m"
        )


def main() -> None:
    rclpy.init()
    node = FKComparisonNode()
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        node.destroy_node()


if __name__ == "__main__":
    main()
