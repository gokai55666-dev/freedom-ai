"""LoRA training mode - One-click automation"""

import streamlit as st
import os
import subprocess
import time
import re
from pathlib import Path

def render(config):
    """Render LoRA training interface"""
    st.header("👤 LoRA Training Factory")
    
    st.markdown("""
    **One-click character/style training**
    
    1. Prepare dataset (30-50 images)
    2. Configure parameters
    3. Click train - fully automated
    """)
    
    # Dataset section
    st.subheader("📁 Step 1: Dataset")
    
    dataset_path = st.text_input("Dataset folder path", "/root/datasets/mystyle")
    char_name = st.text_input("Character/Style name", "mystyle")
    trigger_word = st.text_input("Trigger word", "mystyle person")
    
    # Analyze dataset
    if st.button("📊 ANALYZE DATASET", use_container_width=True):
        if not os.path.exists(dataset_path):
            st.info(f"Creating folder: {dataset_path}")
            os.makedirs(dataset_path, exist_ok=True)
        
        files = [f for f in os.listdir(dataset_path) 
                if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))]
        
        if len(files) == 0:
            st.warning(f"⚠️ No images found in {dataset_path}")
            st.info("Add 30-50 images and click analyze again")
        else:
            st.success(f"✅ Found {len(files)} images")
            
            # Show samples
            cols = st.columns(min(4, len(files)))
            for col, file in zip(cols, files[:4]):
                with col:
                    try:
                        img_path = os.path.join(dataset_path, file)
                        st.image(img_path, caption=file[:15], use_column_width=True)
                    except:
                        st.text(file[:15])
            
            # Auto-rename option
            if st.checkbox("Auto-rename with trigger word", value=True):
                renamed = 0
                for i, old_file in enumerate(files):
                    old_path = os.path.join(dataset_path, old_file)
                    ext = Path(old_file).suffix
                    new_name = f"{trigger_word.replace(' ', '_')}_{i+1:03d}{ext}"
                    new_path = os.path.join(dataset_path, new_name)
                    
                    if old_path != new_path and not os.path.exists(new_path):
                        os.rename(old_path, new_path)
                        renamed += 1
                
                if renamed > 0:
                    st.success(f"Renamed {renamed} files")
            
            # Create captions
            if st.checkbox("Create caption files", value=True):
                created = 0
                for file in os.listdir(dataset_path):
                    if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                        caption_file = os.path.join(dataset_path, Path(file).stem + '.txt')
                        if not os.path.exists(caption_file):
                            with open(caption_file, 'w') as f:
                                f.write(f"{trigger_word}, detailed, high quality, masterpiece")
                            created += 1
                
                if created > 0:
                    st.success(f"Created {created} caption files")
    
    # Training configuration
    st.subheader("⚙️ Step 2: Configuration")
    
    col1, col2 = st.columns(2)
    with col1:
        network_rank = st.slider("Network Rank (Dim)", 8, 128, 32, 
                                help="Capacity vs overfitting")
        network_alpha = st.slider("Alpha", 4, 64, 16,
                                 help="Usually half of rank")
    with col2:
        epochs = st.slider("Epochs", 10, 50, 15,
                          help="Training iterations")
        resolution = st.selectbox("Resolution", [512, 768, 1024], index=2,
                                 help="Higher = better quality, more VRAM")
    
    batch_size = st.slider("Batch Size", 1, 4, 2,
                        help="Higher = faster, needs more VRAM")
    
    learning_rate = st.selectbox("Learning Rate", 
                                ["1e-4 (Fast)", "5e-5 (Balanced)", "1e-5 (Precise)"],
                                index=1)
    
    # Training execution
    st.subheader("🚀 Step 3: Train")
    
    if st.button("▶️ START TRAINING", type="primary", use_container_width=True):
        # Validation
        if not os.path.exists(dataset_path):
            st.error("Dataset folder doesn't exist!")
            return
        
        files = [f for f in os.listdir(dataset_path) 
                if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        if len(files) < 10:
            st.error(f"Need at least 10 images, found {len(files)}")
            return
        
        # Build configuration
        lr_clean = learning_rate.split(" ")[0]
        output_dir = f"/root/ai_system/loras/{char_name}"
        os.makedirs(output_dir, exist_ok=True)
        
        # Build command
        cmd_parts = [
            "python3", "/root/kohya_ss/train_network.py",
            "--pretrained_model_name_or_path=/root/ai_system/sd/sd_xl_base_1.0.safetensors",
            f"--train_data_dir={dataset_path}",
            f"--output_dir={output_dir}",
            f"--output_name={char_name}_lora",
            "--network_module=networks.lora",
            f"--network_dim={network_rank}",
            f"--network_alpha={network_alpha}",
            f"--resolution={resolution}",
            f"--train_batch_size={batch_size}",
            f"--max_train_epochs={epochs}",
            f"--learning_rate={lr_clean}",
            "--optimizer_type=AdamW8bit",
            "--mixed_precision=fp16",
            "--save_every_n_epochs=2",
            f"--logging_dir={output_dir}/logs",
            "--log_with=tensorboard",
            "--clip_skip=2",
            "--xformers",
            "--cache_latents"
        ]
        
        cmd = " ".join(cmd_parts)
        
        # Display
        st.code(cmd, language='bash')
        
        # Execute
        with st.spinner("Launching training process..."):
            try:
                process = subprocess.Popen(
                    cmd,
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    cwd="/root/kohya_ss"
                )
                
                # Store job
                if 'lora_jobs' not in st.session_state:
                    st.session_state.lora_jobs = []
                
                st.session_state.lora_jobs.append({
                    'id': f"lora_{int(time.time())}",
                    'name': char_name,
                    'process': process,
                    'start_time': time.time(),
                    'output_dir': output_dir
                })
                
                st.success(f"🚀 Training started! PID: {process.pid}")
                st.info(f"Output: {output_dir}")
                
                # Quick status check
                time.sleep(2)
                if process.poll() is None:
                    st.success("Process is running normally")
                    st.info("Training will take 30-120 minutes depending on settings")
                else:
                    stdout, stderr = process.communicate()
                    if stderr:
                        st.error(stderr[:500])
                
            except Exception as e:
                st.error(f"Failed to start: {e}")
