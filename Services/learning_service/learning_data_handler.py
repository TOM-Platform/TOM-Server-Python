'''
This file contains the functions for the learning service.
'''
from DataFormat.ProtoFiles.Learning import learning_data_pb2
from DataFormat.ProtoFiles.Common import highlight_point_data_pb2


# Build Data (Protobuf)


def build_highlight_point_data(x, y, z, details):
    highlight_point_data_proto = highlight_point_data_pb2.HighlightPointData(
        world_x=x,
        world_y=y,
        world_z=z,
        details=details,
    )

    return highlight_point_data_proto


def build_learning_data(instruction, detail, speech):
    learning_data_proto = learning_data_pb2.LearningData(
        instruction=instruction,
        detail=detail,
        speech=speech,
    )

    return learning_data_proto
