import cv2

import base_keys
from Utilities import environment_utility, time_utility, file_utility, logging_utility
from Utilities.video_stream import VideoStream
from base_component import BaseComponent

# Constants for default values and configurations
_DEFAULT_FRAME_HEIGHT = 480
_DEFAULT_FRAME_WIDTH = 640
_DEFAULT_FRAME_RATE = 30  # fps

_FRAME_WAIT_DELAY_SECONDS = 1.0 / _DEFAULT_FRAME_RATE
_CAPTURE_WAIT_DELAY_SECONDS = 0.5
_VIDEO_WAIT_DELAY_SECONDS = 3

_SETUP_RETRY_ATTEMPTS = 3
_SETUP_RETRY_DELAY_SECONDS = 1

_MAX_EMPTY_FRAME_COUNT_FOR_RESET = 10
_MAX_EMPTY_STREAM_FRAME_COUNT_FOR_LOGGING = 20

_logger = logging_utility.setup_logger(__name__)


class CameraWidget(BaseComponent):
    """
    Sends the camera frames to the next component

    camera_frame: Camera Frame in Numpy Array Format
    camera_frame_width: Width of each frame of the camera_frame
    camera_frame_height: Height of each frame of the camera_frame
    camera_fps: Frames per Seconds (FPS) of each frame of the camera_frame
    """

    def __init__(self, name) -> None:
        super().__init__(name)

        self.video_path = environment_utility.get_env_int_or_string(base_keys.CAMERA_VIDEO_SOURCE)

        self.useStream = False
        self.useWebcam = False
        self.captureInProgress = False
        self.capture = None
        self.stream = None
        self.retry = False

        self.setup_error = False

        _logger.info("CameraWidget::__init__()")
        _logger.info("OpenCV Version : {version}", version=cv2.__version__)
        _logger.info("Initialising CameraWidget with the following parameters: ")

        self.__set_video_source(self.video_path)

    def start(self):
        self._retry_if_setup_errors()
        if self.setup_error:
            _logger.error("Failed to setup camera after maximum retries")
            return

        _logger.info("Listening on CameraWidget")
        super().set_component_status(base_keys.COMPONENT_IS_RUNNING_STATUS)

        empty_frame_count = 0

        while True:
            frame = None
            try:
                if self.useStream:
                    if not self.stream.more():
                        empty_frame_count += 1
                        if empty_frame_count >= _MAX_EMPTY_STREAM_FRAME_COUNT_FOR_LOGGING:
                            _logger.debug("No frame available in stream queue. Waiting ...")
                            empty_frame_count = 0

                        time_utility.sleep_seconds(_FRAME_WAIT_DELAY_SECONDS)
                        continue

                    frame = self.stream.read()

                else:
                    if self.capture is None or not self.capture.isOpened():
                        _logger.error("Capture is not available or not opened")
                        time_utility.sleep_seconds(_CAPTURE_WAIT_DELAY_SECONDS)
                        self.__set_video_source(self.video_path)
                        continue

                    grabbed, frame = self.capture.read()
                    if not grabbed or frame is None:
                        empty_frame_count += 1
                        _logger.warning("Failed to grab frame from capture. Count: {n}", n=empty_frame_count)

                        if empty_frame_count >= _MAX_EMPTY_FRAME_COUNT_FOR_RESET:
                            _logger.warning("Too many consecutive empty frames, resetting capture")
                            self.__set_video_source(self.video_path)
                            empty_frame_count = 0

                        time_utility.sleep_seconds(_FRAME_WAIT_DELAY_SECONDS)
                        continue

                    # Reset counter on successful frame read
                    empty_frame_count = 0

            except Exception:
                _logger.exception("Error Reading Frame")
                time_utility.sleep_seconds(_CAPTURE_WAIT_DELAY_SECONDS)
                continue

            if frame is None or frame.size == 0:
                _logger.warning("Received an empty frame, skipping.")
                time_utility.sleep_seconds(_FRAME_WAIT_DELAY_SECONDS)
                continue

            try:
                camera_fps, frame_width, frame_height = self.__get_capture_details()
                super().send_to_component(camera_frame=frame,
                                          camera_frame_width=frame_width,
                                          camera_frame_height=frame_height,
                                          camera_fps=camera_fps)
            except Exception:
                _logger.exception("Error processing or sending frame")

    def _retry_if_setup_errors(self):
        retry_attempts = 0

        while self.setup_error and retry_attempts < _SETUP_RETRY_ATTEMPTS:
            _logger.error("Error occurred setting up camera widget")

            if self.retry:
                time_utility.sleep_seconds(_SETUP_RETRY_DELAY_SECONDS)
                self.__set_video_source(self.video_path)
                retry_attempts += 1
            else:
                # If do not retry, stop execution of camera widget
                return

    def __set_video_source(self, new_video_path):
        _logger.info("Video Path: {path}", path=new_video_path)

        # Clean up existing resources first
        self.__cleanup_resources()

        try:
            self.videoPath = new_video_path
            self.useWebcam = self.__IsCaptureDev(new_video_path)
            self.useStream = self.__IsRtsp(new_video_path)

            if self.useWebcam:
                _logger.info("   - Using webcam")
                self.capture = cv2.VideoCapture(new_video_path)
                if self.capture.isOpened():
                    # Set some properties for better performance
                    self.capture.set(cv2.CAP_PROP_BUFFERSIZE, 2)
                    self.captureInProgress = True
                else:
                    _logger.error("cv2.VideoCapture failed to open webcam.")
            elif self.useStream:
                _logger.info("   - Using stream")
                self.stream = VideoStream(new_video_path).start()
                for _ in range(int(_VIDEO_WAIT_DELAY_SECONDS / _FRAME_WAIT_DELAY_SECONDS)):
                    time_utility.sleep_seconds(_FRAME_WAIT_DELAY_SECONDS)
                    if self.stream.more():
                        self.captureInProgress = True
                        break
            else:
                _logger.info("   - Using video file")
                self.capture = cv2.VideoCapture(new_video_path)
                if self.capture.isOpened():
                    self.captureInProgress = True
                else:
                    _logger.error("cv2.VideoCapture failed to open video file.")

            if not self.captureInProgress:
                _logger.error("\nWARNING : Failed to Open Video Source\n")
                self.setup_error = True
            else:
                self.setup_error = False

        except Exception:
            _logger.exception("Error occurred setting up camera widget")
            self.setup_error = True

    def __cleanup_resources(self):
        self.captureInProgress = False

        if self.capture:
            try:
                self.capture.release()
            except Exception:
                _logger.exception("Error releasing capture")
            finally:
                self.capture = None

        if self.stream:
            try:
                self.stream.stop()
            except Exception:
                _logger.exception("Error stopping stream")
            finally:
                self.stream = None

    def __IsCaptureDev(self, video_path):
        try:
            # Check if video_path is a capture device
            if isinstance(video_path, str) and '/dev/video' in video_path.lower():
                return True
        except (ValueError, AttributeError):
            pass  # Handle case where video_path.lower() fails

        # Check if video_path is an integer, typically representing a camera index
        if isinstance(video_path, int):
            return True

        # Check if video_path is a valid file path
        return isinstance(video_path, str) and file_utility.is_file_exists(video_path)

    def __IsRtsp(self, video_path):
        if not isinstance(video_path, str):
            return False

        try:
            video_path_lower = video_path.lower()
            # Check for RTSP and other streaming protocols or paths
            if ('rtsp:' in video_path_lower or '/api/holographic/stream' in video_path_lower or
                    'http:' in video_path_lower or 'https:' in video_path_lower):
                return True
        except (ValueError, AttributeError):
            # In case videoPath.lower() raises an error, indicating that videoPath is not a string
            return False

        return False

    def __get_capture_details(self):
        camera_fps = 0
        frame_width = 0
        frame_height = 0

        try:
            if self.useStream and self.stream and hasattr(self.stream, 'stream'):
                camera_fps = int(self.stream.stream.get(cv2.CAP_PROP_FPS))
                frame_width = int(self.stream.stream.get(cv2.CAP_PROP_FRAME_WIDTH))
                frame_height = int(self.stream.stream.get(cv2.CAP_PROP_FRAME_HEIGHT))
            elif self.capture and self.capture.isOpened():
                camera_fps = int(self.capture.get(cv2.CAP_PROP_FPS))
                frame_width = int(self.capture.get(cv2.CAP_PROP_FRAME_WIDTH))
                frame_height = int(self.capture.get(cv2.CAP_PROP_FRAME_HEIGHT))

            # Fallback to default values if any property is missing
            if camera_fps <= 0:
                camera_fps = _DEFAULT_FRAME_RATE
                _logger.warning("Using default FPS value: {camera_fps}", camera_fps=camera_fps)
            if frame_width <= 0:
                frame_width = _DEFAULT_FRAME_WIDTH
                _logger.warning("Using default frame width: {frame_width}", frame_width=frame_width)
            if frame_height <= 0:
                frame_height = _DEFAULT_FRAME_HEIGHT
                _logger.warning("Using default frame height: {frame_height}", frame_height=frame_height)

        except Exception:
            _logger.exception("Error getting capture details")
            # Default values as fallback
            camera_fps = _DEFAULT_FRAME_RATE
            frame_width = _DEFAULT_FRAME_WIDTH
            frame_height = _DEFAULT_FRAME_HEIGHT

        return (camera_fps, frame_width, frame_height)

    def stop(self):
        _logger.info("Stopping CameraWidget")
        self.__cleanup_resources()
        super().set_component_status(base_keys.COMPONENT_IS_STOPPED_STATUS)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()
