#!/usr/bin/env python3
"""Test loopscale_v2.json with the updated AnchorPy implementation."""

import json
import tempfile
from pathlib import Path
from anchorpy3_core.idl import Idl
from anchorpy import Program, Provider
from anchorpy.clientgen.accounts import gen_accounts
from anchorpy.clientgen.errors import gen_errors
from anchorpy.clientgen.instructions import gen_instructions
from anchorpy.clientgen.program_id import gen_program_id
from anchorpy.clientgen.types import gen_types

def test_loopscale_v2():
    """Test loopscale_v2.json IDL parsing and client generation."""

    print("="*60)
    print("Testing loopscale_v2.json")
    print("="*60)

    # Load the IDL
    idl_path = Path(__file__).parent.parent / "loopscale_v2.json"
    print(f"Loading IDL from: {idl_path}")

    with open(idl_path) as f:
        idl_json = json.load(f)

    # Test 1: Parse as Idl object
    print("\n1. Testing IDL parsing...")
    try:
        idl_obj = Idl.from_json(json.dumps(idl_json))
        print(f"   ✅ Successfully parsed IDL")
        print(f"   - Version: {idl_json.get('version', 'N/A')}")
        print(f"   - Address: {idl_json.get('address', 'N/A')}")
        if idl_obj.metadata:
            print(f"   - Metadata spec: {getattr(idl_obj.metadata, 'spec', 'N/A')}")
        print(f"   - Accounts: {len(idl_obj.accounts) if idl_obj.accounts else 0}")
        print(f"   - Instructions: {len(idl_obj.instructions) if idl_obj.instructions else 0}")
        print(f"   - Types: {len(idl_obj.types) if idl_obj.types else 0}")
        print(f"   - Events: {len(idl_obj.events) if idl_obj.events else 0}")
        print(f"   - Errors: {len(idl_obj.errors) if idl_obj.errors else 0}")

        # Check for discriminators (new format indicator)
        if idl_obj.accounts and len(idl_obj.accounts) > 0:
            first_acc = idl_obj.accounts[0]
            if hasattr(first_acc, 'discriminator') or (isinstance(first_acc, dict) and 'discriminator' in first_acc):
                print("   ✅ New format detected (has discriminators)")
            else:
                print("   ℹ️ Old format detected (no discriminators)")

    except Exception as e:
        print(f"   ❌ Failed to parse IDL: {e}")
        return False

    # Test 2: Create Program object
    print("\n2. Testing Program creation...")
    try:
        provider = Provider.local()
        program_id = idl_json.get('address', 'So11111111111111111111111111111111111111112')
        program = Program(idl_json, program_id, provider)
        print(f"   ✅ Successfully created Program object")
        print(f"   - Program ID: {program.program_id}")
    except Exception as e:
        print(f"   ❌ Failed to create Program: {e}")
        return False

    # Test 3: Generate client code
    print("\n3. Testing client code generation...")
    program_id = idl_json.get('address')
    if not program_id:
        metadata = idl_json.get('metadata', {})
        program_id = metadata.get('address')
    if not program_id:
        program_id = 'So11111111111111111111111111111111111111112'

    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = Path(tmpdir) / "generated"
        output_path.mkdir()

        try:
            # Generate each component
            gen_program_id(program_id, output_path)
            print("   ✅ Generated program_id.py")

            gen_errors(idl_obj, output_path)
            print("   ✅ Generated errors.py")

            gen_instructions(idl_obj, output_path, gen_pdas=False)
            print("   ✅ Generated instructions")

            gen_types(idl_obj, output_path)
            print("   ✅ Generated types")

            gen_accounts(idl_obj, output_path)
            print("   ✅ Generated accounts")

            # Count generated files
            account_files = list((output_path / "accounts").glob("*.py")) if (output_path / "accounts").exists() else []
            instruction_files = list((output_path / "instructions").glob("*.py")) if (output_path / "instructions").exists() else []
            type_files = list((output_path / "types").glob("*.py")) if (output_path / "types").exists() else []

            print(f"\n   Summary:")
            print(f"   - {len(account_files)} account files")
            print(f"   - {len(instruction_files)} instruction files")
            print(f"   - {len(type_files)} type files")

            # List some account names for verification
            if account_files:
                print(f"\n   Sample accounts generated:")
                for f in sorted(account_files)[:5]:
                    print(f"     - {f.stem}")
                if len(account_files) > 5:
                    print(f"     ... and {len(account_files) - 5} more")

            return True

        except Exception as e:
            print(f"   ❌ Failed to generate client code: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == "__main__":
    success = test_loopscale_v2()

    print("\n" + "="*60)
    if success:
        print("✅ SUCCESS: loopscale_v2.json fully supported!")
    else:
        print("❌ FAILED: Issues with loopscale_v2.json")
    print("="*60)