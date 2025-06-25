from base_component import BaseComponent
import base_keys
from Processors.PoseLandmarkDetection.pose_landmark_detection import draw_landmarks_on_image, PoseLandmarkDetection, \
    Poses


class PoseLandmarkDetector(BaseComponent):
    """
    A component that performs pose landmark detection on incoming (camera) frames.

    This component receives (camera) frame data from a previous component (e.g., a camera widget), processes the frame
    to detect pose landmarks, and sends two outputs to the next component:

    1. pose_frame: The camera frame annotated with pose landmarks.
    2. pose_detection: The most recent poses (i.e., pose landmarks) detected.
    3. base_data: The original input data received from the previous component, including the unmodified camera frame
    and associated metadata (e.g., resolution, FPS).

    The component maintains and updates its internal status during processing, and uses MediaPipe's pose landmark
    detection under the hood.
    """

    def __init__(self, name):
        super().__init__(name)
        super().set_component_status(base_keys.COMPONENT_NOT_STARTED_STATUS)
        self.detector = PoseLandmarkDetection()

    def run(self, raw_data):
        if super().get_component_status() != base_keys.COMPONENT_IS_RUNNING_STATUS:
            super().set_component_status(base_keys.COMPONENT_IS_RUNNING_STATUS)

        # OpenCV frame (numpy array)
        frame = raw_data[base_keys.CAMERA_FRAME]

        # Detects pose landmarks
        mediapipe_detection_result = self.detector.detect(frame)

        # Annotate
        annotated_image = draw_landmarks_on_image(frame, mediapipe_detection_result)

        # Convert to supported format
        detection_results = Poses.from_mediapipe(mediapipe_detection_result)

        super().send_to_component(
            pose_frame=annotated_image,
            pose_detection=detection_results,
            base_data=raw_data)

    def close(self):
        super().set_component_status(base_keys.COMPONENT_IS_STOPPED_STATUS)
        self.detector.close()
