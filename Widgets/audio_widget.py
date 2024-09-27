import io
from datetime import datetime, timedelta
from multiprocessing import Queue
from sys import platform

import speech_recognition as sr

import base_keys
from Utilities import environment_utility, logging_utility, time_utility
from base_component import BaseComponent

_ENV_MIC = environment_utility.get_env_string("WHISPER_MIC")
_WHISPER_SAMPLE_RATE = environment_utility.get_env_int("WHISPER_SAMPLE_RATE")
_WHISPER_WINDOW = environment_utility.get_env_float("WHISPER_WINDOW")
_WHISPER_PHRASE_THRESHOLD = environment_utility.get_env_float("WHISPER_PHRASE_THRESHOLD")
_WHISPER_ENERGY_THRESHOLD = environment_utility.get_env_float("WHISPER_ENERGY_THRESHOLD")

_WHISPER_DYNAMIC_ENERGY_THRESHOLD = False
_WHISPER_PHRASE_COMPLETE = True
_WHISPER_SRC = 0

_logger = logging_utility.setup_logger(__name__)


class AudioWidget(BaseComponent):
    """
    Sends the audio_data received through the microphone / input device to the next component

    audio_data: Audio Data in wav format
    """

    def __init__(self, name) -> None:
        super().__init__(name)
        super().set_component_status(base_keys.COMPONENT_NOT_STARTED_STATUS)

        self.src = _WHISPER_SRC
        self.data_queue = Queue()
        self.phrase_time = None  # timestamp of last retrieved from queue
        self.last_sample = bytes()  # current raw sample
        self.phrase_complete = _WHISPER_PHRASE_COMPLETE
        self.now = None

        # in sec
        self.window = _WHISPER_WINDOW
        self.phrase_threshold = _WHISPER_PHRASE_THRESHOLD

        self.sample_rate = _WHISPER_SAMPLE_RATE

        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = _WHISPER_ENERGY_THRESHOLD
        # lowers energy threshold dramatically to a point where recording never stops
        self.recognizer.dynamic_energy_threshold = _WHISPER_DYNAMIC_ENERGY_THRESHOLD
        self.recognizer.pause_threshold = 3
        # needed to ensure that the audio widget does not run into performance issues
        self.listen_delay = 0.05

    def start(self):
        if super().get_component_status() != base_keys.COMPONENT_IS_RUNNING_STATUS:
            super().set_component_status(base_keys.COMPONENT_IS_RUNNING_STATUS)
        self.__check_source()

        with self.src:
            self.recognizer.adjust_for_ambient_noise(self.src)

        # background thread to pass raw audio bytes
        self.recognizer.listen_in_background(
            self.src, self.record_callback, phrase_time_limit=self.window)

        while True:
            if not self.data_queue.empty():
                self.phrase_complete = False

                self.__check_phrase()

                # when new data received
                self.phrase_time = self.now

                # concat current data with latest
                while not self.data_queue.empty():
                    data = self.data_queue.get()
                    self.last_sample += data

                raw_data = sr.AudioData(
                    self.last_sample, self.sample_rate, self.src.SAMPLE_WIDTH)
                wav_data = io.BytesIO(raw_data.get_wav_data())

                _logger.info("\nSending audio data to processors")
                super().send_to_component(audio_data=wav_data)

            time_utility.sleep_seconds(self.listen_delay)

    def record_callback(self, _, audio):
        '''
        threaded callback function to store audio data
        audio: AudioData containing the recorded bytes
        '''
        # get bytes and send to next component(s)
        data = audio.get_raw_data()
        self.data_queue.put(data)

    def __check_phrase(self):
        '''
        clear current working audio buffer
        '''
        self.now = datetime.utcnow()

        # check phrase complete threshold
        if self.phrase_time and self.now - self.phrase_time > timedelta(
                seconds=self.phrase_threshold):
            self.last_sample = bytes()
            self.phrase_complete = True

    def __check_source(self):
        '''
        validate audio source
        '''
        if not self.src:
            if "linux" in platform:
                mic = _ENV_MIC

                if not mic or mic == "list":
                    _logger.info("available devices: ")
                    for _, name in enumerate(sr.Microphone.list_microphone_names()):
                        _logger.info("{name} found", name=name)
                    return

                if mic in sr.Microphone.list_microphone_names():
                    self.src = sr.Microphone(sample_rate=self.sample_rate,
                                             device_index=sr.Microphone.list_microphone_names().index(mic))
            else:
                self.src = sr.Microphone(sample_rate=self.sample_rate)
