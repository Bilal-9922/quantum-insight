from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.routes_analysis import router as analysis_router
from app.api.routes_health import router as health_router
from app.api.routes_optimizer import router as optimizer_router
from app.api.routes_debugger import router as debugger_router
from app.api.routes_reports import router as reports_router

app = FastAPI(title=settings.app_name, version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analysis_router, prefix="/api")
app.include_router(health_router, prefix="/api")
app.include_router(optimizer_router, prefix="/api")
app.include_router(debugger_router, prefix="/api")
app.include_router(reports_router, prefix="/api")

@app.get("/")
def root():
    return {"name": settings.app_name, "status": "ok"}

@app.get("/api/healthcheck")
def healthcheck():
    return {"status": "healthy"}
