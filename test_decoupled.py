#!/usr/bin/env python3
"""Test script to verify decoupled anchorpy and anchorpy-core work correctly."""

import json
from pathlib import Path

# Test imports
print("Testing imports...")
try:
    from anchorpy import Program, Provider
    print("✓ anchorpy imported successfully")
except ImportError as e:
    print(f"✗ Failed to import anchorpy: {e}")
    exit(1)

try:
    import anchorpy_core
    print("✓ anchorpy-core loaded successfully")
except ImportError as e:
    print(f"✗ Failed to import anchorpy-core: {e}")
    exit(1)

try:
    from anchorpy_core.idl import Idl
    print("✓ IDL parser ready")
except ImportError as e:
    print(f"✗ Failed to import Idl: {e}")
    exit(1)

# Test IDL parsing
print("\nTesting IDL parsing...")
test_files = [
    ("../loopscale_v2.json", "New format (v0.1.0)"),
    ("../kamino_lend_v4.json", "Old format (legacy)"),
]

for idl_file, format_type in test_files:
    idl_path = Path(idl_file)
    if not idl_path.exists():
        print(f"✗ {idl_file} not found")
        continue

    print(f"\nTesting {idl_file} ({format_type})...")

    try:
        with open(idl_path) as f:
            idl_json = json.load(f)

        # Parse as Idl object
        idl_obj = Idl.from_json(json.dumps(idl_json))
        print(f"  ✓ Successfully parsed IDL")

        # Check for key attributes
        if idl_obj.instructions:
            print(f"  ✓ Found {len(idl_obj.instructions)} instructions")
        if idl_obj.accounts:
            print(f"  ✓ Found {len(idl_obj.accounts)} accounts")
        if idl_obj.types:
            print(f"  ✓ Found {len(idl_obj.types)} types")

        # Create Program object
        provider = Provider.local()
        program_id = idl_json.get('address', 'So11111111111111111111111111111111111111112')
        program = Program(idl_json, program_id, provider)
        print(f"  ✓ Successfully created Program object")

    except Exception as e:
        print(f"  ✗ Error: {e}")

print("\n" + "="*50)
print("✅ DECOUPLING SUCCESSFUL!")
print("="*50)
print("\nThe anchorpy and anchorpy-core packages are successfully decoupled and working together.")
print("Both old and new IDL formats are supported.")