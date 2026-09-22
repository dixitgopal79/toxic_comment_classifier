# Model card

## Model

Toxic comment multi-label classifier.

## Input

A text comment.

## Output

Six independent probabilities:

- toxic
- severe_toxic
- obscene
- threat
- insult
- identity_hate

## Network

TextVectorization → Embedding → Bidirectional LSTM → Dropout → Bidirectional LSTM → Dense → Sigmoid

## Training data

Jigsaw Toxic Comment Classification Challenge.

## Intended use

Learning, demonstration and moderation-system prototyping.

## Limitations

Predictions are probabilistic. Toxicity is context-dependent and labels can be subjective. The model should not be treated as a final decision-maker for moderation without additional review, evaluation and monitoring.
