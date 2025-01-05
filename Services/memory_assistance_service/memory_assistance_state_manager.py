from .memory_assistance_enum import MemoryAssistanceState, MemoryAssistanceAction


# Utility functions to manage state

def get_init_state():
    return MemoryAssistanceState.MEMORY_SAVING_STATE


def get_next_state(curr_state, action):
    if (curr_state is MemoryAssistanceState.MEMORY_SAVING_STATE
            and action is MemoryAssistanceAction.MEMORY_RECALL_START):
        return MemoryAssistanceState.MEMORY_RECALL_ENABLE_TRANSIENT_STATE
    if (curr_state is MemoryAssistanceState.MEMORY_RECALL_ENABLE_TRANSIENT_STATE
            and action is MemoryAssistanceAction.MEMORY_RECALL_END):
        return MemoryAssistanceState.MEMORY_RECALL_STATE
    if (curr_state is MemoryAssistanceState.MEMORY_RECALL_STATE
            and action is MemoryAssistanceAction.MEMORY_RECALL_END):
        return MemoryAssistanceState.MEMORY_SAVING_STATE

    return curr_state
