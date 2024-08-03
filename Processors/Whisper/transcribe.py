# reference: https://github.com/Synteraction-Lab/PANDALens/blob/main/src/Module/Audio/live_transcriber.py
from tempfile import NamedTemporaryFile

import torch
import base_keys
from base_component import BaseComponent

import whisper
from Utilities import environment_utility, logging_utility

_WHISPER_TRANSCRIPTION_MODEL = environment_utility.get_env_string("WHISPER_TRANSCRIPTION_MODEL")

_logger = logging_utility.setup_logger(__name__)


class Transcriber(BaseComponent):
    def __init__(self, name):
        super().__init__(name)
        super().set_component_status(base_keys.COMPONENT_NOT_STARTED_STATUS)
        self.temp_file = NamedTemporaryFile().name
        self.transcription_model = _WHISPER_TRANSCRIPTION_MODEL
        self.audio_model = whisper.load_model(self.transcription_model)
        
    def to_text(self, raw_data):
        '''
        Sends one key-value data pair to the next component:
        1. audio_transcript: The transcribed text from the audio data in string format
        '''
        if (super().get_component_status() != base_keys.COMPONENT_IS_RUNNING_STATUS):
            super().set_component_status(base_keys.COMPONENT_IS_RUNNING_STATUS)
        wav_data = raw_data[base_keys.AUDIO_DATA]
        with open(self.temp_file, "w+b") as f:
            f.write(wav_data.read())

        # no_speech_threshold: The threshold for the probability of the presence of no speech in the audio. If no speech is detected, the model will return an empty string.
        # logprob_threshold: ""if the average log probability over sampled tokens is below this value, treat as failed"" from source code
        result = self.audio_model.transcribe(self.temp_file, fp16=torch.cuda.is_available(),
                                                                   no_speech_threshold=0.2,
                                                                   logprob_threshold=None, )
        text = result['text'].strip()

        _logger.info("\nTranscribed sentence: {text}", text = text)
        super().send_to_component(audio_transcript=text)
