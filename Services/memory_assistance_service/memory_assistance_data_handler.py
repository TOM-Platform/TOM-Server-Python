from DataFormat.ProtoFiles.Common import key_event_type_pb2
from DataFormat.ProtoFiles.Template import template_data_pb2

import base_keys


def get_key_event_type(key_event_data):
    if key_event_data.type == key_event_type_pb2.KeyEventType.PRESS:
        return base_keys.KEYBOARD_EVENT_PRESS

    if key_event_data.type == key_event_type_pb2.KeyEventType.RELEASE:
        return base_keys.KEYBOARD_EVENT_RELEASE

    # Default to press event
    return base_keys.KEYBOARD_EVENT_PRESS


def build_template_data(text: str, image: bytes) -> template_data_pb2.TemplateData:
    template_data_proto = template_data_pb2.TemplateData(
        text=text,
        image=image,
    )

    return template_data_proto
