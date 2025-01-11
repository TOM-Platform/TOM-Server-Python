from DataFormat.ProtoFiles.PandaLens import (pandalens_reset_pb2)
from Services.pandalens_service.pandalens_data_handler import (build_pandalens_question,
                                                               build_pandalens_response,
                                                               build_pandalens_moments,
                                                               build_pandalens_error,
                                                               build_pandalens_reset)


def test_build_pandalens_question():
    # Define test data
    image_of_interest = "test_image"
    content = "test_content"
    speech = "test_speech"

    # Call the function
    result = build_pandalens_question(image_of_interest, content, speech)

    # Verify the result
    assert result.image == image_of_interest
    assert result.content == content
    assert result.speech == speech


def test_build_pandalens_response():
    # Define test data
    content = "test_content"
    speech = "test_speech"

    # Call the function
    result = build_pandalens_response(content, speech)

    # Verify the result
    assert result.content == content
    assert result.speech == speech


def test_build_pandalens_moments():
    # Define test data
    moments = ["moment1", "moment2"]

    # Call the function
    result = build_pandalens_moments(moments)

    # Verify the result
    assert result.moments == moments


def test_build_pandalens_error():
    # Define test data
    error = "test_error"

    # Call the function
    result = build_pandalens_error(error)

    # Verify the result
    assert result.error == error


def test_build_pandalens_reset():
    # Call the function
    result = build_pandalens_reset("")

    # Verify the result (assuming no fields to check, just ensure it's created)
    assert isinstance(result, pandalens_reset_pb2.PandaLensReset)
