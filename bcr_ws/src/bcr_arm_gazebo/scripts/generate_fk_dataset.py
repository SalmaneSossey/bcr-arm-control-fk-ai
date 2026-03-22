#!/usr/bin/env python3
import argparse
import csv
import math
from pathlib import Path

import numpy as np

L1 = 0.200
L2_OFFSET = 0.065
L3 = 0.410
L4_OFFSET = -0.065
L5 = 0.310
L6_OFFSET = 0.060
L7 = 0.105

JOINT_LIMITS = [
    (-6.28, 6.28),
    (-2.0, 2.0),
    (-6.28, 6.28),
    (-2.0, 2.0),
    (-6.28, 6.28),
    (-2.0, 2.0),
    (-6.28, 6.28),
]


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


def fk_xyz(joints: np.ndarray) -> np.ndarray:
    params = [
        (joints[0], L1, 0.0, math.pi / 2.0),
        (joints[1], 0.0, L2_OFFSET, -math.pi / 2.0),
        (joints[2], L3, 0.0, math.pi / 2.0),
        (joints[3], 0.0, L4_OFFSET, -math.pi / 2.0),
        (joints[4], L5, 0.0, math.pi / 2.0),
        (joints[5], 0.0, L6_OFFSET, -math.pi / 2.0),
        (joints[6], L7, 0.0, 0.0),
    ]
    transform = np.eye(4)
    for theta, d, a, alpha in params:
        transform = transform @ dh_matrix(theta, d, a, alpha)
    return transform[:3, 3]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--samples", type=int, default=10000)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "data" / "fk_dataset.csv",
    )
    args = parser.parse_args()

    args.output.parent.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(42)

    with args.output.open("w", newline="") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["q1", "q2", "q3", "q4", "q5", "q6", "q7", "x", "y", "z"])
        for _ in range(args.samples):
            joints = np.array(
                [rng.uniform(low, high) for low, high in JOINT_LIMITS], dtype=float
            )
            xyz = fk_xyz(joints)
            writer.writerow([*joints.tolist(), *xyz.tolist()])

    print(f"Generated {args.samples} samples at {args.output}")


if __name__ == "__main__":
    main()
