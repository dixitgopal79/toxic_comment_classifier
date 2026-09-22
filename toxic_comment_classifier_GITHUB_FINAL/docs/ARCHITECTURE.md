# Architecture

## Request flow

```text
Browser
   |
   | POST /api/predict
   v
FastAPI
   |
   +--> Pydantic validation
   |
   +--> rate limit / API key
   |
   +--> ModelService
   |       |
   |       +--> TensorFlow model
   |       |
   |       +--> six probabilities
   |
   +--> DatabaseService
   |       |
   |       +--> MongoDB
   |
   +--> JSON response
```

## Training flow

```text
Kaggle
  |
  v
train.csv
  |
  v
data checks
  |
  v
train / validation split
  |
  v
TextVectorization
  |
  v
Embedding
  |
  v
BiLSTM
  |
  v
Dense + Sigmoid
  |
  v
Keras model
  |
  +--> model_config.json
  +--> training_report.json
```

## Why six outputs?

The source competition treats toxicity as multiple categories and asks models to predict a probability for each category. A comment may therefore trigger more than one label. citeturn0search0
