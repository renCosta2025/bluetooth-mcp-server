from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api import bluetooth, session

# Create the FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG
)

# Configure CORS to allow requests from external clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register the API routers
app.include_router(bluetooth.router)
app.include_router(session.router)

# Health check route
@app.get("/health")
async def health_check():
    """
    Simple route to verify that the server is running.
    """
    return {"status": "ok"}
