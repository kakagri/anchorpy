#!/bin/bash

# AnchorPy Installation Script (Decoupled Version)
# This script installs anchorpy and anchorpy-core from separate GitHub repositories

set -e

echo "======================================"
echo "AnchorPy GitHub Installation Script"
echo "======================================"
echo ""
echo "This will install:"
echo "1. anchorpy-core (Rust extension) from GitHub"
echo "2. anchorpy (Python package) from GitHub"
echo ""

# Check if Rust is installed (required for building anchorpy-core from source)
if ! command -v cargo &> /dev/null; then
    echo "⚠️  Warning: Rust toolchain not found!"
    echo ""
    echo "anchorpy-core requires Rust to build from source."
    echo "Install Rust from: https://rustup.rs/"
    echo ""
    echo "Run this command:"
    echo "  curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh"
    echo ""
    echo "After installing Rust, restart your terminal and run this script again."
    exit 1
fi

echo "✓ Rust toolchain found: $(cargo --version)"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 not found!"
    echo "Please install Python 3.9 or later."
    exit 1
fi

echo "✓ Python found: $(python3 --version)"
echo ""

# Parse command line arguments
EDITABLE_MODE=false
ANCHORPY_CORE_REPO="https://github.com/kakagri/anchorpy-core.git"
ANCHORPY_REPO="."  # Default to current directory

while [[ "$#" -gt 0 ]]; do
    case $1 in
        -e|--editable) EDITABLE_MODE=true ;;
        --anchorpy-core-repo) ANCHORPY_CORE_REPO="$2"; shift ;;
        --anchorpy-repo) ANCHORPY_REPO="$2"; shift ;;
        -h|--help)
            echo "Usage: $0 [options]"
            echo ""
            echo "Options:"
            echo "  -e, --editable              Install anchorpy in editable mode"
            echo "  --anchorpy-core-repo URL    Custom anchorpy-core repository URL"
            echo "  --anchorpy-repo URL         Custom anchorpy repository URL or path"
            echo "  -h, --help                  Show this help message"
            exit 0
            ;;
        *) echo "Unknown option: $1"; exit 1 ;;
    esac
    shift
done

echo "Configuration:"
echo "  anchorpy-core repo: $ANCHORPY_CORE_REPO"
echo "  anchorpy repo: $ANCHORPY_REPO"
echo "  Editable mode: $EDITABLE_MODE"
echo ""

# Step 1: Install anchorpy-core from GitHub
echo "Step 1: Installing anchorpy-core from GitHub..."
echo "This will build the Rust extension (may take a few minutes)..."
pip install "git+${ANCHORPY_CORE_REPO}@main"

# Verify anchorpy-core installation
python3 -c "import anchorpy_core; print('✓ anchorpy-core installed successfully')" || {
    echo "❌ Failed to install anchorpy-core"
    exit 1
}

# Step 2: Install anchorpy
echo ""
echo "Step 2: Installing anchorpy..."

if [ "$ANCHORPY_REPO" == "." ]; then
    # Installing from current directory
    if [ ! -f "pyproject.toml" ]; then
        echo "Error: Not in anchorpy directory (pyproject.toml not found)"
        exit 1
    fi

    if [ "$EDITABLE_MODE" == true ]; then
        echo "Installing anchorpy in editable mode from current directory..."
        pip install -e .
    else
        echo "Installing anchorpy from current directory..."
        pip install .
    fi
else
    # Installing from GitHub URL
    if [ "$EDITABLE_MODE" == true ]; then
        echo "Note: Editable mode requires local repository. Cloning first..."
        TEMP_DIR=$(mktemp -d)
        git clone "$ANCHORPY_REPO" "$TEMP_DIR/anchorpy"
        cd "$TEMP_DIR/anchorpy"
        pip install -e .
        echo "Cloned to: $TEMP_DIR/anchorpy"
    else
        echo "Installing anchorpy from GitHub..."
        pip install "git+${ANCHORPY_REPO}@main"
    fi
fi

echo ""
echo "======================================"
echo "Installation Complete!"
echo "======================================"
echo ""

# Verify installation
echo "Verifying installation..."
python3 -c "
import anchorpy
import anchorpy_core
from anchorpy import Program, Provider
print('✓ anchorpy version:', getattr(anchorpy, '__version__', 'unknown'))
print('✓ anchorpy-core loaded successfully')
print('✓ All imports working correctly')
" || {
    echo "❌ Installation verification failed"
    exit 1
}

echo ""
echo "You can now use anchorpy in your Python scripts:"
echo "  from anchorpy import Program, Provider"
echo ""
echo "To test client generation:"
echo "  anchorpy client-gen <idl_file.json> <output_dir>"
echo ""