#!/usr/bin/env python3
"""Test client generation directly using the same approach as the CLI."""

import json
import tempfile
from pathlib import Path
from anchorpy_core.idl import Idl
from anchorpy.clientgen.accounts import gen_accounts
from anchorpy.clientgen.errors import gen_errors
from anchorpy.clientgen.instructions import gen_instructions
from anchorpy.clientgen.program_id import gen_program_id
from anchorpy.clientgen.types import gen_types
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
    idl_obj = Idl.from_json(json.dumps(idl_json))

    # Get program ID
    program_id = idl_json.get('address')
    if not program_id:
        # Try metadata
        metadata = idl_json.get('metadata', {})
        program_id = metadata.get('address')
    if not program_id:
        # Use a default for testing
        program_id = 'So11111111111111111111111111111111111111112'

    print(f"Program ID: {program_id}")

    # Create a temporary directory for generated code
    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = Path(tmpdir) / "generated"
        output_path.mkdir()

        print(f"Generating client code to: {output_path}")

        try:
            # Generate each component like the CLI does
            print("  Generating program_id.py...")
            gen_program_id(program_id, output_path)

            print("  Generating errors.py...")
            gen_errors(idl_obj, output_path)

            print("  Generating instructions...")
            gen_instructions(idl_obj, output_path, gen_pdas=False)

            print("  Generating types...")
            gen_types(idl_obj, output_path)

            print("  Generating accounts...")
            gen_accounts(idl_obj, output_path)

            print(f"✅ Successfully generated client code for {idl_name}")

            # List generated files
            print("\nGenerated files:")
            for file in sorted(output_path.rglob("*.py")):
                rel_path = file.relative_to(output_path)
                print(f"  - {rel_path}")

            # Check if accounts were generated
            accounts_dir = output_path / "accounts"
            if accounts_dir.exists():
                account_files = list(accounts_dir.glob("*.py"))
                print(f"\n✅ Generated {len(account_files)} account files")
                # Try to read one to verify it's valid Python
                if account_files:
                    sample = account_files[0].read_text()
                    if "class " in sample:
                        print(f"✅ Account files contain class definitions")

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