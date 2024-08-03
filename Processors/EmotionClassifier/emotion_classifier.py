from Utilities import environment_utility, logging_utility
from base_component import BaseComponent
from transformers import pipeline
import base_keys

_EMOTION_MODEL_FROM_TEXT = environment_utility.get_env_string("EMOTION_MODEL_FROM_TEXT")

_logger = logging_utility.setup_logger(__name__)

class EmotionClassifier(BaseComponent):
    """
    Receives audio_transcription from transcribe.py and sends emotion scores (if any) to the next component

    emotion_scores: Emotion scores of the transcribed text in dictionary format (e.g. {'joy': 0.99, 'surprise': 0.01}), can be None if no emotion detected
    """
    def __init__(self, name):
        super().__init__(name)
        super().set_component_status(base_keys.COMPONENT_NOT_STARTED_STATUS)
        self.emotion_model = _EMOTION_MODEL_FROM_TEXT
        self.emotion_classifier = pipeline("text-classification", model=self.emotion_model, top_k=None)
        self.emotion_scores = None

    def analyse_emotion(self, raw_data):
        '''
        Receives raw_data from transcribe.py which contains the transcribed text from the audio data in string format under the key 'audio_transcription'
        Sends one key-value data pair to the next component:
        1. emotion_scores: The emotion scores of the transcribed text (if any) in dictionary format (e.g. {'joy': 0.99, 'surprise': 0.01}), can be empty dict if no emotion detected
        '''
        text = raw_data[base_keys.AUDIO_TRANSCRIPTION_DATA]
        if text != "":
            # Flattening the data
            data = self.emotion_classifier(text)[0]

            # Create a dictionary to store scores
            score_dict = {}

            # Iterating over the data and storing scores in dictionary
            for d in data:
                score_dict[d['label']] = d['score']

            self.emotion_scores = score_dict
            _logger.info("\nSentence: {text}\nJoy score: {joy_score} Surprise score: {surprise_score}", text = text, joy_score = self.emotion_scores['joy'], surprise_score = self.emotion_scores['surprise'])
        else:
            self.emotion_scores = {}
            _logger.info("\nSentence: {text}\nNo emotion detected", text = text)
        super().send_to_component(emotion_scores = self.emotion_scores)