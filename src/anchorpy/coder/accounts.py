"""This module provides `AccountsCoder` and `_account_discriminator`."""
from hashlib import sha256
from typing import Any, Tuple

from anchorpy_core.idl import Idl
from construct import Adapter, Bytes, Container, Sequence, Switch

from anchorpy.coder.idl import _typedef_layout
from anchorpy.coder.idl_compat import get_account_discriminator, get_account_type_definition
from anchorpy.program.common import NamedInstruction as AccountToSerialize

ACCOUNT_DISCRIMINATOR_SIZE = 8  # bytes


class AccountsCoder(Adapter):
    """Encodes and decodes account data."""

    def __init__(self, idl: Idl) -> None:
        """Init.

        Args:
            idl: The parsed IDL object.
        """
        # Build account layouts - handling both old and new formats
        self._accounts_layout = {}
        for acc in idl.accounts:
            # Get account name (handle both object and dict)
            acc_name = acc.name if hasattr(acc, 'name') else acc.get('name')
            # Get the type definition (handles both old and new format)
            type_def = get_account_type_definition(acc, idl.types)
            self._accounts_layout[acc_name] = _typedef_layout(type_def, idl.types, acc_name)

        # Support both calculated and precomputed discriminators
        self.acc_name_to_discriminator = {}
        for acc in idl.accounts:
            # Get account name (handle both object and dict)
            acc_name = acc.name if hasattr(acc, 'name') else acc.get('name')
            # New format: use precomputed discriminator if available
            disc_list = get_account_discriminator(acc)
            if disc_list:
                disc = bytes(disc_list)
            else:
                # Old format: calculate from name
                disc = _account_discriminator(acc_name)
            self.acc_name_to_discriminator[acc_name] = disc
        self.discriminator_to_acc_name = {
            disc: acc_name for acc_name, disc in self.acc_name_to_discriminator.items()
        }
        discriminator_to_typedef_layout = {
            disc: self._accounts_layout[acc_name]
            for acc_name, disc in self.acc_name_to_discriminator.items()
        }
        subcon = Sequence(
            "discriminator" / Bytes(ACCOUNT_DISCRIMINATOR_SIZE),
            Switch(lambda this: this.discriminator, discriminator_to_typedef_layout),
        )
        super().__init__(subcon)  # type: ignore

    def decode(self, obj: bytes) -> Container[Any]:
        """Decode account data.

        Args:
            obj: Data to decode.

        Returns:
            Decoded data.
        """
        return self.parse(obj).data

    def _decode(self, obj: Tuple[bytes, Any], context, path) -> AccountToSerialize:
        return AccountToSerialize(
            data=obj[1],
            name=self.discriminator_to_acc_name[obj[0]],
        )

    def _encode(self, obj: AccountToSerialize, context, path) -> Tuple[bytes, Any]:
        discriminator = self.acc_name_to_discriminator[obj.name]
        return discriminator, obj.data


def _account_discriminator(name: str) -> bytes:
    """Calculate unique 8 byte discriminator prepended to all anchor accounts.

    Args:
        name: The account name.

    Returns:
        The discriminator in bytes.
    """
    return sha256(f"account:{name}".encode()).digest()[:ACCOUNT_DISCRIMINATOR_SIZE]
