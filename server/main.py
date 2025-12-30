from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from server.routes.languages import router as languages_router
from server.routes.model import router as model_router
from server.routes.preferences import router as preferences_router
from server.routes.saved import router as saved_router
from server.routes.translate import router as translate_router

app = FastAPI(
    title="Babelo API",
    description="A FastAPI backend service",
    version="0.1.0",
)

# Configure CORS to allow the frontend to make requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(saved_router)
app.include_router(languages_router)
app.include_router(model_router)
app.include_router(preferences_router)
app.include_router(translate_router)


@app.get("/")
async def root():
    """Health check endpoint."""
    return {"status": "ok", "service": "Babelo API"}
