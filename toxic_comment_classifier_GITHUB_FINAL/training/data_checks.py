from pathlib import Path
import pandas as pd
from training.config import LABELS

def validate_dataset(path: Path):
    if not path.exists():
        raise FileNotFoundError(path)

    df = pd.read_csv(path)
    required = {"comment_text", *LABELS}
    missing = required.difference(df.columns)
    if missing:
        raise ValueError(f"Missing columns: {sorted(missing)}")

    df["comment_text"] = df["comment_text"].fillna("").astype(str)
    df = df[df["comment_text"].str.strip().str.len() > 0]

    return {
        "rows": len(df),
        "columns": len(df.columns),
        "empty_comments": int(df["comment_text"].eq("").sum()),
        "label_distribution": {
            label: int(df[label].sum()) for label in LABELS
        },
    }
