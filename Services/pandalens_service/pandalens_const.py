import math

MIN_PANDALENS_CONTENT_DISPLAY_DURATION_MILLIS = 10000  # use 12000 for demo if needed
OBJECT_DETECTION_CONFIDENCE_THRESHOLD = 0.50
POINTER_LLM_INVOKE_COOLDOWN_MILLIS = 30000  # 30 seconds
FINGER_POINTING_TRIGGER_DURATION_SECONDS = 3
POINTING_LOCATION_OFFSET_PERCENTAGE = 1  # 25% of the screen width/height
FINGER_DETECTION_DURATION_SECONDS = 1  # seconds (depends on the client)
FINGER_POINTING_BUFFER_SIZE = math.ceil(FINGER_POINTING_TRIGGER_DURATION_SECONDS / FINGER_DETECTION_DURATION_SECONDS)
PANDALENS_QUESTION_LIMIT = 3

# Pandalens LLM Keywords
LLM_NO_QUESTIONS = None
LLM_JSON_AUTHORING_RESPONSE_SUMMARY_KEY = "summary of new content"
LLM_JSON_AUTHORING_RESPONSE_QUESTION_KEY = "question to users"
LLM_JSON_BLOGGING_RESPONSE_INTRO_KEY = "introduction of blog"
LLM_JSON_BLOGGING_RESPONSE_CONCLUSION_KEY = "conclusion of blog"

# User Action Keys
CAMERA_ACTION_FOR_LLM = "user took a camera photo"
POINTER_INTEREST_ACTION_FOR_LLM = "user has been staring at this photo"
IDLE_ACTION = "idle"

# Client Input Event Keys
CAMERA_INPUT_EVENT_KEY = "photo"
IDLE_INPUT_EVENT_KEY = "idle"
SUMMARY_INPUT_KEY = "summary"

# Database const
MOMENTS_TABLE = "PandaLensMomentTable"
SUMMARY_COLUMN_NAME = "summary"
IMAGE_FILE_COLUMN_NAME = "image_filename"

# Paths
SEQUENCE_PATH_TO_IMAGES_FROM_PROJECT_ROOT = ["Services", "pandalens_service", "Images"]
SEQUENCE_PATH_TO_BLOGS_FROM_PROJECT_ROOT = ["Services", "pandalens_service", "Blogs"]

# Pandalens error messages
MOMENT_LIST_EMPTY_MESSAGE = "There are no moments to blog about."

# Pandalens database json structure
DB_MOMENT_FILENAME_KEY = "image_filename"
DB_MOMENT_SUMMARY_KEY = "summary"
