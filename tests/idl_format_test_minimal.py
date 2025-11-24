#!/usr/bin/env python3
"""Test minimal IDL structures to isolate the issue."""

import json
from anchorpy3_core.idl import Idl

# Test 1: Empty IDL with null version
print("Test 1: Empty IDL with null version")
minimal = {
    "version": None,
    "name": "test",
    "instructions": [],
    "accounts": [],
    "types": [],
    "errors": []
}

try:
    idl = Idl.from_json(json.dumps(minimal))
    print("  ✅ Parsed successfully")
    print(f"     Version: {idl.version}")
    print(f"     Name: {idl.name}")
except Exception as e:
    print(f"  ❌ Failed: {e}")

# Test 2: Add metadata
print("\nTest 2: With metadata")
minimal["metadata"] = {
    "name": "test",
    "version": "0.1.0",
    "spec": "0.1.0"
}

try:
    idl = Idl.from_json(json.dumps(minimal))
    print("  ✅ Parsed successfully")
except Exception as e:
    print(f"  ❌ Failed: {e}")

# Test 3: Add a new format account
print("\nTest 3: With new format account")
minimal["accounts"] = [
    {
        "name": "TestAccount",
        "discriminator": [1, 2, 3, 4, 5, 6, 7, 8]
    }
]

try:
    idl = Idl.from_json(json.dumps(minimal))
    print("  ✅ Parsed successfully")
    print(f"     Accounts: {len(idl.accounts)}")
except Exception as e:
    print(f"  ❌ Failed: {e}")

# Test 4: Add an error
print("\nTest 4: With error")
minimal["errors"] = [
    {
        "code": 6000,
        "name": "TestError",
        "msg": "Test error message"
    }
]

try:
    idl = Idl.from_json(json.dumps(minimal))
    print("  ✅ Parsed successfully")
    print(f"     Errors: {len(idl.errors) if idl.errors else 0}")
except Exception as e:
    print(f"  ❌ Failed: {e}")

# Test 5: Load actual loopscale_v2.json errors section
print("\nTest 5: With loopscale_v2.json errors")
with open('../loopscale_v2.json') as f:
    v2_data = json.load(f)

minimal["errors"] = v2_data["errors"]

try:
    idl = Idl.from_json(json.dumps(minimal))
    print("  ✅ Parsed successfully")
    print(f"     Errors: {len(idl.errors) if idl.errors else 0}")
except Exception as e:
    print(f"  ❌ Failed: {e}")
    print(f"     Error position suggests issue around: {str(e)}")

# Test 6: Try with types
print("\nTest 6: With loopscale_v2.json types")
minimal["errors"] = []
minimal["types"] = v2_data["types"][:5]  # Try with first 5 types

try:
    idl = Idl.from_json(json.dumps(minimal))
    print("  ✅ Parsed successfully")
    print(f"     Types: {len(idl.types)}")
except Exception as e:
    print(f"  ❌ Failed: {e}")