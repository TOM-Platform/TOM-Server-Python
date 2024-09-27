from enum import Enum


class PandaLensAction(Enum):
    """
    Enum Declarations
    """
    # Actions are Client actions
    CLIENT_CAMERA_PRESS = 0
    CLIENT_INTEREST = 1
    CLIENT_SUMMARY_PRESS = 2


class PandaLensState(Enum):
    """
    States are Server states
    """
    SERVER_OBSERVING_STATE = 0  # Looking out for interesting moments
    SERVER_QNA_STATE = 1  # Conversing with users to ask questions
    SERVER_BLOGGING_STATE = 2  # Server is awaiting the blogging orders
