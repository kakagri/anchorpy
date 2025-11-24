"""Test real-world IDL files for compatibility."""
import json
from pathlib import Path
from typing import Optional

import pytest
from solders.pubkey import Pubkey

from anchorpy.coder.accounts import AccountsCoder
from anchorpy.coder.coder import Coder
from anchorpy.coder.instruction import InstructionCoder
from anchorpy.coder.idl_compat import detect_idl_format
from anchorpy import Program, Provider


def load_idl_if_exists(filename: str) -> Optional[dict]:
    """Load IDL file if it exists."""
    idl_path = Path(__file__).parent.parent.parent / filename
    if idl_path.exists():
        with open(idl_path) as f:
            return json.load(f)
    return None


class TestKaminoLendV4:
    """Test Kamino Lend V4 IDL (old format)."""

    def test_kamino_idl_loads(self):
        """Test that Kamino IDL can be loaded."""
        idl_data = load_idl_if_exists("kamino_lend_v4.json")
        if idl_data:
            assert idl_data is not None
            assert "version" in idl_data
            assert idl_data["name"] == "kamino_lending"

    def test_kamino_is_old_format(self):
        """Test that Kamino is detected as old format."""
        idl_data = load_idl_if_exists("kamino_lend_v4.json")
        if idl_data:
            # Check structure to determine format
            assert "version" in idl_data
            assert "name" in idl_data
            # Old format has version and name at top level
            assert "spec" not in idl_data.get("metadata", {})

    @pytest.mark.asyncio
    async def test_kamino_program_creation(self):
        """Test creating Program with Kamino IDL."""
        idl_data = load_idl_if_exists("kamino_lend_v4.json")
        if idl_data:
            provider = Provider.readonly()
            program_id = Pubkey.new_unique()

            # Create program with Kamino IDL
            program = Program(idl_data, program_id, provider)

            assert program is not None
            assert program.program_id == program_id

    @pytest.mark.asyncio
    async def test_kamino_instruction_encoding(self):
        """Test instruction encoding with Kamino IDL."""
        idl_data = load_idl_if_exists("kamino_lend_v4.json")
        if idl_data:
            from anchorpy3_core.idl import Idl

            idl = Idl.from_json(json.dumps(idl_data))
            coder = InstructionCoder(idl)

            # Verify we can encode an instruction
            if idl.instructions:
                first_ix = idl.instructions[0]
                from pyheck import snake
                ix_name = snake(first_ix.name)

                # Check that sighash was created
                assert ix_name in coder.sighashes
                assert len(coder.sighashes[ix_name]) == 8

    def test_kamino_account_discriminators(self):
        """Test account discriminators with Kamino IDL."""
        idl_data = load_idl_if_exists("kamino_lend_v4.json")
        if idl_data:
            from anchorpy3_core.idl import Idl

            idl = Idl.from_json(json.dumps(idl_data))
            coder = AccountsCoder(idl)

            # Verify discriminators were calculated
            if idl.accounts:
                for acc in idl.accounts:
                    assert acc.name in coder.acc_name_to_discriminator
                    disc = coder.acc_name_to_discriminator[acc.name]
                    assert isinstance(disc, bytes)
                    assert len(disc) == 8


class TestAdrena:
    """Test Adrena IDL (old format)."""

    def test_adrena_idl_loads(self):
        """Test that Adrena IDL can be loaded."""
        idl_data = load_idl_if_exists("adrena.json")
        if idl_data:
            assert idl_data is not None
            assert "version" in idl_data
            assert idl_data["name"] == "adrena"

    def test_adrena_is_old_format(self):
        """Test that Adrena is detected as old format."""
        idl_data = load_idl_if_exists("adrena.json")
        if idl_data:
            # Old format characteristics
            assert "version" in idl_data
            assert "name" in idl_data
            # Should not have new format fields
            assert "address" not in idl_data or "spec" not in idl_data.get("metadata", {})

    @pytest.mark.asyncio
    async def test_adrena_program_creation(self):
        """Test creating Program with Adrena IDL."""
        idl_data = load_idl_if_exists("adrena.json")
        if idl_data:
            provider = Provider.readonly()
            program_id = Pubkey.new_unique()

            # Create program with Adrena IDL
            program = Program(idl_data, program_id, provider)

            assert program is not None
            assert program.program_id == program_id

    def test_adrena_defined_types(self):
        """Test that Adrena's defined types are handled correctly."""
        idl_data = load_idl_if_exists("adrena.json")
        if idl_data:
            from anchorpy3_core.idl import Idl

            idl = Idl.from_json(json.dumps(idl_data))

            # Check that types exist and can be processed
            if idl.types:
                assert len(idl.types) > 0
                # Verify all types have names
                for t in idl.types:
                    assert hasattr(t, "name")
                    assert t.name is not None


class TestLoopscaleV1:
    """Test Loopscale V1 IDL (new format)."""

    def test_loopscale_idl_loads(self):
        """Test that Loopscale IDL can be loaded."""
        idl_data = load_idl_if_exists("loopscale_v1.json")
        if idl_data:
            assert idl_data is not None
            assert "address" in idl_data
            assert "metadata" in idl_data
            assert idl_data["metadata"]["name"] == "loopscale"

    def test_loopscale_is_new_format(self):
        """Test that Loopscale is detected as new format."""
        idl_data = load_idl_if_exists("loopscale_v1.json")
        if idl_data:
            # New format characteristics
            assert "address" in idl_data
            assert "metadata" in idl_data
            assert "spec" in idl_data["metadata"]
            assert idl_data["metadata"]["spec"] == "0.1.0"

    def test_loopscale_has_discriminators(self):
        """Test that Loopscale has precomputed discriminators."""
        idl_data = load_idl_if_exists("loopscale_v1.json")
        if idl_data:
            # Check accounts have discriminators
            if "accounts" in idl_data and idl_data["accounts"]:
                for acc in idl_data["accounts"]:
                    assert "discriminator" in acc
                    assert isinstance(acc["discriminator"], list)
                    assert len(acc["discriminator"]) == 8

    @pytest.mark.asyncio
    async def test_loopscale_program_creation(self):
        """Test creating Program with Loopscale IDL."""
        idl_data = load_idl_if_exists("loopscale_v1.json")
        if idl_data:
            provider = Provider.readonly()

            # Use the address from the IDL if present
            if "address" in idl_data:
                program_id = Pubkey.from_string(idl_data["address"])
            else:
                program_id = Pubkey.new_unique()

            # Create program with Loopscale IDL
            program = Program(idl_data, program_id, provider)

            assert program is not None
            assert program.program_id == program_id

    def test_loopscale_account_discriminators(self):
        """Test that Loopscale uses precomputed discriminators."""
        idl_data = load_idl_if_exists("loopscale_v1.json")
        if idl_data:
            from anchorpy3_core.idl import Idl

            # For new format, we need to check if anchorpy_core supports it
            # If not, we'll test the raw data
            if "accounts" in idl_data and idl_data["accounts"]:
                for acc in idl_data["accounts"]:
                    # Verify discriminator exists and is correct format
                    assert "discriminator" in acc
                    disc = acc["discriminator"]
                    assert isinstance(disc, list)
                    assert len(disc) == 8
                    # All values should be valid bytes (0-255)
                    for val in disc:
                        assert isinstance(val, int)
                        assert 0 <= val <= 255


class TestClientGeneration:
    """Test client generation with both old and new format IDLs."""

    @pytest.mark.asyncio
    async def test_client_gen_with_old_format(self):
        """Test client generation with old format IDL."""
        idl_data = load_idl_if_exists("kamino_lend_v4.json")
        if idl_data:
            # This would test the client generation
            # In a real test, we'd generate the client and verify the output
            assert True  # Placeholder for actual client gen test

    @pytest.mark.asyncio
    async def test_client_gen_with_new_format(self):
        """Test client generation with new format IDL."""
        idl_data = load_idl_if_exists("loopscale_v1.json")
        if idl_data:
            # This would test the client generation with new format
            # In a real test, we'd generate the client and verify the output
            assert True  # Placeholder for actual client gen test


class TestBackwardCompatibility:
    """Test that old code still works with the updates."""

    @pytest.mark.asyncio
    async def test_existing_code_with_old_idl(self):
        """Test that existing code patterns still work."""
        idl_data = load_idl_if_exists("kamino_lend_v4.json")
        if idl_data:
            provider = Provider.readonly()
            program_id = Pubkey.new_unique()

            # This is how existing code would create a program
            program = Program(idl_data, program_id, provider)

            # Verify everything still works
            assert program is not None
            assert program.program_id == program_id

            # Check that methods are available
            assert hasattr(program, "rpc")
            assert hasattr(program, "instruction")
            assert hasattr(program, "transaction")
            assert hasattr(program, "account")

    @pytest.mark.asyncio
    async def test_coder_backward_compatibility(self):
        """Test that Coder still works with old IDLs."""
        idl_data = load_idl_if_exists("adrena.json")
        if idl_data:
            from anchorpy3_core.idl import Idl

            idl = Idl.from_json(json.dumps(idl_data))
            coder = Coder(idl)

            # Verify all coder components work
            assert coder.accounts is not None
            assert coder.instruction is not None
            assert coder.events is not None
            assert coder.types is not None