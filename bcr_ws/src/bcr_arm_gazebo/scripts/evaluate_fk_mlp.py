#!/usr/bin/env python3
import argparse
import csv
from pathlib import Path

import numpy as np
import torch
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


def main() -> None:
    package_root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--dataset",
        type=Path,
        default=package_root / "data" / "fk_dataset.csv",
    )
    parser.add_argument(
        "--model",
        type=Path,
        default=package_root / "models" / "fk_mlp.pt",
    )
    parser.add_argument(
        "--examples-output",
        type=Path,
        default=package_root / "plots" / "fk_prediction_examples.csv",
    )
    parser.add_argument("--examples", type=int, default=10)
    args = parser.parse_args()

    if not args.dataset.exists():
        raise SystemExit(f"Dataset not found: {args.dataset}")
    if not args.model.exists():
        raise SystemExit(f"Model not found: {args.model}")

    raw = np.loadtxt(args.dataset, delimiter=",", skiprows=1).astype(np.float32)
    x = raw[:, :7]
    y = raw[:, 7:]

    checkpoint = torch.load(args.model, map_location="cpu")
    model = FKMLP()
    model.load_state_dict(checkpoint["model_state_dict"])
    model.eval()

    x_mean = checkpoint["x_mean"].numpy()
    x_std = checkpoint["x_std"].numpy()
    y_mean = checkpoint["y_mean"].numpy()
    y_std = checkpoint["y_std"].numpy()

    sample_indices = np.linspace(0, len(x) - 1, num=args.examples, dtype=int)
    x_samples = x[sample_indices]
    y_true = y[sample_indices]
    x_samples_n = (x_samples - x_mean) / x_std

    with torch.no_grad():
        y_pred_n = model(torch.from_numpy(x_samples_n)).numpy()
    y_pred = y_pred_n * y_std + y_mean

    args.examples_output.parent.mkdir(parents=True, exist_ok=True)
    with args.examples_output.open("w", newline="") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(
            [
                "sample",
                "q1",
                "q2",
                "q3",
                "q4",
                "q5",
                "q6",
                "q7",
                "x_true",
                "y_true",
                "z_true",
                "x_pred",
                "y_pred",
                "z_pred",
            ]
        )
        for idx, joints, truth, pred in zip(sample_indices, x_samples, y_true, y_pred):
            writer.writerow([idx, *joints.tolist(), *truth.tolist(), *pred.tolist()])
            print(
                f"sample={idx} "
                f"true=({truth[0]:.4f}, {truth[1]:.4f}, {truth[2]:.4f}) "
                f"pred=({pred[0]:.4f}, {pred[1]:.4f}, {pred[2]:.4f})"
            )

    mae = np.mean(np.abs(y_pred - y_true), axis=0)
    rmse = np.sqrt(np.mean((y_pred - y_true) ** 2, axis=0))
    print(
        "Example MAE  -> "
        f"x={mae[0]:.6f}, y={mae[1]:.6f}, z={mae[2]:.6f}"
    )
    print(
        "Example RMSE -> "
        f"x={rmse[0]:.6f}, y={rmse[1]:.6f}, z={rmse[2]:.6f}"
    )
    print(f"Saved comparison examples to {args.examples_output}")


if __name__ == "__main__":
    main()
