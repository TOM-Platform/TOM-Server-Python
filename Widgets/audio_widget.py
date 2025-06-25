import io
from datetime import datetime, timedelta
from multiprocessing import Queue

import speech_recognition as sr

import base_keys
from Utilities import environment_utility, logging_utility, time_utility
from base_component import BaseComponent

# Variables from the environment

_MIC = environment_utility.get_env_string("AUDIO_MIC")
""" Microphone name """

_MIC_SAMPLE_RATE = environment_utility.get_env_int("AUDIO_MIC_SAMPLE_RATE")
""" Sampling rate (Hz) for audio recording """

_SPEECH_RECOGNITION_WINDOW = environment_utility.get_env_float("SPEECH_RECOGNITION_WINDOW")
""" Max length (seconds) for speech recognition per phrase"""

_SPEECH_RECOGNITION_PHRASE_THRESHOLD = environment_utility.get_env_float("SPEECH_RECOGNITION_PHRASE_THRESHOLD")
""" Duration threshold (seconds) to consider a phrase complete """

_SPEECH_RECOGNITION_ENERGY_THRESHOLD = environment_utility.get_env_float("SPEECH_RECOGNITION_ENERGY_THRESHOLD")
""" Minimum audio energy for speech detection """

_PAUSE_THRESHOLD = environment_utility.get_env_float("SPEECH_PAUSE_THRESHOLD")
""" Pause duration to detect end of speech (seconds) """

_SPEECH_RECOGNITION_DYNAMIC_ENERGY_THRESHOLD = False
""" Disable dynamic adjustment of energy threshold (set False for stable recording) """

_logger = logging_utility.setup_logger(__name__)


class AudioWidget(BaseComponent):
    """
    Sends the audio_data received through the microphone / input device to the next component

    audio_data: Audio Data in wav format
    """

    def __init__(self, name) -> None:
        super().__init__(name)
        super().set_component_status(base_keys.COMPONENT_NOT_STARTED_STATUS)

        self.src = None  # Audio input source (microphone), initialized later
        self.data_queue = Queue()  # Thread-safe queue to store audio data chunks
        self.phrase_time = None  # Timestamp of the last processed audio data chunk
        self.last_sample = io.BytesIO()  # Buffer holding audio data bytes
        self.phrase_complete = True  # Indicates whether the current speech phrase has completed
        self.current_time = None  # Indicates whether the current speech phrase has completed

        # in seconds
        self.recognition_window = _SPEECH_RECOGNITION_WINDOW
        self.phrase_threshold = _SPEECH_RECOGNITION_PHRASE_THRESHOLD

        self.sample_rate = _MIC_SAMPLE_RATE

        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = _SPEECH_RECOGNITION_ENERGY_THRESHOLD
        # lowers energy threshold dramatically to a point where recording never stops
        self.recognizer.dynamic_energy_threshold = _SPEECH_RECOGNITION_DYNAMIC_ENERGY_THRESHOLD
        self.recognizer.pause_threshold = _PAUSE_THRESHOLD

        self.listen_delay = 0.05
        """ Sleep duration (seconds) between listening cycles to reduce CPU usage """

    def start(self):
        if super().get_component_status() != base_keys.COMPONENT_IS_RUNNING_STATUS:
            super().set_component_status(base_keys.COMPONENT_IS_RUNNING_STATUS)

        try:
            self.__check_source(_MIC)
        except Exception:
            _logger.exception("Failed the audio source validation/setup.")

        if not self.src:
            _logger.error("No valid audio source detected. Exiting audio widget.")
            super().set_component_status(base_keys.COMPONENT_IS_STOPPED_STATUS)
            return

        with self.src as source:
            try:
                self.recognizer.adjust_for_ambient_noise(source)
                _logger.info("Ambient noise level adjusted successfully.")
            except Exception:
                _logger.exception("Failed to adjust ambient noise.")
                super().set_component_status(base_keys.COMPONENT_IS_STOPPED_STATUS)
                return

        # background thread to pass raw audio bytes
        self.recognizer.listen_in_background(self.src, self.record_callback, phrase_time_limit=self.recognition_window)
        _logger.debug("AudioWidget background listening thread started.")

        while super().get_component_status() == base_keys.COMPONENT_IS_RUNNING_STATUS:
            try:
                self._listen_and_send_audio()
                time_utility.sleep_seconds(self.listen_delay)
            except Exception:
                _logger.exception("An error occurred while listening and sending audio data")

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
        """
        threaded callback function to store audio data
        audio: AudioData containing the recorded bytes
        """
        try:
            # get bytes and send to next component(s)
            data = audio.get_raw_data()
            self.data_queue.put(data)
        except Exception:
            _logger.exception("Failed to process audio in record_callback")

    def __check_phrase(self):
        """
        clear current working audio buffer
        """
        self.current_time = datetime.utcnow()

        # check phrase complete threshold
        if self.phrase_time and self.current_time - self.phrase_time > timedelta(seconds=self.phrase_threshold):
            _logger.debug("Phrase complete. Clearing the buffer.")
            self.last_sample = io.BytesIO()
            self.phrase_complete = True

    def __check_source(self, mic_name):
        """
        validate audio source
        """

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
            _logger.info("Microphone '{name}' selected (index: {mic_index}).", name=mic_name, mic_index=mic_index)
        else:
            _logger.error("Microphone '{mic_name}' not found among available devices.", mic_name=mic_name)
            _logger.warning("Selecting default microphone.")
            self.src = sr.Microphone(sample_rate=self.sample_rate)

    def stop(self):
        """
        Gracefully stops the audio widget by setting the shutdown event
        """
        super().set_component_status(base_keys.COMPONENT_IS_STOPPED_STATUS)
        _logger.info("AudioWidget shutdown event set. Stopping audio processing.")
