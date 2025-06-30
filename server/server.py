import os
import sys
sys.stdout.reconfigure(encoding='utf-8')
import asyncio
import time
import logging
import psutil
import torch
from datetime import datetime
from typing import Dict, List, Any, Optional
from contextlib import asynccontextmanager

# Import dotenv to load environment variables
from dotenv import load_dotenv
# Load environment variables from .env file
load_dotenv()

import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import ValidationError

# Import models and services
from models import (
    GenerativeArtRequest, GenerativeArtResponse,
    GenerativeVideoRequest, GenerativeVideoResponse,
    StreamingGenerativeRequest, StreamingGenerativeResponse,
    ModelLoadRequest, ModelLoadResponse, ModelUnloadRequest,
    BaseResponse
)

from generative_service import generative_service
from model_manager import model_manager, force_clear_gpu_memory

# Configure logging
logging.basicConfig(
    level=logging.INFO if os.getenv("DEBUG", "True").lower() == "true" else logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('ai_server.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

# Global state
app_state = {
    'start_time': time.time(),
    'request_count': 0,
    'service_stats': {
        'generative_art_requests': 0,
        'generative_video_requests': 0,
        'streaming_generative_requests': 0,
        'errors': 0
    }
}

# Rate limiting storage (simple in-memory)
rate_limit_storage = {}

# Lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan"""
    # Startup
    logger.info("🚀 Starting AI Generator Server")
    asyncio.create_task(cleanup_task())  
    yield
    # Shutdown
    logger.info("🔄 Shutting down AI Generator Server...")

# Create FastAPI app
app = FastAPI(
    title="AI Generator API",
    description="API for generating art, video and streaming content with AI",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Middleware
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:5173,http://127.0.0.1:5173").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["localhost", "127.0.0.1", "0.0.0.0"]
)

# Simple rate limiting function
def check_rate_limit(client_ip: str) -> bool:
    """Simple rate limiting check"""
    current_time = time.time()
    max_requests = int(os.getenv("MAX_REQUESTS_PER_MINUTE", "30"))
    
    if client_ip not in rate_limit_storage:
        rate_limit_storage[client_ip] = []
    
    # Clean old requests (older than 1 minute)
    rate_limit_storage[client_ip] = [
        req_time for req_time in rate_limit_storage[client_ip]
        if current_time - req_time < 60
    ]
    
    # Check rate limit
    if len(rate_limit_storage[client_ip]) >= max_requests:
        return False
    
    # Add current request
    rate_limit_storage[client_ip].append(current_time)
    return True

# Request tracking middleware
@app.middleware("http")
async def track_requests(request: Request, call_next):
    """Track request statistics"""
    start_time = time.time()
    app_state['request_count'] += 1
    
    # Simple rate limiting
    client_ip = request.client.host
    if not check_rate_limit(client_ip):
        return JSONResponse(
            status_code=429,
            content={"detail": "Rate limit exceeded. Maximum 30 requests per minute."}
        )
    
    logger.info(f"📨 {request.method} {request.url.path}")
    
    try:
        response = await call_next(request)
        return response
    except Exception as e:
        app_state['service_stats']['errors'] += 1
        logger.error(f"❌ Request error: {e}")
        raise
    finally:
        processing_time = time.time() - start_time
        logger.info(f"✅ {request.method} {request.url.path} - {processing_time:.3f}s")

# Health check endpoint
@app.get("/health", response_model=BaseResponse)
async def health_check():
    """Health check endpoint"""
    uptime = time.time() - app_state['start_time']
    
    # Get models status
    model_status = await model_manager.get_status()
    
    return BaseResponse(
        success=True,
        message="AI Generator Server is healthy",
        timestamp=datetime.now()
    )

# AI Collections endpoints
@app.post("/generate-art", response_model=GenerativeArtResponse)
async def generate_art(request: GenerativeArtRequest):
    """Generate art using prompthero/openjourney model"""
    try:
        app_state['service_stats']['generative_art_requests'] += 1
        logger.info(f"🎨 Art generation request: {request.prompt[:50]}...")
        
        response = await generative_service.generate_art(request)
        
        if not response.success:
            app_state['service_stats']['errors'] += 1
            
        return response
        
    except Exception as e:
        logger.error(f"❌ Art generation error: {e}")
        app_state['service_stats']['errors'] += 1
        raise HTTPException(status_code=500, detail=f"Art generation failed: {str(e)}")

@app.post("/generate-video", response_model=GenerativeVideoResponse)
async def generate_video(request: GenerativeVideoRequest):
    """Generate video using AnimateDiff-Lightning model"""
    try:
        app_state['service_stats']['generative_video_requests'] += 1
        logger.info(f"🎬 Video generation request: {request.prompt[:50]}...")
        
        response = await generative_service.generate_video(request)
        
        if response.success:
            # Set video URL if video was generated successfully
            if response.video_filename:
                response.video_url = f"/videos/{response.video_filename}"
            logger.info(f"✅ Video generated successfully in {response.processing_time:.2f}s")
        else:
            app_state['service_stats']['errors'] += 1
            
        return response
        
    except Exception as e:
        logger.error(f"❌ Video generation error: {e}")
        app_state['service_stats']['errors'] += 1
        raise HTTPException(status_code=500, detail=f"Video generation failed: {str(e)}")

@app.post("/generate-streaming", response_model=StreamingGenerativeResponse)
async def generate_streaming(request: StreamingGenerativeRequest):
    """Generate streaming art using SDXL-Turbo model"""
    try:
        app_state['service_stats']['streaming_generative_requests'] += 1
        logger.info(f"⚡ Streaming generation request: {request.prompt[:50]}...")
        
        response = await generative_service.generate_streaming(request)
        
        if not response.success:
            app_state['service_stats']['errors'] += 1
            
        return response
        
    except Exception as e:
        logger.error(f"❌ Streaming generation error: {e}")
        app_state['service_stats']['errors'] += 1
        raise HTTPException(status_code=500, detail=f"Streaming generation failed: {str(e)}")

# Model management endpoints
@app.post("/models/load", response_model=ModelLoadResponse)
async def load_model(request: ModelLoadRequest):
    """Load a specific model"""
    try:
        logger.info(f"📥 Loading model: {request.model_type}")
        
        response = await model_manager.load_model(request.model_type, request.force_reload)
            
        return response
        
    except Exception as e:
        logger.error(f"❌ Model loading error: {e}")
        raise HTTPException(status_code=500, detail=f"Model loading failed: {str(e)}")

@app.post("/models/unload")
async def unload_model(request: ModelUnloadRequest):
    """Unload a specific model"""
    try:
        logger.info(f"📥 Unloading model: {request.model_type}")
        
        success = await model_manager.unload_model(request.model_type)
        
        if success:
            logger.info(f"✅ Model {request.model_type} unloaded successfully")
            return {"success": True, "message": f"Model {request.model_type} unloaded successfully"}
        else:
            return {"success": False, "message": f"Failed to unload model {request.model_type}"}
            
    except Exception as e:
        logger.error(f"❌ Model unloading error: {e}")
        raise HTTPException(status_code=500, detail=f"Model unloading failed: {str(e)}")

@app.post("/models/clear-all")
async def clear_all_models():
    """Force clear ALL models and GPU memory"""
    start_time = time.time()
    logger.info(f"📨 POST /models/clear-all")
    
    try:
        logger.info("🧹 Force clearing ALL models and memory...")
        
        # Unload all models
        await model_manager.unload_all_except(None)
        
        # Additional aggressive cleanup
        force_clear_gpu_memory()
        
        # Additional aggressive cleanup
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            torch.cuda.ipc_collect()
            torch.cuda.reset_peak_memory_stats()
            torch.cuda.reset_accumulated_memory_stats()
            torch.cuda.synchronize()
            logger.info("💥 Performed nuclear GPU cleanup")
        
        processing_time = time.time() - start_time
        logger.info(f"✅ Models cleared - {processing_time:.3f}s")
        
        return {
            "success": True,
            "message": "ALL models cleared successfully",
            "processing_time": processing_time
        }
        
    except Exception as e:
        logger.error(f"❌ Error clearing models: {e}")
        return {
            "success": False,
            "message": f"Error clearing models: {str(e)}",
            "processing_time": time.time() - start_time
        }

@app.get("/models/status")
async def get_model_status():
    """Get model status"""
    try:
        status = await model_manager.get_status()
        return {
            "success": True,
            "data": status
        }
    except Exception as e:
        logger.error(f"❌ Error getting model status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get model status: {str(e)}")

# Video streaming endpoint
@app.get("/videos/{filename}")
async def stream_video(filename: str):
    """Stream video files"""
    try:
        # Security: validate filename
        if not filename.endswith('.mp4') or '/' in filename or '\\' in filename:
            raise HTTPException(status_code=400, detail="Invalid filename")
        
        # Use absolute path to match where videos are saved
        videos_dir = os.path.abspath("videos")
        video_path = os.path.join(videos_dir, filename)
        
        # Check if file exists
        if not os.path.exists(video_path):
            raise HTTPException(status_code=404, detail="Video not found")
        
        # Return video file with proper streaming headers
        from fastapi.responses import FileResponse
        
        return FileResponse(
            path=video_path,
            media_type="video/mp4",
            headers={
                "Accept-Ranges": "bytes",
                "Content-Type": "video/mp4",
                "Cache-Control": "public, max-age=3600"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error streaming video {filename}: {e}")
        raise HTTPException(status_code=500, detail="Failed to stream video")

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "service": "AI Generator API",
        "version": "1.0.0",
        "description": "Generate art, video and streaming content with AI",
        "endpoints": {
            "health": "/health",
            "generate-art": "/generate-art",
            "generate-video": "/generate-video",
            "generate-streaming": "/generate-streaming",
            "docs": "/docs"
        },
        "uptime_seconds": time.time() - app_state['start_time']
    }

# Background task for cleanup
async def cleanup_task():
    """Background cleanup task"""
    while True:
        try:
            current_time = time.time()
            for client_ip in list(rate_limit_storage.keys()):
                rate_limit_storage[client_ip] = [
                    req_time for req_time in rate_limit_storage[client_ip]
                    if current_time - req_time < 300
                ]
                
                if not rate_limit_storage[client_ip]:
                    del rate_limit_storage[client_ip]
            
            await asyncio.sleep(300)  # Run every 5 minutes
            
        except Exception as e:
            logger.error(f"Cleanup task error: {e}")
            await asyncio.sleep(60)

# Create videos directory if it doesn't exist
os.makedirs("videos", exist_ok=True)

if __name__ == "__main__":
    # Get configuration from environment variables
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    debug = os.getenv("DEBUG", "True").lower() == "true"
    
    logger.info(f"🚀 Starting AI Generator Server on {host}:{port} (debug={debug})...")
    
    uvicorn.run(
        "server:app",
        host=host,
        port=port,
        reload=debug,
        log_level="info" if debug else "warning",
        access_log=True
    )