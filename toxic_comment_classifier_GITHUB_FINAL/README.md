# Toxic Comment Classification

A multi-label NLP application that detects different types of toxic comments using a deep learning model.

The project provides a web interface where users can enter a comment and get toxicity predictions through a FastAPI backend.

## Features

- Detects multiple types of toxic comments
- Multi-label text classification
- BiLSTM-based deep learning model
- FastAPI REST API
- HTML, CSS and JavaScript frontend
- MongoDB for storing prediction history
- Batch prediction support
- Prediction history and analytics
- Feedback collection
- Docker and Docker Compose support
- DVC pipeline for ML workflow
- Pytest tests
- GitHub Actions CI

## Toxicity Categories

The model classifies comments into six categories:

- Toxic
- Severe Toxic
- Obscene
- Threat
- Insult
- Identity Hate

A single comment can belong to more than one category.

## Tech Stack

### Frontend
- HTML
- CSS
- JavaScript

### Backend
- Python
- FastAPI
- Pydantic

### Machine Learning
- TensorFlow
- Keras
- NLP
- BiLSTM
- Multi-label Classification
- Scikit-learn

### Database
- MongoDB
- PyMongo

### Tools
- Git
- GitHub
- Docker
- Docker Compose
- DVC
- Pytest
- GitHub Actions

## Project Structure

```text
toxic_comment_classifier/
│
├── backend/
│   ├── api/
│   │   └── routes.py
│   ├── services/
│   │   ├── database_service.py
│   │   ├── metrics_service.py
│   │   ├── model_service.py
│   │   ├── security.py
│   │   └── text_service.py
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
│   ├── train_model.py
│   ├── evaluate_model.py
│   ├── data_checks.py
│   ├── data_report.py
│   ├── inference_test.py
│   └── config.py
│
├── scripts/
│   ├── download_jigsaw.py
│   ├── api_smoke_test.py
│   └── batch_predict.py
│
├── tests/
│   ├── test_api.py
│   └── test_services.py
│
├── data/
│   └── raw/
│
├── models/
│
├── reports/
│
├── docs/
│
├── Dockerfile
├── docker-compose.yml
├── dvc.yaml
├── requirements.txt
├── .env.example
└── README.md
