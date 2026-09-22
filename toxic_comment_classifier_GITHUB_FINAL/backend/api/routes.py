from datetime import datetime, timezone
from uuid import uuid4
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, Request
from backend.schemas import (
    PredictionRequest, BatchPredictionRequest, PredictionResponse, FeedbackRequest, HistoryItem
)
from backend.services.security import rate_limiter, optional_api_key
from backend.services.text_service import basic_text_stats
from backend.services.metrics_service import MetricsService

router = APIRouter(prefix="/api", tags=["Toxic Classification"])

def get_services(request: Request):
    return request.app.state.model_service, request.app.state.db

def build_risk(scores):
    max_score = max(scores.values()) if scores else 0
    if max_score >= 0.80:
        return "HIGH"
    if max_score >= 0.50:
        return "MEDIUM"
    return "LOW"

def save_doc(db, request_id, text, scores, labels, risk, confidence):
    db.save_prediction({
        "request_id": request_id,
        "text": text,
        "scores": scores,
        "labels": labels,
        "overall_toxic": any(labels.values()),
        "risk_level": risk,
        "confidence": confidence,
        "created_at": datetime.now(timezone.utc),
    })

@router.post("/predict", response_model=PredictionResponse, dependencies=[Depends(optional_api_key)])
async def predict(payload: PredictionRequest, request: Request, background_tasks: BackgroundTasks):
    client_id = request.client.host if request.client else "unknown"
    rate_limiter.check(client_id)

    model, db = get_services(request)
    if not model.loaded:
        raise HTTPException(status_code=503, detail="Model is not loaded. Train the model first.")

    scores, labels = model.predict(payload.text)
    confidence = max(scores.values()) if scores else 0.0
    risk = build_risk(scores)
    request_id = str(uuid4())

    background_tasks.add_task(
        save_doc, db, request_id, payload.text, scores, labels, risk, confidence
    )

    response = PredictionResponse(
        request_id=request_id,
        text=payload.text,
        overall_toxic=any(labels.values()),
        risk_level=risk,
        confidence=round(confidence, 4),
        labels=labels,
        scores={k: round(v, 4) for k, v in scores.items()},
        model_version=model.version,
        history_saved=db.connected,
    )


@router.post("/predict/batch", dependencies=[Depends(optional_api_key)])
async def predict_batch(payload: BatchPredictionRequest, request: Request):
    client_id = request.client.host if request.client else "unknown"
    rate_limiter.check(client_id)

    model, _ = get_services(request)
    if not model.loaded:
        raise HTTPException(status_code=503, detail="Model is not loaded.")

    results = []
    for text in payload.texts:
        scores, labels = model.predict(text)
        confidence = max(scores.values()) if scores else 0.0
        results.append({
            "text": text,
            "overall_toxic": any(labels.values()),
            "risk_level": build_risk(scores),
            "confidence": round(confidence, 4),
            "labels": labels,
            "scores": {k: round(v, 4) for k, v in scores.items()},
        })
    return {"count": len(results), "results": results}

@router.get("/history", response_model=list[HistoryItem], dependencies=[Depends(optional_api_key)])
async def history(
    request: Request,
    limit: int = Query(50, ge=1, le=100),
    toxic_only: bool | None = None
):
    _, db = get_services(request)
    if not db.connected:
        raise HTTPException(status_code=503, detail="MongoDB is unavailable.")
    return db.history(limit=limit, toxic_only=toxic_only)

@router.get("/stats", dependencies=[Depends(optional_api_key)])
async def stats(request: Request):
    _, db = get_services(request)
    return db.stats()

@router.get("/model", dependencies=[Depends(optional_api_key)])
async def model_info(request: Request):
    model, _ = get_services(request)
    return model.summary()

@router.post("/feedback", dependencies=[Depends(optional_api_key)])
async def feedback(payload: FeedbackRequest, request: Request):
    _, db = get_services(request)
    if not db.connected:
        raise HTTPException(status_code=503, detail="MongoDB is unavailable.")
    if not db.save_feedback(payload.request_id, payload.correct, payload.note):
        raise HTTPException(status_code=404, detail="Prediction not found.")
    return {"message": "Feedback saved."}


@router.get("/analyze-text", dependencies=[Depends(optional_api_key)])
async def analyze_text(text: str, request: Request):
    if not text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty.")
    if len(text) > 5000:
        raise HTTPException(status_code=400, detail="Text is limited to 5000 characters.")
    return basic_text_stats(text)

@router.get("/analytics", dependencies=[Depends(optional_api_key)])
async def analytics(request: Request):
    _, db = get_services(request)
    if not db.connected:
        raise HTTPException(status_code=503, detail="MongoDB is unavailable.")
    rows = db.history(limit=1000)
    return MetricsService().summarize(rows)

@router.get("/history/search", dependencies=[Depends(optional_api_key)])
async def search_history(request: Request, q: str = Query(..., min_length=1, max_length=100)):
    _, db = get_services(request)
    if not db.connected:
        raise HTTPException(status_code=503, detail="MongoDB is unavailable.")
    rows = db.history(limit=500)
    q_lower = q.lower()
    return [r for r in rows if q_lower in r.get("text", "").lower()][:100]

@router.get("/export", dependencies=[Depends(optional_api_key)])
async def export(request: Request):
    from fastapi.responses import StreamingResponse
    import csv, io
    _, db = get_services(request)
    if not db.connected:
        raise HTTPException(status_code=503, detail="MongoDB is unavailable.")
    rows = db.history(limit=1000)
    out = io.StringIO()
    writer = csv.writer(out)
    writer.writerow(["request_id", "created_at", "risk_level", "overall_toxic", "text"])
    for row in rows:
        writer.writerow([
            row.get("request_id"),
            row.get("created_at"),
            row.get("risk_level"),
            row.get("overall_toxic"),
            row.get("text", ""),
        ])
    out.seek(0)
    return StreamingResponse(
        iter([out.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=toxic_predictions.csv"}
    )
