import io
from datetime import datetime, timedelta
from multiprocessing import Queue

import speech_recognition as sr

import base_keys
from Utilities import environment_utility, logging_utility, time_utility
from base_component import BaseComponent

_MIC = environment_utility.get_env_string("AUDIO_MIC")
_MIC_SAMPLE_RATE = environment_utility.get_env_int("AUDIO_MIC_SAMPLE_RATE")
_SPEECH_RECOGNITION_WINDOW = environment_utility.get_env_float("SPEECH_RECOGNITION_WINDOW")
_SPEECH_RECOGNITION_PHRASE_THRESHOLD = environment_utility.get_env_float("SPEECH_RECOGNITION_PHRASE_THRESHOLD")
_SPEECH_RECOGNITION_ENERGY_THRESHOLD = environment_utility.get_env_float("SPEECH_RECOGNITION_ENERGY_THRESHOLD")

_SPEECH_RECOGNITION_DYNAMIC_ENERGY_THRESHOLD = False

_PAUSE_THRESHOLD = 3

_logger = logging_utility.setup_logger(__name__)


class AudioWidget(BaseComponent):
    """
    Sends the audio_data received through the microphone / input device to the next component

    audio_data: Audio Data in wav format
    """

    def __init__(self, name) -> None:
        super().__init__(name)
        super().set_component_status(base_keys.COMPONENT_NOT_STARTED_STATUS)

        self.src = None  # Microphone source, initialized later
        self.data_queue = Queue()
        self.phrase_time = None  # timestamp of last retrieved from queue
        self.last_sample = io.BytesIO()  # Efficient buffer to hold audio data
        self.phrase_complete = True
        self.current_time = None

        # in sec
        self.recognition_window = _SPEECH_RECOGNITION_WINDOW
        self.phrase_threshold = _SPEECH_RECOGNITION_PHRASE_THRESHOLD

        self.sample_rate = _MIC_SAMPLE_RATE

        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = _SPEECH_RECOGNITION_ENERGY_THRESHOLD
        # lowers energy threshold dramatically to a point where recording never stops
        self.recognizer.dynamic_energy_threshold = _SPEECH_RECOGNITION_DYNAMIC_ENERGY_THRESHOLD
        self.recognizer.pause_threshold = _PAUSE_THRESHOLD
        # needed to ensure that the audio widget does not run into performance issues
        self.listen_delay = 0.05

    def start(self):
        if super().get_component_status() != base_keys.COMPONENT_IS_RUNNING_STATUS:
            super().set_component_status(base_keys.COMPONENT_IS_RUNNING_STATUS)

        try:
            self.__check_source(_MIC)
        except Exception:
            _logger.exception("Error while checking/setting up the audio source")

        if not self.src:
            _logger.error("No valid audio source found. Exiting start method.")
            super().set_component_status(base_keys.COMPONENT_IS_STOPPED_STATUS)
            return

        with self.src as source:
            try:
                self.recognizer.adjust_for_ambient_noise(source)
                _logger.info("Adjusted for ambient noise using microphone source.")
            except Exception:
                _logger.exception("Failed to adjust for ambient noise")
                super().set_component_status(base_keys.COMPONENT_IS_STOPPED_STATUS)
                return

        # background thread to pass raw audio bytes
        self.recognizer.listen_in_background(self.src, self.record_callback, phrase_time_limit=self.recognition_window)
        _logger.debug("Listening to AudioWidget")

        while super().get_component_status() == base_keys.COMPONENT_IS_RUNNING_STATUS:
            try:
                self._listen_and_send_audio()
                time_utility.sleep_seconds(self.listen_delay)
            except Exception as e:
                _logger.debug("An error occurred while listening and sending audio data: {e}", e=e)

    def _listen_and_send_audio(self):
        if not self.data_queue.empty():
            self.phrase_complete = False

            self.__check_phrase()

            # when new data received
            self.phrase_time = self.current_time

            # concat current data with latest
            while not self.data_queue.empty():
                data = self.data_queue.get()
                self.last_sample.write(data)

            # Resetting pointer of BytesIO buffer to the beginning
            self.last_sample.seek(0)
            raw_data = sr.AudioData(self.last_sample.read(), self.src.SAMPLE_RATE, self.src.SAMPLE_WIDTH)
            wav_data = io.BytesIO(raw_data.get_wav_data())

            _logger.debug("\nSending audio data to processors")
            super().send_to_component(audio_data=wav_data)

            # Clear last_sample buffer for the next data
            self.last_sample = io.BytesIO()

    def record_callback(self, _, audio):
        '''
        threaded callback function to store audio data
        audio: AudioData containing the recorded bytes
        '''
        try:
            # get bytes and send to next component(s)
            data = audio.get_raw_data()
            self.data_queue.put(data)
        except Exception:
            _logger.exception("Failed to process audio in record_callback")

    def __check_phrase(self):
        '''
        clear current working audio buffer
        '''
        self.current_time = datetime.utcnow()

        # check phrase complete threshold
        if self.phrase_time and self.current_time - self.phrase_time > timedelta(seconds=self.phrase_threshold):
            _logger.debug("Phrase complete. Clearing the buffer.")
            self.last_sample = io.BytesIO()
            self.phrase_complete = True

    def __check_source(self, mic_name):
        '''
        validate audio source
        '''

        # List all available microphones
        available_mics = sr.Microphone.list_microphone_names()

        # If still no mic_name, list the available devices
        if not mic_name or mic_name == "list" or mic_name not in available_mics:
            _logger.debug("Available audio devices: ")
            for _, name in enumerate(available_mics):
                _logger.debug("{name} found", name=name)

        # Check if the provided microphone name exists in the available microphones
        if mic_name in available_mics:
            mic_index = available_mics.index(mic_name)
            self.src = sr.Microphone(sample_rate=self.sample_rate, device_index=mic_index)
            _logger.info(f"Microphone '{mic_name}' selected (index: {mic_index}).")
        else:
            _logger.error("Microphone '{mic_name}' not found among available devices.", mic_name=mic_name)
            _logger.warn("Selecting default microphone.")
            self.src = sr.Microphone(sample_rate=self.sample_rate)

    def stop(self):
        '''
        Gracefully stops the audio widget by setting the shutdown event
        '''
        super().set_component_status(base_keys.COMPONENT_IS_STOPPED_STATUS)
        _logger.info("AudioWidget shutdown event set. Stopping audio processing.")
