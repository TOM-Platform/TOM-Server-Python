from typing import Optional

import cv2
import base_keys
from base_component import BaseComponent
from Utilities import environment_utility, logging_utility, file_utility

_SAVE_VIDEO = environment_utility.get_env_bool("VIDEO_OUTPUT_SAVE")
_SAVE_VIDEO_PATH = environment_utility.get_env_string("VIDEO_OUTPUT_PATH")
_IMAGE_DISPLAY_DELAY_MILLISECONDS = 5

_logger = logging_utility.setup_logger(__name__)


class VideoOutput(BaseComponent):
    """
    A class to handle video output, including displaying frames and saving them to a file.
    """

    # Update this if needed
    _ORIGIN_TO_FRAME_KEY_MAPPING = {
        base_keys.FACE_DETECTION_PROCESSOR: base_keys.FACE_FRAME,
        base_keys.POSE_LANDMARK_DETECTION_PROCESSOR: base_keys.POSE_FRAME,
        base_keys.YOLOV8_PROCESSOR: base_keys.YOLOV8_FRAME,
        base_keys.CAMERA_WIDGET: base_keys.CAMERA_FRAME,
    }

    def __init__(
            self,
            name: str,
            save: bool = _SAVE_VIDEO,
            save_path: str = _SAVE_VIDEO_PATH,
            fourcc: str = "XVID",
            window_name: str = "VideoOutput",
            display_delay_ms: int = _IMAGE_DISPLAY_DELAY_MILLISECONDS,
    ) -> None:
        super().__init__(name)

        # Configuration
        self.save: bool = save
        self.save_path: str = save_path
        self.fourcc: str = fourcc
        self.window_name: str = window_name
        self.display_delay_ms: int = display_delay_ms

        # Internal state
        self._video_writer: Optional[cv2.VideoWriter] = None

        if self.save:
            file_utility.create_directory_for_file(self.save_path)

        _logger.info("VideoOutput::__init__()")
        _logger.info("-- save: [{save}], save_path: [{save_path}]", save=str(self.save), save_path=str(self.save_path))

    def play(self, raw_data):
        origin = raw_data[base_keys.ORIGIN_KEY]

        frame_key = self._ORIGIN_TO_FRAME_KEY_MAPPING.get(origin)

        if not frame_key:
            _logger.warning("Unsupported origin key: {origin}", origin=origin)
            return

        frame = raw_data[frame_key]
        width = raw_data[base_keys.CAMERA_FRAME_WIDTH]
        height = raw_data[base_keys.CAMERA_FRAME_HEIGHT]
        fps = raw_data[base_keys.CAMERA_FPS]

        if frame is None or width is None or height is None or fps is None:
            _logger.error("Incomplete raw_data; skipping frame")
            return

        self._handle_video_data(frame, int(width), int(height), float(fps))

    def _handle_video_data(self, frame, camera_frame_width, camera_frame_height, camera_fps):
        # _logger.debug("_handle_video_data - camera_frame_width: {camera_frame_width}, "
        #               "camera_frame_height: {camera_frame_height}, camera_fps: {camera_fps}",
        #               camera_frame_width=camera_frame_width, camera_frame_height=camera_frame_height,
        #               camera_fps=camera_fps)
        if self.save:
            if self._video_writer is None:
                codec = cv2.VideoWriter_fourcc(*self.fourcc)
                writer = cv2.VideoWriter(self.save_path, codec, camera_fps, (camera_frame_width, camera_frame_height))

                if not writer.isOpened():
                    _logger.error(f"Failed to open VideoWriter at {self.save_path}")
                else:
                    self._video_writer = writer
                    _logger.debug("VideoWriter opened successfully")
            else:
                self._video_writer.write(frame)

        cv2.imshow(self.window_name, frame)
        cv2.waitKey(_IMAGE_DISPLAY_DELAY_MILLISECONDS)

    def stop(self):
        if self._video_writer:
            _logger.debug("Releasing VideoWriter")
            self._video_writer.release()
            self._video_writer = None

        cv2.destroyWindow(self.window_name)
        _logger.debug("Destroyed window {name}", name=self.window_name)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()
