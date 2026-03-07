"""Video generation mode - Wan 2.2 fully automated"""

import streamlit as st
import requests
import time
import os


def check_comfyui():
    """Check if ComfyUI is running"""
    try:
        response = requests.get(
            "http://localhost:8188/system_stats", 
            timeout=2
        )
        return response.status_code == 200
    except:
        return False


def build_workflow(image_path, prompt, duration, fps, quality):
    """Build ComfyUI workflow for video generation"""
    num_frames = duration * fps
    
    # Model settings: (filename, steps, (width, height))
    models = {
        "Fast": ("Wan2.2_TI2V_5B_fp16.safetensors", 20, (832, 480)),
        "Balanced": ("Wan2.2_TI2V_5B_fp16.safetensors", 30, (1280, 720)),
        "Quality": ("Wan2.2_I2V_A14B_fp16.safetensors", 40, (1280, 720))
    }
    
    model, steps, (width, height) = models.get(quality, models["Balanced"])
    
    # Build workflow dictionary with proper formatting
    workflow = {
        "1": {
            "inputs": {"image": image_path},
            "class_type": "LoadImage"
        },
        "2": {
            "inputs": {
                "model_name": model,
                "precision": "fp16"
            },
            "class_type": "WanVideoLoader"
        },
        "3": {
            "inputs": {
                "positive": prompt,
                "negative": "blur, low quality",
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
        "5": {
            "inputs": {
                "samples": ["4", 0],
                "vae": ["2", 1]
            },
            "class_type": "WanVideoDecode"
        },
        "6": {
            "inputs": {
                "filename_prefix": "SamanthaVideo",
                "fps": fps,
                "video": ["5", 0]
            },
            "class_type": "SaveVideo"
        }
    }
    
    return workflow


def render(config):
    """Render video generation interface"""
    st.header("Video Generation")
    
    # Check ComfyUI status
    if not check_comfyui():
        st.error("ComfyUI not running")
        if st.button("Start ComfyUI"):
            os.system("systemctl start samantha-comfyui")
            time.sleep(5)
            st.rerun()
        return
    
    # File upload
    uploaded = st.file_uploader(
        "Upload image", 
        type=['png', 'jpg', 'jpeg']
    )
    
    if not uploaded:
        st.info("Upload an image to animate")
        return
    
    # Save temp file
    temp_path = f"/tmp/samantha_video_{int(time.time())}.png"
    with open(temp_path, "wb") as f:
        f.write(uploaded.getbuffer())
    
    st.image(temp_path, use_column_width=True)
    
    # Controls
    motion = st.text_area(
        "Motion description", 
        "slow cinematic camera movement"
    )
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        duration = st.selectbox(
            "Duration", 
            [2, 5, 10], 
            format_func=lambda x: f"{x}s", 
            index=1
        )
    
    with col2:
        quality = st.selectbox(
            "Quality", 
            ["Fast", "Balanced", "Quality"], 
            index=1
        )
    
    with col3:
        fps = st.selectbox(
            "FPS", 
            [16, 24], 
            index=0
        )
    
    # Generate button
    if st.button(
        "GENERATE VIDEO", 
        type="primary", 
        use_container_width=True
    ):
        try:
            workflow = build_workflow(
                temp_path, 
                motion, 
                duration, 
                fps, 
                quality
            )
            
            response = requests.post(
                "http://localhost:8188/prompt", 
                json={"prompt": workflow}, 
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                prompt_id = result.get('prompt_id', 'unknown')
                st.success(f"Queued! ID: {prompt_id[:8]}")
                st.balloons()
                st.info(
                    f"ETA: {9 if quality == 'Fast' else 15} minutes"
                )
            else:
                st.error(f"Error: {response.status_code}")
                
        except Exception as e:
            st.error(f"Failed: {str(e)}")
