#!/usr/bin/env python3
"""Test full loopscale_v2.json piece by piece."""

import json
from anchorpy_core.idl import Idl

with open('../loopscale_v2.json') as f:
    v2_data = json.load(f)

# Build up the IDL piece by piece
test_idl = {
    "version": v2_data.get("version"),
    "name": v2_data.get("name"),
    "address": v2_data.get("address"),
    "metadata": v2_data.get("metadata"),
    "instructions": [],
    "accounts": [],
    "types": [],
    "errors": [],
    "events": []
}

print("Testing loopscale_v2.json components...")
print("="*50)

# Test 1: Base structure
print("\n1. Base structure only")
try:
    idl = Idl.from_json(json.dumps(test_idl))
    print("   ✅ Base structure works")
except Exception as e:
    print(f"   ❌ Base structure failed: {e}")
    exit(1)

# Test 2: Add errors
print("\n2. Adding errors")
test_idl["errors"] = v2_data.get("errors", [])
try:
    idl = Idl.from_json(json.dumps(test_idl))
    print(f"   ✅ Errors work ({len(test_idl['errors'])} errors)")
except Exception as e:
    print(f"   ❌ Errors failed: {e}")
    exit(1)

# Test 3: Add accounts
print("\n3. Adding accounts")
test_idl["accounts"] = v2_data.get("accounts", [])
try:
    idl = Idl.from_json(json.dumps(test_idl))
    print(f"   ✅ Accounts work ({len(test_idl['accounts'])} accounts)")
except Exception as e:
    print(f"   ❌ Accounts failed: {e}")
    exit(1)

# Test 4: Add types
print("\n4. Adding types")
test_idl["types"] = v2_data.get("types", [])
try:
    idl = Idl.from_json(json.dumps(test_idl))
    print(f"   ✅ Types work ({len(test_idl['types'])} types)")
except Exception as e:
    print(f"   ❌ Types failed: {e}")
    # Try to find which type is problematic
    print("\n   Finding problematic type...")
    for i in range(len(v2_data["types"])):
        test_idl["types"] = v2_data["types"][:i+1]
        try:
            Idl.from_json(json.dumps(test_idl))
        except Exception as e2:
            print(f"   Type {i} ({v2_data['types'][i].get('name')}) causes issue")
            print(f"   Error: {e2}")
            print(f"   Type structure: {json.dumps(v2_data['types'][i], indent=2)}")
            break
    exit(1)

# Test 5: Add events
print("\n5. Adding events")
test_idl["events"] = v2_data.get("events", [])
try:
    idl = Idl.from_json(json.dumps(test_idl))
    print(f"   ✅ Events work ({len(test_idl['events'])} events)")
except Exception as e:
    print(f"   ❌ Events failed: {e}")
    exit(1)

# Test 6: Add instructions
print("\n6. Adding instructions")
test_idl["instructions"] = v2_data.get("instructions", [])
try:
    idl = Idl.from_json(json.dumps(test_idl))
    print(f"   ✅ Instructions work ({len(test_idl['instructions'])} instructions)")
except Exception as e:
    print(f"   ❌ Instructions failed: {e}")
    exit(1)

print("\n" + "="*50)
print("✅ All components work individually!")
print("\nTesting full IDL...")

# Test the full IDL
try:
    idl = Idl.from_json(json.dumps(v2_data))
    print("✅ Full IDL parsed successfully!")
except Exception as e:
    print(f"❌ Full IDL failed: {e}")