# Setup checklist

## 1. Python

```powershell
python --version
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## 2. Kaggle

Configure your Kaggle account and accept the competition rules.

Then:

```powershell
python scripts/download_jigsaw.py
```

## 3. Check the dataset

```powershell
python training/data_report.py
```

## 4. Train

```powershell
python training/train_model.py
```

## 5. MongoDB

```powershell
docker compose up -d mongodb
```

## 6. Run

```powershell
uvicorn backend.main:app --reload
```

## 7. Test

```powershell
pytest -q
python scripts/api_smoke_test.py
```
