#!/usr/bin/env python3
"""Comprehensive test of all IDL formats with AnchorPy."""

import json
import tempfile
from pathlib import Path
from anchorpy_core.idl import Idl
from anchorpy import Program, Provider
from anchorpy.clientgen.accounts import gen_accounts
from anchorpy.clientgen.errors import gen_errors
from anchorpy.clientgen.instructions import gen_instructions
from anchorpy.clientgen.program_id import gen_program_id
from anchorpy.clientgen.types import gen_types
import sys

def test_idl_comprehensive(idl_name: str, description: str):
    """Comprehensive test of an IDL file."""
    print(f"\n{'='*70}")
    print(f"Testing: {idl_name}")
    print(f"Format: {description}")
    print(f"{'='*70}")

    # Load the IDL
    idl_path = Path(__file__).parent.parent / idl_name
    print(f"📁 Loading from: {idl_path}")

    with open(idl_path) as f:
        idl_json = json.load(f)

    # Test 1: Parse as Idl object
    print("\n1️⃣  IDL Parsing...")
    try:
        idl_obj = Idl.from_json(json.dumps(idl_json))
        print(f"   ✅ Successfully parsed IDL")

        # Display IDL stats
        print(f"\n   📊 IDL Statistics:")
        print(f"      Version: {idl_json.get('version', 'None')}")
        print(f"      Address: {idl_json.get('address', 'None')}")

        if idl_obj.metadata:
            spec = getattr(idl_obj.metadata, 'spec', None) if hasattr(idl_obj.metadata, 'spec') else (
                idl_obj.metadata.get('spec') if isinstance(idl_obj.metadata, dict) else None
            )
            if spec:
                print(f"      Spec: {spec}")

        print(f"      Accounts: {len(idl_obj.accounts) if idl_obj.accounts else 0}")
        print(f"      Instructions: {len(idl_obj.instructions) if idl_obj.instructions else 0}")
        print(f"      Types: {len(idl_obj.types) if idl_obj.types else 0}")
        print(f"      Events: {len(idl_obj.events) if idl_obj.events else 0}")
        print(f"      Errors: {len(idl_obj.errors) if idl_obj.errors else 0}")

        # Check format
        if idl_obj.accounts and len(idl_obj.accounts) > 0:
            first_acc = idl_obj.accounts[0]
            if hasattr(first_acc, 'discriminator') or (isinstance(first_acc, dict) and 'discriminator' in first_acc):
                print(f"      Format: New (v0.1.0+) - has discriminators")
            else:
                print(f"      Format: Old (legacy)")

    except Exception as e:
        print(f"   ❌ Failed to parse IDL: {e}")
        return False

    # Test 2: Create Program object
    print("\n2️⃣  Program Creation...")
    try:
        provider = Provider.local()
        program_id = idl_json.get('address', 'So11111111111111111111111111111111111111112')
        program = Program(idl_json, program_id, provider)
        print(f"   ✅ Successfully created Program object")
        print(f"      Program ID: {program.program_id}")

        # Check available methods
        if hasattr(program, 'rpc'):
            rpc_methods = dir(program.rpc)
            user_methods = [m for m in rpc_methods if not m.startswith('_')]
            print(f"      RPC methods available: {len(user_methods)}")
            if user_methods:
                print(f"      Sample methods: {', '.join(user_methods[:3])}")

        if hasattr(program, 'account'):
            account_types = dir(program.account)
            user_accounts = [a for a in account_types if not a.startswith('_')]
            print(f"      Account types available: {len(user_accounts)}")
            if user_accounts:
                print(f"      Sample accounts: {', '.join(user_accounts[:3])}")

    except Exception as e:
        print(f"   ❌ Failed to create Program: {e}")
        return False

    # Test 3: Generate client code
    print("\n3️⃣  Client Code Generation...")
    program_id = idl_json.get('address')
    if not program_id:
        metadata = idl_json.get('metadata', {})
        program_id = metadata.get('address')
    if not program_id:
        program_id = 'So11111111111111111111111111111111111111112'

    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = Path(tmpdir) / "generated"
        output_path.mkdir()

        generation_steps = [
            ("program_id.py", lambda: gen_program_id(program_id, output_path)),
            ("errors", lambda: gen_errors(idl_obj, output_path)),
            ("instructions", lambda: gen_instructions(idl_obj, output_path, gen_pdas=False)),
            ("types", lambda: gen_types(idl_obj, output_path)),
            ("accounts", lambda: gen_accounts(idl_obj, output_path))
        ]

        all_success = True
        for step_name, step_func in generation_steps:
            try:
                step_func()
                print(f"   ✅ Generated {step_name}")
            except Exception as e:
                print(f"   ❌ Failed to generate {step_name}: {e}")
                all_success = False
                break

        if all_success:
            # Count generated files
            account_files = list((output_path / "accounts").glob("*.py")) if (output_path / "accounts").exists() else []
            instruction_files = list((output_path / "instructions").glob("*.py")) if (output_path / "instructions").exists() else []
            type_files = list((output_path / "types").glob("*.py")) if (output_path / "types").exists() else []
            error_files = list((output_path / "errors").glob("*.py")) if (output_path / "errors").exists() else []

            print(f"\n   📦 Generated Files Summary:")
            print(f"      Account files: {len(account_files)}")
            print(f"      Instruction files: {len(instruction_files)}")
            print(f"      Type files: {len(type_files)}")
            print(f"      Error files: {len(error_files)}")
            print(f"      Total: {len(account_files) + len(instruction_files) + len(type_files) + len(error_files) + 1} files")

            # Sample generated content validation
            if account_files:
                sample_account = account_files[0].read_text()
                if "class " in sample_account and "def fetch" in sample_account:
                    print(f"   ✅ Account files contain proper class definitions")

            if instruction_files:
                sample_ix = instruction_files[0].read_text()
                if "def " in sample_ix:
                    print(f"   ✅ Instruction files contain function definitions")

            return True
        else:
            return False

# Test all IDLs
idls = [
    ("kamino_lend_v4.json", "Old format (legacy)"),
    ("adrena.json", "Old format (legacy)"),
    ("loopscale_v1.json", "New format (v0.1.0)"),
    ("loopscale_v2.json", "New format (v0.1.0 with events)")
]

results = []
for idl_file, description in idls:
    success = test_idl_comprehensive(idl_file, description)
    results.append((idl_file, success))

# Print final summary
print(f"\n{'='*70}")
print("FINAL SUMMARY")
print(f"{'='*70}")
print(f"{'IDL File':<30} {'Status':<10} {'Result'}")
print(f"{'-'*30} {'-'*10} {'-'*20}")

for idl_file, success in results:
    status = "✅ PASSED" if success else "❌ FAILED"
    result = "Full support" if success else "Issues found"
    print(f"{idl_file:<30} {status:<10} {result}")

# Overall result
all_passed = all(success for _, success in results)
print(f"\n{'='*70}")
if all_passed:
    print("🎉 SUCCESS: All IDLs are fully supported!")
    print("\nAnchorPy now supports:")
    print("  ✅ Old format IDLs (legacy Anchor)")
    print("  ✅ New format IDLs (v0.1.0 spec)")
    print("  ✅ Full backward compatibility")
    print("  ✅ Complete client code generation")
    print("  ✅ Program object creation")
    sys.exit(0)
else:
    print("⚠️ PARTIAL SUCCESS: Some IDLs have issues")
    sys.exit(1)