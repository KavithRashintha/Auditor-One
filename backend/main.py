from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.config import settings

app = FastAPI(title="Auditor-One API")

# Configure CORS dynamically based on settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "Accept"],
)

from backend.api.router import router as api_router

app.include_router(api_router)

@app.get("/health")
async def health_check():
    return {"status": "ok"}
