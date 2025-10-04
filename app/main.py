from fastapi import FastAPI
from app.core.config import settings
from app.api.endpoints import filter

app = FastAPI(title=settings.PROJECT_NAME)

app.include_router(filter.router, prefix="/api/v1/filter", tags=["Filter"])

@app.get("/health", tags=["Health"])
def read_root():
    return {"status": "ok"}