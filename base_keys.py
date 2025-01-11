'''
This file is to maintain various constants across the entire server.

The format for each constant is as follows:
<Name>_<Type> = "<keyname>"
'''

############# DO NOT CHANGE the values, but feel free to add new ones #############


##############################################################################################################
# Component Names, which are defined at the config files (.yaml) in the 'Config' folder
##############################################################################################################

WEBSOCKET_WIDGET = "input:websocket"
AUDIO_WIDGET = "input:audio"
CAMERA_WIDGET = "input:camera"
KEYBOARD_WIDGET = "input:keyboard"

YOLOV8_PROCESSOR = "processing:yolov8"
AUDIO_CONTEXT_PROCESSOR = "processing:audioContext"
WHISPER_PROCESSOR = "processing:whisper"

LEARNING_SERVICE = "service:learning"
RUNNING_SERVICE = "service:running"
MARTIAL_ARTS_SERVICE = "service:martial_arts"
RUNNING_DEMO_SERVICE = "service:runningDemo"
CONTEXT_SERVICE = "service:context"
DASHBOARD_SERVICE = "service:dashboardService"

WEBSOCKET_OUTPUT = "output:websocket"

##############################################################################################################
# Component Statuses, to indicate the current status for each component
##############################################################################################################

# NOTE: Component Status
MEMORY_COMPONENT_STATUS_KEY = "component_status"
COMPONENT_IS_RUNNING_STATUS = "COMPONENT_IS_RUNNING_STATUS"
COMPONENT_IS_STOPPED_STATUS = "COMPONENT_IS_STOPPED_STATUS"
COMPONENT_NOT_STARTED_STATUS = "COMPONENT_NOT_STARTED_STATUS"

##############################################################################################################
# keys to parse data between components, which are the parameters of the `send_to_component` function
##############################################################################################################

# NOTE: Base Message Keys
BASE_DATA_KEY = "base_data"
ORIGIN_KEY = "origin"
TIMESTAMP_KEY = "timestamp"

# NOTE: Audio
AUDIO_DATA = "audio_data"

# NOTE: Transcriber (Speech to Text)
AUDIO_TRANSCRIPTION_DATA = "audio_transcript"

# NOTE: Emotion Classifier
EMOTION_SCORES = "emotion_scores"

# NOTE: Websocket
WEBSOCKET_DATATYPE = "websocket_datatype"
WEBSOCKET_MESSAGE = "websocket_message"
WEBSOCKET_CLIENT_TYPE = "websocket_client_type"

UNITY_CLIENT = "unity"
WEAROS_CLIENT = "wearOS"
DASHBOARD_CLIENT = "dashboard"

# NOTE: Camera
CAMERA_FRAME = "camera_frame"
CAMERA_FRAME_WIDTH = "camera_frame_width"
CAMERA_FRAME_HEIGHT = "camera_frame_height"
CAMERA_FPS = "camera_fps"

# NOTE: Keyboard
KEYBOARD_KEY_NAME = "key_name"
KEYBOARD_KEY_CODE = "key_code"
KEYBOARD_EVENT = "key_event"
KEYBOARD_EVENT_PRESS = "key_event_press"
KEYBOARD_EVENT_RELEASE = "key_event_release"

# NOTE: Yolov8
YOLOV8_LAST_DETECTION = "last_detection"
YOLOV8_CLASS_LABELS = "class_labels"
YOLOV8_FRAME = "yolo_frame"

##############################################################################################################
# keys identify values defined at environment variables
##############################################################################################################

# NOTE: Environment Keys
DIRECTIONS_OPTION = "DIRECTIONS_OPTION"
ORS_OPTION = "ORS_OPTION"
STATIC_MAPS_OPTION = "STATIC_MAPS_OPTION"
FPV_OPTION = "FPV_OPTION"

CAMERA_VIDEO_SOURCE = "CAMERA_VIDEO_SOURCE"

# NOTE: Map Keys (Option Values for Running Service)
PLACES_OPTION_OSM = 0
PLACES_OPTION_GOOGLE = 1
DIRECTIONS_OPTION_ORS = 0
DIRECTIONS_OPTION_GOOGLE = 1
STATIC_MAPS_OPTION_GEOAPIFY = 0
STATIC_MAPS_OPTION_GOOGLE = 1
ORS_OPTION_API = 0
ORS_OPTION_DOCKER = 1

# NOTE: API credential files defined at environment variables
HOLOLENS_CREDENTIALS_FILE_KEY_NAME = "HOLOLENS_CREDENTIAL_FILE"
FITBIT_CREDENTIAL_FILE_KEY_NAME = "FITBIT_CREDENTIAL_FILE"
GOOGLE_MAPS_CREDENTIAL_FILE_KEY_NAME = "GOOGLE_MAPS_CREDENTIAL_FILE"
GOOGLE_CLOUD_CREDENTIAL_FILE_KEY_NAME = "GOOGLE_CLOUD_CREDENTIAL_FILE"
OPENAI_CREDENTIAL_FILE_KEY_NAME = "OPENAI_CREDENTIAL_FILE"
GEMINI_CREDENTIAL_FILE_KEY_NAME = "GEMINI_CREDENTIAL_FILE"
ANTHROPIC_CREDENTIAL_FILE_KEY_NAME = "ANTHROPIC_CREDENTIAL_FILE"
ORS_CREDENTIAL_FILE_KEY_NAME = "ORS_CREDENTIAL_FILE"
GEOAPIFY_CREDENTIAL_FILE_KEY_NAME = "GEOAPIFY_CREDENTIAL_FILE"
