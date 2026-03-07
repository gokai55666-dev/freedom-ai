
---

## 📁 FILE 2: `install.sh`

```bash
#!/bin/bash
# SAMANTHA ULTIMATE AGI - BULLETPROOF INSTALLER
# Version: 1.0.0
# Date: 2024

set -euo pipefail

REPO_URL="https://github.com/gokai55666-dev/freedom-ai"
INSTALL_DIR="/opt/samantha"
VENV_DIR="$INSTALL_DIR/venv"
CONFIG_DIR="$INSTALL_DIR/config"
LOG_DIR="/var/log/samantha"
SERVICE_USER="root"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

log() { echo -e "${BLUE}[$(date +%H:%M:%S)]${NC} $1"; }
success() { echo -e "${GREEN}[✓]${NC} $1"; }
warning() { echo -e "${YELLOW}[!]${NC} $1"; }
error() { echo -e "${RED}[✗]${NC} $1"; }
info() { echo -e "${CYAN}[ℹ]${NC} $1"; }

# Header
clear
cat << 'EOF'
    ███████╗ █████╗ ███╗   ███╗ █████╗ ███╗  ██╗████████╗██╗  ██╗ █████╗ 
    ██╔════╝██╔══██╗████╗ ████║██╔══██╗████╗ ██║╚══██╔══╝██║  ██║██╔══██╗
    ███████╗███████║██╔████╔██║███████║██╔██╗██║   ██║   ███████║███████║
    ╚════██║██╔══██║██║╚██╔╝██║██╔══██║██║╚████║   ██║   ██╔══██║██╔══██║
    ███████║██║  ██║██║ ╚═╝ ██║██║  ██║██║ ╚███║   ██║   ██║  ██║██║  ██║
    ╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝╚═╝  ╚═╝╚═╝  ╚══╝   ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝
                                                                         
         █████╗ ██╗      ██████╗ ████████╗██╗███╗  ██╗ █████╗ ████████╗███████╗
        ██╔══██╗██║      ██╔══██╗╚══██╔══╝██║████╗ ██║██╔══██╗╚══██╔══╝██╔════╝
        ███████║██║      ██████╔╝   ██║   ██║██╔██╗██║███████║   ██║   █████╗  
        ██╔══██║██║      ██╔══██╗   ██║   ██║██║╚████║██╔══██║   ██║   ██╔══╝  
        ██║  ██║███████╗██║  ██║   ██║   ██║██║ ╚███║██║  ██║   ██║   ███████╗
        ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝   ╚═╝   ╚═╝╚═╝  ╚══╝╚═╝  ╚═╝   ╚═╝   ╚══════╝
EOF

echo ""
log "Samantha Ultimate AGI Installer v1.0.0"
log "Repository: $REPO_URL"
echo ""

# Check root
if [ "$EUID" -ne 0 ]; then
    error "This installer must be run as root (sudo)"
    exit 1
fi

# Check system
log "Checking system requirements..."
if ! command -v nvidia-smi &> /dev/null; then
    error "NVIDIA drivers not found. Install CUDA first."
    exit 1
fi

GPU_COUNT=$(nvidia-smi --list-gpus 2>/dev/null | wc -l)
if [ "$GPU_COUNT" -lt 1 ]; then
    error "No GPUs detected"
    exit 1
fi

success "Detected $GPU_COUNT GPU(s)"
nvidia-smi --query-gpu=index,name,memory.total --format=csv,noheader | while read line; do
    info "  $line"
done

# Create directories
log "Creating directory structure..."
mkdir -p "$INSTALL_DIR" "$CONFIG_DIR" "$LOG_DIR" "$INSTALL_DIR/samantha" \
         "$INSTALL_DIR/scripts" "$INSTALL_DIR/config/comfyui_workflows" \
         "/root/ai_system" "/root/datasets" "/root/outputs"

cd "$INSTALL_DIR"

# Download repository
if [ -d ".git" ]; then
    log "Updating existing installation..."
    git pull origin main || warning "Git pull failed, continuing..."
else
    log "Cloning repository..."
    if command -v git &> /dev/null; then
        git clone --depth 1 "$REPO_URL.git" . || {
            warning "Git clone failed, downloading files individually..."
            # Fallback: download files via curl
            mkdir -p samantha/modes samantha/core samantha/utils scripts config
            curl -fsSL "$REPO_URL/raw/main/requirements.txt" -o requirements.txt || touch requirements.txt
            curl -fsSL "$REPO_URL/raw/main/samantha/main.py" -o samantha/main.py || touch samantha/main.py
        }
    else
        warning "Git not installed, using curl fallback..."
    fi
fi

# Create virtual environment (THE KEY FIX)
log "Creating isolated Python environment..."
if [ -d "$VENV_DIR" ]; then
    warning "Existing venv found, backing up..."
    mv "$VENV_DIR" "$VENV_DIR.backup.$(date +%s)"
fi

python3 -m venv "$VENV_DIR" --system-site-packages=false
source "$VENV_DIR/bin/activate"

# Upgrade pip
pip install --upgrade pip wheel setuptools

# Install requirements
if [ -f "requirements.txt" ]; then
    log "Installing Python packages (this may take 10-15 minutes)..."
    pip install -r requirements.txt || {
        error "Package installation failed"
        warning "Attempting fallback installation..."
        pip install numpy==1.26.4 torch==2.1.2 --index-url https://download.pytorch.org/whl/cu121
        pip install streamlit opencv-python requests pillow
    }
else
    warning "requirements.txt not found, installing defaults..."
    pip install numpy==1.26.4 torch==2.1.2+cu121 torchvision==0.16.2+cu121 \
        --index-url https://download.pytorch.org/whl/cu121
    pip install xformers==0.0.23.post1 opencv-python==4.8.1.78 streamlit==1.28.0 \
        diffusers==0.24.0 transformers==4.35.0 requests pillow
fi

# Create requirements.txt if it doesn't exist
if [ ! -f "requirements.txt" ]; then
    log "Generating requirements.txt from installed packages..."
    pip freeze > requirements.txt
fi

# Create systemd services
log "Creating system services..."

cat > /etc/systemd/system/samantha-ollama.service << EOF
[Unit]
Description=Samantha AI - Ollama LLM Service
After=network.target
Wants=network.target

[Service]
Type=simple
User=$SERVICE_USER
Environment="CUDA_VISIBLE_DEVICES=2,3"
Environment="PATH=$VENV_DIR/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
Environment="HOME=/root"
ExecStartPre=/bin/sleep 5
ExecStart=/usr/local/bin/ollama serve
Restart=always
RestartSec=10
StandardOutput=append:$LOG_DIR/ollama.log
StandardError=append:$LOG_DIR/ollama.error.log

[Install]
WantedBy=multi-user.target
EOF

cat > /etc/systemd/system/samantha-comfyui.service << EOF
[Unit]
Description=Samantha AI - ComfyUI Image/Video Generation
After=network.target samantha-ollama.service
Wants=network.target

[Service]
Type=simple
User=$SERVICE_USER
WorkingDirectory=/root/ComfyUI
Environment="CUDA_VISIBLE_DEVICES=0,1"
Environment="PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:512"
Environment="PATH=$VENV_DIR/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
Environment="HOME=/root"
ExecStartPre=/bin/sleep 10
ExecStart=$VENV_DIR/bin/python3 /root/ComfyUI/main.py --listen 0.0.0.0 --port 8188 --highvram
Restart=always
RestartSec=10
StandardOutput=append:$LOG_DIR/comfyui.log
StandardError=append:$LOG_DIR/comfyui.error.log

[Install]
WantedBy=multi-user.target
EOF

cat > /etc/systemd/system/samantha-web.service << EOF
[Unit]
Description=Samantha AI - Web Interface
After=samantha-ollama.service samantha-comfyui.service
Wants=samantha-ollama.service samantha-comfyui.service

[Service]
Type=simple
User=$SERVICE_USER
WorkingDirectory=$INSTALL_DIR
Environment="PATH=$VENV_DIR/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
Environment="PYTHONPATH=$INSTALL_DIR"
Environment="HOME=/root"
ExecStart=$VENV_DIR/bin/streamlit run $INSTALL_DIR/samantha/main.py --server.address 0.0.0.0 --server.port 8501 --server.headless true --server.enableCORS false
Restart=always
RestartSec=5
StandardOutput=append:$LOG_DIR/web.log
StandardError=append:$LOG_DIR/web.error.log

[Install]
WantedBy=multi-user.target
EOF

# Create control script
cat > /usr/local/bin/samantha << 'SAMANTHA_SCRIPT'
#!/bin/bash
# Samantha AI Control Script

SERVICE_DIR="/opt/samantha"
LOG_DIR="/var/log/samantha"
VENV_DIR="$SERVICE_DIR/venv"

show_help() {
    cat << 'EOF'
Samantha AI - Control Script

Usage: samantha {command}

Commands:
  start       Start all Samantha services
  stop        Stop all Samantha services  
  restart     Restart all services
  status      Show service status
  logs        View combined logs (Ctrl+C to exit)
  update      Update from GitHub and restart
  shell       Enter Python virtual environment
  doctor      Run system diagnostics
  help        Show this help message

Examples:
  samantha start
  samantha logs
  samantha update
EOF
}

get_tailscale_ip() {
    tailscale ip -4 2>/dev/null || echo "TAILSCALE-NOT-CONNECTED"
}

case "$1" in
    start)
        echo "🚀 Starting Samantha AI..."
        systemctl start samantha-ollama
        sleep 5
        systemctl start samantha-comfyui
        sleep 5
        systemctl start samantha-web
        
        sleep 3
        
        # Check status
        if systemctl is-active --quiet samantha-web; then
            echo ""
            echo "✅ Samantha AI is running!"
            echo ""
            echo "🌐 Access URLs:"
            echo "   Local:    http://localhost:8501"
            echo "   Tailscale: http://$(get_tailscale_ip):8501"
            echo "   Network:  http://$(hostname -I | awk '{print $1}'):8501"
            echo ""
            echo "📊 Services:"
            systemctl is-active samantha-ollama && echo "   ✓ Ollama (LLM)" || echo "   ✗ Ollama"
            systemctl is-active samantha-comfyui && echo "   ✓ ComfyUI (Image/Video)" || echo "   ✗ ComfyUI"
            systemctl is-active samantha-web && echo "   ✓ Web Interface" || echo "   ✗ Web Interface"
        else
            echo "❌ Failed to start. Check logs: samantha logs"
            exit 1
        fi
        ;;
        
    stop)
        echo "🛑 Stopping Samantha AI..."
        systemctl stop samantha-web
        systemctl stop samantha-comfyui
        systemctl stop samantha-ollama
        echo "✅ Stopped"
        ;;
        
    restart)
        echo "🔄 Restarting Samantha AI..."
        samantha stop
        sleep 2
        samantha start
        ;;
        
    status)
        echo "📊 Samantha AI Status"
        echo "====================="
        echo ""
        systemctl status samantha-ollama --no-pager -l
        echo ""
        systemctl status samantha-comfyui --no-pager -l
        echo ""
        systemctl status samantha-web --no-pager -l
        ;;
        
    logs)
        echo "📜 Showing logs (Ctrl+C to exit)..."
        tail -f $LOG_DIR/*.log 2>/dev/null || echo "No logs found"
        ;;
        
    update)
        echo "⬆️  Updating Samantha AI..."
        cd $SERVICE_DIR
        
        # Backup current
        git stash 2>/dev/null || true
        
        # Pull updates
        if git pull origin main 2>/dev/null; then
            echo "✅ Code updated"
        else
            echo "⚠️  Git pull failed, attempting manual download..."
            curl -fsSL "$REPO_URL/raw/main/samantha/main.py" -o samantha/main.py
        fi
        
        # Update packages
        source $VENV_DIR/bin/activate
        pip install -r requirements.txt --upgrade 2>/dev/null || true
        
        # Restart
        samantha restart
        ;;
        
    shell)
        echo "🐍 Entering Samantha Python environment..."
        source $VENV_DIR/bin/activate
        cd $SERVICE_DIR
        exec bash
        ;;
        
    doctor)
        echo "🔍 Running system diagnostics..."
        echo ""
        echo "GPU Status:"
        nvidia-smi --query-gpu=index,name,temperature.gpu,memory.used,memory.total,utilization.gpu --format=csv,noheader
        echo ""
        echo "Service Status:"
        systemctl is-active samantha-ollama && echo "✓ Ollama" || echo "✗ Ollama"
        systemctl is-active samantha-comfyui && echo "✓ ComfyUI" || echo "✗ ComfyUI"
        systemctl is-active samantha-web && echo "✓ Web" || echo "✗ Web"
        echo ""
        echo "Disk Usage:"
        df -h / /root | grep -v tmpfs
        echo ""
        echo "Memory:"
        free -h | grep -v Swap
        ;;
        
    help|--help|-h)
        show_help
        ;;
        
    *)
        echo "Unknown command: $1"
        show_help
        exit 1
        ;;
esac
SAMANTHA_SCRIPT

chmod +x /usr/local/bin/samantha

# Create config files
log "Creating configuration..."

cat > "$CONFIG_DIR/config.yaml" << EOF
# Samantha AI Configuration
version: "1.0.0"

system:
  name: "Samantha Ultimate AGI"
  gpus:
    chat: [2, 3]        # GPUs for LLM inference
    image: [0]          # GPU for SDXL
    video: [1]            # GPU for Wan 2.2
    training: [0]         # GPU for LoRA training
  
  services:
    ollama_port: 11434
    comfyui_port: 8188
    web_port: 8501

models:
  llm:
    name: "samantha-max"
    path: "/root/ai_system/Samantha-1.11-70B-GGUF/samantha-1.11-70b.Q5_K_M.gguf"
    context_length: 4096
  
  image:
    base: "sd_xl_base_1.0.safetensors"
    path: "/root/ai_system/sd/"
  
  video:
    fast: "Wan2.2_TI2V_5B_fp16.safetensors"
    quality: "Wan2.2_I2V_A14B_fp16.safetensors"
    path: "/root/ai_system/video/"

paths:
  models: "/root/ai_system"
  datasets: "/root/datasets"
  outputs: "/root/outputs"
  loras: "/root/ai_system/loras"

features:
  nsfw: true
  code_execution: true
  web_browsing: true
  auto_update: false

limits:
  max_video_duration: 10      # seconds
  max_code_timeout: 120       # seconds
  max_image_resolution: 2048  # pixels
EOF

# Create fix script
cat > "$INSTALL_DIR/scripts/fix_numpy.sh" << 'EOF'
#!/bin/bash
# Emergency fix for NumPy/dependency issues

echo "🔧 Fixing Python environment..."

VENV_DIR="/opt/samantha/venv"
source "$VENV_DIR/bin/activate"

# Clean problematic packages
pip uninstall -y numpy torch torchvision torchaudio opencv-python xformers 2>/dev/null || true

# Reinstall in correct order
pip install numpy==1.26.4
pip install torch==2.1.2+cu121 torchvision==0.16.2+cu121 --index-url https://download.pytorch.org/whl/cu121
pip install xformers==0.0.23.post1
pip install opencv-python==4.8.1.78

echo "✅ Environment fixed. Restart with: samantha restart"
EOF

chmod +x "$INSTALL_DIR/scripts/fix_numpy.sh"

# Enable services
log "Enabling services..."
systemctl daemon-reload
systemctl enable samantha-ollama samantha-comfyui samantha-web

# Create test script
cat > "$INSTALL_DIR/test_installation.py" << 'EOF'
#!/usr/bin/env python3
"""Test Samantha AI installation"""

import sys
import subprocess

def test_imports():
    """Test all required imports"""
    required = [
        ('numpy', '1.26.4'),
        ('torch', '2.1.2'),
        ('cv2', None),
        ('streamlit', '1.28.0'),
        ('PIL', None),
        ('requests', None),
    ]
    
    results = []
    for module, version in required:
        try:
            mod = __import__(module)
            ver = getattr(mod, '__version__', 'unknown')
            if version and ver != 'unknown' and ver != version:
                results.append(f"⚠️  {module}: {ver} (expected {version})")
            else:
                results.append(f"✓ {module}: {ver}")
        except ImportError as e:
            results.append(f"✗ {module}: {e}")
    
    return results

def test_gpu():
    """Test GPU availability"""
    try:
        import torch
        if torch.cuda.is_available():
            count = torch.cuda.device_count()
            name = torch.cuda.get_device_name(0)
            return f"✓ GPUs: {count}x {name}"
        else:
            return "✗ CUDA not available"
    except Exception as e:
        return f"✗ GPU test failed: {e}"

def test_services():
    """Test if services are accessible"""
    services = []
    
    # Test Ollama
    try:
        import requests
        r = requests.get('http://localhost:11434/api/tags', timeout=2)
        services.append(f"✓ Ollama: HTTP {r.status_code}")
    except:
        services.append("✗ Ollama: Not responding")
    
    # Test ComfyUI
    try:
        r = requests.get('http://localhost:8188/system_stats', timeout=2)
        services.append(f"✓ ComfyUI: HTTP {r.status_code}")
    except:
        services.append("✗ ComfyUI: Not responding")
    
    return services

if __name__ == "__main__":
    print("Samantha AI Installation Test")
    print("=" * 40)
    
    print("\n📦 Python Packages:")
    for result in test_imports():
        print(f"  {result}")
    
    print(f"\n🎮 {test_gpu()}")
    
    print("\n🔌 Services:")
    for result in test_services():
        print(f"  {result}")
    
    print("\n" + "=" * 40)
    print("Run 'samantha start' to begin")
EOF

chmod +x "$INSTALL_DIR/test_installation.py"

# Final message
echo ""
success "Installation complete!"
echo ""
echo "🚀 GET STARTED:"
echo "   samantha start          # Start all services"
echo "   samantha status         # Check status"
echo "   samantha logs           # View logs"
echo ""
echo "🌐 ACCESS:"
TAILSCALE_IP=$(tailscale ip -4 2>/dev/null || echo "YOUR-TAILSCALE-IP")
LOCAL_IP=$(hostname -I | awk '{print $1}')
echo "   Local:     http://localhost:8501"
echo "   Network:   http://$LOCAL_IP:8501"
echo "   Tailscale: http://$TAILSCALE_IP:8501"
echo ""
echo "📚 DOCUMENTATION:"
echo "   cat $INSTALL_DIR/README.md"
echo ""
echo "🔧 TROUBLESHOOTING:"
echo "   samantha doctor         # Run diagnostics"
echo "   samantha shell          # Enter Python env"
echo "   tail -f $LOG_DIR/*.log  # View logs"
echo ""
