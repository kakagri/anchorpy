"""Pure Python adapter types replacing the old PyO3 IDL classes.

This module provides backward-compatible Python classes that wrap the canonical
JSON output of ``anchorpy_core.idl.parse_idl_compat_py``. All types that were
previously exposed as PyO3 classes (``Idl``, ``IdlTypeSimple``, etc.) are
re-implemented here as plain Python objects.
"""

from __future__ import annotations

import json
import warnings
from enum import IntEnum
from typing import Any, Dict, List, Optional, Sequence, Tuple, Union

from anchorpy_core.idl import parse_idl_compat_py

# ---------------------------------------------------------------------------
# IdlTypeSimple
# ---------------------------------------------------------------------------


class IdlTypeSimple(IntEnum):
    """Enum representing simple / scalar IDL types."""

    Bool = 0
    U8 = 1
    I8 = 2
    U16 = 3
    I16 = 4
    U32 = 5
    I32 = 6
    F32 = 7
    U64 = 8
    I64 = 9
    F64 = 10
    U128 = 11
    I128 = 12
    Bytes = 13
    String = 14
    PublicKey = 15
    Pubkey = 15  # alias for PublicKey
    U256 = 16
    I256 = 17


# Canonical JSON string -> IdlTypeSimple mapping
_SIMPLE_TYPE_MAP: Dict[str, IdlTypeSimple] = {
    "bool": IdlTypeSimple.Bool,
    "u8": IdlTypeSimple.U8,
    "i8": IdlTypeSimple.I8,
    "u16": IdlTypeSimple.U16,
    "i16": IdlTypeSimple.I16,
    "u32": IdlTypeSimple.U32,
    "i32": IdlTypeSimple.I32,
    "f32": IdlTypeSimple.F32,
    "u64": IdlTypeSimple.U64,
    "i64": IdlTypeSimple.I64,
    "f64": IdlTypeSimple.F64,
    "u128": IdlTypeSimple.U128,
    "i128": IdlTypeSimple.I128,
    "bytes": IdlTypeSimple.Bytes,
    "string": IdlTypeSimple.String,
    "publicKey": IdlTypeSimple.PublicKey,
    "pubkey": IdlTypeSimple.PublicKey,
    "u256": IdlTypeSimple.U256,
    "i256": IdlTypeSimple.I256,
}

# ---------------------------------------------------------------------------
# Compound type wrappers
# ---------------------------------------------------------------------------


class IdlTypeDefined:
    """Wraps a user-defined type reference."""

    __slots__ = ("defined",)

    def __init__(self, defined: str) -> None:
        self.defined = defined

    def __repr__(self) -> str:
        return f"IdlTypeDefined({self.defined!r})"

    def __eq__(self, other: object) -> bool:
        return isinstance(other, IdlTypeDefined) and self.defined == other.defined

    def __hash__(self) -> int:
        return hash(("IdlTypeDefined", self.defined))


class IdlTypeOption:
    """Wraps an Option<T> type."""

    __slots__ = ("option",)

    def __init__(self, option: "IdlType") -> None:
        self.option = option

    def __repr__(self) -> str:
        return f"IdlTypeOption({self.option!r})"


class IdlTypeVec:
    """Wraps a Vec<T> type."""

    __slots__ = ("vec",)

    def __init__(self, vec: "IdlType") -> None:
        self.vec = vec

    def __repr__(self) -> str:
        return f"IdlTypeVec({self.vec!r})"


class IdlTypeArray:
    """Wraps a fixed-size array [T; N]."""

    __slots__ = ("array",)

    def __init__(self, array: Tuple["IdlType", int]) -> None:
        self.array = array

    def __repr__(self) -> str:
        return f"IdlTypeArray({self.array!r})"


class IdlTypeGenericLenArray:
    """Wraps a generic-length array [T; G]."""

    __slots__ = ("generic_len_array",)

    def __init__(self, generic_len_array: Tuple["IdlType", str]) -> None:
        self.generic_len_array = generic_len_array

    def __repr__(self) -> str:
        return f"IdlTypeGenericLenArray({self.generic_len_array!r})"


class IdlTypeGeneric:
    """Wraps a generic type parameter."""

    __slots__ = ("generic",)

    def __init__(self, generic: str) -> None:
        self.generic = generic

    def __repr__(self) -> str:
        return f"IdlTypeGeneric({self.generic!r})"


class IdlTypeDefinedWithTypeArgs:
    """Wraps a defined type with generic type arguments."""

    __slots__ = ("name", "args")

    def __init__(self, name: str, args: list) -> None:
        self.name = name
        self.args = args

    def __repr__(self) -> str:
        return f"IdlTypeDefinedWithTypeArgs({self.name!r}, {self.args!r})"


# Union of compound types
IdlTypeCompound = Union[
    IdlTypeDefined,
    IdlTypeOption,
    IdlTypeVec,
    IdlTypeArray,
    IdlTypeGenericLenArray,
    IdlTypeGeneric,
    IdlTypeDefinedWithTypeArgs,
]

# The full IdlType union
IdlType = Union[IdlTypeCompound, IdlTypeSimple]

# ---------------------------------------------------------------------------
# IdlField
# ---------------------------------------------------------------------------


class IdlField:
    """A single field in a struct / instruction arg."""

    __slots__ = ("name", "docs", "ty")

    def __init__(
        self,
        name: str,
        docs: Optional[List[str]],
        ty: IdlType,
    ) -> None:
        self.name = name
        self.docs = docs
        self.ty = ty

    def __repr__(self) -> str:
        return f"IdlField(name={self.name!r}, ty={self.ty!r})"


# ---------------------------------------------------------------------------
# IdlConst
# ---------------------------------------------------------------------------


class IdlConst:
    """A constant defined in the IDL."""

    __slots__ = ("name", "ty", "value")

    def __init__(self, name: str, ty: IdlType, value: str) -> None:
        self.name = name
        self.ty = ty
        self.value = value


# ---------------------------------------------------------------------------
# Type-definition body variants
# ---------------------------------------------------------------------------


class IdlTypeDefinitionTyStruct:
    """Struct body of a type definition."""

    __slots__ = ("fields",)

    def __init__(self, fields: List[IdlField]) -> None:
        self.fields = fields

    def __repr__(self) -> str:
        return f"IdlTypeDefinitionTyStruct(fields={self.fields!r})"


class EnumFieldsNamed:
    """Named fields in an enum variant."""

    __slots__ = ("fields",)

    def __init__(self, fields: List[IdlField]) -> None:
        self.fields = fields


class EnumFieldsTuple:
    """Tuple (unnamed) fields in an enum variant."""

    __slots__ = ("fields",)

    def __init__(self, fields: List[IdlType]) -> None:
        self.fields = fields


EnumFields = Union[EnumFieldsNamed, EnumFieldsTuple]


class IdlEnumVariant:
    """A single variant in an enum type definition."""

    __slots__ = ("name", "fields")

    def __init__(
        self,
        name: str,
        fields: Optional[EnumFields],
    ) -> None:
        self.name = name
        self.fields = fields

    def __repr__(self) -> str:
        return f"IdlEnumVariant(name={self.name!r}, fields={self.fields!r})"


class IdlTypeDefinitionTyEnum:
    """Enum body of a type definition."""

    __slots__ = ("variants",)

    def __init__(self, variants: List[IdlEnumVariant]) -> None:
        self.variants = variants

    def __repr__(self) -> str:
        return f"IdlTypeDefinitionTyEnum(variants={self.variants!r})"


class IdlTypeDefinitionTyAlias:
    """Type-alias body of a type definition."""

    __slots__ = ("value",)

    def __init__(self, value: IdlType) -> None:
        self.value = value

    def __repr__(self) -> str:
        return f"IdlTypeDefinitionTyAlias(value={self.value!r})"


IdlTypeDefinitionTy = Union[
    IdlTypeDefinitionTyStruct,
    IdlTypeDefinitionTyEnum,
    IdlTypeDefinitionTyAlias,
]


class IdlTypeDefinition:
    """A user-defined type (struct, enum, or alias)."""

    __slots__ = ("name", "docs", "ty", "generics")

    def __init__(
        self,
        name: str,
        docs: Optional[List[str]],
        ty: IdlTypeDefinitionTy,
        generics: Optional[List[Any]] = None,
    ) -> None:
        self.name = name
        self.docs = docs
        self.ty = ty
        self.generics = generics or []

    def __repr__(self) -> str:
        return f"IdlTypeDefinition(name={self.name!r})"


# ---------------------------------------------------------------------------
# Instruction-account types
# ---------------------------------------------------------------------------


class IdlAccount:
    """A single instruction account."""

    __slots__ = (
        "name",
        "_writable",
        "_signer",
        "_is_optional",
        "docs",
        "pda",
        "relations",
    )

    def __init__(
        self,
        name: str,
        writable: bool = False,
        signer: bool = False,
        is_optional: bool = False,
        docs: Optional[List[str]] = None,
        pda: Optional["IdlPda"] = None,
        relations: Optional[List[str]] = None,
    ) -> None:
        self.name = name
        self._writable = writable
        self._signer = signer
        self._is_optional = is_optional
        self.docs = docs
        self.pda = pda
        self.relations = relations or []

    # New-style properties
    @property
    def writable(self) -> bool:
        return self._writable

    @property
    def signer(self) -> bool:
        return self._signer

    @property
    def optional(self) -> bool:
        return self._is_optional

    # Old-style backward-compat properties
    @property
    def is_mut(self) -> bool:
        return self._writable

    @property
    def is_signer(self) -> bool:
        return self._signer

    @property
    def is_optional(self) -> bool:
        return self._is_optional

    def __repr__(self) -> str:
        return (
            f"IdlAccount(name={self.name!r}, "
            f"writable={self._writable}, signer={self._signer})"
        )


class IdlAccounts:
    """A composite (nested) group of instruction accounts."""

    __slots__ = ("name", "accounts")

    def __init__(
        self,
        name: str,
        accounts: List["IdlAccountItem"],
    ) -> None:
        self.name = name
        self.accounts = accounts

    def __repr__(self) -> str:
        return f"IdlAccounts(name={self.name!r}, accounts={self.accounts!r})"


IdlAccountItem = Union[IdlAccount, IdlAccounts]

# ---------------------------------------------------------------------------
# PDA / Seed types
# ---------------------------------------------------------------------------


class IdlSeedConst:
    """A constant PDA seed."""

    __slots__ = ("ty", "value")

    def __init__(self, ty: IdlType, value: Any) -> None:
        self.ty = ty
        self.value = value


class IdlSeedArg:
    """An argument-based PDA seed."""

    __slots__ = ("ty", "path")

    def __init__(self, ty: IdlType, path: str) -> None:
        self.ty = ty
        self.path = path


class IdlSeedAccount:
    """An account-based PDA seed."""

    __slots__ = ("ty", "account", "path")

    def __init__(
        self, ty: IdlType, account: Optional[str], path: str
    ) -> None:
        self.ty = ty
        self.account = account
        self.path = path


IdlSeed = Union[IdlSeedConst, IdlSeedArg, IdlSeedAccount]


class IdlPda:
    """PDA definition."""

    __slots__ = ("seeds", "program_id")

    def __init__(
        self,
        seeds: List[IdlSeed],
        program_id: Optional[Any] = None,
    ) -> None:
        self.seeds = seeds
        self.program_id = program_id


# ---------------------------------------------------------------------------
# Instruction
# ---------------------------------------------------------------------------


class IdlInstruction:
    """An instruction defined in the IDL."""

    __slots__ = ("name", "docs", "accounts", "args", "returns", "discriminator")

    def __init__(
        self,
        name: str,
        docs: Optional[List[str]],
        accounts: List[IdlAccountItem],
        args: List[IdlField],
        returns: Optional[IdlType] = None,
        discriminator: Optional[List[int]] = None,
    ) -> None:
        self.name = name
        self.docs = docs
        self.accounts = accounts
        self.args = args
        self.returns = returns
        self.discriminator = discriminator or []


# ---------------------------------------------------------------------------
# Event types
# ---------------------------------------------------------------------------


class IdlEventField:
    """A field inside an event."""

    __slots__ = ("name", "ty", "index")

    def __init__(self, name: str, ty: IdlType, index: bool) -> None:
        self.name = name
        self.ty = ty
        self.index = index


class IdlEvent:
    """An event defined in the IDL."""

    __slots__ = ("name", "fields", "discriminator")

    def __init__(
        self,
        name: str,
        fields: List[IdlEventField],
        discriminator: Optional[List[int]] = None,
    ) -> None:
        self.name = name
        self.fields = fields
        self.discriminator = discriminator or []


# ---------------------------------------------------------------------------
# Error
# ---------------------------------------------------------------------------


class IdlErrorCode:
    """An error code defined in the IDL."""

    __slots__ = ("code", "name", "msg")

    def __init__(self, code: int, name: str, msg: Optional[str]) -> None:
        self.code = code
        self.name = name
        self.msg = msg


# ---------------------------------------------------------------------------
# State (legacy, not used in new format but kept for compat)
# ---------------------------------------------------------------------------


class IdlState:
    """Legacy state definition."""

    __slots__ = ("strct", "methods")

    def __init__(
        self,
        strct: IdlTypeDefinition,
        methods: List[IdlInstruction],
    ) -> None:
        self.strct = strct
        self.methods = methods


# ---------------------------------------------------------------------------
# JSON -> Python parsing helpers
# ---------------------------------------------------------------------------


def _parse_type(raw: Any) -> IdlType:
    """Parse a type from the canonical JSON representation."""
    if isinstance(raw, str):
        simple = _SIMPLE_TYPE_MAP.get(raw)
        if simple is not None:
            return simple
        # Treat unknown string types as defined references
        return IdlTypeDefined(raw)

    if isinstance(raw, dict):
        if "option" in raw:
            return IdlTypeOption(_parse_type(raw["option"]))
        if "vec" in raw:
            return IdlTypeVec(_parse_type(raw["vec"]))
        if "array" in raw:
            arr = raw["array"]
            return IdlTypeArray((_parse_type(arr[0]), arr[1]))
        if "defined" in raw:
            defined_val = raw["defined"]
            if isinstance(defined_val, str):
                return IdlTypeDefined(defined_val)
            # New format: {"defined": {"name": "X", "generics": [...]}}
            return IdlTypeDefined(defined_val["name"])
        if "generic" in raw:
            return IdlTypeGeneric(raw["generic"])
        if "genericLenArray" in raw:
            gla = raw["genericLenArray"]
            return IdlTypeGenericLenArray((_parse_type(gla[0]), gla[1]))

    raise ValueError(f"Cannot parse IDL type: {raw!r}")


def _parse_field(raw: Dict[str, Any]) -> IdlField:
    """Parse a field from JSON."""
    return IdlField(
        name=raw["name"],
        docs=raw.get("docs"),
        ty=_parse_type(raw["type"]),
    )


def _parse_enum_variant(raw: Dict[str, Any]) -> IdlEnumVariant:
    """Parse an enum variant from JSON."""
    name = raw["name"]
    raw_fields = raw.get("fields")

    if raw_fields is None or len(raw_fields) == 0:
        return IdlEnumVariant(name=name, fields=None)

    # Determine if named or tuple fields
    first = raw_fields[0]
    if isinstance(first, dict) and "name" in first:
        # Named fields
        fields = [_parse_field(f) for f in raw_fields]
        return IdlEnumVariant(name=name, fields=EnumFieldsNamed(fields))
    else:
        # Tuple fields - each element is a type
        types = [_parse_type(f) for f in raw_fields]
        return IdlEnumVariant(name=name, fields=EnumFieldsTuple(types))


def _parse_type_definition(raw: Dict[str, Any]) -> IdlTypeDefinition:
    """Parse a type definition from JSON."""
    name = raw["name"]
    docs = raw.get("docs")
    generics = raw.get("generics", [])
    ty_raw = raw["type"]
    kind = ty_raw["kind"]

    if kind == "struct":
        fields_raw = ty_raw.get("fields", [])
        if fields_raw is None:
            fields_raw = []
        fields = [_parse_field(f) for f in fields_raw]
        ty: IdlTypeDefinitionTy = IdlTypeDefinitionTyStruct(fields)
    elif kind == "enum":
        variants_raw = ty_raw.get("variants", [])
        variants = [_parse_enum_variant(v) for v in variants_raw]
        ty = IdlTypeDefinitionTyEnum(variants)
    elif kind == "type":
        alias_raw = ty_raw.get("alias")
        ty = IdlTypeDefinitionTyAlias(_parse_type(alias_raw))
    else:
        raise ValueError(f"Unknown type definition kind: {kind}")

    return IdlTypeDefinition(
        name=name,
        docs=docs,
        ty=ty,
        generics=generics,
    )


def _parse_seed(raw: Dict[str, Any]) -> IdlSeed:
    """Parse a PDA seed from JSON.

    Canonical format has no ``type`` field on seeds — only ``kind`` + ``value``/``path``.
    Old format may include ``type``.  We handle both gracefully.
    """
    kind = raw.get("kind")
    raw_ty = raw.get("type")
    ty = _parse_type(raw_ty) if raw_ty is not None else _parse_type("bytes")
    if kind == "const":
        return IdlSeedConst(ty=ty, value=raw["value"])
    elif kind == "arg":
        return IdlSeedArg(ty=ty, path=raw["path"])
    elif kind == "account":
        return IdlSeedAccount(
            ty=ty,
            account=raw.get("account"),
            path=raw.get("path", ""),
        )
    # Fallback for old format without kind
    return IdlSeedConst(ty=ty, value=raw.get("value"))


def _parse_pda(raw: Optional[Dict[str, Any]]) -> Optional[IdlPda]:
    """Parse PDA definition from JSON."""
    if raw is None:
        return None
    seeds = [_parse_seed(s) for s in raw.get("seeds", [])]
    return IdlPda(seeds=seeds, program_id=raw.get("programId"))


def _parse_account_item(raw: Dict[str, Any]) -> IdlAccountItem:
    """Parse an instruction account item from JSON."""
    if "accounts" in raw:
        # Composite / nested
        return IdlAccounts(
            name=raw["name"],
            accounts=[_parse_account_item(a) for a in raw["accounts"]],
        )
    # Single account
    return IdlAccount(
        name=raw["name"],
        writable=raw.get("writable", raw.get("isMut", False)),
        signer=raw.get("signer", raw.get("isSigner", False)),
        is_optional=raw.get("optional", raw.get("isOptional", False)),
        docs=raw.get("docs"),
        pda=_parse_pda(raw.get("pda")),
        relations=raw.get("relations", []),
    )


def _parse_instruction(raw: Dict[str, Any]) -> IdlInstruction:
    """Parse an instruction from JSON."""
    accounts = [_parse_account_item(a) for a in raw.get("accounts", [])]
    args = [_parse_field(a) for a in raw.get("args", [])]
    returns = None
    if raw.get("returns") is not None:
        returns = _parse_type(raw["returns"])
    return IdlInstruction(
        name=raw["name"],
        docs=raw.get("docs"),
        accounts=accounts,
        args=args,
        returns=returns,
        discriminator=raw.get("discriminator", []),
    )


def _parse_event(
    raw: Dict[str, Any],
    types_by_name: Dict[str, IdlTypeDefinition],
) -> IdlEvent:
    """Parse an event from JSON.

    In the new format, events only have name + discriminator; fields come
    from the matching entry in the ``types`` array.  In the old format the
    event already has ``fields`` directly.
    """
    name = raw["name"]
    discriminator = raw.get("discriminator", [])

    # Old format: event has fields directly
    raw_fields = raw.get("fields")
    if raw_fields:
        fields = [
            IdlEventField(
                name=f["name"],
                ty=_parse_type(f["type"]),
                index=f.get("index", False),
            )
            for f in raw_fields
        ]
        return IdlEvent(name=name, fields=fields, discriminator=discriminator)

    # New format: resolve fields from types
    typedef = types_by_name.get(name)
    if typedef is not None and isinstance(typedef.ty, IdlTypeDefinitionTyStruct):
        fields = [
            IdlEventField(name=f.name, ty=f.ty, index=False)
            for f in typedef.ty.fields
        ]
        return IdlEvent(name=name, fields=fields, discriminator=discriminator)

    # No fields found
    return IdlEvent(name=name, fields=[], discriminator=discriminator)


def _parse_error(raw: Dict[str, Any]) -> IdlErrorCode:
    """Parse an error from JSON."""
    return IdlErrorCode(
        code=raw["code"],
        name=raw["name"],
        msg=raw.get("msg"),
    )


# ---------------------------------------------------------------------------
# Idl  -- the top-level wrapper
# ---------------------------------------------------------------------------


class Idl:
    """Top-level IDL object.

    Constructed via :meth:`from_json`, which first normalises the raw JSON
    through the Rust ``parse_idl_compat_py`` function and then builds the
    Python type hierarchy.
    """

    __slots__ = (
        "_raw",
        "metadata",
        "instructions",
        "types",
        "events",
        "errors",
        "constants",
        "state",
        "_accounts",
        "_types_by_name",
        "address",
    )

    def __init__(
        self,
        *,
        raw: Dict[str, Any],
        metadata: Dict[str, Any],
        instructions: List[IdlInstruction],
        types: List[IdlTypeDefinition],
        events: Optional[List[IdlEvent]],
        errors: Optional[List[IdlErrorCode]],
        constants: Optional[List[IdlConst]],
        state: Optional[IdlState],
        accounts_raw: List[Dict[str, Any]],
        types_by_name: Dict[str, IdlTypeDefinition],
        address: Optional[str],
    ) -> None:
        self._raw = raw
        self.metadata = metadata
        self.instructions = instructions
        self.types = types
        self.events = events
        self.errors = errors
        self.constants = constants
        self.state = state
        self._accounts = accounts_raw
        self._types_by_name = types_by_name
        self.address = address

    # -- Backward-compatible property aliases --------------------------------

    @property
    def name(self) -> str:
        """Program name (from metadata)."""
        return self.metadata.get("name", "")

    @property
    def version(self) -> str:
        """Program version (from metadata)."""
        return self.metadata.get("version", "")

    # -- accounts property ---------------------------------------------------
    # In the old IDL format ``idl.accounts`` returned ``List[IdlTypeDefinition]``
    # (the struct definitions for on-chain accounts).  In the new canonical JSON
    # ``accounts`` is a list of ``{name, discriminator}`` and the actual struct
    # definitions live in ``types``.  We resolve them here.

    @property
    def accounts(self) -> List[IdlTypeDefinition]:
        """Return account type definitions.

        Each element has ``.name``, ``.ty``, ``.docs`` like
        ``IdlTypeDefinition``.
        """
        result: List[IdlTypeDefinition] = []
        for acc_raw in self._accounts:
            name = acc_raw["name"]
            typedef = self._types_by_name.get(name)
            if typedef is not None:
                result.append(typedef)
            else:
                # Create a minimal stub so callers don't crash
                result.append(
                    IdlTypeDefinition(
                        name=name,
                        docs=None,
                        ty=IdlTypeDefinitionTyStruct(fields=[]),
                    )
                )
        return result

    # -- Factory -------------------------------------------------------------

    @classmethod
    def from_json(cls, raw_json: str) -> "Idl":
        """Parse an IDL from its JSON string representation.

        Handles both old (pre-0.30) and new (0.30+) Anchor IDL formats
        by delegating to ``parse_idl_compat_py`` for normalisation.
        """
        canonical_json = parse_idl_compat_py(raw_json)
        data: Dict[str, Any] = json.loads(canonical_json)

        # Parse types first -- needed for event field resolution
        types_raw = data.get("types", []) or []
        types = [_parse_type_definition(t) for t in types_raw]
        types_by_name = {t.name: t for t in types}

        # Instructions
        instructions = [_parse_instruction(ix) for ix in data.get("instructions", [])]

        # Events
        events_raw = data.get("events")
        events: Optional[List[IdlEvent]] = None
        if events_raw is not None:
            events = [_parse_event(e, types_by_name) for e in events_raw]

        # Errors
        errors_raw = data.get("errors")
        errors: Optional[List[IdlErrorCode]] = None
        if errors_raw is not None:
            errors = [_parse_error(e) for e in errors_raw]

        # Constants
        constants_raw = data.get("constants")
        constants: Optional[List[IdlConst]] = None
        if constants_raw is not None:
            constants = [
                IdlConst(
                    name=c["name"],
                    ty=_parse_type(c.get("type", c.get("ty", "bytes"))),
                    value=c["value"],
                )
                for c in constants_raw
            ]

        # Metadata
        metadata = data.get("metadata", {})
        if not metadata:
            # Fallback for very old format
            metadata = {"name": data.get("name", ""), "version": data.get("version", "")}

        # Accounts raw (list of {name, discriminator})
        accounts_raw = data.get("accounts", []) or []

        return cls(
            raw=data,
            metadata=metadata,
            instructions=instructions,
            types=types,
            events=events,
            errors=errors,
            constants=constants,
            state=None,
            accounts_raw=accounts_raw,
            types_by_name=types_by_name,
            address=data.get("address"),
        )
