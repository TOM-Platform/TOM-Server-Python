# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: ma_pad_config.proto
# Protobuf Python Version: 4.25.2
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from . import ma_vector_pb2 as ma__vector__pb2

DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x13ma_pad_config.proto\x1a\x0fma_vector.proto\"m\n\tPadConfig\x12\x1b\n\x08position\x18\x01 \x01(\x0b\x32\t.MaVector\x12\x1b\n\x08rotation\x18\x02 \x01(\x0b\x32\t.MaVector\x12\x12\n\nhandedness\x18\x03 \x01(\x05\x12\x12\n\npunch_type\x18\x04 \x01(\x05')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'ma_pad_config_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
  DESCRIPTOR._options = None
  _globals['_PADCONFIG']._serialized_start=40
  _globals['_PADCONFIG']._serialized_end=149
# @@protoc_insertion_point(module_scope)