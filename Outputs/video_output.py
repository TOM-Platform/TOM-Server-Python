import cv2
import base_keys
from base_component import BaseComponent
from Utilities import environment_utility, logging_utility

_SAVE_VIDEO = environment_utility.get_env_bool("VIDEO_OUTPUT_SAVE")
_SAVE_VIDEO_PATH = environment_utility.get_env_string("VIDEO_OUTPUT_PATH")
_IMAGE_DISPLAY_DELAY_MILLISECONDS = 5

_logger = logging_utility.setup_logger(__name__)


class VideoOutput(BaseComponent):
    """
    A class to handle video output, including displaying frames and saving them to a file.
    """

    def __init__(self, name) -> None:
        super().__init__(name)

        self.save = _SAVE_VIDEO
        self.save_path = _SAVE_VIDEO_PATH
        self.video_writer = None

        _logger.info("VideoOutput::__init__()")
        _logger.info("-- save: [{save}], save_path: [{save_path}]", save=str(self.save), save_path=str(self.save_path))

    def play(self, raw_data):
        origin = raw_data[base_keys.ORIGIN_KEY]

        if origin == base_keys.YOLOV8_PROCESSOR:
            frame = raw_data[base_keys.YOLOV8_FRAME]
            camera_frame_width = raw_data[base_keys.CAMERA_FRAME_WIDTH]
            camera_frame_height = raw_data[base_keys.CAMERA_FRAME_HEIGHT]
            camera_fps = raw_data[base_keys.CAMERA_FPS]

            self._handle_video_data(frame, camera_frame_width, camera_frame_height, camera_fps)

        if origin == base_keys.CAMERA_WIDGET:
            frame = raw_data[base_keys.CAMERA_FRAME]
            camera_frame_width = raw_data[base_keys.CAMERA_FRAME_WIDTH]
            camera_frame_height = raw_data[base_keys.CAMERA_FRAME_HEIGHT]
            camera_fps = raw_data[base_keys.CAMERA_FPS]

            self._handle_video_data(frame, camera_frame_width, camera_frame_height, camera_fps)

    def _handle_video_data(self, frame, camera_frame_width, camera_frame_height, camera_fps):
        # _logger.debug("_handle_video_data - camera_frame_width: {camera_frame_width}, "
        #               "camera_frame_height: {camera_frame_height}, camera_fps: {camera_fps}",
        #               camera_frame_width=camera_frame_width, camera_frame_height=camera_frame_height,
        #               camera_fps=camera_fps)
        if self.save:
            if self.video_writer is None:
                self.video_writer = cv2.VideoWriter(self.save_path, cv2.VideoWriter_fourcc(*'XVID'), camera_fps,
                                                    (camera_frame_width, camera_frame_height))
            else:
                self.video_writer.write(frame)

        cv2.imshow("VideoOutput", frame)
        cv2.waitKey(_IMAGE_DISPLAY_DELAY_MILLISECONDS)

    def stop(self):
        if self.video_writer is not None:
            self.video_writer.release()
            self.video_writer = None

        cv2.destroyAllWindows()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()
