#!/bin/bash
# SAMANTHA AI - TERMUX QUICK INSTALLER
# This script downloads and sets up everything automatically

set -e

REPO="https://github.com/gokai55666-dev/freedom-ai"
INSTALL_DIR="$HOME/samantha"
VENV_DIR="$INSTALL_DIR/venv"

echo "🧠 SAMANTHA AI - Termux Installer"
echo "=================================="

# Check if running in Termux
if [ -z "$TERMUX_VERSION" ] && [ ! -d "/data/data/com.termux" ]; then
    echo "⚠️  Warning: Not in Termux environment"
fi

# Install dependencies
echo "[*] Installing packages..."
pkg update -y
pkg install -y python git wget curl

# Create directory
echo "[*] Creating directories..."
mkdir -p "$INSTALL_DIR"
cd "$INSTALL_DIR"

# Download repository
echo "[*] Downloading Samantha AI..."
if command -v git &> /dev/null; then
    git clone --depth 1 "$REPO.git" . 2>/dev/null || {
        echo "[*] Git clone failed, downloading files individually..."
        # Download main files
        curl -fsSL "$REPO/raw/main/samantha/main.py" -o samantha_main.py
        curl -fsSL "$REPO/raw/main/requirements.txt" -o requirements.txt 2>/dev/null || touch requirements.txt
    }
else
    echo "[*] Git not available, using curl..."
    mkdir -p samantha modes core utils
    curl -fsSL "$REPO/raw/main/samantha/main.py" -o samantha/main.py
fi

# Create virtual environment
echo "[*] Setting up Python environment..."
python -m venv "$VENV_DIR"
source "$VENV_DIR/bin/activate"

# Install requirements
pip install --upgrade pip
pip install streamlit requests pillow 2>/dev/null || pip install streamlit requests pillow

# Create launcher
echo "[*] Creating launcher..."
cat > "$PREFIX/bin/samantha" << 'EOF'
#!/bin/bash
cd $HOME/samantha
source venv/bin/activate
exec streamlit run samantha/main.py --server.address 0.0.0.0 --server.port 8501 "$@"
EOF
chmod +x "$PREFIX/bin/samantha"

echo ""
echo "✅ Installation complete!"
echo ""
echo "🚀 START: samantha"
echo "🌐 Access: http://localhost:8501"
echo ""
