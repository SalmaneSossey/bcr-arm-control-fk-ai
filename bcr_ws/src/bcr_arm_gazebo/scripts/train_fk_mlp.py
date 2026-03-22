#!/usr/bin/env python3
import argparse
import json
import os
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import torch
from torch import nn
from torch.utils.data import DataLoader, TensorDataset


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


def split_dataset(x: np.ndarray, y: np.ndarray) -> tuple[np.ndarray, ...]:
    rng = np.random.default_rng(123)
    indices = rng.permutation(len(x))
    train_end = int(0.7 * len(x))
    val_end = int(0.85 * len(x))
    train_idx = indices[:train_end]
    val_idx = indices[train_end:val_end]
    test_idx = indices[val_end:]
    return (
        x[train_idx],
        y[train_idx],
        x[val_idx],
        y[val_idx],
        x[test_idx],
        y[test_idx],
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    package_root = Path(__file__).resolve().parents[1]
    parser.add_argument(
        "--dataset",
        type=Path,
        default=package_root / "data" / "fk_dataset.csv",
    )
    parser.add_argument(
        "--model-output",
        type=Path,
        default=package_root / "models" / "fk_mlp.pt",
    )
    parser.add_argument(
        "--metrics-output",
        type=Path,
        default=package_root / "models" / "fk_mlp_metrics.json",
    )
    parser.add_argument(
        "--plot-output",
        type=Path,
        default=package_root / "plots" / "fk_mlp_loss.png",
    )
    parser.add_argument("--epochs", type=int, default=150)
    parser.add_argument("--batch-size", type=int, default=128)
    parser.add_argument("--learning-rate", type=float, default=1e-3)
    args = parser.parse_args()

    if not args.dataset.exists():
        raise SystemExit(f"Dataset not found: {args.dataset}")

    os.environ.setdefault(
        "MPLCONFIGDIR", str(package_root / ".cache" / "matplotlib")
    )
    Path(os.environ["MPLCONFIGDIR"]).mkdir(parents=True, exist_ok=True)
    args.model_output.parent.mkdir(parents=True, exist_ok=True)
    args.plot_output.parent.mkdir(parents=True, exist_ok=True)

    raw = np.loadtxt(args.dataset, delimiter=",", skiprows=1)
    x = raw[:, :7].astype(np.float32)
    y = raw[:, 7:].astype(np.float32)

    x_train, y_train, x_val, y_val, x_test, y_test = split_dataset(x, y)

    x_mean = x_train.mean(axis=0)
    x_std = x_train.std(axis=0) + 1e-8
    y_mean = y_train.mean(axis=0)
    y_std = y_train.std(axis=0) + 1e-8

    x_train_n = (x_train - x_mean) / x_std
    x_val_n = (x_val - x_mean) / x_std
    x_test_n = (x_test - x_mean) / x_std
    y_train_n = (y_train - y_mean) / y_std
    y_val_n = (y_val - y_mean) / y_std

    train_loader = DataLoader(
        TensorDataset(
            torch.from_numpy(x_train_n), torch.from_numpy(y_train_n)
        ),
        batch_size=args.batch_size,
        shuffle=True,
    )

    model = FKMLP()
    optimizer = torch.optim.Adam(model.parameters(), lr=args.learning_rate)
    criterion = nn.MSELoss()

    train_losses: list[float] = []
    val_losses: list[float] = []
    best_state = None
    best_val_loss = float("inf")

    x_val_tensor = torch.from_numpy(x_val_n)
    y_val_tensor = torch.from_numpy(y_val_n)

    for epoch in range(args.epochs):
        model.train()
        running_loss = 0.0
        for batch_x, batch_y in train_loader:
            optimizer.zero_grad()
            predictions = model(batch_x)
            loss = criterion(predictions, batch_y)
            loss.backward()
            optimizer.step()
            running_loss += loss.item() * batch_x.size(0)

        train_loss = running_loss / len(x_train_n)
        train_losses.append(train_loss)

        model.eval()
        with torch.no_grad():
            val_pred = model(x_val_tensor)
            val_loss = criterion(val_pred, y_val_tensor).item()
        val_losses.append(val_loss)

        if val_loss < best_val_loss:
            best_val_loss = val_loss
            best_state = {k: v.cpu().clone() for k, v in model.state_dict().items()}

        if (epoch + 1) % 25 == 0 or epoch == 0:
            print(
                f"Epoch {epoch + 1:03d}/{args.epochs} "
                f"train_loss={train_loss:.6f} val_loss={val_loss:.6f}"
            )

    assert best_state is not None
    model.load_state_dict(best_state)
    model.eval()

    with torch.no_grad():
        y_test_pred_n = model(torch.from_numpy(x_test_n)).numpy()

    y_test_pred = y_test_pred_n * y_std + y_mean
    abs_err = np.abs(y_test_pred - y_test)
    sq_err = (y_test_pred - y_test) ** 2
    mae = abs_err.mean(axis=0)
    rmse = np.sqrt(sq_err.mean(axis=0))

    checkpoint = {
        "model_state_dict": model.state_dict(),
        "x_mean": torch.from_numpy(x_mean),
        "x_std": torch.from_numpy(x_std),
        "y_mean": torch.from_numpy(y_mean),
        "y_std": torch.from_numpy(y_std),
    }
    torch.save(checkpoint, args.model_output)

    metrics = {
        "mae": {"x": float(mae[0]), "y": float(mae[1]), "z": float(mae[2])},
        "rmse": {"x": float(rmse[0]), "y": float(rmse[1]), "z": float(rmse[2])},
        "dataset": {
            "train": int(len(x_train)),
            "validation": int(len(x_val)),
            "test": int(len(x_test)),
        },
    }
    args.metrics_output.write_text(json.dumps(metrics, indent=2))

    plt.figure(figsize=(8, 5))
    plt.plot(train_losses, label="train")
    plt.plot(val_losses, label="validation")
    plt.xlabel("Epoch")
    plt.ylabel("MSE loss")
    plt.title("FK MLP training loss")
    plt.legend()
    plt.tight_layout()
    plt.savefig(args.plot_output, dpi=150)

    print(f"Model saved to {args.model_output}")
    print(f"Metrics saved to {args.metrics_output}")
    print(f"Loss plot saved to {args.plot_output}")
    print(
        "Test MAE  -> "
        f"x={mae[0]:.6f}, y={mae[1]:.6f}, z={mae[2]:.6f}"
    )
    print(
        "Test RMSE -> "
        f"x={rmse[0]:.6f}, y={rmse[1]:.6f}, z={rmse[2]:.6f}"
    )


if __name__ == "__main__":
    main()
