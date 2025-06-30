import os
import gc
import time
import base64
import logging
import numpy as np
from io import BytesIO
from PIL import Image
from typing import Dict, Any, Optional
import torch
import imageio
from datetime import datetime

from model_manager import model_manager, force_clear_gpu_memory, get_gpu_memory_info
from models import (
    GenerativeArtRequest, GenerativeArtResponse,
    GenerativeVideoRequest, GenerativeVideoResponse, 
    StreamingGenerativeRequest, StreamingGenerativeResponse
)

logger = logging.getLogger(__name__)

class GenerativeService:
    """Service for handling all generative AI operations"""
    
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
    def _image_to_base64(self, image: Image.Image) -> str:
        """Convert PIL Image to base64 string"""
        buffer = BytesIO()
        image.save(buffer, format="PNG")
        img_str = base64.b64encode(buffer.getvalue()).decode("utf-8")
        return img_str
    
    def _save_video_file(self, frames, fps: int = 5) -> str:
        """Save video frames to MP4 file and return filename"""
        try:
            # Generate unique filename
            timestamp = int(time.time() * 1000)
            filename = f"video_{timestamp}.mp4"
            
            # Use absolute path to ensure file is saved in correct location
            videos_dir = os.path.abspath("videos")
            os.makedirs(videos_dir, exist_ok=True)  # Ensure directory exists
            filepath = os.path.join(videos_dir, filename)
            
            logger.info(f"📁 Saving video to: {filepath}")
            
            # Convert frames to numpy arrays
            frame_arrays = []
            for frame in frames:
                if hasattr(frame, 'numpy'):
                    frame_arrays.append(frame.numpy())
                else:
                    frame_arrays.append(np.array(frame))
            
            # Write video to file using imageio
            with imageio.get_writer(filepath, fps=fps, codec='libx264', quality=8) as writer:
                for frame in frame_arrays:
                    writer.append_data(frame)
            
            logger.info(f"📹 Video saved as: {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"Error saving video file: {e}")
            return ""
    
    def _create_enhanced_prompt(self, user_prompt: str, prompt_type: str = "art") -> str:
        """Create enhanced prompt for better generation quality"""
        if prompt_type == "art":
            return (
                f"mdjrny-v4 style {user_prompt}, masterpiece, 8k uhd, "
                "ultra-realistic, hyper detailed, volumetric lighting, cinematic composition, "
                "dramatic lighting, ray tracing, subsurface scattering, octane render, unreal engine 5, "
                "trending on artstation, award winning, professional photography, highly detailed, "
                "sharp focus, rich colors, intricate details, elegant, luxurious, ethereal atmosphere, "
                "perfect composition, color grading, post-processing, artistic masterpiece, featured on behance, "
                "featured on artstation, NFT art, digital art"
            )
        elif prompt_type == "video":
            return f"{user_prompt}, high quality, smooth motion, cinematic, detailed"
        else:  # streaming
            return user_prompt  # Keep simple for fast generation
    
    def _get_negative_prompt(self, prompt_type: str = "art") -> str:
        """Get negative prompt for better quality"""
        if prompt_type in ["art", "video"]:
            return (
                "ugly, deformed, noisy, blurry, low quality, duplicate, mutated, extra limbs, "
                "poorly drawn face, poorly drawn hands, distorted, underexposed, overexposed, "
                "bad art, beginner art, amateur, watermark, signature, text"
            )
        return "low quality, blurry, distorted"
    
    async def generate_art(self, request: GenerativeArtRequest) -> GenerativeArtResponse:
        """Generate art using prompthero/openjourney model"""
        start_time = time.time()
        
        try:
            # Clear memory before generation
            force_clear_gpu_memory()
            pre_gen_memory = get_gpu_memory_info()
            logger.info(f"📊 Pre-generation: {pre_gen_memory}")
            
            # Load model if not already loaded
            load_result = await model_manager.load_model('generative_art')
            if not load_result.loaded:
                raise Exception(f"Failed to load generative art model: {load_result.error}")
            
            # Get the model
            pipe = model_manager.get_model('generative_art')
            if not pipe:
                raise Exception("Generative art model not available")
            
            # Prepare prompts
            enhanced_prompt = self._create_enhanced_prompt(request.prompt, "art")
            negative_prompt = self._get_negative_prompt("art")
            
            logger.info(f"🎨 Generating art with prompt: {request.prompt}")
            
            # Clear cache before generation
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            
            # Generate image
            try:
                if self.device == "cuda":
                    with torch.autocast("cuda"):
                        result = pipe(
                            prompt=enhanced_prompt,
                            negative_prompt=negative_prompt,
                            num_inference_steps=request.num_inference_steps,
                            guidance_scale=request.guidance_scale,
                            width=request.width,
                            height=request.height
                        )
                else:
                    result = pipe(
                        prompt=enhanced_prompt,
                        negative_prompt=negative_prompt,
                        num_inference_steps=request.num_inference_steps,
                        guidance_scale=request.guidance_scale,
                        width=request.width,
                        height=request.height
                    )
                
                image = result.images[0]
                
                # Clear intermediate results
                del result
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()
                
            except torch.cuda.OutOfMemoryError as e:
                logger.error(f"🔥 CUDA OOM during art generation: {e}")
                force_clear_gpu_memory()
                raise Exception("GPU out of memory during generation. Try reducing image size or num_inference_steps.")
            
            # Convert to base64
            image_base64 = self._image_to_base64(image)
            
            # Clear image from memory
            del image
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            
            processing_time = time.time() - start_time
            final_memory = get_gpu_memory_info()
            logger.info(f"✅ Art generated in {processing_time:.2f}s")
            logger.info(f"📊 Final: {final_memory}")
            
            return GenerativeArtResponse(
                image_base64=image_base64,
                prompt_used=request.prompt,
                processing_time=processing_time,
                model_used="prompthero/openjourney"
            )
            
        except Exception as e:
            logger.error(f"❌ Error generating art: {e}")
            # Clear memory on error
            force_clear_gpu_memory()
            # Return fallback response
            return GenerativeArtResponse(
                success=False,
                message=f"Failed to generate art: {str(e)}",
                image_base64="",
                prompt_used=request.prompt,
                processing_time=time.time() - start_time
            )
    
    async def generate_video(self, request: GenerativeVideoRequest) -> GenerativeVideoResponse:
        """Generate video using AnimateDiff-Lightning model"""
        start_time = time.time()
        
        try:
            # Load model if not already loaded
            load_result = await model_manager.load_model('generative_video')
            if not load_result.loaded:
                raise Exception(f"Failed to load generative video model: {load_result.error}")
            
            # Get the model
            pipe = model_manager.get_model('generative_video')
            if not pipe:
                raise Exception("Generative video model not available")
            
            # Prepare prompt
            enhanced_prompt = self._create_enhanced_prompt(request.prompt, "video")
            
            logger.info(f"🎬 Generating video with prompt: {request.prompt}")
            
            # Generate video frames
            output = pipe(
                prompt=enhanced_prompt,
                guidance_scale=request.guidance_scale,
                num_inference_steps=request.num_inference_steps,
                num_frames=request.num_frames,
                width=request.width,
                height=request.height
            )
            
            frames = output.frames[0]
            fps = 5  # Standard FPS for generated videos
            
            # Save video file
            video_filename = self._save_video_file(frames, fps)
            
            processing_time = time.time() - start_time
            logger.info(f"✅ Video generated in {processing_time:.2f}s")
            
            return GenerativeVideoResponse(
                video_filename=video_filename,
                prompt_used=request.prompt,
                processing_time=processing_time,
                num_frames=request.num_frames,
                fps=fps,
                model_used="ByteDance/AnimateDiff-Lightning + emilianJR/epiCRealism"
            )
            
        except Exception as e:
            logger.error(f"❌ Error generating video: {e}")
            return GenerativeVideoResponse(
                success=False,
                message=f"Failed to generate video: {str(e)}",
                video_filename="",
                prompt_used=request.prompt,
                processing_time=time.time() - start_time,
                num_frames=request.num_frames
            )
    
    async def generate_streaming(self, request: StreamingGenerativeRequest) -> StreamingGenerativeResponse:
        """Generate image using SDXL-Turbo for streaming (fast generation)"""
        start_time = time.time()
        
        try:
            # Light memory clearing for streaming (don't want to slow down too much)
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            
            # Load model if not already loaded
            load_result = await model_manager.load_model('streaming_generative')
            if not load_result.loaded:
                raise Exception(f"Failed to load streaming generative model: {load_result.error}")
            
            # Get the model
            pipe = model_manager.get_model('streaming_generative')
            if not pipe:
                raise Exception("Streaming generative model not available")
            
            logger.info(f"⚡ Generating streaming image with prompt: {request.prompt}")
            
            # Generate image (fast generation with minimal steps)
            try:
                result = pipe(
                    prompt=request.prompt,
                    num_inference_steps=request.num_inference_steps,
                    guidance_scale=request.guidance_scale,
                    width=request.width,
                    height=request.height
                )
                
                image = result.images[0]
                
                # Quick cleanup for streaming
                del result
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()
                
            except torch.cuda.OutOfMemoryError as e:
                logger.error(f"🔥 CUDA OOM during streaming generation: {e}")
                force_clear_gpu_memory()
                raise Exception("GPU out of memory during streaming generation. Try reducing image size.")
            
            # Convert to base64
            image_base64 = self._image_to_base64(image)
            
            # Quick cleanup for streaming
            del image
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            
            processing_time = time.time() - start_time
            logger.info(f"✅ Streaming image generated in {processing_time:.2f}s")
            
            return StreamingGenerativeResponse(
                image_base64=image_base64,
                prompt_used=request.prompt,
                processing_time=processing_time,
                model_used="stabilityai/sdxl-turbo"
            )
            
        except Exception as e:
            logger.error(f"❌ Error generating streaming image: {e}")
            # Light memory cleanup on error for streaming
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            return StreamingGenerativeResponse(
                success=False,
                message=f"Failed to generate streaming image: {str(e)}",
                image_base64="",
                prompt_used=request.prompt,
                processing_time=time.time() - start_time
            )

# Global service instance
generative_service = GenerativeService()