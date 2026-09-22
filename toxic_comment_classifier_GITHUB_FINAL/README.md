# Toxic Comment Classifier

A web application that checks online comments for six common toxicity categories.

The project includes model training, a REST API, a small web dashboard and MongoDB storage. The same application can be run locally without changing the code structure.

## Features

- Six-label toxic comment classification
- TensorFlow/Keras BiLSTM model
- Jigsaw training data downloader
- FastAPI REST API
- MongoDB prediction history
- Prediction feedback
- CSV export
- Simple analytics dashboard
- Dark/light theme
- API health check
- Request rate limiting
- Optional API key
- Docker setup
- GitHub Actions test workflow
- DVC training pipeline
- Automated model evaluation report

## Project structure

```text
toxic_comment_classifier/
│
├── backend/
│   ├── api/
│   │   └── routes.py
│   ├── services/
│   │   ├── database_service.py
│   │   ├── model_service.py
│   │   └── security.py
│   ├── config.py
│   ├── schemas.py
│   └── main.py
│
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── app.js
│
├── training/
│   ├── config.py
│   ├── train_model.py
│   └── evaluate_model.py
│
├── scripts/
│   └── download_jigsaw.py
│
├── tests/
├── data/
├── models/
├── reports/
├── docs/
├── Dockerfile
├── docker-compose.yml
├── dvc.yaml
├── requirements.txt
└── .env.example
```

## How it works

```text
Comment
   |
   v
Web page
   |
   v
FastAPI
   |
   +----> Validation
   |
   +----> TensorFlow model
   |          |
   |          v
   |     6 probabilities
   |
   +----> MongoDB
              |
              +-- history
              +-- feedback
              +-- statistics
```

The model predicts:

```text
toxic
severe_toxic
obscene
threat
insult
identity_hate
```

A comment can belong to more than one category.

## Requirements

- Python 3.11 recommended
- MongoDB
- Kaggle account for downloading the competition data

## Setup on Windows

Create the environment:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

Install packages:

```powershell
pip install -r requirements.txt
```

Copy the environment file:

```powershell
copy .env.example .env
```

## Download training data

The downloader uses the official Kaggle competition files.

```powershell
python scripts/download_jigsaw.py
```

The Kaggle account must have access to the competition data.

The data is deliberately kept out of Git.

## Train the model

```powershell
python training/train_model.py
```

The training script creates:

```text
models/toxic_comment_model.keras
models/model_config.json
reports/training_report.json
```

To run the separate evaluation:

```powershell
python training/evaluate_model.py
```

## Start MongoDB

If MongoDB is installed locally, make sure the MongoDB service is running.

Or use Docker:

```powershell
docker compose up -d mongodb
```

## Start the application

```powershell
uvicorn backend.main:app --reload
```

Open:

```text
http://127.0.0.1:8000
```

The API documentation is available at:

```text
http://127.0.0.1:8000/docs
```

FastAPI provides the interactive API documentation automatically.

## API endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/health` | Application/model/database status |
| POST | `/api/predict` | Classify a comment |
| POST | `/api/predict/batch` | Classify up to 20 comments in one request |
| GET | `/api/history` | View recent predictions |
| GET | `/api/stats` | View basic application statistics |
| GET | `/api/model` | View model information |
| POST | `/api/feedback` | Save prediction feedback |
| GET | `/api/export` | Download prediction history |

Example:

```json
POST /api/predict

{
  "text": "Example comment"
}
```

## Docker

Build and start everything:

```powershell
docker compose up --build
```

The web application will run on port `8000`.

The model file still needs to be created before starting the application if it is not already present.

## Testing

```powershell
pytest -q
```

## DVC

The training process is defined in `dvc.yaml`.

```powershell
dvc repro
```

## Configuration

The main settings are in `.env`.

```text
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB=toxic_comment_db
MODEL_PATH=models/toxic_comment_model.keras
RATE_LIMIT_PER_MINUTE=60
```

## Notes

The Jigsaw competition data is not included in this repository. It is downloaded using the user's own Kaggle access.

The trained model is also not committed to Git because model files are generated artifacts.

For a resume, describe the technologies that are actually present in this repository. This version uses TensorFlow/Keras, FastAPI, MongoDB, HTML/CSS/JavaScript and DVC.


## Useful development commands

Create a dataset report:

```powershell
python training/data_report.py
```

Check model inference locally:

```powershell
python training/inference_test.py
```

Run a basic API smoke test while the server is running:

```powershell
python scripts/api_smoke_test.py
```

Send multiple comments to the batch endpoint:

```powershell
python scripts/batch_predict.py "This is fine" "Another comment"
```

The API also exposes:

```text
GET /api/analytics
GET /api/analyze-text?text=hello
GET /api/history/search?q=hello
POST /api/predict/batch
```

## Development approach

The project is intentionally split into separate areas:

- `training/` contains model and dataset code.
- `backend/services/` contains model/database logic.
- `backend/api/` contains HTTP routes.
- `frontend/` contains the browser interface.
- `scripts/` contains local utility commands.
- `tests/` contains automated tests.
- `docs/` contains architecture and setup notes.

This keeps the training code independent from the API and UI.
