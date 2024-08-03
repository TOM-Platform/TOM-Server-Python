from shared_memory_dict import SharedMemoryDict
from Utilities import logging_utility

_logger = logging_utility.setup_logger(__name__)

# memory config
_SHARED_MEMORY_NAME = 'TOM_SHARED_MEMORY'
_SHARED_MEMORY_SIZE_IN_BYTES = int(10 * 1024 * 1024)  # 10 Mb

_UNSAVED_VALUES = ["origin", "timestamp"]

# Global _memory instance
_memory = None


def init():
    """Initializes the shared memory object."""
    global _memory
    _memory = SharedMemoryDict(name=_SHARED_MEMORY_NAME, size=_SHARED_MEMORY_SIZE_IN_BYTES)


def close():
    """Close the shared memory object."""
    global _memory
    if _memory:
        _memory.shm.close()
        _memory.shm.unlink()

        # del _memory
        # _memory = None


def get_shared_memory():
    """Returns the shared memory object if available, or initializes it."""
    global _memory
    if not _memory:
        init()
    return _memory


def update_shared_memory(message):
    """Updates the shared memory with multiple values from a dictionary."""
    global _memory
    if not _memory:
        init()
    for key, val in message.items():
        if key not in _UNSAVED_VALUES:
            _memory[key] = val


def update_shared_memory_item(key, val):
    """Updates a single item in the shared memory."""
    global _memory
    if not _memory:
        init()
    if key not in _UNSAVED_VALUES:
        _memory[key] = val
    else:
        _logger.debug("{key} is an ignored value, not saved in shared memory", key=key)


def get_shared_memory_item(key):
    """Retrieves a single item from the shared memory."""
    global _memory
    if not _memory:
        init()

    try:
        return _memory[key]
    except KeyError:
        return None
