from DataFormat.ProtoFiles.Aiget import aiget_data_pb2


#### Build Data (Protobuf) ######

def build_aiget_data(text: str, image: bytes, audio_text: str, display_duration: int) -> aiget_data_pb2.AigetData:
    aiget_data_proto = aiget_data_pb2.AigetData(
        text=text,
        image=image,
        audio_text=audio_text,
        display_duration=display_duration
    )

    return aiget_data_proto
