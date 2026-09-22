import json
import os
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import tensorflow as tf
from sklearn.metrics import classification_report, roc_auc_score
from sklearn.model_selection import train_test_split

from training.config import (
    LABELS, MAX_TOKENS, SEQUENCE_LENGTH, EMBEDDING_DIM,
    LSTM_UNITS, BATCH_SIZE, EPOCHS, VALIDATION_SPLIT, RANDOM_SEED
)

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "raw" / "train.csv"
MODEL_DIR = ROOT / "models"
REPORT_DIR = ROOT / "reports"
MODEL_DIR.mkdir(exist_ok=True)
REPORT_DIR.mkdir(exist_ok=True)

tf.keras.utils.set_random_seed(RANDOM_SEED)

def load_data():
    if not DATA.exists():
        raise FileNotFoundError(
            f"{DATA} not found. Run: python scripts/download_jigsaw.py"
        )
    df = pd.read_csv(DATA)
    required = ["comment_text", *LABELS]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Missing columns: {missing}")
    df["comment_text"] = df["comment_text"].fillna("").astype(str).str.strip()
    df = df[df["comment_text"].str.len() > 0].copy()
    return df

def build_model():
    vectorizer = tf.keras.layers.TextVectorization(
        max_tokens=MAX_TOKENS,
        output_mode="int",
        output_sequence_length=SEQUENCE_LENGTH,
        standardize="lower_and_strip_punctuation",
    )
    model = tf.keras.Sequential([
        tf.keras.Input(shape=(), dtype=tf.string),
        vectorizer,
        tf.keras.layers.Embedding(MAX_TOKENS, EMBEDDING_DIM, mask_zero=True),
        tf.keras.layers.Bidirectional(tf.keras.layers.LSTM(LSTM_UNITS, return_sequences=True)),
        tf.keras.layers.Dropout(0.35),
        tf.keras.layers.Bidirectional(tf.keras.layers.LSTM(LSTM_UNITS // 2)),
        tf.keras.layers.Dropout(0.30),
        tf.keras.layers.Dense(96, activation="relu"),
        tf.keras.layers.Dropout(0.25),
        tf.keras.layers.Dense(len(LABELS), activation="sigmoid"),
    ])
    return model, vectorizer

def main():
    df = load_data()
    x = df["comment_text"].values
    y = df[LABELS].values.astype("float32")

    x_train, x_val, y_train, y_val = train_test_split(
        x, y, test_size=VALIDATION_SPLIT, random_state=RANDOM_SEED
    )

    model, vectorizer = build_model()
    vectorizer.adapt(tf.data.Dataset.from_tensor_slices(x_train).batch(BATCH_SIZE))

    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=1e-3),
        loss="binary_crossentropy",
        metrics=[
            tf.keras.metrics.BinaryAccuracy(name="binary_accuracy"),
            tf.keras.metrics.AUC(name="auc", multi_label=True),
            tf.keras.metrics.Precision(name="precision"),
            tf.keras.metrics.Recall(name="recall"),
        ],
    )

    callbacks = [
        tf.keras.callbacks.EarlyStopping(
            monitor="val_auc", mode="max", patience=2, restore_best_weights=True
        ),
        tf.keras.callbacks.ReduceLROnPlateau(
            monitor="val_auc", mode="max", factor=0.5, patience=1, min_lr=1e-5
        ),
    ]

    history = model.fit(
        x_train, y_train,
        validation_data=(x_val, y_val),
        epochs=EPOCHS,
        batch_size=BATCH_SIZE,
        callbacks=callbacks,
        verbose=1,
    )

    val_probs = model.predict(x_val, batch_size=BATCH_SIZE, verbose=1)
    val_pred = (val_probs >= 0.5).astype(int)

    report = classification_report(
        y_val, val_pred, target_names=LABELS, output_dict=True, zero_division=0
    )
    try:
        macro_auc = float(roc_auc_score(y_val, val_probs, average="macro"))
    except ValueError:
        macro_auc = None

    model_path = MODEL_DIR / "toxic_comment_model.keras"
    model.save(model_path)

    version = datetime.now(timezone.utc).strftime("v%Y.%m.%d.%H%M")
    config = {
        "model_version": version,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "labels": LABELS,
        "thresholds": {label: 0.5 for label in LABELS},
        "architecture": "TextVectorization → Embedding → BiLSTM → BiLSTM → Dense → Sigmoid",
        "training": {
            "rows": int(len(df)),
            "train_rows": int(len(x_train)),
            "validation_rows": int(len(x_val)),
            "max_tokens": MAX_TOKENS,
            "sequence_length": SEQUENCE_LENGTH,
            "embedding_dim": EMBEDDING_DIM,
            "lstm_units": LSTM_UNITS,
            "batch_size": BATCH_SIZE,
            "epochs_requested": EPOCHS,
            "epochs_completed": len(history.history["loss"]),
        },
        "metrics": {
            "macro_auc": macro_auc,
            "classification_report": report,
        },
    }
    (MODEL_DIR / "model_config.json").write_text(
        json.dumps(config, indent=2, default=str), encoding="utf-8"
    )

    (REPORT_DIR / "training_report.json").write_text(
        json.dumps(config, indent=2, default=str), encoding="utf-8"
    )
    print(f"\nSaved model: {model_path}")
    print(f"Saved config: {MODEL_DIR / 'model_config.json'}")
    print(f"Macro AUC: {macro_auc}")

if __name__ == "__main__":
    main()
