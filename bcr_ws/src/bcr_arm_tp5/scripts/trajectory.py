#!/usr/bin/python3
import numpy as np
from builtin_interfaces.msg import Duration
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint

JOINT_NAMES = [f"joint{i}" for i in range(1, 8)]


def quintic_blend(s: float) -> float:
    return 10.0 * s**3 - 15.0 * s**4 + 6.0 * s**5


def quintic_trajectory(
    start: np.ndarray | list[float],
    goal: np.ndarray | list[float],
    duration: float = 4.0,
    steps: int = 40,
) -> list[tuple[float, np.ndarray]]:
    start_array = np.asarray(start, dtype=float).reshape(7)
    goal_array = np.asarray(goal, dtype=float).reshape(7)
    if steps < 2:
        raise ValueError("steps must be >= 2")
    samples: list[tuple[float, np.ndarray]] = []
    for index in range(steps):
        s = index / (steps - 1)
        t = duration * s
        q = start_array + quintic_blend(s) * (goal_array - start_array)
        samples.append((t, q))
    return samples


def _duration_from_seconds(seconds: float) -> Duration:
    sec = int(seconds)
    nanosec = int(round((seconds - sec) * 1_000_000_000))
    if nanosec >= 1_000_000_000:
        sec += 1
        nanosec -= 1_000_000_000
    return Duration(sec=sec, nanosec=nanosec)


def make_joint_trajectory(
    start: np.ndarray | list[float],
    goal: np.ndarray | list[float],
    duration: float = 4.0,
    steps: int = 40,
    joint_names: list[str] | None = None,
) -> JointTrajectory:
    msg = JointTrajectory()
    msg.joint_names = joint_names or JOINT_NAMES
    for t, q in quintic_trajectory(start, goal, duration=duration, steps=steps):
        point = JointTrajectoryPoint()
        point.positions = [float(value) for value in q]
        point.time_from_start = _duration_from_seconds(t)
        msg.points.append(point)
    return msg


def main() -> None:
    trajectory = quintic_trajectory(np.zeros(7), np.array([0.2, -0.1, 0.1, -0.3, 0.1, 0.2, 0.0]))
    print(f"samples={len(trajectory)} start={trajectory[0][1].round(4)} goal={trajectory[-1][1].round(4)}")


if __name__ == "__main__":
    main()
