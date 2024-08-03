from DataFormat.ProtoFiles.Common import speech_data_pb2
from .voice_commands import (
    SET_DURATION_INPUT,
    SET_INTERVAL_INPUT,
    SET_DURATION_CMD,
    SET_INTERVAL_CMD,
)
from .martial_arts_keys import SPEECH_INPUT_DATA
import re


class MartialArtsSpeechService:
    digit_pattern = r'(\d+(\.\d)?)'

    def __init__(self, martial_arts_service) -> None:
        self.martial_arts_service = martial_arts_service

    def handle_speech_input(self, speech_input_data) -> None:
        parsed_data = self.parse_speech_input(speech_input_data.lower())
        if not parsed_data or len(parsed_data) != 2:
            return

        # join with semicolon
        output = ";".join(parsed_data)
        speech_data_pb2.SpeechData(voice=output)
        self.martial_arts_service.send_to_component(
            websocket_message=speech_data_pb2.SpeechData(voice=output),
            websocket_datatype=SPEECH_INPUT_DATA)

    def parse_speech_input(self, speech_input_data) -> list:
        if SET_DURATION_INPUT in speech_input_data:
            idx = speech_input_data.find(SET_DURATION_INPUT)
            duration = self.parse_number(
                speech_input_data[idx + len(SET_DURATION_INPUT):])
            return [SET_DURATION_CMD, str(duration)]

        if SET_INTERVAL_INPUT in speech_input_data:
            idx = speech_input_data.find(SET_INTERVAL_INPUT)
            interval = self.parse_number(
                speech_input_data[idx + len(SET_INTERVAL_INPUT):])
            return [SET_INTERVAL_CMD, str(interval)]
        return []

    def parse_number(self, string) -> str:
        matches = re.findall(self.digit_pattern, string)
        if not matches or len(matches) == 0:
            return None
        return matches[0][0]
