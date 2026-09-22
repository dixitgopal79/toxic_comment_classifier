import json
from pathlib import Path
import numpy as np
import pandas as pd
import tensorflow as tf
from sklearn.metrics import classification_report, roc_auc_score
from training.config import LABELS

ROOT = Path(__file__).resolve().parent.parent
MODEL = ROOT / "models" / "toxic_comment_model.keras"
DATA = ROOT / "data" / "raw" / "train.csv"

if not MODEL.exists():
    raise SystemExit("Train the model first: python training/train_model.py")
if not DATA.exists():
    raise SystemExit("Download data first: python scripts/download_jigsaw.py")

df = pd.read_csv(DATA).dropna(subset=["comment_text"])
df["comment_text"] = df["comment_text"].astype(str)
x = df["comment_text"].values
y = df[LABELS].values.astype(int)

model = tf.keras.models.load_model(MODEL)
probs = model.predict(x, batch_size=256, verbose=1)
preds = (probs >= 0.5).astype(int)

report = classification_report(y, preds, target_names=LABELS, output_dict=True, zero_division=0)
auc = roc_auc_score(y, probs, average="macro")

out = {"macro_auc": float(auc), "classification_report": report}
(Path(ROOT / "reports") / "evaluation.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
print(json.dumps(out, indent=2))
