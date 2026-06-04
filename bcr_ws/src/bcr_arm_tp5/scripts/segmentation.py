#!/usr/bin/python3
from dataclasses import dataclass

import numpy as np


@dataclass
class Cluster:
    points: np.ndarray
    centroid: np.ndarray
    label: int


def _require_open3d():
    try:
        import open3d as o3d
    except ImportError as exc:
        raise RuntimeError(
            "Open3D is required for TP5 segmentation. Install it with: python3 -m pip install open3d"
        ) from exc
    return o3d


def remove_plane_ransac(
    points: np.ndarray,
    distance_threshold: float = 0.015,
    ransac_n: int = 3,
    num_iterations: int = 1000,
) -> tuple[np.ndarray, np.ndarray]:
    o3d = _require_open3d()
    points = np.asarray(points, dtype=np.float64).reshape((-1, 3))
    points = points[np.isfinite(points).all(axis=1)]
    if len(points) < ransac_n:
        return points.astype(np.float32), np.empty((0, 3), dtype=np.float32)

    cloud = o3d.geometry.PointCloud()
    cloud.points = o3d.utility.Vector3dVector(points)
    _, inliers = cloud.segment_plane(
        distance_threshold=distance_threshold,
        ransac_n=ransac_n,
        num_iterations=num_iterations,
    )
    plane = cloud.select_by_index(inliers)
    objects = cloud.select_by_index(inliers, invert=True)
    return (
        np.asarray(objects.points, dtype=np.float32),
        np.asarray(plane.points, dtype=np.float32),
    )


def extract_clusters(
    points: np.ndarray,
    eps: float = 0.035,
    min_points: int = 30,
) -> list[Cluster]:
    o3d = _require_open3d()
    points = np.asarray(points, dtype=np.float64).reshape((-1, 3))
    points = points[np.isfinite(points).all(axis=1)]
    if len(points) == 0:
        return []

    cloud = o3d.geometry.PointCloud()
    cloud.points = o3d.utility.Vector3dVector(points)
    labels = np.asarray(cloud.cluster_dbscan(eps=eps, min_points=min_points, print_progress=False))
    clusters: list[Cluster] = []
    for label in sorted(set(labels.tolist())):
        if label < 0:
            continue
        cluster_points = points[labels == label].astype(np.float32)
        if len(cluster_points) == 0:
            continue
        clusters.append(
            Cluster(
                points=cluster_points,
                centroid=cluster_points.mean(axis=0).astype(np.float32),
                label=int(label),
            )
        )
    return sorted(clusters, key=lambda cluster: len(cluster.points), reverse=True)


def segment_objects(points: np.ndarray) -> tuple[list[Cluster], np.ndarray]:
    object_points, plane_points = remove_plane_ransac(points)
    clusters = extract_clusters(object_points)
    return clusters, plane_points


def main() -> None:
    rng = np.random.default_rng(7)
    table = rng.normal([0.45, 0.0, 0.40], [0.18, 0.12, 0.002], size=(1200, 3))
    cup = rng.normal([0.45, 0.10, 0.50], [0.025, 0.025, 0.04], size=(300, 3))
    clusters, plane = segment_objects(np.vstack([table, cup]))
    print(f"plane_points={len(plane)} clusters={len(clusters)}")
    for cluster in clusters:
        print(f"cluster label={cluster.label} size={len(cluster.points)} centroid={cluster.centroid.round(4)}")


if __name__ == "__main__":
    main()
