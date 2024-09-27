import cv2

import base_keys
from base_component import BaseComponent
from Utilities.video_stream import VideoStream
from Utilities import environment_utility, time_utility, file_utility, logging_utility

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
        while self.setup_error:
            _logger.error("Error occurred setting up camera widget")

            if self.retry:
                time_utility.sleep_seconds(1)
                self.__set_video_source(self.video_path)
            else:
                # If do not retry, stop execution of camera widget
                return

        _logger.info("Listening on CameraWidget")
        super().set_component_status(base_keys.COMPONENT_IS_RUNNING_STATUS)

        while True:
            try:
                if self.useStream:
                    frame = self.stream.read()
                else:
                    frame = self.capture.read()[1]
            except Exception:
                _logger.exception("Error Reading Frame with message")

            camera_fps, frame_width, frame_height = self.__get_capture_details()

            super().send_to_component(camera_frame=frame,
                                      camera_frame_width=frame_width,
                                      camera_frame_height=frame_height,
                                      camera_fps=camera_fps)
            """
            Note that you cannot directly save camera frames in the database since it is a NumPy Array, 
            which is not supported in SQLAlchemy.  An alternative would be to serialise it into Json which is accepted.
            Refer to this: https://stackoverflow.com/questions/61370118/storing-arrays-in-database-using-sqlalchemy
            """

    def __set_video_source(self, new_video_path):
        _logger.info("Video Path: {path}", path=new_video_path)

        if self.captureInProgress:
            self.captureInProgress = False

        if self.capture:
            self.capture.release()
            self.capture = None
        elif self.stream:
            self.stream.stop()
            self.stream = None

        try:
            self.videoPath = new_video_path
            self.useWebcam = self.__IsCaptureDev(new_video_path)
            self.useStream = self.__IsRtsp(new_video_path)

            if self.useWebcam:
                _logger.info("   - Using webcam")
                self.capture = cv2.VideoCapture(new_video_path)
                if self.capture.isOpened():
                    self.captureInProgress = True
            elif self.useStream:
                _logger.info("   - Using stream")
                self.stream = VideoStream(new_video_path).start()
                time_utility.sleep_seconds(1)  # wait until loading at least one frame
                self.captureInProgress = True
            else:
                _logger.info("   - Using video file")

            if not self.captureInProgress:
                _logger.error("\nWARNING : Failed to Open Video Source\n")

            self.setup_error = False
        except Exception:
            _logger.exception("Error occurred setting up camera widget")
            self.setup_error = True

    def __IsCaptureDev(self, video_path):
        try:
            # Check if video_path is a capture device
            if '/dev/video' in video_path.lower():
                return True
        except (ValueError, AttributeError):
            pass  # Handle case where video_path.lower() fails

        # Check if video_path is an integer, typically representing a camera index
        if isinstance(video_path, int):
            return True

        # Check if video_path is a valid file path
        return file_utility.is_file_exists(video_path)

    def __IsRtsp(self, video_path):
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

        if self.useStream:
            camera_fps = int(self.stream.stream.get(cv2.CAP_PROP_FPS))
            frame_width = int(self.stream.stream.get(cv2.CAP_PROP_FRAME_WIDTH))
            frame_height = int(self.stream.stream.get(cv2.CAP_PROP_FRAME_HEIGHT))
        elif self.useWebcam:
            camera_fps = int(self.capture.get(cv2.CAP_PROP_FPS))
            frame_width = int(self.capture.get(cv2.CAP_PROP_FRAME_WIDTH))
            frame_height = int(self.capture.get(cv2.CAP_PROP_FRAME_HEIGHT))

        if camera_fps == 0:
            raise Exception("Error reading frame : Could not get FPS")

        return (camera_fps, frame_width, frame_height)

    def stop(self):
        _logger.info("Stopping CameraWidget")
        if self.capture:
            self.capture.release()
            self.capture = None
        elif self.stream:
            self.stream.stop()
            self.stream = None

        super().set_component_status(base_keys.COMPONENT_IS_STOPPED_STATUS)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()
