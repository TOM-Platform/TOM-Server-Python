from DataFormat.ProtoFiles.Template import template_data_pb2


#### Build Data (Protobuf) ######

def build_template_data(text: str, image: bytes, audio_path: str) -> template_data_pb2.TemplateData:
    template_data_proto = template_data_pb2.TemplateData(
        text=text,
        image=image,
        audio_path=audio_path,
    )

    return template_data_proto
