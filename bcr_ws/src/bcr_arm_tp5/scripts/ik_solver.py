#!/usr/bin/python3
import numpy as np

JOINT_NAMES = [f"joint{i}" for i in range(1, 8)]
JOINT_LIMITS = np.array(
    [
        [-6.28, 6.28],
        [-2.00, 2.00],
        [-6.28, 6.28],
        [-2.00, 2.00],
        [-6.28, 6.28],
        [-2.00, 2.00],
        [-6.28, 6.28],
    ],
    dtype=float,
)

JOINT_ORIGINS = [
    np.array([0.0, 0.0, 0.025], dtype=float),
    np.array([0.0, 0.0, 0.200], dtype=float),
    np.array([0.065, 0.0, 0.0], dtype=float),
    np.array([0.0, 0.0, 0.410], dtype=float),
    np.array([-0.065, 0.0, 0.0], dtype=float),
    np.array([0.0, 0.0, 0.310], dtype=float),
    np.array([0.060, 0.0, 0.0], dtype=float),
]
JOINT_AXES = [
    np.array([0.0, 0.0, 1.0], dtype=float),
    np.array([1.0, 0.0, 0.0], dtype=float),
    np.array([0.0, 0.0, 1.0], dtype=float),
    np.array([1.0, 0.0, 0.0], dtype=float),
    np.array([0.0, 0.0, 1.0], dtype=float),
    np.array([1.0, 0.0, 0.0], dtype=float),
    np.array([0.0, 0.0, 1.0], dtype=float),
]
TOOL_OFFSET = np.array([0.0, 0.0, 0.105], dtype=float)


def translation_matrix(xyz: np.ndarray) -> np.ndarray:
    transform = np.eye(4)
    transform[:3, 3] = xyz
    return transform


def axis_angle_matrix(axis: np.ndarray, angle: float) -> np.ndarray:
    axis = np.asarray(axis, dtype=float)
    axis = axis / np.linalg.norm(axis)
    x, y, z = axis
    c = float(np.cos(angle))
    s = float(np.sin(angle))
    one_c = 1.0 - c
    rotation = np.array(
        [
            [c + x * x * one_c, x * y * one_c - z * s, x * z * one_c + y * s],
            [y * x * one_c + z * s, c + y * y * one_c, y * z * one_c - x * s],
            [z * x * one_c - y * s, z * y * one_c + x * s, c + z * z * one_c],
        ],
        dtype=float,
    )
    transform = np.eye(4)
    transform[:3, :3] = rotation
    return transform


def compute_fk(joints: np.ndarray | list[float]) -> np.ndarray:
    q = np.asarray(joints, dtype=float).reshape(7)
    transform = np.eye(4)
    for origin, axis, angle in zip(JOINT_ORIGINS, JOINT_AXES, q):
        transform = transform @ translation_matrix(origin) @ axis_angle_matrix(axis, float(angle))
    transform = transform @ translation_matrix(TOOL_OFFSET)
    return transform


def fk_position(joints: np.ndarray | list[float]) -> np.ndarray:
    transform = compute_fk(joints)
    return np.asarray(transform[:3, 3], dtype=float)


def numerical_position_jacobian(q: np.ndarray, step: float = 1e-5) -> np.ndarray:
    q = np.asarray(q, dtype=float).reshape(7)
    jacobian = np.zeros((3, 7), dtype=float)
    for index in range(7):
        dq = np.zeros(7, dtype=float)
        dq[index] = step
        jacobian[:, index] = (fk_position(q + dq) - fk_position(q - dq)) / (2.0 * step)
    return jacobian


def solve_ik(
    target_xyz: np.ndarray | list[float],
    seed: np.ndarray | list[float] | None = None,
    damping: float = 0.08,
    max_iterations: int = 350,
    tolerance: float = 0.01,
    step_scale: float = 0.7,
) -> tuple[np.ndarray, bool, float]:
    target = np.asarray(target_xyz, dtype=float).reshape(3)
    q = np.zeros(7, dtype=float) if seed is None else np.asarray(seed, dtype=float).reshape(7)
    q = np.clip(q, JOINT_LIMITS[:, 0], JOINT_LIMITS[:, 1])

    for _ in range(max_iterations):
        error = target - fk_position(q)
        error_norm = float(np.linalg.norm(error))
        if error_norm <= tolerance:
            return q, True, error_norm

        jacobian = numerical_position_jacobian(q)
        lhs = jacobian @ jacobian.T + (damping**2) * np.eye(3)
        dq = jacobian.T @ np.linalg.solve(lhs, error)
        max_abs = float(np.max(np.abs(dq)))
        if max_abs > 0.25:
            dq *= 0.25 / max_abs
        q = q + step_scale * dq
        q = np.clip(q, JOINT_LIMITS[:, 0], JOINT_LIMITS[:, 1])

    final_error = float(np.linalg.norm(target - fk_position(q)))
    return q, final_error <= tolerance, final_error


def main() -> None:
    target = np.array([0.45, 0.10, 0.53], dtype=float)
    q, success, error = solve_ik(target)
    print(f"target={target.round(4)} success={success} error={error:.4f} m")
    print("joint_names=" + ",".join(JOINT_NAMES))
    print("solution=" + np.array2string(q, precision=4, separator=", "))
    print("fk_position=" + np.array2string(fk_position(q), precision=4, separator=", "))


if __name__ == "__main__":
    main()
