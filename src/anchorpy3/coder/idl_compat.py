"""IDL compatibility helpers for supporting both old and new Anchor IDL formats."""
from typing import Any, Dict, List, Optional, Union


def detect_idl_format(idl: Any) -> str:
    """Detect IDL format version.

    Args:
        idl: The IDL object.

    Returns:
        "old" for legacy format, "new" for spec 0.1.0+
    """
    # New format has 'spec' field in metadata
    if hasattr(idl, 'metadata') and idl.metadata and hasattr(idl.metadata, 'spec'):
        return "new"

    # New format has 'address' at top level
    if hasattr(idl, 'address') and idl.address:
        return "new"

    # Check for discriminator in first instruction (if any)
    if hasattr(idl, 'instructions') and idl.instructions:
        first_ix = idl.instructions[0]
        if hasattr(first_ix, 'discriminator') and first_ix.discriminator:
            return "new"

    # Check for discriminator in first account (if any)
    if hasattr(idl, 'accounts') and idl.accounts:
        first_acc = idl.accounts[0]
        if hasattr(first_acc, 'discriminator') and first_acc.discriminator:
            return "new"

    return "old"


def get_account_discriminator(account: Any) -> Optional[List[int]]:
    """Get precomputed discriminator from account if available.

    Args:
        account: The account object from IDL.

    Returns:
        List of 8 integers representing discriminator, or None if not present.
    """
    if hasattr(account, 'discriminator') and account.discriminator:
        return account.discriminator
    elif isinstance(account, dict) and 'discriminator' in account:
        return account['discriminator']
    return None


def get_instruction_discriminator(instruction: Any) -> Optional[List[int]]:
    """Get precomputed discriminator from instruction if available.

    Args:
        instruction: The instruction object from IDL.

    Returns:
        List of 8 integers representing discriminator, or None if not present.
    """
    if hasattr(instruction, 'discriminator') and instruction.discriminator:
        return instruction.discriminator
    return None


def get_event_discriminator(event: Any) -> Optional[List[int]]:
    """Get precomputed discriminator from event if available.

    Args:
        event: The event object from IDL.

    Returns:
        List of 8 integers representing discriminator, or None if not present.
    """
    if hasattr(event, 'discriminator') and event.discriminator:
        return event.discriminator
    return None


def get_account_writable(account: Any) -> bool:
    """Get writable flag with backward compatibility.

    Args:
        account: The account object from IDL instruction.

    Returns:
        True if account is writable/mutable, False otherwise.
    """
    # New format uses 'writable'
    if hasattr(account, 'writable'):
        return bool(account.writable)
    # Old format uses 'isMut'
    if hasattr(account, 'isMut'):
        return bool(account.isMut)
    # Default to False if neither field exists
    return False


def get_account_signer(account: Any) -> bool:
    """Get signer flag with backward compatibility.

    Args:
        account: The account object from IDL instruction.

    Returns:
        True if account is a signer, False otherwise.
    """
    # New format uses 'signer'
    if hasattr(account, 'signer'):
        return bool(account.signer)
    # Old format uses 'isSigner'
    if hasattr(account, 'isSigner'):
        return bool(account.isSigner)
    # Default to False if neither field exists
    return False


def get_account_address(account: Any) -> Optional[str]:
    """Get constant address from account if available.

    Args:
        account: The account object from IDL instruction.

    Returns:
        The address string if present (new format), None otherwise.
    """
    if hasattr(account, 'address') and account.address:
        return account.address
    return None


def get_defined_type_name(type_defined: Any) -> str:
    """Get the name of a defined type with backward compatibility.

    Args:
        type_defined: The defined type, either a string (old) or object with 'name' (new).

    Returns:
        The type name string.

    Raises:
        ValueError: If the type format is not recognized.
    """
    # Old format: defined is a string
    if isinstance(type_defined, str):
        return type_defined

    # New format: defined is an object with 'name' field
    if hasattr(type_defined, 'name'):
        return type_defined.name

    # Also handle dict format (for JSON-parsed IDLs)
    if isinstance(type_defined, dict) and 'name' in type_defined:
        return type_defined['name']

    raise ValueError(f"Unknown defined type format: {type_defined}")


def normalize_defined_type(type_obj: Any) -> Any:
    """Normalize defined type to handle both old and new formats.

    This updates the type object in place if needed.

    Args:
        type_obj: The type object that may contain a 'defined' field.

    Returns:
        The same type object (possibly modified).
    """
    if hasattr(type_obj, 'defined'):
        # If defined is already a string (old format), leave it as is
        if isinstance(type_obj.defined, str):
            return type_obj

        # If defined is an object with 'name' (new format), we may need to handle it
        # depending on how the anchorpy_core types are structured
        # For now, we'll leave it as is and handle in the specific code locations

    return type_obj


def get_account_type_definition(account: Any, types: Optional[List[Any]] = None) -> Any:
    """Get the type definition for an account.

    In the old format, accounts contain their full type definition.
    In the new format, accounts only have name + discriminator, and the
    type definition must be looked up in the types array.

    Args:
        account: The account object from the IDL accounts array.
        types: The types array from the IDL (needed for new format).

    Returns:
        The type definition for the account, or the account itself if it's old format.

    Raises:
        ValueError: If the type definition cannot be found.
    """
    # Handle both object and dict forms
    acc_name = None
    if hasattr(account, 'name'):
        acc_name = account.name
    elif isinstance(account, dict) and 'name' in account:
        acc_name = account['name']

    # Old format: account has a 'ty' field (it IS the type definition)
    if hasattr(account, 'ty'):
        return account
    elif isinstance(account, dict) and 'ty' in account:
        # Dict version of old format
        return account

    # Old format alternative: account has 'type' field
    if hasattr(account, 'type') and account.type:
        return account
    elif isinstance(account, dict) and 'type' in account:
        return account

    # Old format alternative: account has 'kind' field (it IS the type definition)
    if hasattr(account, 'kind'):
        return account
    elif isinstance(account, dict) and 'kind' in account:
        return account

    # New format: account only has name + discriminator, look up in types
    if types is None:
        raise ValueError(f"Types array required for new format account: {acc_name}")

    # Find the type definition by matching name
    for type_def in types:
        type_name = None
        if hasattr(type_def, 'name'):
            type_name = type_def.name
        elif isinstance(type_def, dict) and 'name' in type_def:
            type_name = type_def['name']

        if type_name == acc_name:
            return type_def

    raise ValueError(f"Type definition not found for account: {acc_name}")