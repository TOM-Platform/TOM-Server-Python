from .pandalens_enum import PandaLensState, PandaLensAction


# Utility functions to manage state
def get_init_state():
    return PandaLensState.SERVER_OBSERVING_STATE


def get_next_state(curr_state, client_action=None):
    if curr_state is PandaLensState.SERVER_OBSERVING_STATE:
        if client_action is PandaLensAction.CLIENT_CAMERA_PRESS or client_action is PandaLensAction.CLIENT_INTEREST:
            return PandaLensState.SERVER_QA_STATE
        if client_action is PandaLensAction.CLIENT_SUMMARY_PRESS:
            return PandaLensState.SERVER_BLOGGING_STATE

    return curr_state


def reset():
    return PandaLensState.SERVER_OBSERVING_STATE
