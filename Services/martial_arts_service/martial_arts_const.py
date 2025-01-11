CONFIG_TABLE_NAME = "MaSessionConfigTable"
CONFIG_ROW_ID = 0

PAD_DIAMETER = 0.13  # diameter of entire pad on Client-Side
ON_TARGET_RELATIVE_SIZE = 0.56  # relative size of on-target portion compared to the entire pad
DISTANCE_TO_TARGET_FEEDBACK_THRESHOLD = PAD_DIAMETER * ON_TARGET_RELATIVE_SIZE / 2
# radius of on-target portion, to be on target, distance from center of target should be less than radius of the on-target portion
ANGLE_FEEDBACK_THRESHOLD_LOWER = 15  # angle in degrees, lower limit for straight punch
ANGLE_FEEDBACK_THRESHOLD_HIGHER = 40  # angle in degrees, upper limit for straight punch

METRICS_TABLE_NAME = "MaMetricsTable"
SESSION_TIMESTAMP_KEY = "session_timestamp"
TOTAL_REACTION_TIME_KEY = "total_reaction_time"
FEEDBACK_CATEGORY = "feedback_category"
RAW_DATA_KEY = "raw_data"
PUNCH_DICT_KEY = "punch_dict"
TOTAL_PUNCHES_KEY = "total_punches"
UNCATEGORIZED_PUNCHES_KEY = "uncategorized"

LEFT_HAND = 1
RIGHT_HAND = 2

# Feedback
GOOD = "Good"
PUNCH_LOWER = "Punch lower"
PUNCH_HIGHER = "Punch higher"
PUNCH_RIGHT = "Aim more right"
PUNCH_LEFT = "Aim more left"
PUNCH_NOT_STRAIGHT = "Punch is not straight"

GOOD_PUNCH = "good_punch"
OFF_TARGET = "off_target"
BAD_ANGLE = "bad_angle"

DATETIME = "datetime"
SESSION_DURATION = "session_duration"
INTERVAL_DURATION = "interval_duration"

OFF_TARGET_FEEDBACK = [PUNCH_LOWER, PUNCH_HIGHER, PUNCH_RIGHT, PUNCH_LEFT]
