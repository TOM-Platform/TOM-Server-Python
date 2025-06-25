from enum import Enum


class PandaLensAction(Enum):
    """
    Enumeration of actionable events in the PandaLens application originating from either the client (smart glasses UI)
    or the system’s automated processes.
    """
    CLIENT_INTEREST_CAMERA_PRESS = 0  # Occurs when the user presses the camera button to capture an image or initiate
    # an observation sequence.

    CLIENT_INTEREST_SYSTEM_DETECT = 1  # Occurs when the system automatically detects a point of interest based on the
    # user’s profile, gaze direction, or contextual cues.

    CLIENT_INTEREST_USER_SPEAK = 2  # Occurs when the user triggers a speech-based input or command (e.g., asking a
    # question)

    CLIENT_SUMMARY_PRESS = 3  # Occurs when the user presses the summary button to request a synthesized moments of the
    # currently observed scene


class PandaLensState(Enum):
    """
    Enumeration of server-side operational states within PandaLens, synchronized with the  client UI to accurately
    reflect the current workflow stage.
    """
    SERVER_OBSERVING_STATE = 0  # Looking out for interesting moments
    SERVER_QA_STATE_USER_INITIATE = 1  # Conversing with users to ask questions, when user initiate (e.g., take photo)
    SERVER_QA_STATE_SYSTEM_INITIATE = 2  # Conversing with users to ask questions, when system initiate (e.g., gaze at)
    SERVER_BLOGGING_STATE = 3  # Server is awaiting the blogging orders
