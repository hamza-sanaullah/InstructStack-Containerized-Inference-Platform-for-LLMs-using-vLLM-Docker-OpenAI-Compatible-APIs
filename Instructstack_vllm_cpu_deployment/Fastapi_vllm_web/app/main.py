"""
FastAPI vLLM Web Application

This module serves as the main entry point for the vLLM AI Assistant web application.
It configures the FastAPI app, middleware, static files, and routes.

Author: AI Assistant
Version: 1.0.0
"""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from api.routes import router as ui_router
from prometheus_fastapi_instrumentator import Instrumentator

# Initialize FastAPI application
app = FastAPI(
    title="vLLM AI Assistant",
    description="Advanced Language Model Testing Interface with vLLM Backend",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Enable Prometheus metrics collection
Instrumentator().instrument(app).expose(app)

# Configure CORS middleware for potential frontend extensions
# Note: In production, consider restricting allow_origins to specific domains
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for CSS, JavaScript, and other assets
app.mount("/static", StaticFiles(directory="static"), name="static")

# Configure Jinja2 templates for HTML rendering
templates = Jinja2Templates(directory="templates")

# Include the main UI router
app.include_router(ui_router, prefix="", tags=["UI"])

# Health check endpoint for monitoring
@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring and load balancers."""
    return {"status": "healthy", "service": "vLLM AI Assistant"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
