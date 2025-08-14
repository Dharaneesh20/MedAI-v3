"""
ASGI config for medai project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

import os
from django.core.asgi import get_asgi_application
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medai.settings')

# Get Django ASGI application
django_asgi_app = get_asgi_application()

# Create FastAPI app
fastapi_app = FastAPI(
    title="MedAi API",
    description="Drug Interaction Analysis API",
    version="1.0.0"
)

# Add CORS middleware
fastapi_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import routers
from api.routers import auth, analysis, history

# Include routers
fastapi_app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
fastapi_app.include_router(analysis.router, prefix="/api/analysis", tags=["Analysis"])
fastapi_app.include_router(history.router, prefix="/api/history", tags=["History"])

@fastapi_app.get("/")
async def root():
    return {"message": "MedAi API is running"}

# Mount Django on /django
from fastapi.applications import FastAPI
from fastapi.middleware.wsgi import WSGIMiddleware

app = FastAPI()
app.mount("/api", fastapi_app)
app.mount("/", WSGIMiddleware(django_asgi_app))
