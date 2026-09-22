from pathlib import Path
from fastapi import FastAPI, Request
import time
import uuid
from backend.logging_config import configure_logging
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from backend.config import get_settings
from backend.api.routes import router
from backend.services.model_service import ModelService
from backend.services.database_service import DatabaseService

configure_logging()
settings = get_settings()
app = FastAPI(
    title="Toxic Comment Classifier — Production-Style Toxic Comment Classifier",
    description="Multi-label NLP classification API with analytics, feedback, history and model metadata.",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_list,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def request_metadata(request: Request, call_next):
    request_id = str(uuid.uuid4())
    start = time.perf_counter()
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Response-Time-ms"] = str(round((time.perf_counter() - start) * 1000, 2))
    return response

@app.middleware("http")
async def security_headers(request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response

@app.on_event("startup")
async def startup():
    app.state.model_service = ModelService(settings.model_path, settings.model_config_path)
    try:
        app.state.model_service.load()
    except Exception:
        # App remains available so /health and /docs explain what is missing.
        pass
    app.state.db = DatabaseService()

@app.on_event("shutdown")
async def shutdown():
    app.state.db.close()

@app.get("/health")
async def health():
    model = app.state.model_service
    db = app.state.db
    return {
        "status": "ok" if model.loaded else "degraded",
        "model_loaded": model.loaded,
        "database_connected": db.connected,
        "model_version": model.version,
    }

app.include_router(router)

FRONTEND = Path(__file__).resolve().parent.parent / "frontend"
app.mount("/static", StaticFiles(directory=FRONTEND), name="static")

@app.get("/", include_in_schema=False)
async def home():
    return FileResponse(FRONTEND / "index.html")
