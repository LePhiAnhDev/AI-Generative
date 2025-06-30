import os
import gc
import time
import torch
import psutil
import logging
from typing import Dict, Optional, Any
from datetime import datetime
from diffusers import StableDiffusionPipeline, AnimateDiffPipeline, MotionAdapter, EulerDiscreteScheduler, DiffusionPipeline
from huggingface_hub import hf_hub_download
from safetensors.torch import load_file
from models import ModelLoadResponse

logger = logging.getLogger(__name__)

def force_clear_gpu_memory():
    """Aggressive GPU memory clearing"""
    try:
        if torch.cuda.is_available():
            # Clear all cached memory
            torch.cuda.empty_cache()
            torch.cuda.ipc_collect()
            
            # Force garbage collection
            gc.collect()
            
            # Additional aggressive clearing
            torch.cuda.reset_peak_memory_stats()
            torch.cuda.reset_accumulated_memory_stats()
            
            logger.info("🧹 GPU memory cleared aggressively")
            
    except Exception as e:
        logger.warning(f"⚠️ Error clearing GPU memory: {e}")

def get_gpu_memory_info():
    """Get detailed GPU memory information"""
    if not torch.cuda.is_available():
        return "CPU mode - no GPU memory info"
    
    try:
        allocated = torch.cuda.memory_allocated() / 1024**3  # GB
        cached = torch.cuda.memory_reserved() / 1024**3     # GB
        total = torch.cuda.get_device_properties(0).total_memory / 1024**3  # GB
        free = total - allocated
        
        return f"GPU Memory: {allocated:.2f}GB/{total:.2f}GB allocated, {cached:.2f}GB cached, {free:.2f}GB free"
    except Exception as e:
        return f"Error getting GPU info: {e}"

class ModelManager:
    """Manages loading and unloading of AI models for load balancing"""
    
    def __init__(self):
        self.models: Dict[str, Any] = {}
        self.model_configs = {
            'generative_art': {
                'model_id': 'prompthero/openjourney',
                'type': 'stable_diffusion',
                'memory_estimate': 2500,  # MB - Very conservative for 8GB GPU
            },
            'generative_video': {
                'model_id': 'ByteDance/AnimateDiff-Lightning',
                'base_model': 'emilianJR/epiCRealism',
                'type': 'animatediff',
                'memory_estimate': 4500,  # MB - Conservative for 8GB GPU
            },
            'streaming_generative': {
                'model_id': 'stabilityai/sdxl-turbo',
                'type': 'sdxl_turbo',
                'memory_estimate': 2000,  # MB - Very light, optimized for speed
            }
        }
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.max_memory_mb = 6500  # Very conservative limit for 8GB GPU (leave 1.5GB buffer)
        self.currently_loaded = set()
        
    def get_memory_usage(self) -> float:
        """Get current GPU memory usage in MB"""
        if torch.cuda.is_available():
            return torch.cuda.memory_allocated() / (1024 * 1024)
        return 0.0
    
    def get_available_memory(self) -> float:
        """Get available GPU memory in MB"""
        if torch.cuda.is_available():
            return torch.cuda.memory_reserved() / (1024 * 1024)
        return float('inf')
    
    async def can_load_model(self, model_type: str) -> bool:
        """Check if we can load a model without exceeding memory limits"""
        if model_type not in self.model_configs:
            logger.error(f"❌ Unknown model type: {model_type}")
            return False
            
        required_memory = self.model_configs[model_type]['memory_estimate']
        current_memory = self.get_memory_usage()
        current_memory_gb = current_memory / 1024  # Convert to GB
        required_memory_gb = required_memory / 1024  # Convert to GB
        max_memory_gb = self.max_memory_mb / 1024  # Convert to GB
        
        # Get actual GPU memory info
        gpu_info = get_gpu_memory_info()
        logger.info(f"🔍 Memory Check for {model_type}:")
        logger.info(f"   Required: {required_memory_gb:.2f}GB")
        logger.info(f"   Current allocated: {current_memory_gb:.2f}GB") 
        logger.info(f"   Max limit: {max_memory_gb:.2f}GB")
        logger.info(f"   {gpu_info}")
        
        # For GPU 8GB, be more aggressive - if we have > 2GB free, allow loading
        if torch.cuda.is_available():
            total_memory = torch.cuda.get_device_properties(0).total_memory / 1024**3  # GB
            allocated_memory = torch.cuda.memory_allocated() / 1024**3  # GB
            free_memory = total_memory - allocated_memory
            
            logger.info(f"   Free GPU memory: {free_memory:.2f}GB")
            
            # More relaxed check for 8GB GPU
            if model_type == 'streaming_generative' and free_memory > 2.0:
                logger.info(f"✅ Allowing {model_type} - enough free memory for streaming")
                return True
            elif model_type == 'generative_art' and free_memory > 2.5:
                logger.info(f"✅ Allowing {model_type} - enough free memory for art generation")
                return True
            elif free_memory > 3.0:
                logger.info(f"✅ Allowing {model_type} - enough free memory")
                return True
            else:
                logger.warning(f"⚠️ Not enough free memory for {model_type}: {free_memory:.2f}GB available")
                return False
        
        # Fallback to original check for non-CUDA
        can_load = (current_memory + required_memory) <= self.max_memory_mb
        logger.info(f"{'✅' if can_load else '❌'} Memory check result: {can_load}")
        
        return can_load
    
    async def unload_model(self, model_type: str) -> bool:
        """Unload a specific model to free memory"""
        try:
            if model_type in self.models:
                # Store reference to model for explicit deletion
                model_to_delete = self.models[model_type]
                
                # Delete the model reference
                del self.models[model_type]
                del model_to_delete
                
                # Remove from loaded set
                self.currently_loaded.discard(model_type)
                
                # Aggressive memory clearing
                force_clear_gpu_memory()
                
                memory_info = get_gpu_memory_info()
                logger.info(f"✅ Unloaded model: {model_type}")
                logger.info(f"📊 {memory_info}")
                return True
                
        except Exception as e:
            logger.error(f"❌ Error unloading model {model_type}: {e}")
            # Still try to clear memory even if unload failed
            force_clear_gpu_memory()
            
        return False
    
    async def unload_all_except(self, keep_model: str = None) -> None:
        """Unload all models except the specified one"""
        models_to_unload = []
        for model_type in list(self.currently_loaded):
            if model_type != keep_model:
                models_to_unload.append(model_type)
        
        for model_type in models_to_unload:
            await self.unload_model(model_type)
    
    async def load_generative_art_model(self) -> bool:
        """Load prompthero/openjourney model for generative art"""
        pipe = None
        try:
            logger.info("🎨 Loading Generative Art model...")
            start_time = time.time()
            
            # Clear memory before loading
            force_clear_gpu_memory()
            pre_load_memory = get_gpu_memory_info()
            logger.info(f"📊 Pre-load: {pre_load_memory}")
            
            model_id = self.model_configs['generative_art']['model_id']
            
            if self.device == "cuda":
                pipe = StableDiffusionPipeline.from_pretrained(
                    model_id,
                    torch_dtype=torch.float16,
                    safety_checker=None,
                    requires_safety_checker=False,
                    low_cpu_mem_usage=True,
                    use_safetensors=True
                )
            else:
                pipe = StableDiffusionPipeline.from_pretrained(
                    model_id,
                    safety_checker=None,
                    requires_safety_checker=False,
                    low_cpu_mem_usage=True
                )
            
            # Move to device with memory monitoring
            pre_device_memory = get_gpu_memory_info()
            logger.info(f"📊 Pre-device: {pre_device_memory}")
            
            pipe.to(self.device)
            
            post_device_memory = get_gpu_memory_info()
            logger.info(f"📊 Post-device: {post_device_memory}")
            
            self.models['generative_art'] = pipe
            self.currently_loaded.add('generative_art')
            
            loading_time = time.time() - start_time
            logger.info(f"✅ Generative Art model loaded in {loading_time:.2f}s")
            return True
            
        except torch.cuda.OutOfMemoryError as e:
            logger.error(f"🔥 CUDA OOM loading Generative Art model: {e}")
            # Clean up on OOM
            if pipe is not None:
                del pipe
            force_clear_gpu_memory()
            return False
        except Exception as e:
            logger.error(f"❌ Error loading Generative Art model: {e}")
            # Clean up on any error
            if pipe is not None:
                del pipe
            force_clear_gpu_memory()
            return False
    
    async def load_generative_video_model(self) -> bool:
        """Load AnimateDiff-Lightning model for generative video"""
        try:
            logger.info("🎬 Loading Generative Video model...")
            start_time = time.time()
            
            repo = "ByteDance/AnimateDiff-Lightning"
            ckpt = "animatediff_lightning_4step_diffusers.safetensors"
            base = "emilianJR/epiCRealism"
            
            # Motion adapter
            adapter = MotionAdapter().to(self.device, torch.float16)
            adapter.load_state_dict(load_file(hf_hub_download(repo, ckpt), device=self.device))
            
            # Pipeline
            pipe = AnimateDiffPipeline.from_pretrained(
                base,
                motion_adapter=adapter,
                torch_dtype=torch.float16
            ).to(self.device)
            
            pipe.scheduler = EulerDiscreteScheduler.from_config(
                pipe.scheduler.config,
                timestep_spacing="trailing",
                beta_schedule="linear"
            )
            
            self.models['generative_video'] = pipe
            self.currently_loaded.add('generative_video')
            
            loading_time = time.time() - start_time
            logger.info(f"✅ Generative Video model loaded in {loading_time:.2f}s")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error loading Generative Video model: {e}")
            return False
    
    async def load_streaming_generative_model(self) -> bool:
        """Load SDXL-Turbo model for streaming generative art"""
        pipe = None
        try:
            logger.info("⚡ Loading Streaming Generative model...")
            start_time = time.time()
            
            # Clear memory before loading
            force_clear_gpu_memory()
            pre_load_memory = get_gpu_memory_info()
            logger.info(f"📊 Pre-load: {pre_load_memory}")
            
            model_id = self.model_configs['streaming_generative']['model_id']
            
            if self.device == "cuda":
                pipe = DiffusionPipeline.from_pretrained(
                    model_id,
                    torch_dtype=torch.float16,
                    variant="fp16",
                    low_cpu_mem_usage=True,
                    use_safetensors=True
                )
            else:
                pipe = DiffusionPipeline.from_pretrained(
                    model_id,
                    low_cpu_mem_usage=True
                )
            
            # Move to device with memory monitoring
            pre_device_memory = get_gpu_memory_info()
            logger.info(f"📊 Pre-device: {pre_device_memory}")
            
            pipe.to(self.device)
            
            post_device_memory = get_gpu_memory_info()
            logger.info(f"📊 Post-device: {post_device_memory}")
            
            self.models['streaming_generative'] = pipe
            self.currently_loaded.add('streaming_generative')
            
            loading_time = time.time() - start_time
            logger.info(f"✅ Streaming Generative model loaded in {loading_time:.2f}s")
            return True
            
        except torch.cuda.OutOfMemoryError as e:
            logger.error(f"🔥 CUDA OOM loading Streaming Generative model: {e}")
            # Clean up on OOM
            if pipe is not None:
                del pipe
            force_clear_gpu_memory()
            return False
        except Exception as e:
            logger.error(f"❌ Error loading Streaming Generative model: {e}")
            # Clean up on any error
            if pipe is not None:
                del pipe
            force_clear_gpu_memory()
            return False
    
    async def load_model(self, model_type: str, force_reload: bool = False) -> ModelLoadResponse:
        """Load a specific model with load balancing"""
        start_time = time.time()
        
        try:
            # Log initial memory state
            initial_memory = get_gpu_memory_info()
            logger.info(f"🚀 Loading model: {model_type}")
            logger.info(f"📊 Initial: {initial_memory}")
            logger.info(f"📋 Currently loaded models: {list(self.currently_loaded)}")
            
            # Check if model is already loaded
            if model_type in self.currently_loaded and not force_reload:
                logger.info(f"✅ Model {model_type} already loaded, skipping")
                return ModelLoadResponse(
                    model_type=model_type,
                    loaded=True,
                    loading_time=0.0,
                    memory_usage_mb=self.get_memory_usage()
                )
            
            # Force clear all memory before any operations
            logger.info("🧹 Clearing all GPU memory before loading...")
            force_clear_gpu_memory()
            
            # Unload ALL models to make maximum room
            logger.info("🗑️ Unloading all existing models...")
            await self.unload_all_except(None)  # Unload everything
            
            # Clear memory again after unloading
            force_clear_gpu_memory()
            
            after_clear_memory = get_gpu_memory_info()
            logger.info(f"📊 After clearing: {after_clear_memory}")
            
            # Check if we can load the model
            if not await self.can_load_model(model_type):
                return ModelLoadResponse(
                    model_type=model_type,
                    loaded=False,
                    loading_time=0.0,
                    memory_usage_mb=self.get_memory_usage(),
                    error="Insufficient memory to load model even after clearing"
                )
            
            # Load the requested model
            success = False
            try:
                if model_type == 'generative_art':
                    success = await self.load_generative_art_model()
                elif model_type == 'generative_video':
                    success = await self.load_generative_video_model()
                elif model_type == 'streaming_generative':
                    success = await self.load_streaming_generative_model()
                else:
                    raise ValueError(f"Unknown model type: {model_type}")
                    
            except torch.cuda.OutOfMemoryError as e:
                logger.error(f"🔥 CUDA OOM Error loading {model_type}: {e}")
                # Clear memory and try to recover
                force_clear_gpu_memory()
                success = False
                error_msg = f"CUDA out of memory loading {model_type}. Try closing other applications or use a smaller model."
                return ModelLoadResponse(
                    model_type=model_type,
                    loaded=False,
                    loading_time=time.time() - start_time,
                    memory_usage_mb=self.get_memory_usage(),
                    error=error_msg
                )
            
            loading_time = time.time() - start_time
            final_memory = get_gpu_memory_info()
            
            if success:
                logger.info(f"✅ Model {model_type} loaded successfully in {loading_time:.2f}s")
                logger.info(f"📊 Final: {final_memory}")
            else:
                logger.error(f"❌ Failed to load model {model_type}")
                # Clear memory on failure
                force_clear_gpu_memory()
            
            return ModelLoadResponse(
                model_type=model_type,
                loaded=success,
                loading_time=loading_time,
                memory_usage_mb=self.get_memory_usage(),
                error=None if success else "Failed to load model"
            )
            
        except Exception as e:
            logger.error(f"❌ Error in load_model: {e}")
            # Clear memory on any error
            force_clear_gpu_memory()
            return ModelLoadResponse(
                model_type=model_type,
                loaded=False,
                loading_time=time.time() - start_time,
                memory_usage_mb=self.get_memory_usage(),
                error=str(e)
            )
    
    def get_model(self, model_type: str) -> Optional[Any]:
        """Get a loaded model"""
        return self.models.get(model_type)
    
    def is_model_loaded(self, model_type: str) -> bool:
        """Check if a model is currently loaded"""
        return model_type in self.currently_loaded
    
    async def get_status(self) -> Dict[str, Any]:
        """Get current status of all models"""
        status = {
            'loaded_models': list(self.currently_loaded),
            'memory_usage_mb': self.get_memory_usage(),
            'device': self.device,
            'models_status': {}
        }
        
        for model_type in self.model_configs:
            status['models_status'][model_type] = {
                'loaded': self.is_model_loaded(model_type),
                'memory_estimate_mb': self.model_configs[model_type]['memory_estimate'],
                'model_id': self.model_configs[model_type]['model_id']
            }
        
        return status

# Global model manager instance
model_manager = ModelManager()