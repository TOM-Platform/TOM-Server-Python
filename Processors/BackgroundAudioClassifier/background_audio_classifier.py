import base_keys
from Utilities import environment_utility
from Utilities.audio_utility import to_wav
from base_component import BaseComponent
from .audio_classification import AudioClassification, AudioClassificationResult

_DEFAULT_SAMPLE_RATE = environment_utility.get_env_int("AUDIO_MIC_SAMPLE_RATE")


class BackgroundAudioClassifier(BaseComponent):
    """
    Receives audio_data and forwards audio context labels.

    Inputs:
        raw_data: dict containing base_keys.AUDIO_DATA as BytesIO
    Outputs:
        audio_context: list of category names/labels from YamNet (e.g., ["Music", "Speech", "Conversation, ...])
            labels: https://storage.googleapis.com/mediapipe-tasks/audio_classifier/yamnet_label_list.txt
        audio_classification_result: AudioClassificationResult
    """

    def __init__(self, name: str):
        super().__init__(name)
        self.set_component_status(base_keys.COMPONENT_NOT_STARTED_STATUS)
        self.max_results = 4
        self.score_threshold = 0.1

        self.classifier = AudioClassification(
            max_results=self.max_results,
            score_threshold=self.score_threshold
        )

    def get_context(self, raw_data: dict) -> AudioClassificationResult:
        """
        Classify the given raw audio data and send results downstream.
        """

        if super().get_component_status() != base_keys.COMPONENT_IS_RUNNING_STATUS:
            super().set_component_status(base_keys.COMPONENT_IS_RUNNING_STATUS)

        # Reset file pointer to beginning of audio data
        raw_data[base_keys.AUDIO_DATA].seek(0)

        # Convert audio data to WAV format
        wav_data = to_wav(raw_data[base_keys.AUDIO_DATA], _DEFAULT_SAMPLE_RATE)

        # Convert TensorFlow Tensor to NumPy array if needed
        if hasattr(wav_data, 'numpy'):
            # It's a TensorFlow Tensor, convert to numpy
            wav_array = wav_data.numpy()
        else:
            # It's already a numpy array
            wav_array = wav_data

        # Run audio classification using MediaPipe
        classification_result = self.classifier.classify(
            wav_array,
            _DEFAULT_SAMPLE_RATE
        )

        # Extract top category names for backward compatibility
        result = classification_result.get_top_categories(self.max_results)

        # Forward classification result downstream
        super().send_to_component(
            audio_context=result,
            audio_classification_result=classification_result
        )

        return classification_result

    def close(self):
        """Close the component and release resources"""
        super().set_component_status(base_keys.COMPONENT_IS_STOPPED_STATUS)
        self.classifier.close()
