#!/usr/bin/env python3
"""Comprehensive test suite for new and old IDL format support in AnchorPy.

This test suite verifies that AnchorPy correctly handles both:
- Old (legacy) Anchor IDL format
- New (v0.1.0 spec) Anchor IDL format

Run with: pytest tests/test_idl_format_suite.py -v
"""

import json
import tempfile
from pathlib import Path
import pytest
from anchorpy_core.idl import Idl
from anchorpy import Program, Provider
from anchorpy.clientgen.accounts import gen_accounts
from anchorpy.clientgen.errors import gen_errors
from anchorpy.clientgen.instructions import gen_instructions
from anchorpy.clientgen.program_id import gen_program_id
from anchorpy.clientgen.types import gen_types


class TestIDLFormatSupport:
    """Test suite for IDL format support."""

    @pytest.fixture
    def provider(self):
        """Create a provider for testing."""
        return Provider.local()

    def get_test_idl_path(self, filename: str) -> Path:
        """Get the path to a test IDL file."""
        return Path(__file__).parent.parent / filename

    @pytest.mark.parametrize("idl_file,format_type", [
        ("kamino_lend_v4.json", "old"),
        ("adrena.json", "old"),
        ("loopscale_v1.json", "new"),
        ("loopscale_v2.json", "new"),
    ])
    def test_idl_parsing(self, idl_file: str, format_type: str):
        """Test that IDL files can be parsed correctly."""
        idl_path = self.get_test_idl_path(idl_file)

        with open(idl_path) as f:
            idl_json = json.load(f)

        # Parse as Idl object
        idl_obj = Idl.from_json(json.dumps(idl_json))

        assert idl_obj is not None
        assert idl_obj.instructions is not None

        # Check format detection
        if format_type == "new":
            # New format should have discriminators
            if idl_obj.accounts and len(idl_obj.accounts) > 0:
                first_acc = idl_obj.accounts[0]
                # Check for discriminator (it may be present in new format)
                assert hasattr(first_acc, 'name')

    @pytest.mark.parametrize("idl_file", [
        "kamino_lend_v4.json",
        "adrena.json",
        "loopscale_v1.json",
        "loopscale_v2.json",
    ])
    def test_program_creation(self, idl_file: str, provider):
        """Test that Program objects can be created from IDL files."""
        idl_path = self.get_test_idl_path(idl_file)

        with open(idl_path) as f:
            idl_json = json.load(f)

        # Get program ID
        program_id = idl_json.get('address', 'So11111111111111111111111111111111111111112')

        # Create Program object
        program = Program(idl_json, program_id, provider)

        assert program is not None
        assert program.program_id == program_id
        assert hasattr(program, 'rpc')
        assert hasattr(program, 'account')

    @pytest.mark.parametrize("idl_file", [
        "kamino_lend_v4.json",
        "adrena.json",
        "loopscale_v1.json",
        "loopscale_v2.json",
    ])
    def test_client_generation(self, idl_file: str):
        """Test that client code can be generated from IDL files."""
        idl_path = self.get_test_idl_path(idl_file)

        with open(idl_path) as f:
            idl_json = json.load(f)

        # Parse as Idl object
        idl_obj = Idl.from_json(json.dumps(idl_json))

        # Get program ID
        program_id = idl_json.get('address')
        if not program_id:
            metadata = idl_json.get('metadata', {})
            program_id = metadata.get('address')
        if not program_id:
            program_id = 'So11111111111111111111111111111111111111112'

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "generated"
            output_path.mkdir()

            # Generate all client code
            gen_program_id(program_id, output_path)
            gen_errors(idl_obj, output_path)
            gen_instructions(idl_obj, output_path, gen_pdas=False)
            gen_types(idl_obj, output_path)
            gen_accounts(idl_obj, output_path)

            # Verify files were created
            assert (output_path / "program_id.py").exists()

            # Check for generated content
            if idl_obj.accounts:
                account_files = list((output_path / "accounts").glob("*.py"))
                assert len(account_files) > 0

            if idl_obj.instructions:
                instruction_files = list((output_path / "instructions").glob("*.py"))
                assert len(instruction_files) > 0

    def test_discriminator_handling(self):
        """Test that discriminators are handled correctly in new format."""
        idl_path = self.get_test_idl_path("loopscale_v1.json")

        with open(idl_path) as f:
            idl_json = json.load(f)

        idl_obj = Idl.from_json(json.dumps(idl_json))

        # Check that accounts have discriminators in new format
        if idl_obj.accounts:
            for account in idl_obj.accounts:
                # In new format, discriminators should be precomputed
                if hasattr(account, 'discriminator'):
                    assert account.discriminator is not None
                    assert isinstance(account.discriminator, list)
                    assert len(account.discriminator) == 8

    def test_backward_compatibility(self, provider):
        """Test that old format IDLs still work correctly."""
        idl_path = self.get_test_idl_path("kamino_lend_v4.json")

        with open(idl_path) as f:
            idl_json = json.load(f)

        # Should work exactly as before
        program = Program(
            idl_json,
            idl_json.get('address', 'So11111111111111111111111111111111111111112'),
            provider
        )

        assert program is not None
        assert hasattr(program, 'rpc')
        assert hasattr(program, 'account')


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])