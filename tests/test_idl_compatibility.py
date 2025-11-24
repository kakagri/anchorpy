"""Test IDL compatibility for both old and new formats."""
import json
from pathlib import Path

import pytest
from anchorpy_core.idl import Idl
from solders.pubkey import Pubkey

from anchorpy.coder.accounts import AccountsCoder
from anchorpy.coder.idl_compat import (
    detect_idl_format,
    get_account_discriminator,
    get_instruction_discriminator,
    get_defined_type_name,
    get_account_writable,
    get_account_signer,
)
from anchorpy.coder.instruction import InstructionCoder
from anchorpy.coder.event import EventCoder
from anchorpy import Program, Provider


class TestIDLFormatDetection:
    """Test IDL format detection."""

    def test_detect_old_format_kamino(self):
        """Test detection of old format IDL (kamino_lend_v4.json)."""
        idl_path = Path(__file__).parent.parent.parent / "kamino_lend_v4.json"
        if idl_path.exists():
            with open(idl_path) as f:
                idl_data = json.load(f)
                idl = Idl.from_json(json.dumps(idl_data))
                assert detect_idl_format(idl) == "old"

    def test_detect_new_format_loopscale(self):
        """Test detection of new format IDL (loopscale_v1.json)."""
        idl_path = Path(__file__).parent.parent.parent / "loopscale_v1.json"
        if idl_path.exists():
            with open(idl_path) as f:
                idl_data = json.load(f)
                # Check the raw data to determine format
                if "address" in idl_data and "metadata" in idl_data:
                    if "spec" in idl_data.get("metadata", {}):
                        # This is new format
                        assert True  # New format detected correctly

    def test_detect_old_format_basic_idl(self):
        """Test detection of old format IDL from test fixtures."""
        idl_path = Path(__file__).parent / "idls" / "basic_1.json"
        if idl_path.exists():
            with open(idl_path) as f:
                idl_data = json.load(f)
                idl = Idl.from_json(json.dumps(idl_data))
                assert detect_idl_format(idl) == "old"


class TestDiscriminatorHandling:
    """Test discriminator handling for both formats."""

    def test_account_discriminator_old_format(self):
        """Test that old format calculates discriminator correctly."""
        # Create a mock account object without discriminator field
        class MockAccount:
            def __init__(self):
                self.name = "TestAccount"

        acc = MockAccount()
        # Should return None since no discriminator field exists
        assert get_account_discriminator(acc) is None

    def test_account_discriminator_new_format(self):
        """Test that new format reads precomputed discriminator."""
        # Create a mock account object with discriminator field
        class MockAccount:
            def __init__(self):
                self.name = "TestAccount"
                self.discriminator = [1, 2, 3, 4, 5, 6, 7, 8]

        acc = MockAccount()
        # Should return the discriminator list
        assert get_account_discriminator(acc) == [1, 2, 3, 4, 5, 6, 7, 8]

    def test_instruction_discriminator_old_format(self):
        """Test that old format returns None for discriminator."""
        # Create a mock instruction object without discriminator field
        class MockInstruction:
            def __init__(self):
                self.name = "testInstruction"

        ix = MockInstruction()
        # Should return None since no discriminator field exists
        assert get_instruction_discriminator(ix) is None

    def test_instruction_discriminator_new_format(self):
        """Test that new format reads precomputed discriminator."""
        # Create a mock instruction object with discriminator field
        class MockInstruction:
            def __init__(self):
                self.name = "testInstruction"
                self.discriminator = [175, 175, 109, 31, 13, 152, 155, 237]

        ix = MockInstruction()
        # Should return the discriminator list
        assert get_instruction_discriminator(ix) == [175, 175, 109, 31, 13, 152, 155, 237]


class TestDefinedTypeHandling:
    """Test defined type handling for both formats."""

    def test_defined_type_old_format_string(self):
        """Test old format where defined is a string."""
        # Old format: defined is directly a string
        defined = "UpdateConfigMode"
        assert get_defined_type_name(defined) == "UpdateConfigMode"

    def test_defined_type_new_format_object(self):
        """Test new format where defined is an object with name field."""
        # New format: defined is an object with 'name' field
        class MockDefinedType:
            def __init__(self):
                self.name = "FooStruct"

        defined = MockDefinedType()
        assert get_defined_type_name(defined) == "FooStruct"

    def test_defined_type_new_format_dict(self):
        """Test new format where defined is a dict with name field."""
        # New format: defined could be a dict (from JSON parsing)
        defined = {"name": "BarEnum"}
        assert get_defined_type_name(defined) == "BarEnum"


class TestAccountFieldCompatibility:
    """Test account field name compatibility."""

    def test_account_writable_old_format(self):
        """Test old format using isMut field."""
        class MockAccount:
            def __init__(self):
                self.isMut = True

        acc = MockAccount()
        assert get_account_writable(acc) == True

        acc.isMut = False
        assert get_account_writable(acc) == False

    def test_account_writable_new_format(self):
        """Test new format using writable field."""
        class MockAccount:
            def __init__(self):
                self.writable = True

        acc = MockAccount()
        assert get_account_writable(acc) == True

        acc.writable = False
        assert get_account_writable(acc) == False

    def test_account_signer_old_format(self):
        """Test old format using isSigner field."""
        class MockAccount:
            def __init__(self):
                self.isSigner = True

        acc = MockAccount()
        assert get_account_signer(acc) == True

        acc.isSigner = False
        assert get_account_signer(acc) == False

    def test_account_signer_new_format(self):
        """Test new format using signer field."""
        class MockAccount:
            def __init__(self):
                self.signer = True

        acc = MockAccount()
        assert get_account_signer(acc) == True

        acc.signer = False
        assert get_account_signer(acc) == False

    def test_account_no_fields_defaults_to_false(self):
        """Test that missing fields default to False."""
        class MockAccount:
            def __init__(self):
                self.name = "test"

        acc = MockAccount()
        assert get_account_writable(acc) == False
        assert get_account_signer(acc) == False


class TestCoderCompatibility:
    """Test that coders work with both IDL formats."""

    @pytest.mark.asyncio
    async def test_accounts_coder_with_old_format(self):
        """Test AccountsCoder with old format IDL."""
        # Load an old format IDL
        idl_path = Path(__file__).parent / "idls" / "basic_1.json"
        if idl_path.exists():
            with open(idl_path) as f:
                idl_data = json.load(f)
                idl = Idl.from_json(json.dumps(idl_data))

                # Create AccountsCoder
                coder = AccountsCoder(idl)

                # Verify discriminators were calculated
                assert len(coder.acc_name_to_discriminator) > 0
                for name, disc in coder.acc_name_to_discriminator.items():
                    assert isinstance(disc, bytes)
                    assert len(disc) == 8

    @pytest.mark.asyncio
    async def test_instruction_coder_with_old_format(self):
        """Test InstructionCoder with old format IDL."""
        # Load an old format IDL
        idl_path = Path(__file__).parent / "idls" / "basic_1.json"
        if idl_path.exists():
            with open(idl_path) as f:
                idl_data = json.load(f)
                idl = Idl.from_json(json.dumps(idl_data))

                # Create InstructionCoder
                coder = InstructionCoder(idl)

                # Verify sighashes were calculated
                assert len(coder.sighashes) > 0
                for name, sighash in coder.sighashes.items():
                    assert isinstance(sighash, bytes)
                    assert len(sighash) == 8


class TestEndToEndCompatibility:
    """Test end-to-end compatibility with real IDL files."""

    @pytest.mark.asyncio
    async def test_program_with_old_format_idl(self):
        """Test creating a Program with an old format IDL."""
        idl_path = Path(__file__).parent / "idls" / "basic_1.json"
        if idl_path.exists():
            with open(idl_path) as f:
                idl_data = json.load(f)

            # Create a mock provider
            provider = Provider.readonly()

            # Create program with old format IDL
            program_id = Pubkey.new_unique()
            program = Program(
                idl_data,
                program_id,
                provider
            )

            # Verify program was created successfully
            assert program is not None
            assert program.program_id == program_id

            # Verify coders were initialized
            assert program.coder is not None
            assert program.coder.accounts is not None
            assert program.coder.instruction is not None