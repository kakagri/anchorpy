#!/usr/bin/env python3
"""Test client generation for both old and new IDL formats."""

import json
import tempfile
from pathlib import Path
from anchorpy import Program, Provider
from anchorpy_core.idl import Idl
from anchorpy.clientgen import generate
import sys

def test_clientgen(idl_name: str):
    """Test client generation for a specific IDL."""
    print(f"\n{'='*60}")
    print(f"Testing client generation for {idl_name}")
    print(f"{'='*60}")

    # Load the IDL
    idl_path = Path(__file__).parent.parent / idl_name
    print(f"Loading IDL from: {idl_path}")

    with open(idl_path) as f:
        idl_json = json.load(f)

    # Parse as Idl object
    idl = Idl.from_json(json.dumps(idl_json))

    # Create a temporary directory for generated code
    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = Path(tmpdir) / "generated"
        output_path.mkdir()

        print(f"Generating client code to: {output_path}")

        try:
            # Generate the client code
            generate(
                idl=idl,
                root=output_path,
                program_id=idl_json.get('address', 'So11111111111111111111111111111111111111112')
            )
            print(f"✅ Successfully generated client code for {idl_name}")

            # List generated files
            print("\nGenerated files:")
            for file in sorted(output_path.rglob("*.py")):
                rel_path = file.relative_to(output_path)
                print(f"  - {rel_path}")

            # Try to import the generated module (basic validation)
            if (output_path / "__init__.py").exists():
                print("\n✅ Generated __init__.py exists")

            # Check if accounts were generated
            accounts_dir = output_path / "accounts"
            if accounts_dir.exists():
                account_files = list(accounts_dir.glob("*.py"))
                print(f"\n✅ Generated {len(account_files)} account files")

            # Check if instructions were generated
            instructions_dir = output_path / "instructions"
            if instructions_dir.exists():
                instruction_files = list(instructions_dir.glob("*.py"))
                print(f"✅ Generated {len(instruction_files)} instruction files")

            # Check if types were generated
            types_dir = output_path / "types"
            if types_dir.exists():
                type_files = list(types_dir.glob("*.py"))
                print(f"✅ Generated {len(type_files)} type files")

            return True

        except Exception as e:
            print(f"❌ Failed to generate client code: {e}")
            import traceback
            traceback.print_exc()
            return False

# Test all three IDLs
idls = [
    ("kamino_lend_v4.json", "Old format IDL"),
    ("adrena.json", "Old format IDL"),
    ("loopscale_v1.json", "New format IDL (v0.1.0)")
]

results = []
for idl_file, description in idls:
    print(f"\nTesting {idl_file} ({description})...")
    success = test_clientgen(idl_file)
    results.append((idl_file, success))

# Print summary
print(f"\n{'='*60}")
print("SUMMARY")
print(f"{'='*60}")
for idl_file, success in results:
    status = "✅ PASSED" if success else "❌ FAILED"
    print(f"{idl_file:30} {status}")

# Exit with appropriate code
if all(success for _, success in results):
    print("\n🎉 All client generation tests passed!")
    sys.exit(0)
else:
    print("\n⚠️ Some client generation tests failed.")
    sys.exit(1)