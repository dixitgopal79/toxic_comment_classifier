from datetime import datetime
from typing import Dict, List, Optional
from pydantic import BaseModel, Field

LABELS = ["toxic", "severe_toxic", "obscene", "threat", "insult", "identity_hate"]

class PredictionRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=5000)

class BatchPredictionRequest(BaseModel):
    texts: List[str] = Field(..., min_length=1, max_length=20)

class PredictionResponse(BaseModel):
    request_id: str
    text: str
    overall_toxic: bool
    risk_level: str
    confidence: float
    labels: Dict[str, bool]
    scores: Dict[str, float]
    model_version: str
    history_saved: bool

class HistoryItem(BaseModel):
    request_id: str
    text: str
    overall_toxic: bool
    risk_level: str
    confidence: float
    labels: Dict[str, bool]
    scores: Dict[str, float]
    created_at: datetime

class FeedbackRequest(BaseModel):
    request_id: str
    correct: bool
    note: Optional[str] = Field(default="", max_length=1000)

class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    database_connected: bool
    model_version: str
