from typing import Any, Optional, Dict
from shared_memory_dict import SharedMemoryDict
from Utilities import logging_utility, environment_utility

_logger = logging_utility.setup_logger(__name__)

# memory config
_SHARED_MEMORY_NAME = 'TOM_SHARED_MEMORY'

_UNSAVED_VALUES = {"origin", "timestamp"}

# Global _memory instance
_memory: Optional[SharedMemoryDict] = None


def init() -> None:
    """Initializes the shared memory object if not already done."""
    global _memory
    if _memory is None:
        try:
            memory_size_mb = environment_utility.get_env_int("SHARED_MEMORY_SIZE_MB")
            memory_size_bytes = int(memory_size_mb * 1024 * 1024)  # Convert MB to bytes
            _memory = SharedMemoryDict(name=_SHARED_MEMORY_NAME, size=memory_size_bytes)
        except Exception:
            _logger.exception("Failed to initialize shared memory 'TOM_SHARED_MEMORY'")
            raise


def close() -> None:
    """Closes and unlinks the shared memory object, resetting state."""
    global _memory
    if _memory is not None:
        try:
            _memory.shm.close()
            _memory.shm.unlink()
        except FileNotFoundError:
            _logger.warning("Shared memory 'TOM_SHARED_MEMORY' was not found when closing")
        except Exception:
            _logger.exception("Error closing shared memory 'TOM_SHARED_MEMORY'")
        finally:
            _memory = None


def get_shared_memory() -> SharedMemoryDict:
    """Returns the shared memory object, initializing if necessary."""
    if _memory is None:
        init()
    return _memory  # type: ignore[return-value]


def update_shared_memory(message: Dict[str, Any]) -> None:
    """Updates the shared memory with multiple values from a dictionary."""
    for key, val in message.items():
        update_shared_memory_item(key, val)


def update_shared_memory_item(key: str, val: Any) -> None:
    """Updates a single item in the shared memory, unless it’s unsaved."""
    if key in _UNSAVED_VALUES:
        _logger.debug("{key} is an ignored value; not saved.", key=key)
        return

    mem = get_shared_memory()
    try:
        mem[key] = val
    except Exception:
        _logger.exception("Failed to set '{key}' in shared memory", key=key)


def get_shared_memory_item(key: str) -> Any:
    """Retrieves a single item from the shared memory, or None if missing."""
    mem = get_shared_memory()
    return mem.get(key)
