import csv
from Utilities.audio_utility import to_wav
from base_component import BaseComponent
import base_keys
from Utilities import environment_utility
import numpy as np

import scipy

import tensorflow as tf
import tensorflow_hub as hub

_YAMNET_MODEL = environment_utility.get_env_string("WHISPER_YAMNET")
_DEFAULT_SAMPLE_RATE = environment_utility.get_env_int("WHISPER_SAMPLE_RATE")

class BackgroundAudioClassifier(BaseComponent):
    """
    Receives audio_data from audio_widget and sends the audio context labels to the next component

    audio_data: Audio Data in BytesIO format
    audio_context: Audio Context labels in numpy array (e.g. ["Speech", "Music", "Silence", "Small Room"])
    """
    
    def __init__(self, name):
        super().__init__(name)
        super().set_component_status(base_keys.COMPONENT_NOT_STARTED_STATUS)
        self.model = _YAMNET_MODEL
        self.max_results = 4

        self.init_model()

        # get list of labels from class map
        self.labels = self.get_classes(self.clf.class_map_path().numpy())

    def init_model(self):
        '''
        initialize model
        '''
        # load model
        self.clf = hub.load(self.model)

    def check_rate(self, original_rate, waveform, desired_rate=_DEFAULT_SAMPLE_RATE):
        '''
        resample waveform if required
        '''
        if original_rate != desired_rate:
            desired_len = int(round(float(len(waveform)) / desired_rate))

            waveform = scipy.signal.resample(waveform, desired_len)

        return desired_rate, waveform

    def get_classes(self, class_map):
        '''
        get list of labels corresponding to score vector
        '''
        labels = []

        with tf.io.gfile.GFile(class_map) as f:
            reader = csv.DictReader(f)

            for row in reader:
                labels.append(row["display_name"])

        return labels

    def get_context(self, raw_data):
        '''
        get context of audio
        '''
        # read wav
        '''
        sr, wav_data = wavfile.read(f, 'rb')
        sr, wav_data = self.check_rate(sr, wav_data)
        '''
        if super().get_component_status() != base_keys.COMPONENT_IS_RUNNING_STATUS:
            super().set_component_status(base_keys.COMPONENT_IS_RUNNING_STATUS)
        
        # seek(0) is needed because transcribe.py writes the BytesIO audio data to temp file which sets the internal file pointer to the end of the file
        # this helps to reset the file pointer back to the beginning
        raw_data[base_keys.AUDIO_DATA].seek(0)
        wav_data = to_wav(raw_data[base_keys.AUDIO_DATA], _DEFAULT_SAMPLE_RATE)

        waveform = wav_data / tf.int16.max

        # run model
        scores, _, _ = self.clf(waveform)

        # get top k classes
        result = np.array(self.labels)[np.argsort(
            scores.numpy().mean(axis=0))[:: -1][: self.max_results]]

        super().send_to_component(audio_context=result)
