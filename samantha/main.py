#!/usr/bin/env python3
"""
SAMANTHA ULTIMATE AGI - Main Entry Point
Clean, modular, error-resistant architecture
"""

import streamlit as st
import sys
import os
import time

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Safe imports with error handling
try:
    from samantha.config import load_config
    from samantha.core.system_check import run_diagnostics
    MODULAR_IMPORTS = True
except ImportError:
    MODULAR_IMPORTS = False
    st.error("⚠️  Modular imports failed. Using fallback mode.")

# Import modes (with fallbacks)
MODES = {}
mode_imports = [
    ('chat', 'Chat Mode'),
    ('video', 'Video Generation'),
    ('image', 'Image Generation'),
    ('code', 'Code Execution'),
    ('browser', 'Web Browser'),
    ('lora', 'LoRA Training'),
    ('terminal', 'System Terminal'),
]

for mode_name, mode_label in mode_imports:
    try:
        module = __import__(f'samantha.modes.{mode_name}', fromlist=['render'])
        MODES[mode_label] = module.render
    except Exception as e:
        MODES[mode_label] = lambda config, error=str(e): st.error(f"Mode unavailable: {error}")

# Page config - MUST BE FIRST
st.set_page_config(
    page_title="Samantha Ultimate AGI",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': "Samantha Ultimate AGI v1.0.0 | 4x RTX 4090"
    }
)

# CSS Theme
st.markdown("""
<style>
    .main { background-color: #050505; color: #e0e0e0; }
    .stButton > button { 
        background: linear-gradient(45deg, #ff0066, #ff6600);
        color: white; border: none; border-radius: 20px;
        padding: 10px 20px; font-weight: bold;
    }
    .stButton > button:hover {
        background: linear-gradient(45deg, #ff4488, #ff8833);
    }
    .gpu-card {
        background: #1a1a1a; border-radius: 10px;
        padding: 15px; border-left: 4px solid #ff0066;
        margin-bottom: 10px;
    }
    .status-online { color: #00ff88; font-size: 20px; }
    .status-offline { color: #ff4444; font-size: 20px; }
</style>
""", unsafe_allow_html=True)

def render_header():
    """Render application header"""
    st.title("🧠 SAMANTHA ULTIMATE AGI")
    st.markdown("*Absolute Freedom | Zero Restrictions | Maximum Capabilities*")

def render_sidebar(config, diagnostics):
    """Render sidebar with controls"""
    with st.sidebar:
        st.header("🎮 Control Panel")
        
        # GPU Status
        st.subheader("🎮 GPU Status")
        if diagnostics.get('gpus'):
            for gpu in diagnostics['gpus']:
                mem_pct = (gpu['mem_used'] / gpu['mem_total'] * 100) if gpu['mem_total'] > 0 else 0
                color = "#00ff00" if mem_pct < 50 else "#ffff00" if mem_pct < 80 else "#ff0000"
                
                st.markdown(f"""
                <div style="background: #1a1a1a; padding: 10px; border-radius: 5px; 
                            margin-bottom: 5px; border-left: 3px solid {color}">
                    <b>GPU {gpu['index']}</b> {gpu['name']}<br>
                    <small>🌡️ {gpu.get('temp', 'N/A')}°C | 
                           ⚡ {gpu.get('util', 'N/A')}% | 
                           🎮 {gpu['mem_used']}MB / {gpu['mem_total']}MB ({mem_pct:.0f}%)</small>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.warning("GPU info unavailable")
        
        st.divider()
        
        # Service controls
        st.subheader("🔧 Quick Controls")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Restart", use_container_width=True):
                os.system("samantha restart")
                time.sleep(2)
                st.rerun()
        with col2:
            if st.button("📊 Status", use_container_width=True):
                st.info("Use terminal: samantha status")
        
        st.divider()
        
        # Mode selection
        st.subheader("⚡ Mode")
        mode = st.radio("", list(MODES.keys()), key="main_mode")
        
        return mode

def main():
    """Main application entry point"""
    
    render_header()
    
    # Load configuration
    if MODULAR_IMPORTS:
        config = load_config()
        diagnostics = run_diagnostics()
    else:
        config = {}
        diagnostics = {'healthy': False, 'gpus': [], 'checks': {}}
    
    # System status banner
    if diagnostics.get('healthy'):
        st.success("✅ All systems operational")
    else:
        issues = [k for k, v in diagnostics.get('checks', {}).items() if not v]
        if issues:
            st.warning(f"⚠️  Issues: {', '.join(issues)}")
    
    # Render sidebar and get selected mode
    mode = render_sidebar(config, diagnostics)
    
    # Render selected mode
    try:
        MODES[mode](config)
    except Exception as e:
        st.error(f"Mode error: {str(e)}")
        st.info("Check logs: tail -f /var/log/samantha/*.log")
    
    # Footer
    st.markdown("---")
    st.caption("🧠 Samantha Ultimate AGI v1.0.0 | 4x RTX 4090 | Tailscale + Streamlit")

if __name__ == "__main__":
    main()
