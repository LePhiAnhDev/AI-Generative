#!/usr/bin/env python3
"""
GPU Memory Management Utilities
For debugging and manual memory management in AI Collections
"""

import os
import gc
import time
import torch
import psutil
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_detailed_gpu_info():
    """Get comprehensive GPU memory information"""
    if not torch.cuda.is_available():
        return {"status": "CUDA not available - running on CPU"}
    
    try:
        allocated = torch.cuda.memory_allocated() / 1024**3  # GB
        cached = torch.cuda.memory_reserved() / 1024**3     # GB
        total = torch.cuda.get_device_properties(0).total_memory / 1024**3  # GB
        free = total - allocated
        
        return {
            "total_gb": round(total, 2),
            "allocated_gb": round(allocated, 2),
            "cached_gb": round(cached, 2),
            "free_gb": round(free, 2),
            "utilization_percent": round((allocated / total) * 100, 1)
        }
        
    except Exception as e:
        return {"error": str(e)}

def aggressive_memory_cleanup():
    """Perform aggressive GPU memory cleanup"""
    logger.info("🧹 Starting aggressive GPU memory cleanup...")
    
    try:
        # Python garbage collection
        collected = gc.collect()
        logger.info(f"🗑️ Python GC collected {collected} objects")
        
        if torch.cuda.is_available():
            # Clear CUDA cache
            torch.cuda.empty_cache()
            logger.info("🧹 CUDA cache cleared")
            
            # Clear IPC memory
            torch.cuda.ipc_collect()
            logger.info("🧹 CUDA IPC collected")
            
            # Reset memory stats
            torch.cuda.reset_peak_memory_stats()
            torch.cuda.reset_accumulated_memory_stats()
            logger.info("📊 CUDA memory stats reset")
            
            # Force synchronization
            torch.cuda.synchronize()
            logger.info("⚡ CUDA synchronized")
            
        logger.info("✅ Aggressive cleanup completed")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error during cleanup: {e}")
        return False

def print_memory_report():
    """Print comprehensive memory report"""
    print("\n" + "="*60)
    print("🔍 GPU MEMORY DIAGNOSTIC REPORT")
    print("="*60)
    
    # GPU info
    print("\n🖥️ GPU Information:")
    gpu_info = get_detailed_gpu_info()
    if "error" in gpu_info:
        print(f"   Error: {gpu_info['error']}")
    elif "status" in gpu_info:
        print(f"   Status: {gpu_info['status']}")
    else:
        print(f"   Total: {gpu_info['total_gb']} GB")
        print(f"   Used: {gpu_info['allocated_gb']} GB ({gpu_info['utilization_percent']}%)")
        print(f"   Cached: {gpu_info['cached_gb']} GB")
        print(f"   Free: {gpu_info['free_gb']} GB")
    
    # System memory
    memory = psutil.virtual_memory()
    print(f"\n💾 System RAM:")
    print(f"   Total: {memory.total / 1024**3:.1f} GB")
    print(f"   Used: {memory.used / 1024**3:.1f} GB ({memory.percent}%)")
    print(f"   Free: {memory.available / 1024**3:.1f} GB")
    
    print("\n" + "="*60)

if __name__ == "__main__":
    print("GPU Memory Management Utilities")
    print("1. Memory Report")
    print("2. Aggressive Cleanup")
    print("3. Both")
    
    choice = input("Choose option (1-3): ").strip()
    
    if choice in ["1", "3"]:
        print_memory_report()
    
    if choice in ["2", "3"]:
        aggressive_memory_cleanup()
        if choice == "3":
            print("\nAfter cleanup:")
            print_memory_report()