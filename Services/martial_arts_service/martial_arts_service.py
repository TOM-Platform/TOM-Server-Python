from base_keys import ORIGIN_KEY, WEBSOCKET_WIDGET, WEBSOCKET_MESSAGE, WEBSOCKET_DATATYPE
from base_component import BaseComponent
from .martial_arts_sequence_service import MartialArtsSequenceService
from .martial_arts_coach_service import MartialArtsCoachService
from .martial_arts_config_service import MartialArtsConfigService
from .martial_arts_metrics_service import MartialArtsMetricsService
from .martial_arts_speech_service import MartialArtsSpeechService
from .martial_arts_keys import (
    MA_REQUEST_SEQUENCE_DATA,
    MA_METRICS_DATA,
    MA_UPDATE_SESSION_CONFIG_COMMAND,
    MA_BEGIN_SESSION_COMMAND,
    MA_END_SESSION_COMMAND,
    MA_REQUEST_CONFIG_DATA,
    SPEECH_INPUT_DATA
)
from DataFormat import datatypes_helper


class MartialArtsService(BaseComponent):
    def __init__(self, name) -> None:
        super().__init__(name)
        # Services
        self.ma_sequence_service = MartialArtsSequenceService(
            martial_arts_service=self)
        self.ma_coach_service = MartialArtsCoachService(
            martial_arts_service=self)
        self.ma_config_service = MartialArtsConfigService(
            martial_arts_service=self)
        self.ma_metrics_service = MartialArtsMetricsService(
            martial_arts_service=self)
        self.ma_speech_service = MartialArtsSpeechService(
            martial_arts_service=self)
        self.is_running = False

    def run(self, raw_data) -> None:
        if not self.is_running:
            self.is_running = True

        origin = raw_data[ORIGIN_KEY]

        if origin == WEBSOCKET_WIDGET:
            print("raw_data", raw_data)
            datatype = raw_data[WEBSOCKET_DATATYPE]
            data = raw_data[WEBSOCKET_MESSAGE]

            # FIXME: remove this conversion once all components are using protobuf and use object values?
            data = datatypes_helper.convert_json_to_protobuf(datatype, data)
            self._handle_websocket_data(datatype, data)

    def _handle_websocket_data(self, socket_data_type, decoded_data) -> None:
        if socket_data_type == MA_REQUEST_SEQUENCE_DATA:
            # Generate the next sequence
            self.ma_sequence_service.generate_next_sequence()
            return
        elif socket_data_type == MA_METRICS_DATA:
            # Generate live feedback
            live_feedback = self.ma_coach_service.analyse_live_data(
                decoded_data)
            if live_feedback:
                self.ma_coach_service.send_live_feedback(live_feedback)

            feedback_category = self.ma_coach_service.categorize_feedback(
                live_feedback)
            # Record metrics
            self.ma_metrics_service.record_metrics(
                decoded_data, feedback_category)
            return
        elif socket_data_type == MA_UPDATE_SESSION_CONFIG_COMMAND:
            # Save the session config in DB
            self.ma_config_service.save_config(decoded_data)
            return
        elif socket_data_type == MA_BEGIN_SESSION_COMMAND:
            self.ma_metrics_service.reset()
            return
        elif socket_data_type == MA_END_SESSION_COMMAND:
            # Send post-session metrics
            self.ma_metrics_service.process_save_metrics(decoded_data)
            return
        elif socket_data_type == MA_REQUEST_CONFIG_DATA:
            # TODO: Fix issues with loading config
            self.ma_config_service.send_config()
            return
        elif socket_data_type == SPEECH_INPUT_DATA:
            voice = decoded_data.voice
            self.ma_speech_service.handle_speech_input(voice)
            return
        else:
            # Handle unknown data type
            return
