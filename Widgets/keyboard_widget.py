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
        key_event = base_keys.KEYBOARD_EVENT_PRESS
        key_name = self.get_key_name(key)
        key_code = self.get_key_code(key)

        # Send the key press to the next component
        super().send_to_component(key_event=key_event, key_name=key_name, key_code=key_code)

        # if key == Key.esc:
        #     # Stops the listener
        #     _logger.info("Escape key was pressed - stopping listener")
        #     return False  # Returning False stops the listener

        return True

    def on_release(self, key):
        """Handles key release events."""
        key_event = base_keys.KEYBOARD_EVENT_RELEASE
        key_name = self.get_key_name(key)
        key_code = self.get_key_code(key)

        super().send_to_component(key_event=key_event, key_name=key_name, key_code=key_code)

    def get_key_name(self, key):
        """Extract the name or character of the key pressed."""
        try:
            return key.char
        except AttributeError:
            return str(key)

    def get_key_code(self, key):
        '''
        Get the code of the key pressed.
        :param key:
        :return: 0 if not found, otherwise the key code.
        '''

        try:
            # Try to retrieve vk from key or key.value
            return key.vk
        except AttributeError:
            try:
                # Fallback to key.value.vk if key.vk is unavailable
                return key.value.vk
            except AttributeError:
                # Handle special cases for common non-character keys
                special_key_map = {
                    Key.enter: 13,
                    Key.space: 32,
                    Key.backspace: 8,
                    Key.tab: 9,
                    Key.esc: 27,
                    Key.shift: 16,
                    Key.ctrl: 17,
                    Key.alt: 18,
                    Key.page_up: 33,  # Page Up keycode
                    Key.page_down: 34,  # Page Down keycode
                    # Add more keys as necessary
                }
                return special_key_map.get(key, 0)

    def stop(self):
        _logger.info("Stopping KeyBoard")

        self.listener.stop()

        super().set_component_status(base_keys.COMPONENT_IS_STOPPED_STATUS)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()
