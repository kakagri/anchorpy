# AnchorPy - GitHub Installation Guide (Decoupled Version)

This repository contains AnchorPy with support for both old and new Anchor IDL formats. It depends on anchorpy-core (Rust extension) which is maintained as a separate repository.

## 🚀 Features

- ✅ Full support for new Anchor IDL format (v0.1.0 spec)
- ✅ 100% backward compatibility with old IDL format
- ✅ Clean separation between Python package and Rust extension
- ✅ Easy installation from GitHub

## 📋 Prerequisites

### Required for GitHub Installation

1. **Python 3.9 or later**
2. **Rust toolchain** (required for building anchorpy-core from source)
   ```bash
   # Install Rust if you don't have it
   curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
   source $HOME/.cargo/env
   ```

### Optional (if using PyPI)

If anchorpy-core is published to PyPI, you only need Python (no Rust required).

## 📦 Installation Methods

### Method 1: Automatic Installation Script (Recommended)

```bash
# Clone the repository
git clone https://github.com/yourusername/anchorpy.git
cd anchorpy

# Run the installation script
./install_from_github.sh

# Or for editable/development mode
./install_from_github.sh --editable
```

### Method 2: Two-Step Manual Installation

```bash
# Step 1: Install anchorpy-core (builds from source, requires Rust)
pip install git+https://github.com/kevinheavey/anchorpy-core.git@main

# Step 2: Install anchorpy
pip install git+https://github.com/yourusername/anchorpy.git@main
```

### Method 3: Development Setup

```bash
# Clone both repositories
git clone https://github.com/kevinheavey/anchorpy-core.git
git clone https://github.com/yourusername/anchorpy.git

# Install anchorpy-core (builds Rust extension)
cd anchorpy-core
pip install .

# Install anchorpy in editable mode
cd ../anchorpy
pip install -e .
```

### Method 4: Mixed Installation (PyPI + GitHub)

If anchorpy-core is published to PyPI with pre-built wheels:

```bash
# Get pre-built anchorpy-core from PyPI (no Rust needed!)
pip install anchorpy-core

# Get latest anchorpy from GitHub
pip install git+https://github.com/yourusername/anchorpy.git@main
```

## 🔧 Installation Script Options

The `install_from_github.sh` script supports several options:

```bash
# Install in editable mode
./install_from_github.sh --editable

# Use custom anchorpy-core repository
./install_from_github.sh --anchorpy-core-repo https://github.com/yourfork/anchorpy-core.git

# Install from specific anchorpy repository
./install_from_github.sh --anchorpy-repo https://github.com/yourfork/anchorpy.git

# Show help
./install_from_github.sh --help
```

## ✅ Verify Installation

After installation, verify everything is working:

```python
# Test basic imports
python -c "from anchorpy import Program, Provider; print('✓ anchorpy imported')"
python -c "import anchorpy_core; print('✓ anchorpy-core loaded')"
python -c "from anchorpy_core.idl import Idl; print('✓ IDL parser ready')"

# Test CLI tool
anchorpy --help

# Test client generation
anchorpy client-gen loopscale_v2.json generated_client/
```

## 🧪 Running Tests

```bash
# Run the comprehensive IDL format test suite
pytest tests/test_idl_format_suite.py -v

# Run all IDL format tests
pytest tests/idl_format_test_*.py -v
```

## 📝 IDL Format Support

### Old Format (Legacy)
- Test with: `kamino_lend_v4.json`, `adrena.json`
- Field names: `isMut`, `isSigner`
- Discriminators calculated at runtime

### New Format (v0.1.0 spec)
- Test with: `loopscale_v1.json`, `loopscale_v2.json`
- Field names: `writable`, `signer`
- Precomputed discriminators
- Separated type definitions
- Support for Rust-style type paths

## 🛠️ Troubleshooting

### "Rust toolchain not found" Error

Install Rust first:
```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source $HOME/.cargo/env
```

### "cargo not found" After Installing Rust

Restart your terminal or run:
```bash
source $HOME/.cargo/env
```

### Build Errors with anchorpy-core

Ensure you have the latest Rust toolchain:
```bash
rustup update
```

### ImportError: No module named 'anchorpy_core'

anchorpy-core needs to be installed first:
```bash
pip install git+https://github.com/kevinheavey/anchorpy-core.git@main
```

### "error: Microsoft Visual C++ 14.0 is required" (Windows)

Install Visual Studio Build Tools:
- Download from: https://visualstudio.microsoft.com/downloads/
- Install "Desktop development with C++"

## 🔄 Updating

To update to the latest versions:

```bash
# Update anchorpy-core
pip install --upgrade --force-reinstall git+https://github.com/kevinheavey/anchorpy-core.git@main

# Update anchorpy
pip install --upgrade --force-reinstall git+https://github.com/yourusername/anchorpy.git@main
```

## 📚 Documentation

- [Original AnchorPy Documentation](https://kevinheavey.github.io/anchorpy/)
- [Anchor Framework Documentation](https://www.anchor-lang.com/)
- See test files for usage examples with new IDL format

## 🤝 Contributing

This fork adds new IDL format support to AnchorPy. Contributions are welcome!

1. Fork this repository
2. Create a feature branch
3. Make your changes
4. Run tests: `pytest tests/`
5. Submit a pull request

## 📄 License

This project maintains the same license as the original AnchorPy project.

## 🔗 Related Projects

- [anchorpy-core](https://github.com/kevinheavey/anchorpy-core) - Rust extension for IDL parsing
- [Original AnchorPy](https://github.com/kevinheavey/anchorpy) - The original project
- [Anchor](https://github.com/coral-xyz/anchor) - Solana's Sealevel Framework