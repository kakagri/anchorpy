"""This module deals with (de)serializing Anchor events."""
from hashlib import sha256
from typing import Any, Dict, Optional, Tuple

from anchorpy_core.idl import (
    Idl,
    IdlEvent,
    IdlField,
    IdlTypeDefinition,
    IdlTypeDefinitionTyStruct,
)
from construct import Adapter, Bytes, Construct, Sequence, Switch
from pyheck import snake

from anchorpy.coder.idl import _typedef_layout, _typedef_layout_without_field_name
from anchorpy.coder.idl_compat import get_event_discriminator
from anchorpy.program.common import Event


def _event_discriminator(name: str) -> bytes:
    """Get 8-byte discriminator from event name.

    Args:
        name: The event name.

    Returns:
        Discriminator
    """
    return sha256(f"event:{name}".encode()).digest()[:8]


def _event_layout(event, idl: Idl) -> Construct:  # event can be IdlEvent or dict
    # Handle both object and dict events
    if hasattr(event, 'name'):
        event_name = event.name
        event_fields = getattr(event, 'fields', None)
    elif isinstance(event, dict):
        event_name = event.get('name')
        event_fields = event.get('fields')
    else:
        raise ValueError(f"Unknown event format: {type(event)}")

    # For new format, events might not have fields directly
    # Need to look up in types array
    if event_fields is None:
        # Try to find the event type in the types array
        for type_def in idl.types:
            type_name = type_def.name if hasattr(type_def, 'name') else type_def.get('name')
            if type_name == event_name:
                return _typedef_layout_without_field_name(type_def, idl.types)

        # If not found in types, create empty struct
        event_type_def = IdlTypeDefinition(
            name=event_name,
            docs=None,
            ty=IdlTypeDefinitionTyStruct(fields=[]),
        )
    else:
        # Old format with fields
        event_type_def = IdlTypeDefinition(
            name=event_name,
            docs=None,
            ty=IdlTypeDefinitionTyStruct(
                fields=[
                    IdlField(name=snake(f.name), docs=None, ty=f.ty) for f in event_fields
                ],
            ),
        )

    return _typedef_layout(event_type_def, idl.types, event_name)


class EventCoder(Adapter):
    """Encodes and decodes Anchor events."""

    def __init__(self, idl: Idl):
        """Initialize the EventCoder.

        Args:
            idl: The parsed Idl object.
        """
        self.idl = idl
        idl_events = idl.events
        layouts: Dict[str, Construct]
        if idl_events:
            layouts = {}
            for event in idl_events:
                # Handle both object and dict events
                if hasattr(event, 'name'):
                    event_name = event.name
                elif isinstance(event, dict):
                    event_name = event.get('name')
                else:
                    continue
                layouts[event_name] = _event_layout(event, idl)
        else:
            layouts = {}
        self.layouts = layouts
        # Support both calculated and precomputed discriminators
        self.discriminators: Dict[bytes, str] = {}
        if idl_events:
            for event in idl_events:
                # Get event name (handle both object and dict)
                if hasattr(event, 'name'):
                    event_name = event.name
                elif isinstance(event, dict):
                    event_name = event.get('name')
                else:
                    continue

                # New format: use precomputed discriminator if available
                disc_list = get_event_discriminator(event)
                if disc_list:
                    disc = bytes(disc_list)
                else:
                    # Old format: calculate from name
                    disc = _event_discriminator(event_name)
                self.discriminators[disc] = event_name
        self.discriminator_to_layout = {
            disc: self.layouts[event_name]
            for disc, event_name in self.discriminators.items()
        }
        subcon = Sequence(
            "discriminator" / Bytes(8),  # not base64-encoded here
            Switch(lambda this: this.discriminator, self.discriminator_to_layout),
        )
        super().__init__(subcon)  # type: ignore

    def _decode(self, obj: Tuple[bytes, Any], context, path) -> Optional[Event]:
        disc = obj[0]
        try:
            event_name = self.discriminators[disc]
        except KeyError:
            return None
        return Event(data=obj[1], name=event_name)
