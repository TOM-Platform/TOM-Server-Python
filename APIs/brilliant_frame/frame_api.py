# Documentation: https://github.com/brilliantlabsAR/docs/blob/c33420dc55eb12b27f5a804b9a5a82247d471ae9/frame/building-apps-sdk.md

from typing import Optional, Callable

from frame_sdk import Frame
from frame_sdk.camera import Quality, AutofocusType
from frame_sdk.display import Alignment, PaletteColors

from Utilities import logging_utility
from .direction import Direction

_logger = logging_utility.setup_logger(__name__)


class BrilliantFrame:
    """
    This class is responsible for the Brilliant Frame's APIs.
    """

    def __init__(self):
        """
        This method initializes the Frame device and its components.
        """
        self.frame = Frame()

    async def get_battery_level(self):
        """
        Gets battery level of the frame.

        Returns:
            int: battery level (from 0 to 100)
        """
        async with self.frame as f:
            _logger.info("Starting to get battery level...")
            batt_level = await f.get_battery_level()
            _logger.info(f"Frame battery: {batt_level}%")

        return batt_level

    async def read_file(self, file_path):
        """
        Reads a file from the frame in full as a string. 
        Catches exception and logs an error if file is not found

        Args:
            file_path (str): The path to the file to be read.

        Returns:
            str: the file content
            None: if exception is thrown and file is not found
        """
        try:
            async with self.frame as f:
                _logger.info(f"Starting to read file {file_path}...")
                file_content = (await f.files.read_file(file_path)).decode()
                _logger.info(f"File Content: {file_content}")
            return file_content
        except Exception:
            _logger.error("File not found: {file_path}", file_path=file_path)
            return None

    async def write_file(self, file_path, text):
        """
        Writes text to a file path on the frame.
        Catches exception and logs an error if file cannot be 
        opened, written to, or closed
        
        Args:
            file_path (str): The path to the file to be written to
            text (str): The text to be written to the file

        Returns:
            string: the file content
            None: if exception is thrown and there is an issue writing to file
        """
        try:
            async with self.frame as f:
                _logger.info(f"Starting to write to file {file_path}...")
                await f.files.write_file(file_path, text.encode())
                _logger.info("File successfully written to")
        except Exception:
            _logger.error("File cannot be opened, written to, or closed: {file_path}", file_path=file_path)
            return None

    async def delete_file(self, file_path):
        """
        Delete a file on the device. 
        
        Args:
            file_path (str): The path to the file to be deleted.

        Returns:
            bool: True if the file was deleted, 
                False if it didn’t exist or failed to delete.
        """
        async with self.frame as f:
            _logger.info(f"Startin to delete file {file_path}...")
            isDeleted = await f.files.delete_file(file_path)
            _logger.info(f"File is deleted: {isDeleted}")

        return isDeleted

    async def file_exists(self, file_path):
        """
        Check if a file exists on the frame. 
        Only works on files and not directories

        Args:
            file_path (str): The path to the file to be checked.

        Returns:
            bool: True if the file exists, False otherwise  
        """
        async with self.frame as f:
            _logger.info(f"Locating file {file_path}...")
            exists = await f.files.file_exists(file_path)
            _logger.info(f"File exists: {exists}")

        return exists

    async def take_photo(self, autofocus_seconds: Optional[int] = 3, quality: Quality = Quality.VERY_HIGH,
                         autofocus_type: AutofocusType = AutofocusType.CENTER_WEIGHTED, resolution: Optional[int] = 720,
                         pan: Optional[int] = 0):
        """
        Takes a photo with the frame.
        Catches exception and logs error message if photo capture has failed

        Args: 
            autofocus_seconds (int or None): If provided, the camera will attempt 
                to set exposure and other settings automatically for the specified 
                number of seconds before taking a photo. 
            quality (Quality): quality of the photo to take (VERY_LOW, LOW, MEDIUM, HIGH, VERY_HIGH)
            autofocus_type (AutofocusType): type of autofocus to use (AVERAGE, SPOT, CENTER_WEIGHTED)
            resolution (int or None): If provided, the photo resolution will be the 
                specified square size. Valid range: 100..720
            pan (int or None): If provided, the photo will be panned up (negative) or 
                down (positive) by the specified amount. Valid range: -140..140

        Returns: 
            byte array: The photo data
            None: if an exception is thrown and photo capture has failed
        """
        try:
            async with self.frame as f:
                _logger.info("Taking photo...")
                photo_bytes = await f.camera.take_photo(autofocus_seconds, quality, autofocus_type, resolution, pan)

            _logger.info("Photo capture succeeded")
            return photo_bytes  # use save_image_bytes from image_utility to save to file
        except Exception:
            _logger.error("Photo capture has failed")
            return None

    async def display_text(self, text: str, x: int = 1, y: int = 1, max_width: Optional[int] = 640,
                           max_height: Optional[int] = None, align: Alignment = Alignment.TOP_LEFT,
                           color: PaletteColors = PaletteColors.WHITE):
        """
        Display text on the frame

        Args: 
            text (str): The text to display.
            x (int): The left pixel position to start the text.
            y (int): The top pixel position to start the text. 
            max_width (int or None): The maximum width for the text bounding box. 
                Will be word-wrapped onto multiple lines automatically if text is wider than this. 
                Can be overridden with None to disable word-wrapping.
            max_height (int or None): The maximum height for the text bounding box. 
                Will be cut off at that height if text is taller than this.
                Can be overridden with None to the vertical cutoff.
            align (Alignment): The alignment of the text, 
                both horizontally if a max_width is provided, 
                and vertically if a max_height is provided.
            color (PaletteColors): The colour of the text.

        """
        if not isinstance(text, str):
            text = str(text)

        async with self.frame as f:
            _logger.info("Showing text...")
            await f.display.show_text(text, x, y, max_width, max_height, align, color)

    async def display_scroll_text(self, text, lines_per_frame: int = 5, delay: float = 0.12,
                                  color: PaletteColors = PaletteColors.WHITE):
        """
        Scoll text vertically on the frame's display.

        Args: 
            text (str): The text to scroll. It is automatically wrapped to fit the display width.
            lines_per_frame (int): The number of vertical pixels to scroll per frame.
            delay (float): The delay between frames in seconds. 
            color (PaletteColors): The colour of the text.
        """
        if not isinstance(text, str):
            text = str(text)

        async with self.frame as f:
            _logger.info("Showing scroll text...")
            await f.display.scroll_text(text, lines_per_frame, delay, color)
            # E.g. "Never gonna give you up\nNever gonna let you down\nNever gonna run around and desert you\n
            # Never gonna make you cry\nNever gonna say goodbye\nNever gonna tell a lie and hurt you"

    async def draw_rectangle(self, border, x, y, w, h, border_color: PaletteColors, border_width,
                             color: PaletteColors = PaletteColors.WHITE):
        """
        Draws a filled rectangle with/without border on the display

        Args: 
            border (bool): True if a border is present, False otherwise
            x (int): The x position of the upper-left corner of the rectangle.
            y (int): The y position of the upper-left corner of the rectangle.
            w (int): The width of the rectangle.
            h (int): The height of the rectangle.
            border_color (PaletteColors): The colour of the border
            border_width (int): The width of the border in pixels
            color (PaletteColors): The colour of the rectangle
        """
        async with self.frame as f:
            _logger.info("Starting to draw rectangle...")
            if border:
                await f.display.draw_rect_filled(x, y, w, h, border_width, border_color, color)
            else:
                await f.display.draw_rect(x, y, w, h, color)
            await f.display.show()

    async def run_lua(self, command):
        """
        Runs a lua string on the device.
        Returns immediately and does not block
        """
        async with self.frame as f:
            _logger.info("Running lua string...")
            await f.run_lua(command)

    async def record_audio(self, silence_cutoff_length_in_seconds: Optional[int] = 3, max_length_in_seconds: int = 30):
        """
        Records audio from the frame's microphone

        Args: 
            silence_cutoff_length_in_seconds (int or None): The length of silence to allow 
                before stopping the recording. Can set to None to disable silence detection
            max_length_in_seconds (int): The maximum length of the recording.

        Returns: 
            np.ndarray: The audio data recorded as a numpy array of int16 or int8 depending 
                        on the bit_depth (valid value: 8 or 16)
            int: The sample rate of the frame's microphone 
                (either 8000 or 16000, number of audio samples per second)
        """
        async with self.frame as f:
            _logger.info("Recording audio...")
            audio_data = await f.microphone.record_audio(silence_cutoff_length_in_seconds, max_length_in_seconds)
            sample_rate = f.microphone.sample_rate

        _logger.info("Audio recording succeeded")
        return audio_data, sample_rate

    async def play_audio(self, audio_data):
        """
        Plays audio on the computer
        Did not include sample rate/bit depth as parameters, default to the instance values

        Args: 
            audio_data (np.ndarray): The audio data to play
        """
        async with self.frame as f:
            _logger.info(f"Playing back {len(audio_data) / f.microphone.sample_rate:01.1f} seconds of audio")
            f.microphone.play_audio_background(audio_data, f.microphone.sample_rate, f.microphone.bit_depth)

    async def get_silence_threshold(self):
        """
        Get the value of the frame's microphone's current silence threshold.
        Value is between 0 and 1 

        Returns: 
            float: The current silence threshold
        """
        async with self.frame as f:
            _logger.info("Getting silence threshold...")
            silence_threshold = f.microphone.silence_threshold
            _logger.info(f"Frame Microphone Silence Threshold: {silence_threshold}")

        return silence_threshold

    async def set_silence_threshold(self, silence_threshold: float = 0.02):
        """
        Sets the silence threshold of the frame's microphone. 
        Valid values are between 0 and 1. Default: 0.02

        Args: 
            silence_threshold (float): The value to be set
        """
        if silence_threshold < 0 or silence_threshold > 1:
            _logger.error("Silence threshold to be set must be between 0 and 1")
            return

        async with self.frame as f:
            _logger.info("Setting silence threshold...")
            f.microphone.silence_threshold = silence_threshold

        _logger.info(f"Successfully Set Frame Microphone Silence Threshold to: {silence_threshold}")

    async def get_direction(self):
        """
        Gets the orientation of the frame and deconstructs it into a custom Direction class.
        Note that heading is not yet implemented in the frame, so the reading is always 0

        Returns: 
            Direction: the object containing the parameters of the frame's orientation
        """
        async with self.frame as f:
            _logger.info("Getting frame's orientation...")
            direction_data = await f.motion.get_direction()
            direction = Direction(
                roll=direction_data.roll,
                pitch=direction_data.pitch,
                heading=direction_data.heading,
                amplitude=direction_data.amplitude()
            )
        _logger.info(f"{direction}")
        return direction

    async def run_on_tap(self, lua_script: Optional[str] = None, callback: Optional[Callable[[], None]] = None):
        """
        Runs a Lua script and/or callback when frame is tapped. 
        If None is provided for both, then previously set callbacks will be removed

        Args: 
            lua_script (str or None): the lua script to be run
            callback (Callable or None): the callback to be executed 
        """
        async with self.frame as f:
            _logger.info("Run lua script or callback...")
            await f.motion.run_on_tap(lua_script, callback)

    async def wait_on_tap(self):
        """
        Wait for the frame to be tapped before continuing
        """
        async with self.frame as f:
            _logger.info("Waiting for tap...")
            await f.motion.wait_for_tap()
