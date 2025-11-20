#!/usr/bin/env python3
"""Find types with empty or null fields in loopscale_v2.json."""

import json
from pathlib import Path

idl_path = Path(__file__).parent.parent / "loopscale_v2.json"
with open(idl_path) as f:
    idl = json.load(f)

print("Looking for types with empty/null fields...")
print("="*60)

problematic = []

for type_def in idl.get('types', []):
    name = type_def.get('name')
    type_info = type_def.get('type') or type_def.get('ty')

    if type_info and isinstance(type_info, dict):
        kind = type_info.get('kind')

        if kind == 'struct':
            fields = type_info.get('fields')
            if fields is None:
                problematic.append((name, 'null fields'))
                print(f"❌ {name}: struct with null fields")
            elif fields == []:
                problematic.append((name, 'empty fields []'))
                print(f"⚠️ {name}: struct with empty fields []")
                print(f"   Full definition: {json.dumps(type_def, indent=2)}")
            elif not isinstance(fields, list):
                problematic.append((name, f'non-list fields: {type(fields)}'))
                print(f"❌ {name}: struct with non-list fields ({type(fields)})")

        elif kind == 'enum':
            variants = type_info.get('variants')
            if variants is None:
                problematic.append((name, 'null variants'))
                print(f"❌ {name}: enum with null variants")
            elif variants == []:
                problematic.append((name, 'empty variants []'))
                print(f"⚠️ {name}: enum with empty variants []")

if problematic:
    print(f"\nFound {len(problematic)} types with issues:")
    for name, issue in problematic:
        print(f"  - {name}: {issue}")
else:
    print("\n✅ All types have proper fields/variants")

# Let's also check if any types have 'ty' instead of 'type'
print("\n" + "="*60)
print("Checking field naming...")
ty_count = 0
type_count = 0

for type_def in idl.get('types', []):
    if 'ty' in type_def:
        ty_count += 1
    if 'type' in type_def:
        type_count += 1

print(f"Types with 'ty' field: {ty_count}")
print(f"Types with 'type' field: {type_count}")

# Check for any unusual structures
print("\n" + "="*60)
print("Checking for unit structs (structs with no fields)...")

for type_def in idl.get('types', []):
    name = type_def.get('name')
    type_info = type_def.get('type') or type_def.get('ty')

    if type_info == {"kind": "struct"}:
        print(f"  Found unit struct: {name}")
        print(f"    Full def: {json.dumps(type_def)}")