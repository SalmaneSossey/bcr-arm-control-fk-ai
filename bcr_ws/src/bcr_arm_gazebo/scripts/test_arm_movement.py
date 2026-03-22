#!/usr/bin/env python3
import rclpy
from builtin_interfaces.msg import Duration
from rclpy.node import Node
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint


class ArmMotionTester(Node):
    def __init__(self) -> None:
        super().__init__("test_arm_movement")
        self.publisher = self.create_publisher(
            JointTrajectory,
            "/joint_trajectory_controller/joint_trajectory",
            10,
        )
        self.joint_names = [f"joint{i}" for i in range(1, 8)]
        self.sequence = [
            ("home", [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]),
            ("test", [0.5, -0.5, 0.3, -0.7, 0.2, 0.4, 0.1]),
            ("home", [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]),
        ]
        self.step_index = 0
        self.timer = self.create_timer(4.0, self.publish_next_goal)
        self.get_logger().info("Ready to publish home -> test -> home trajectory goals.")

    def publish_next_goal(self) -> None:
        if self.step_index >= len(self.sequence):
            self.get_logger().info("Motion test complete.")
            self.timer.cancel()
            self.create_timer(1.0, lambda: rclpy.shutdown())
            return

        label, positions = self.sequence[self.step_index]
        msg = JointTrajectory()
        msg.joint_names = self.joint_names

        point = JointTrajectoryPoint()
        point.positions = positions
        point.time_from_start = Duration(sec=3, nanosec=0)
        msg.points = [point]

        self.publisher.publish(msg)
        self.get_logger().info(
            f"Published {label} goal with 3.0 s duration: {positions}"
        )
        self.step_index += 1


def main() -> None:
    rclpy.init()
    node = ArmMotionTester()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()


if __name__ == "__main__":
    main()
