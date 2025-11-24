"""IDL coding."""
from dataclasses import fields as dc_fields
from dataclasses import make_dataclass
from keyword import kwlist
from types import MappingProxyType
from typing import Mapping, Type, cast

from anchorpy3_core.idl import (
    IdlField,
    IdlType,
    IdlTypeArray,
    IdlTypeDefined,
    IdlTypeDefinition,
    IdlTypeDefinitionTyAlias,
    IdlTypeDefinitionTyEnum,
    IdlTypeDefinitionTyStruct,
    IdlTypeOption,
    IdlTypeSimple,
    IdlTypeVec,
)
from anchorpy.coder.idl_compat import get_defined_type_name
from borsh_construct import (
    F32,
    F64,
    I8,
    I16,
    I32,
    I64,
    I128,
    U8,
    U16,
    U32,
    U64,
    U128,
    Bool,
    Bytes,
    CStruct,
    Enum,
    Option,
    String,
    TupleStruct,
    Vec,
)
from construct import Construct
from pyheck import snake

from anchorpy.borsh_extension import BorshPubkey, _DataclassStruct
from anchorpy.idl import TypeDefs

FIELD_TYPE_MAP: Mapping[IdlTypeSimple, Construct] = MappingProxyType(
    {
        IdlTypeSimple.Bool: Bool,
        IdlTypeSimple.U8: U8,
        IdlTypeSimple.I8: I8,
        IdlTypeSimple.U16: U16,
        IdlTypeSimple.I16: I16,
        IdlTypeSimple.U32: U32,
        IdlTypeSimple.I32: I32,
        IdlTypeSimple.F32: F32,
        IdlTypeSimple.U64: U64,
        IdlTypeSimple.I64: I64,
        IdlTypeSimple.F64: F64,
        IdlTypeSimple.U128: U128,
        IdlTypeSimple.I128: I128,
        IdlTypeSimple.Bytes: Bytes,
        IdlTypeSimple.String: String,
        IdlTypeSimple.PublicKey: BorshPubkey,
    },
)


_enums_cache: dict[tuple[str, str], Enum] = {}


def _handle_enum_variants(
    idl_enum,  # Can be IdlTypeDefinitionTyEnum or dict
    types: TypeDefs,
    name: str,
) -> Enum:
    dict_key = (name, str(idl_enum))
    try:
        return _enums_cache[dict_key]
    except KeyError:
        result = _handle_enum_variants_no_cache(idl_enum, types, name)
        _enums_cache[dict_key] = result
        return result


def _handle_enum_variants_no_cache(
    idl_enum,  # Can be IdlTypeDefinitionTyEnum or dict
    types: TypeDefs,
    name: str,
) -> Enum:
    variants = []
    dclasses = {}
    # Get variants handling both object and dict formats
    enum_variants = idl_enum.variants if hasattr(idl_enum, 'variants') else idl_enum.get('variants', [])
    for variant in enum_variants:
        # Handle both object and dict variants
        if hasattr(variant, 'name'):
            variant_name = variant.name
            variant_fields = variant.fields
        elif isinstance(variant, dict):
            variant_name = variant.get('name')
            variant_fields = variant.get('fields')
        else:
            continue

        if variant_fields is None:
            variants.append(variant_name)
        else:
            # Get fields from variant_fields (can be object or dict)
            if hasattr(variant_fields, 'fields'):
                flds = variant_fields.fields
            elif isinstance(variant_fields, dict):
                flds = variant_fields.get('fields', [])
            else:
                flds = variant_fields if isinstance(variant_fields, list) else []
            # Check if fields are named (have 'name' property) or tuple-style
            if flds and (isinstance(flds[0], IdlField) or (isinstance(flds[0], dict) and 'name' in flds[0])):
                fields = []
                named_fields = cast(list[IdlField], flds)
                for fld in named_fields:
                    fields.append(_field_layout(fld, types))
                cstruct = CStruct(*fields)
                datacls = _idl_enum_fields_named_to_dataclass_type(
                    named_fields,
                    variant_name,
                )
                dclasses[variant_name] = datacls
                renamed = variant_name / cstruct
            else:
                fields = []
                unnamed_fields = cast(list[IdlType], flds)
                for type_ in unnamed_fields:
                    fields.append(_type_layout(type_, types))
                tuple_struct = TupleStruct(*fields)
                renamed = variant_name / tuple_struct
            variants.append(renamed)  # type: ignore
    enum_without_types = Enum(*variants, enum_name=name)
    if dclasses:
        for cname in enum_without_types.enum._sumtype_constructor_names:
            try:
                dclass = dclasses[cname]
            except KeyError:
                continue
            dclass_fields = dc_fields(dclass)
            constructr = getattr(enum_without_types.enum, cname)
            for constructor_field in constructr._sumtype_attribs:
                attrib = constructor_field[1]  # type: ignore
                fld_name = constructor_field[0]  # type: ignore
                dclass_field = [f for f in dclass_fields if f.name == fld_name][0]
                attrib.type = dclass_field.type  # type: ignore
    return enum_without_types


def _typedef_layout_without_field_name(
    typedef,  # Can be IdlTypeDefinition or dict
    types: TypeDefs,
) -> Construct:
    # Handle both object and dict formats
    if hasattr(typedef, 'ty'):
        typedef_type = typedef.ty
        name = typedef.name
    elif isinstance(typedef, dict):
        typedef_type = typedef.get('ty') or typedef.get('type')
        name = typedef.get('name')
    else:
        raise ValueError(f"Unknown typedef format: {type(typedef)}")
    # Check typedef_type (can be object or dict)
    is_struct = isinstance(typedef_type, IdlTypeDefinitionTyStruct) or (
        isinstance(typedef_type, dict) and typedef_type.get('kind') == 'struct'
    )
    is_enum = isinstance(typedef_type, IdlTypeDefinitionTyEnum) or (
        isinstance(typedef_type, dict) and typedef_type.get('kind') == 'enum'
    )
    is_alias = isinstance(typedef_type, IdlTypeDefinitionTyAlias) or (
        isinstance(typedef_type, dict) and typedef_type.get('kind') == 'alias'
    )

    if is_struct:
        fields = typedef_type.fields if hasattr(typedef_type, 'fields') else typedef_type.get('fields', [])
        field_layouts = [_field_layout(field, types) for field in fields]
        cstruct = CStruct(*field_layouts)
        datacls = _idl_typedef_ty_struct_to_dataclass_type(typedef_type, name)
        return _DataclassStruct(cstruct, datacls=datacls)
    elif is_enum:
        return _handle_enum_variants(typedef_type, types, name)
    elif is_alias:
        value = typedef_type.value if hasattr(typedef_type, 'value') else typedef_type.get('value')
        return _type_layout(value, types)

    unknown_type = typedef_type.kind if hasattr(typedef_type, 'kind') else typedef_type.get('kind', 'unknown')
    raise ValueError(f"Unknown type {unknown_type}")


def _typedef_layout(
    typedef: IdlTypeDefinition,
    types: list[IdlTypeDefinition],
    field_name: str,
) -> Construct:
    """Map an IDL typedef to a `Construct` object.

    Args:
        typedef: The IDL typedef object.
        types: IDL type definitions.
        field_name: The name of the field.

    Raises:
        ValueError: If an unknown type is passed.

    Returns:
        `Construct` object from `borsh-construct`.
    """
    return field_name / _typedef_layout_without_field_name(typedef, types)


def _type_layout(type_: IdlType, types: TypeDefs) -> Construct:
    if isinstance(type_, IdlTypeSimple):
        return FIELD_TYPE_MAP[type_]
    if isinstance(type_, IdlTypeVec):
        return Vec(_type_layout(type_.vec, types))
    elif isinstance(type_, IdlTypeOption):
        return Option(_type_layout(type_.option, types))
    elif isinstance(type_, IdlTypeDefined):
        # Support both old string format and new object format
        defined = get_defined_type_name(type_.defined)
        if not types:
            raise ValueError("User defined types not provided")
        # Handle both object and dict types
        filtered = []
        for t in types:
            type_name = t.name if hasattr(t, 'name') else t.get('name')
            if type_name == defined:
                filtered.append(t)
        if len(filtered) != 1:
            raise ValueError(f"Type not found {defined}")
        return _typedef_layout_without_field_name(filtered[0], types)
    elif isinstance(type_, IdlTypeArray):
        array_ty = type_.array[0]
        array_len = type_.array[1]
        inner_layout = _type_layout(array_ty, types)
        return inner_layout[array_len]
    raise ValueError(f"Type {type_} not implemented yet")


def _field_layout(field, types: TypeDefs) -> Construct:  # field can be IdlField or dict
    """Map IDL spec to `borsh-construct` types.

    Args:
        field: field object from the IDL.
        types: IDL type definitions.

    Raises:
        ValueError: If the user-defined types are not provided.
        ValueError: If the type is not found.
        ValueError: If the type is not implemented yet.

    Returns:
        `Construct` object from `borsh-construct`.
    """
    # Handle both object and dict fields
    if hasattr(field, 'name'):
        field_name = snake(field.name) if field.name else ""
        field_ty = field.ty
    elif isinstance(field, dict):
        field_name = snake(field.get('name')) if field.get('name') else ""
        field_ty = field.get('ty') or field.get('type')
    else:
        raise ValueError(f"Unknown field format: {type(field)}")
    return field_name / _type_layout(field_ty, types)


def _make_datacls(name: str, fields: list[str]) -> type:
    return make_dataclass(name, fields)


_idl_typedef_ty_struct_to_dataclass_type_cache: dict[tuple[str, str], Type] = {}


def _idl_typedef_ty_struct_to_dataclass_type(
    typedef_type,  # Can be IdlTypeDefinitionTyStruct or dict
    name: str,
) -> Type:
    dict_key = (name, str(typedef_type))
    try:
        return _idl_typedef_ty_struct_to_dataclass_type_cache[dict_key]
    except KeyError:
        result = _idl_typedef_ty_struct_to_dataclass_type_no_cache(typedef_type, name)
        _idl_typedef_ty_struct_to_dataclass_type_cache[dict_key] = result
        return result


def _idl_typedef_ty_struct_to_dataclass_type_no_cache(
    typedef_type,  # Can be IdlTypeDefinitionTyStruct or dict
    name: str,
) -> Type:
    """Generate a dataclass definition from an IDL struct.

    Args:
        typedef_type: The IDL type.
        name: The name of the dataclass.

    Returns:
        Dataclass definition.
    """
    dataclass_fields = []
    # Get fields handling both object and dict formats
    fields = typedef_type.fields if hasattr(typedef_type, 'fields') else typedef_type.get('fields', [])

    for field in fields:
        # Handle both object and dict field formats
        if hasattr(field, 'name'):
            field_name = snake(field.name)
        elif isinstance(field, dict):
            field_name = snake(field.get('name', ''))
        else:
            continue

        field_name_to_use = f"{field_name}_" if field_name in kwlist else field_name
        dataclass_fields.append(
            field_name_to_use,
        )
    return _make_datacls(name, dataclass_fields)


_idl_enum_fields_named_to_dataclass_type_cache: dict[tuple[str, str], Type] = {}


def _idl_enum_fields_named_to_dataclass_type(
    fields: list[IdlField],
    name: str,
) -> Type:
    dict_key = (name, str(fields))
    try:
        return _idl_enum_fields_named_to_dataclass_type_cache[dict_key]
    except KeyError:
        result = _idl_enum_fields_named_to_dataclass_type_no_cache(fields, name)
        _idl_enum_fields_named_to_dataclass_type_cache[dict_key] = result
        return result


def _idl_enum_fields_named_to_dataclass_type_no_cache(
    fields: list[IdlField],
    name: str,
) -> Type:
    """Generate a dataclass definition from IDL named enum fields.

    Args:
        fields: The IDL enum fields.
        name: The name of the dataclass.

    Returns:
        Dataclass type definition.
    """
    dataclass_fields = []
    for field in fields:
        field_name = snake(field.name)
        field_name_to_use = f"{field_name}_" if field_name in kwlist else field_name
        dataclass_fields.append(
            field_name_to_use,
        )
    return _make_datacls(name, dataclass_fields)


def _idl_typedef_to_python_type(
    typedef: IdlTypeDefinition,
    types: TypeDefs,
) -> Type:
    """Generate Python type from IDL user-defined type.

    Args:
        typedef: The user-defined type.
        types: IDL type definitions.

    Raises:
        ValueError: If an unknown type is passed.

    Returns:
        The Python type.
    """
    typedef_type = typedef.ty
    if isinstance(typedef_type, IdlTypeDefinitionTyStruct):
        return _idl_typedef_ty_struct_to_dataclass_type(
            typedef_type,
            typedef.name,
        )
    elif isinstance(typedef_type, IdlTypeDefinitionTyEnum):
        return _handle_enum_variants(typedef_type, types, typedef.name).enum
    elif isinstance(typedef_type, IdlTypeDefinitionTyAlias):
        raise ValueError(f"Alias not handled here: {typedef_type}")
    unknown_type = typedef_type.kind
    raise ValueError(f"Unknown type {unknown_type}")
