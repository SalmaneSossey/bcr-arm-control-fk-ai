#!/usr/bin/python3
import numpy as np
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import PointCloud2
from sensor_msgs_py import point_cloud2


def pointcloud2_to_xyz_array(msg: PointCloud2, skip_nans: bool = True) -> np.ndarray:
    points = point_cloud2.read_points(
        msg,
        field_names=("x", "y", "z"),
        skip_nans=skip_nans,
    )
    if isinstance(points, np.ndarray):
        if points.dtype.names:
            xyz = np.column_stack(
                [points[name].reshape(-1) for name in ("x", "y", "z")]
            ).astype(np.float32)
        else:
            xyz = np.asarray(points, dtype=np.float32).reshape((-1, 3))
    else:
        xyz = np.asarray([[point[0], point[1], point[2]] for point in points], dtype=np.float32)

    if xyz.size == 0:
        return np.empty((0, 3), dtype=np.float32)
    xyz = xyz.reshape((-1, 3))
    return xyz[np.isfinite(xyz).all(axis=1)]


class PointCloudNumpyNode(Node):
    def __init__(self) -> None:
        super().__init__("tp5_perception")
        self.subscription = self.create_subscription(
            PointCloud2, "/camera/points", self.cloud_callback, 10
        )
        self.get_logger().info("Listening on /camera/points and converting PointCloud2 to NumPy Nx3.")

    def cloud_callback(self, msg: PointCloud2) -> None:
        xyz = pointcloud2_to_xyz_array(msg)
        self.get_logger().info(f"PointCloud2 -> NumPy array shape={xyz.shape}", throttle_duration_sec=1.0)


def main() -> None:
    rclpy.init()
    node = PointCloudNumpyNode()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
