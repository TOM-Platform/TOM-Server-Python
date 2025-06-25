import numpy as np
from mediapipe.tasks import python
from mediapipe.tasks.python import audio
from mediapipe.tasks.python.components import containers

from Utilities import environment_utility, logging_utility, file_utility

_logger = logging_utility.setup_logger(__name__)

_MODEL_ASSET_PATH = environment_utility.get_env_string("YAMNET_SOUND_CLASSIFICATION_MODEL")
_DEFAULT_SAMPLE_RATE = environment_utility.get_env_int("AUDIO_MIC_SAMPLE_RATE")


class AudioCategory:
    """
    Represents a classified audio category with confidence score.
    """

    def __init__(self, index: int, score: float, category_name: str, display_name: str = ""):
        self.index = index
        self.score = score
        self.category_name = category_name
        self.display_name = display_name

    def to_dict(self) -> dict:
        return {
            "index": self.index,
            "score": self.score,
            "category_name": self.category_name,
            "display_name": self.display_name
        }

    def __repr__(self) -> str:
        return f"AudioCategory(index={self.index}, score={self.score:.4f}, name='{self.category_name}')"


class AudioClassificationResult:
    """
    Stores multiple audio classification results in a picklable format.
    """

    def __init__(self, classifications: list[AudioCategory], timestamp_ms: int = 0):
        self.classifications = classifications
        self.timestamp_ms = timestamp_ms

    @classmethod
    def from_mediapipe(cls, mp_result, max_results: int = 4) -> 'AudioClassificationResult':
        """
        Converts a MediaPipe AudioClassifierResult or list thereof to a picklable format.

        Args:
            mp_result: MediaPipe AudioClassifierResult or list of such results
            max_results: Maximum number of top results to keep

        Returns:
            AudioClassificationResult instance
        """
        # Handle list of results by taking the first element
        if isinstance(mp_result, list):
            if not mp_result:
                return cls([], 0)
            mp_result = mp_result[0]

        audio_categories: list[AudioCategory] = []
        timestamp_ms = 0

        if getattr(mp_result, 'classifications', None):
            classification = mp_result.classifications[0]
            sorted_categories = sorted(
                classification.categories,
                key=lambda x: x.score,
                reverse=True
            )[:max_results]

            for category in sorted_categories:
                audio_categories.append(
                    AudioCategory(
                        index=category.index,
                        score=category.score,
                        category_name=category.category_name or "",
                        display_name=category.display_name or ""
                    )
                )
            timestamp_ms = getattr(classification, 'timestamp_ms', 0)

        return cls(audio_categories, timestamp_ms)

    def get_top_categories(self, max_results: int = 4) -> list[str]:
        """
        Get list of top category names
            - See https://storage.googleapis.com/mediapipe-tasks/audio_classifier/yamnet_label_list.txt

        Args:
            max_results: Maximum number of categories to return

        Returns:
            List of category names
        """
        return [cat.category_name for cat in self.classifications[:max_results]]


class AudioClassification:
    """
    Use MediaPipe for audio classification

    Details: https://ai.google.dev/edge/mediapipe/solutions/audio/audio_classifier
    """

    def __init__(self, max_results: int = 4, score_threshold: float = 0.0):
        model_path = file_utility.get_path_with_filename(
            file_utility.get_project_root(),
            _MODEL_ASSET_PATH
        )
        base_options = python.BaseOptions(model_asset_path=model_path)
        options = audio.AudioClassifierOptions(
            base_options=base_options,
            running_mode=audio.RunningMode.AUDIO_CLIPS,
            max_results=max_results,
            score_threshold=score_threshold
        )
        self.classifier = audio.AudioClassifier.create_from_options(options)
        self.max_results = max_results

    def classify(
            self,
            audio_data: np.ndarray,
            sample_rate: int = _DEFAULT_SAMPLE_RATE
    ) -> AudioClassificationResult:
        """
        Classify audio data.

        Args:
            audio_data: numpy array of audio samples
            sample_rate: sample rate of the audio data

        Returns:
            AudioClassificationResult
        """
        try:
            # Convert to float32 for consistency
            orig_dtype = audio_data.dtype
            audio_data = audio_data.astype(np.float32)

            # Normalize int16 to [-1,1]
            if orig_dtype == np.int16:
                audio_data /= np.iinfo(np.int16).max

            # Ensure normalized
            max_abs = np.max(np.abs(audio_data)) if audio_data.size else 0
            if max_abs > 1.0:
                audio_data /= max_abs

            # Flatten multi-channel data
            if audio_data.ndim > 1:
                audio_data = audio_data.flatten()

            audio_clip = containers.AudioData.create_from_array(
                audio_data, sample_rate
            )
            mp_result = self.classifier.classify(audio_clip)
            return AudioClassificationResult.from_mediapipe(mp_result, self.max_results)

        except Exception as e:
            _logger.error("Audio classification failed: {err}", err=str(e))
            return AudioClassificationResult([])

    def close(self):
        """Close the classifier and release resources."""
        try:
            self.classifier.close()
        except Exception:
            pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
