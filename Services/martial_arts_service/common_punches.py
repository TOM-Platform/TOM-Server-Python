from DataFormat.ProtoFiles.MartialArts import ma_punch_type_pb2, ma_punch_data_pb2
from .martial_arts_const import LEFT_HAND, RIGHT_HAND

# Define constants for PunchData objects
LEFT_JAB = ma_punch_data_pb2.PunchData(hand=LEFT_HAND, punch_type=ma_punch_type_pb2.PunchType.LEFT_JAB, name="Left Jab")
RIGHT_JAB = ma_punch_data_pb2.PunchData(hand=RIGHT_HAND, punch_type=ma_punch_type_pb2.PunchType.RIGHT_JAB,
                                        name="Right Jab")
LEFT_CROSS = ma_punch_data_pb2.PunchData(hand=LEFT_HAND, punch_type=ma_punch_type_pb2.PunchType.LEFT_CROSS,
                                         name="Left Cross")
RIGHT_CROSS = ma_punch_data_pb2.PunchData(hand=RIGHT_HAND, punch_type=ma_punch_type_pb2.PunchType.RIGHT_CROSS,
                                          name="Right Cross")
