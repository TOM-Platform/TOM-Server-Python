from pynput.keyboard import Key, Listener
import base_keys
from base_component import BaseComponent
from Utilities import logging_utility

_logger = logging_utility.setup_logger(__name__)


class KeyboardWidget(BaseComponent):
    """
    Widget to capture keyboard input events and send them to the next component.
    """

    def __init__(self, name):
        super().__init__(name)
        self.listener = None
        _logger.info("KeyboardWidget initialized with name: {name}", name=name)

    def start(self):
        """Starts the keyboard listener and sets component status to running."""
        super().set_component_status(base_keys.COMPONENT_IS_RUNNING_STATUS)
        _logger.info("KeyboardWidget started listening for key events.")

        # The listener is setup with on_press and on_release callbacks
        self.listener = Listener(on_press=self.on_press, on_release=self.on_release)
        self.listener.start()
        self.listener.join()

    def on_press(self, key):
        """Handles key press events and sends them to the next component."""
        key_name = self.get_key_name(key)

        # Send the key press to the next component
        super().send_to_component(key_name=key_name)

        if key == Key.esc:
            # Stops the listener
            _logger.info("Escape key was pressed - stopping listener")
            return False  # Returning False stops the listener

        return True

    def on_release(self, key):
        """Handles key release events."""
        _logger.info("Key {key_name} released", key_name=self.get_key_name(key))

    def get_key_name(self, key):
        """Extract the name or character of the key pressed."""
        try:
            return key.char
        except AttributeError:
            return str(key)

    def stop(self):
        _logger.info("Stopping KeyBoard")

        self.listener.stop()

        super().set_component_status(base_keys.COMPONENT_IS_STOPPED_STATUS)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()
