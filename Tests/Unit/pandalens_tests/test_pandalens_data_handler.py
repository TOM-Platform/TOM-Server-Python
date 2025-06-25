from DataFormat.ProtoFiles.PandaLens import (pandalens_reset_pb2, pandalens_response_pb2, pandalens_error_pb2,
                                             pandalens_question_pb2, pandalens_moments_pb2)
from Services.pandalens_service.pandalens_data_handler import (build_pandalens_question,
                                                               build_pandalens_moments,
                                                               build_pandalens_error,
                                                               build_pandalens_reset)


def test_build_pandalens_question():
    # Define test data
    image_of_interest = "test_image"
    content = "test_content"
    speech = "test_speech"
    icon = "test_icon"
    show_image = True

    # Call the function
    result = build_pandalens_question(image_of_interest, content, speech, icon, show_image)

    # Verify the result
    assert isinstance(result, pandalens_question_pb2.PandaLensQuestion)
    assert result.image == image_of_interest
    assert result.content == content
    assert result.speech == speech
    assert result.icon == icon
    assert result.show_image == show_image



def test_build_pandalens_response():
    # Define test data
    content = "test_content"
    speech = "test_speech"

    # Call the function
    result = build_pandalens_response(content, speech)

    # Verify the result
    assert isinstance(result, pandalens_response_pb2.PandaLensResponse)
    assert result.content == content
    assert result.speech == speech


def test_build_pandalens_moments():
    # Define test data
    title = "test_title"
    moments = ["moment1", "moment2"]
    speech = "test_speech"

    # Call the function
    result = build_pandalens_moments(title, moments, speech)

    # Verify the result
    assert isinstance(result, pandalens_moments_pb2.PandaLensMoments)
    assert result.title == title
    assert result.moments == moments
    assert result.speech == speech


def test_build_pandalens_error():
    # Define test data
    error = "test_error"
    text = "test_text"
    audio = "test_audio"
    duration = 10

    # Call the function

    result = build_pandalens_error(error, text, audio, duration)

    # Verify the result
    assert isinstance(result, pandalens_error_pb2.PandaLensError)
    assert result.error == error
    assert result.text_description == text
    assert result.audio_description == audio
    assert result.display_seconds == duration


def test_build_pandalens_reset():
    # Call the function
    message = ""
    audio = "test_audio"
    duration = 5
    result = build_pandalens_reset(message, audio, duration)

    # Verify the result (assuming no fields to check, just ensure it's created)
    assert isinstance(result, pandalens_reset_pb2.PandaLensReset)
    assert result.message == message
    assert result.audio == audio
    assert result.duration_seconds == duration
