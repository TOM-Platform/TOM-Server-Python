from Utilities import environment_utility


class MemoryAssistanceConfig:
    ''''
    This class contains constants/configurations for memory assistance service
    '''

    MEMORY_ASSISTANCE_IMAGES_DIRECTORY = "logs/images"
    MEMORY_ASSISTANCE_DATABASE_COLLECTION = "memory_collection"

    MEMORY_RECALL_KEY_CODE = 34  # 'PageDown' key code (in Windows)

    MEMORY_RECALL_SPEECH_PROCESS_DURATION_SECONDS = environment_utility.get_env_int('SPEECH_RECOGNITION_WINDOW')
    # This is the duration for speech transcription window.

    MEMORY_RECALL_INSTANCES_COUNT = 3  # instances to show

    IMAGE_SAMPLING_DURATION_SECONDS = 30  # duration to sample images
