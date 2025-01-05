from enum import Enum


class MemoryAssistanceAction(Enum):
    """
    Actions to retrieve the memory
    """
    MEMORY_RECALL_START = 0
    MEMORY_RECALL_END = 1


class MemoryAssistanceState(Enum):
    """
    States for memory assistance service
    """
    MEMORY_SAVING_STATE = 0
    MEMORY_RECALL_ENABLE_TRANSIENT_STATE = 1
    MEMORY_RECALL_STATE = 2
