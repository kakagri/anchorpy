#!/usr/bin/env python3
"""Test parsing loopscale_v2.json step by step to find the issue."""

import json
from pathlib import Path
from anchorpy3_core.idl import Idl

idl_path = Path(__file__).parent.parent / "loopscale_v2.json"

# First, let's load it as pure JSON
print("Loading as JSON...")
with open(idl_path) as f:
    idl_json = json.load(f)
print("✅ JSON loads successfully")

# Now let's try to parse it with anchorpy_core
print("\nParsing with anchorpy_core.idl.Idl...")

# Try parsing with more detailed error handling
json_str = json.dumps(idl_json)
print(f"JSON string length: {len(json_str)}")

try:
    idl_obj = Idl.from_json(json_str)
    print("✅ Successfully parsed!")
except Exception as e:
    print(f"❌ Failed: {e}")

    # Try to narrow down the issue
    print("\nTrying to narrow down the issue...")

    # Test with minimal IDL
    minimal_idl = {
        "version": idl_json.get("version"),
        "name": idl_json.get("name"),
        "address": idl_json.get("address"),
        "instructions": [],
        "accounts": [],
        "types": [],
        "errors": []
    }

    try:
        print("Testing minimal IDL...")
        Idl.from_json(json.dumps(minimal_idl))
        print("✅ Minimal IDL works")
    except Exception as e2:
        print(f"❌ Even minimal IDL fails: {e2}")

    # Add components one by one
    if idl_json.get("metadata"):
        minimal_idl["metadata"] = idl_json["metadata"]
        try:
            print("Testing with metadata...")
            Idl.from_json(json.dumps(minimal_idl))
            print("✅ Metadata works")
        except Exception as e2:
            print(f"❌ Metadata causes issue: {e2}")

    # Add accounts
    minimal_idl["accounts"] = idl_json.get("accounts", [])
    try:
        print("Testing with accounts...")
        Idl.from_json(json.dumps(minimal_idl))
        print("✅ Accounts work")
    except Exception as e2:
        print(f"❌ Accounts cause issue: {e2}")

    # Add types one by one
    print("\nTesting types one by one...")
    minimal_idl["accounts"] = []  # Remove accounts for now
    for i, type_def in enumerate(idl_json.get("types", [])):
        minimal_idl["types"] = idl_json["types"][:i+1]
        try:
            Idl.from_json(json.dumps(minimal_idl))
        except Exception as e2:
            print(f"❌ Type {i} ({type_def.get('name')}) causes issue: {e2}")
            print(f"   Type definition: {json.dumps(type_def, indent=2)}")
            break
    else:
        print(f"✅ All {len(idl_json.get('types', []))} types work individually")

    # Add instructions
    minimal_idl["types"] = []  # Clear types
    minimal_idl["instructions"] = idl_json.get("instructions", [])
    try:
        print("\nTesting with instructions...")
        Idl.from_json(json.dumps(minimal_idl))
        print("✅ Instructions work")
    except Exception as e2:
        print(f"❌ Instructions cause issue: {e2}")

    # Add errors
    minimal_idl["instructions"] = []  # Clear instructions
    minimal_idl["errors"] = idl_json.get("errors", [])
    try:
        print("Testing with errors...")
        Idl.from_json(json.dumps(minimal_idl))
        print("✅ Errors work")
    except Exception as e2:
        print(f"❌ Errors cause issue: {e2}")

    # Now test everything together
    print("\nTesting full IDL again...")
    full_test = {
        "version": idl_json.get("version"),
        "name": idl_json.get("name"),
        "address": idl_json.get("address"),
        "metadata": idl_json.get("metadata"),
        "instructions": idl_json.get("instructions", []),
        "accounts": idl_json.get("accounts", []),
        "types": idl_json.get("types", []),
        "errors": idl_json.get("errors", [])
    }

    try:
        Idl.from_json(json.dumps(full_test))
        print("✅ Full IDL works when reconstructed")
    except Exception as e2:
        print(f"❌ Full IDL still fails: {e2}")