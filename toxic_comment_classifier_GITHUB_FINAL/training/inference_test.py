from pathlib import Path
import tensorflow as tf

ROOT = Path(__file__).resolve().parent.parent
MODEL = ROOT / "models" / "toxic_comment_model.keras"

if not MODEL.exists():
    raise SystemExit("Model not found. Run training first.")

model = tf.keras.models.load_model(MODEL)
examples = [
    "Thank you for explaining this.",
    "I strongly disagree with this argument.",
]

predictions = model.predict(examples, verbose=0)
for text, scores in zip(examples, predictions):
    print("\n", text)
    print([round(float(x), 4) for x in scores])
