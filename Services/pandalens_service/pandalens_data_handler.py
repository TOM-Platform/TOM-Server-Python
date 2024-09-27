from DataFormat.ProtoFiles.PandaLens import (pandalens_response_pb2,
                                             pandalens_question_pb2,
                                             pandalens_moments_pb2,
                                             pandalens_error_pb2,
                                             pandalens_reset_pb2)


##### Build Data (Protobuf) ######

def build_pandalens_question(image_of_interest, content, speech):
    pandalens_data_proto = pandalens_question_pb2.PandaLensQuestion(
        image=image_of_interest,
        content=content,
        speech=speech,
    )

    return pandalens_data_proto


def build_pandalens_response(content, speech):
    pandalens_data_proto = pandalens_response_pb2.PandaLensResponse(
        content=content,
        speech=speech,
    )

    return pandalens_data_proto


def build_pandalens_moments(moments):
    pandalens_data_proto = pandalens_moments_pb2.PandaLensMoments(
        moments=moments
    )

    return pandalens_data_proto


def build_pandalens_error(error):
    pandalens_data_proto = pandalens_error_pb2.PandaLensError(
        error=error
    )

    return pandalens_data_proto


def build_pandalens_reset(message):
    pandalens_data_proto = pandalens_reset_pb2.PandaLensReset(
        message=message
    )

    return pandalens_data_proto
