from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base response model
class BaseResponse(BaseModel):
    success: bool = True
    message: str = "Request processed successfully"
    timestamp: datetime = Field(default_factory=datetime.now)

# AI Collections models
class GenerativeArtRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=1000, description="Prompt for image generation")
    num_inference_steps: int = Field(default=70, ge=10, le=100)
    guidance_scale: float = Field(default=5.0, ge=1.0, le=20.0)
    width: int = Field(default=512, ge=256, le=1024)
    height: int = Field(default=512, ge=256, le=1024)

class GenerativeArtResponse(BaseResponse):
    image_base64: str = Field(..., description="Generated image in base64 format")
    prompt_used: str = ""
    processing_time: float = 0.0
    model_used: str = "prompthero/openjourney"

class GenerativeVideoRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=1000, description="Prompt for video generation")
    num_frames: int = Field(default=32, ge=8, le=64)
    guidance_scale: float = Field(default=1.0, ge=0.5, le=2.0)
    num_inference_steps: int = Field(default=4, ge=1, le=10)
    width: int = Field(default=512, ge=256, le=1024)
    height: int = Field(default=512, ge=256, le=1024)

class GenerativeVideoResponse(BaseResponse):
    video_filename: str = Field(..., description="Generated video filename")
    video_url: str = Field(default="", description="URL to stream the video")
    prompt_used: str = ""
    processing_time: float = 0.0
    num_frames: int = 32
    fps: int = 5
    model_used: str = "ByteDance/AnimateDiff-Lightning"

class StreamingGenerativeRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=1000, description="Prompt for streaming image generation")
    num_inference_steps: int = Field(default=2, ge=1, le=5)
    guidance_scale: float = Field(default=0.0, ge=0.0, le=1.0)
    width: int = Field(default=512, ge=256, le=1024)
    height: int = Field(default=512, ge=256, le=1024)

class StreamingGenerativeResponse(BaseResponse):
    image_base64: str = Field(..., description="Generated image in base64 format")
    prompt_used: str = ""
    processing_time: float = 0.0
    model_used: str = "stabilityai/sdxl-turbo"

class ModelLoadRequest(BaseModel):
    model_type: str = Field(..., pattern="^(generative_art|generative_video|streaming_generative)$")
    force_reload: bool = False

class ModelUnloadRequest(BaseModel):
    model_type: str = Field(..., pattern="^(generative_art|generative_video|streaming_generative)$")

class ModelLoadResponse(BaseResponse):
    model_type: str
    loaded: bool = False
    loading_time: float = 0.0
    memory_usage_mb: float = 0.0
    error: Optional[str] = None