DEFAULT_USER_PROFILE_NAME = "default_profile.json"
SEQUENCE_PATH_TO_PROFILES_FROM_PROJECT_ROOT = ["Services", "pandalens_service", "profile"]

DEFAULT_LLM_PROMPT_INDEX = "SSI"  # "Travel", "Conference", "SSI" # see pandalens_prompt.py for more details
DEFAULT_LLM_TEMPERATURE = 0.3

PANDALENS_QUESTION_LIMIT = 2

LOCATION_QUERY_MINIMUM_MILLIS = 5 * 60 * 1000  # 5 minutes

AI_INTEREST_DETECT_LLM_INVOKE_COOLDOWN_MILLIS = 30 * 1000  # 30 seconds

POINTING_LOCATION_OFFSET_PERCENTAGE = 40  # 40% of the screen width/height

# PandaLens LLM Keywords
LLM_DEFAULT_QUESTION = "Any Comments?"

# User Action Keys
CAMERA_ACTION_FOR_LLM = "User took this photo using camera."
POINTER_INTEREST_ACTION_FOR_LLM = "User stared at this photo."
IDLE_ACTION = "idle"

# Client Input Event Keys
CAMERA_INPUT_EVENT_KEY = "photo"
IDLE_INPUT_EVENT_KEY = "idle"
SUMMARY_INPUT_KEY = "summary"

# Paths
SEQUENCE_PATH_TO_IMAGES_FROM_PROJECT_ROOT = ["logs", "PandaLens", "Images"]
SEQUENCE_PATH_TO_BLOGS_FROM_PROJECT_ROOT = ["logs", "PandaLens", "Blogs"]

# PandaLens error messages
ERROR_MOMENT_LIST_EMPTY = "Error: No moments."
MESSAGE_MOMENT_LIST_EMPTY_TEXT = "No moments captured yet."
MESSAGE_MOMENT_LIST_EMPTY_AUDIO = ("I didn’t find any moments. "
                                   "Try snapping a photo or pointing at something interesting!")
MESSAGE_MOMENT_LIST_EMPTY_DURATION_SECONDS = 5

MESSAGE_BLOG_GENERATED_TEXT = "Your blog has been successfully generated!"
MESSAGE_BLOG_GENERATED_AUDIO = "Your blog has been generated and sent to your email."
MESSAGE_BLOG_GENERATED_DURATION_SECONDS = 6

MESSAGE_MOMENTS_SUMMARY_TEXT = "Your Captured Moments"
MESSAGE_MOMENTS_SUMMARY_TEXT_AUDIO = (
    "Which moments would you like to include in your blog? "
    "You can say the moment IDs, or just say 'select all' to include everything."
)

# These icons names match the Unity Client icons
INTEREST_DETECT_ICON_GAZE = "fpv_photo_icon"
INTEREST_DETECT_ICON_MANUAL = "robot_icon"
INTEREST_DETECT_ICON_AUDIO = "audio_icon"
INTEREST_DETECT_ICON_USER_PREFERENCE = "like_icon"

# PandaLens database and json structure (See 'Database -> Models')
MOMENTS_TABLE = "PandaLensMomentTable"
DB_MOMENT_IDENTIFIER_KEY = "identifier"
DB_MOMENT_SUMMARY_KEY = "summary"
DB_MOMENT_FILENAME_KEY = "image_filename"

# PandaLens LLM error messages
LLM_REQUEST_MAX_RETRIES = 3
LLM_REQUEST_BACKOFF_BASE_SECONDS = 2

DATE_TIME_FORMAT = "%Y-%m-%d %H:%M:%S"
