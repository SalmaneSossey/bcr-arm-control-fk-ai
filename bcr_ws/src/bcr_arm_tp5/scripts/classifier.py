#!/usr/bin/python3
import importlib.util
import json
from pathlib import Path
from typing import Any

import numpy as np

TP4_ROOT = Path("/home/salmane/Tps/tp4_for_tp5")
DEFAULT_MODEL_PATH = TP4_ROOT / "dgcnn_modelnet.pth"
DEFAULT_CLASS_NAMES_PATH = TP4_ROOT / "class_names.json"
DEFAULT_MODEL_SOURCE = TP4_ROOT / "dgcnn_model.py"
NUM_POINTS = 1024


def normalize_points(points: np.ndarray, num_points: int = NUM_POINTS) -> np.ndarray:
    points = np.asarray(points, dtype=np.float32).reshape((-1, 3))
    points = points[np.isfinite(points).all(axis=1)]
    if len(points) == 0:
        raise ValueError("Cannot classify an empty point cloud cluster.")

    replace = len(points) < num_points
    indices = np.random.choice(len(points), num_points, replace=replace)
    sampled = points[indices]
    sampled = sampled - sampled.mean(axis=0, keepdims=True)
    radius = np.linalg.norm(sampled, axis=1).max()
    if radius > 1e-8:
        sampled = sampled / radius
    return sampled.astype(np.float32)


def _load_dgcnn_class(model_source: Path):
    spec = importlib.util.spec_from_file_location("tp4_dgcnn_model", model_source)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load DGCNN module from {model_source}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    if not hasattr(module, "DGCNN"):
        raise RuntimeError(f"{model_source} does not define a DGCNN class.")
    return module.DGCNN


def _extract_state_dict(checkpoint: Any) -> dict[str, Any]:
    if isinstance(checkpoint, dict):
        for key in ("model_state_dict", "state_dict", "model"):
            value = checkpoint.get(key)
            if isinstance(value, dict):
                return value
        if all(hasattr(value, "shape") for value in checkpoint.values()):
            return checkpoint
    raise RuntimeError("Unsupported DGCNN checkpoint format.")


class DGCNNClassifier:
    def __init__(
        self,
        model_path: Path | str = DEFAULT_MODEL_PATH,
        class_names_path: Path | str = DEFAULT_CLASS_NAMES_PATH,
        model_source: Path | str = DEFAULT_MODEL_SOURCE,
        device: str = "cpu",
    ) -> None:
        try:
            import torch
        except ImportError as exc:
            raise RuntimeError("PyTorch is required for TP5 classification. Install torch first.") from exc

        self.torch = torch
        self.model_path = Path(model_path)
        self.class_names_path = Path(class_names_path)
        self.model_source = Path(model_source)
        self.device = torch.device(device)

        with self.class_names_path.open("r", encoding="utf-8") as file:
            self.class_names = json.load(file)

        DGCNN = _load_dgcnn_class(self.model_source)
        self.model = DGCNN(num_classes=len(self.class_names))
        checkpoint = torch.load(self.model_path, map_location=self.device)
        state_dict = _extract_state_dict(checkpoint)
        clean_state_dict = {key.removeprefix("module."): value for key, value in state_dict.items()}
        self.model.load_state_dict(clean_state_dict, strict=False)
        self.model.to(self.device)
        self.model.eval()

    def classify(self, points: np.ndarray) -> tuple[str, float, int]:
        normalized = normalize_points(points, NUM_POINTS)
        tensor = self.torch.from_numpy(normalized.T).unsqueeze(0).to(self.device)
        with self.torch.no_grad():
            logits = self.model(tensor)
            probabilities = self.torch.softmax(logits, dim=1)
            confidence, class_index = probabilities.max(dim=1)
        index = int(class_index.item())
        return self.class_names[index], float(confidence.item()), index


def main() -> None:
    rng = np.random.default_rng(4)
    points = rng.normal(0.0, 0.2, size=(NUM_POINTS, 3)).astype(np.float32)
    classifier = DGCNNClassifier()
    label, confidence, index = classifier.classify(points)
    print(f"predicted label={label} index={index} confidence={confidence:.3f}")


if __name__ == "__main__":
    main()
