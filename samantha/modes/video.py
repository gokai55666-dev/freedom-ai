"""Video generation mode - Fully automated Wan 2.2 integration"""

import streamlit as st
import requests
import time
import os
import json
from pathlib import Path

def check_comfyui():
    """Check if ComfyUI is accessible"""
    try:
        response = requests.get("http://localhost:8188/system_stats", timeout=2)
        return response.status_code == 200
    except:
        return False

def build_workflow(image_path, prompt, duration, fps, quality):
    """Build ComfyUI workflow for video generation"""
    num_frames = duration * fps
    
    models = {
        "Fast (TI2V-5B)": ("Wan2.2_TI2V_5B_fp16.safetensors", 20, (832, 480)),
        "Balanced": ("Wan2.2_TI2V_5B_fp16.safetensors", 30, (1280, 720)),
        "Quality (I2V-A14B)": ("Wan2.2_I2V_A14B_fp16.safetensors", 40, (1280, 720))
    }
    
    model, steps, (width, height) = models.get(quality, models["Balanced"])
    
    workflow = {
        "1": {"inputs": {"image": image_path}, "class_type": "LoadImage"},
        "2": {"inputs": {"model_name": model, "precision": "fp16"}, "class_type": "WanVideoLoader"},
        "3": {
            "inputs": {
                "positive": prompt,
                "negative": "blur, distortion, low quality",
                "image": ["1", 0],
                "vae": ["2", 1]
            },
            "class_type": "WanVideoEncode"
        },
        "4": {
            "inputs": {
                "seed": int(time.time()) % 2147483647,
                "steps": steps,
                "cfg": 7.0,
                "model": ["2", 0],
                "positive": ["3", 0],
                "negative": ["3", 1],
                "width": width,
                "height": height,
                "num_frames": num_frames
            },
            "class_type": "WanVideoSampler"
        },
        "5": {"inputs": {"samples": ["4", 0], "vae": ["2", 1]}, "class_type": "WanVideoDecode"},
        "6": {
            "inputs": {"filename_prefix": "SamanthaVideo", "fps": fps, "video": ["5", 0]},
            "class_type": "SaveVideo"
        }
    }
    return workflow

def render(config):
    """Render video generation interface"""
    st.header("🎬 Video Generation - Fully Automated")
    
    # Check prerequisites
    if not check_comfyui():
        st.error("❌ ComfyUI not running")
        if st.button("🔄 Start ComfyUI", use_container_width=True):
            os.system("systemctl start samantha-comfyui")
            time.sleep(5)
            st.rerun()
        return
    
    # Step 1: Upload
    st.subheader("Step 1: Upload Image")
    uploaded = st.file_uploader("Choose image to animate", type=['png', 'jpg', 'jpeg'])
    
    if not uploaded:
        st.info("👆 Upload an image to begin")
        return
    
    # Save upload
    timestamp = int(time.time())
    temp_path = f"/tmp/samantha_video_{timestamp}.png"
    with open(temp_path, "wb") as f:
        f.write(uploaded.getbuffer())
    
    st.image(temp_path, caption="Input Image", use_column_width=True)
    
    # Step 2: Configure
    st.subheader("Step 2: Configure")
    motion = st.text_area("Motion Description", 
                         "slow cinematic camera movement, detailed textures, professional lighting",
                         height=80)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        duration = st.selectbox("Duration", [2, 5, 10], index=1, format_func=lambda x: f"{x} seconds")
    with col2:
        quality = st.selectbox("Quality", ["Fast (TI2V-5B)", "Balanced", "Quality (I2V-A14B)"], index=1)
    with col3:
        fps = st.selectbox("FPS", [16, 24], index=0)
    
    # Step 3: Generate
    st.subheader("Step 3: Generate")
    
    if st.button("🎬 AUTO-GENERATE VIDEO", type="primary", use_container_width=True):
        progress = st.progress(0)
        status = st.empty()
        
        try:
            # Build and queue
            workflow = build_workflow(temp_path, motion, duration, fps, quality)
            
            status.info("🎬 Connecting to ComfyUI...")
            progress.progress(10)
            
            response = requests.post(
                "http://localhost:8188/prompt",
                json={"prompt": workflow},
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                prompt_id = result.get('prompt_id', 'unknown')
                
                progress.progress(20)
                status.success(f"✅ Queued successfully! ID: {prompt_id[:8]}")
                
                # Display info
                st.balloons()
                st.info(f"""
                **Video Generation Started**
                
                🎬 **Settings:**
                - Duration: {duration} seconds ({duration * fps} frames @ {fps}fps)
                - Quality: {quality}
                - Model: {workflow['2']['inputs']['model_name']}
                - Steps: {workflow['4']['inputs']['steps']}
                
                ⏱️ **ETA:** {9 if 'Fast' in quality else 12 if 'Balanced' in quality else 20} minutes
                
                📍 **Output:** Check ComfyUI at `:8188` or wait here
                """)
                
                # Store job
                if 'video_jobs' not in st.session_state:
                    st.session_state.video_jobs = []
                
                st.session_state.video_jobs.append({
                    'id': prompt_id,
                    'time': time.time(),
                    'params': {'duration': duration, 'quality': quality, 'fps': fps}
                })
                
                # Monitor option
                with st.expander("🔴 Monitor Progress (Advanced)"):
                    st.code(f"tail -f /var/log/samantha/comfyui.log | grep {prompt_id[:8]}")
                    st.info("Auto-refresh not implemented in v1.0. Check ComfyUI directly.")
            else:
                status.error(f"❌ ComfyUI error: {response.status_code}")
                st.code(response.text[:500])
                
        except Exception as e:
            status.error(f"❌ Failed: {str(e)}")
            st.error("Check that ComfyUI is running: `samantha status`")
