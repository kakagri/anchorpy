# AnchorPy3
<div align="center">
    <img src="https://raw.githubusercontent.com/kevinheavey/anchorpy/main/docs/img/logo.png" width="40%" height="40%">
</div>

---

[![PyPI](https://img.shields.io/pypi/v/anchorpy3.svg)](https://pypi.org/project/anchorpy3/)
[![Python Version](https://img.shields.io/pypi/pyversions/anchorpy3)](https://pypi.org/project/anchorpy3/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> **Note:** This is a fork of [kevinheavey/anchorpy](https://github.com/kevinheavey/anchorpy) with added support for new Anchor IDL formats (v0.1.0 spec). All credit for the original implementation goes to [kevinheavey](https://github.com/kevinheavey).

## What's New in AnchorPy3

- **Full support for new Anchor IDL format (v0.1.0 spec)** with precomputed discriminators
- **100% backward compatibility** with legacy IDL format
- **Automatic format detection** - works seamlessly with both old and new IDL files
- **Decoupled architecture** - anchorpy-core is now a separate package
- **Updated for Python 3.10+**

## Overview

AnchorPy is the gateway to interacting with [Anchor](https://github.com/project-serum/anchor) programs in Python.
It provides:

- A static client generator
- A dynamic client similar to `anchor-ts`
- A Pytest plugin
- A CLI with various utilities for Anchor Python development.

Read the [Documentation](https://kevinheavey.github.io/anchorpy/).



## Installation (requires Python >=3.10)

### Install from PyPI

```sh
pip install anchorpy3[cli,pytest]
```

Or, if you're not using the CLI or Pytest plugin features:

```sh
pip install anchorpy3
```

### Install from GitHub (Latest)

```sh
pip install git+https://github.com/kakagri/anchorpy.git
```

**Note:** Installing from GitHub requires the Rust toolchain (for building anchorpy-core). See [Rust installation](https://www.rust-lang.org/tools/install).

### Development Setup

If you want to contribute to AnchorPy, follow these steps to get set up:

1. Install [uv](https://docs.astral.sh/uv/getting-started/installation/)
2. Run the unit tests:
```sh
uv run --all-extras pytest tests/unit

```
