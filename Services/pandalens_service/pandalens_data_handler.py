import asyncio

from APIs.google_maps.google_maps_api import get_current_location_google, reverse_geocode_google
from DataFormat.ProtoFiles.PandaLens import (pandalens_question_pb2,
                                             pandalens_response_pb2,
                                             pandalens_moments_pb2,
                                             pandalens_error_pb2,
                                             pandalens_reset_pb2)


##### Build Data (Protobuf) ######

def build_pandalens_question(image_of_interest, content, speech, icon, show_image):
    pandalens_data_proto = pandalens_question_pb2.PandaLensQuestion(
        image=image_of_interest,
        content=content,
        speech=speech,
        icon=icon,
        show_image=show_image
    )

    return pandalens_data_proto


def build_pandalens_response(content, speech):
    pandalens_data_proto = pandalens_response_pb2.PandaLensResponse(
        content=content,
        speech=speech,
    )

    return pandalens_data_proto


def build_pandalens_moments(title, moments, speech):
    pandalens_data_proto = pandalens_moments_pb2.PandaLensMoments(
        title=title,
        moments=moments,
        speech=speech,
    )

    return pandalens_data_proto


def build_pandalens_error(error, text="", audio="", duration_seconds=5):
    pandalens_data_proto = pandalens_error_pb2.PandaLensError(
        error=error,
        text_description=text,
        audio_description=audio,
        display_seconds=duration_seconds
    )

    return pandalens_data_proto


def build_pandalens_reset(message, audio="", duration_seconds=0):
    pandalens_data_proto = pandalens_reset_pb2.PandaLensReset(
        message=message,
        audio=audio,
        duration_seconds=duration_seconds
    )

    return pandalens_data_proto


##### Get Current Location ######

def get_current_location() -> dict:
    """
    Get current location using Google Maps API
    :return: dict with keys 'latitude', 'longitude', 'address'
    """

    async def _get_location_and_address():

        additional_payload = {
            "considerIp": True
        }

        try:
            location = await get_current_location_google(additional_payload)
            address = reverse_geocode_google(location['lat'], location['lng'])
            return {
                "latitude": location['lat'],
                "longitude": location['lng'],
                "address": address
            }
        except Exception:
            # Log or handle as needed
            return {
                "latitude": "",
                "longitude": "",
                "address": "Not Found"
            }

    return asyncio.run(_get_location_and_address())
