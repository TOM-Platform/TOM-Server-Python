# common_sequences.py
from DataFormat.ProtoFiles.MartialArts import ma_sequence_data_pb2
from .common_punches import LEFT_JAB, RIGHT_CROSS, RIGHT_JAB, LEFT_CROSS

# Define constants for common sequences
SEQUENCE_1 = ma_sequence_data_pb2.SequenceData(
    punches=[LEFT_JAB, RIGHT_CROSS, LEFT_JAB])

SEQUENCE_2 = ma_sequence_data_pb2.SequenceData(
    punches=[RIGHT_JAB, LEFT_CROSS, RIGHT_JAB])
