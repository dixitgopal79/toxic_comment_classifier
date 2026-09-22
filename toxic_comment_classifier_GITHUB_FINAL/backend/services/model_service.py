import json
from pathlib import Path
from typing import Dict, Tuple
import numpy as np
import tensorflow as tf

LABELS = ["toxic", "severe_toxic", "obscene", "threat", "insult", "identity_hate"]

class ModelService:
    def __init__(self, model_path: str, config_path: str):
        self.model_path = Path(model_path)
        self.config_path = Path(config_path)
        self.model = None
        self.thresholds = {label: 0.5 for label in LABELS}
        self.version = "unavailable"

    def load(self):
        if not self.model_path.exists():
            raise FileNotFoundError(
                f"Model not found at {self.model_path}. Run: python training/train_model.py"
            )
        self.model = tf.keras.models.load_model(self.model_path)
        if self.config_path.exists():
            config = json.loads(self.config_path.read_text(encoding="utf-8"))
            self.thresholds.update(config.get("thresholds", {}))
            self.version = config.get("model_version", "1.0.0")
        else:
            self.version = "1.0.0"
        return self

    @property
    def loaded(self):
        return self.model is not None

    def predict(self, text: str) -> Tuple[Dict[str, float], Dict[str, bool]]:
        if not self.loaded:
            raise RuntimeError("Model is not loaded")
        raw = self.model.predict(np.array([text]), verbose=0)[0]
        scores = {label: float(score) for label, score in zip(LABELS, raw)}
        labels = {
            label: scores[label] >= float(self.thresholds.get(label, 0.5))
            for label in LABELS
        }
        return scores, labels

    def summary(self):
        return {
            "version": self.version,
            "labels": LABELS,
            "thresholds": self.thresholds,
            "architecture": "TextVectorization → Embedding → BiLSTM → Dense → Sigmoid",
            "framework": "TensorFlow / Keras",
        }
