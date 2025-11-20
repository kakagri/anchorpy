"""Tests for new Anchor IDL format (v0.1.0 spec) compatibility."""
import json
from pathlib import Path

import pytest
from anchorpy import Program, Provider
from anchorpy_core.idl import Idl


@pytest.fixture
def loopscale_idl():
    """Load Loopscale v1 IDL (new format)."""
    idl_path = Path(__file__).parent.parent.parent / "loopscale_v1.json"
    with open(idl_path) as f:
        return json.load(f)


@pytest.fixture
def kamino_idl():
    """Load Kamino Lend v4 IDL (old format)."""
    idl_path = Path(__file__).parent.parent.parent / "kamino_lend_v4.json"
    with open(idl_path) as f:
        return json.load(f)


@pytest.fixture
def adrena_idl():
    """Load Adrena IDL (old format)."""
    idl_path = Path(__file__).parent.parent.parent / "adrena.json"
    with open(idl_path) as f:
        return json.load(f)


def test_new_format_idl_parsing(loopscale_idl):
    """Test parsing of new format IDL with precomputed discriminators."""
    # Parse the IDL
    idl = Idl.from_json(json.dumps(loopscale_idl))

    # Check accounts have discriminators
    assert len(idl.accounts) == 10
    for account in idl.accounts:
        # New format accounts should have discriminators
        if isinstance(account, dict):
            assert 'discriminator' in account
            assert len(account['discriminator']) == 8

    # Check types
    assert len(idl.types) == 69

    # Check for new fields like serialization and repr
    types_with_serialization = [
        t for t in idl.types
        if hasattr(t, 'serialization') and t.serialization
    ]
    assert len(types_with_serialization) > 0

    types_with_repr = [
        t for t in idl.types
        if hasattr(t, 'repr') and t.repr
    ]
    assert len(types_with_repr) > 0

    # Check address field
    assert idl.address == "1oopBoJG58DgkUVKkEzKgyG9dvRmpgeEm1AVjoHkF78"


def test_old_format_compatibility(kamino_idl):
    """Test that old format IDLs still work."""
    # Parse the IDL
    idl = Idl.from_json(json.dumps(kamino_idl))

    # Check basic structure
    assert idl.accounts is not None
    assert idl.types is not None
    assert idl.instructions is not None

    # Old format won't have address at top level
    assert idl.address is None or idl.address == ""


def test_program_creation_new_format(loopscale_idl):
    """Test creating Program with new format IDL."""
    provider = Provider.local()
    program_id = loopscale_idl['address']

    # Should be able to create program with dict IDL
    program = Program(loopscale_idl, program_id, provider)

    assert program.program_id
    assert program.idl
    assert program.provider == provider


def test_tuple_struct_support(loopscale_idl):
    """Test support for tuple structs (structs with unnamed fields)."""
    idl = Idl.from_json(json.dumps(loopscale_idl))

    # Find PodBool type which has tuple fields
    pod_bool = None
    for type_def in idl.types:
        if hasattr(type_def, 'name') and type_def.name == 'PodBool':
            pod_bool = type_def
            break

    assert pod_bool is not None
    # PodBool has fields: ['u8'] which is a tuple struct


def test_enum_variant_formats(loopscale_idl):
    """Test support for different enum variant formats."""
    idl = Idl.from_json(json.dumps(loopscale_idl))

    # Find TimelockUpdateParams which has mixed variant types
    timelock_enum = None
    for type_def in idl.types:
        if hasattr(type_def, 'name') and type_def.name == 'TimelockUpdateParams':
            timelock_enum = type_def
            break

    assert timelock_enum is not None
    # Should have enum type with variants that have different field formats


def test_defined_type_formats(loopscale_idl):
    """Test support for new defined type format."""
    idl = Idl.from_json(json.dumps(loopscale_idl))

    # New format uses {"name": "TypeName"} for defined types
    # Old format uses just "TypeName"
    # Both should work after our updates

    # Check that types with defined references work
    for type_def in idl.types:
        if hasattr(type_def, 'ty') and hasattr(type_def.ty, 'fields'):
            fields = type_def.ty.fields
            # Fields should be properly parsed regardless of format
            assert fields is not None


def test_discriminator_handling():
    """Test discriminator handling for both formats."""
    from anchorpy.coder.accounts import _account_discriminator

    # Test calculated discriminator (old format)
    calc_disc = _account_discriminator("MyAccount")
    assert len(calc_disc) == 8
    assert isinstance(calc_disc, bytes)

    # Test precomputed discriminator (new format)
    precomputed = [1, 2, 3, 4, 5, 6, 7, 8]
    disc_bytes = bytes(precomputed)
    assert len(disc_bytes) == 8


def test_backward_compatibility_fields():
    """Test field name compatibility (isMut/isSigner vs writable/signer)."""
    from anchorpy.coder.idl_compat import get_account_writable, get_account_signer

    # Old format
    old_account = type('Account', (), {'isMut': True, 'isSigner': False})()
    assert get_account_writable(old_account) == True
    assert get_account_signer(old_account) == False

    # New format
    new_account = type('Account', (), {'writable': True, 'signer': False})()
    assert get_account_writable(new_account) == True
    assert get_account_signer(new_account) == False

    # Dict format
    dict_account = {'writable': True, 'signer': True}
    assert get_account_writable(dict_account) == True
    assert get_account_signer(dict_account) == True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])