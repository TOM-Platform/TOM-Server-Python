import base_keys
from base_component import BaseComponent
from Processors.FaceDetection.face_detection import visualize, FaceDetection, Faces


class FaceDetector(BaseComponent):
    """
        A component that performs face detection on incoming (camera) frames.

        This component receives (camera) frame data from a previous component (such as a camera widget), uses a face
        detection model to identify  faces in the frame, and outputs:

        1. face_frame: The original frame annotated with bounding boxes or landmarks for detected faces.
        2. face_detection: The most recent face detection results (e.g., bounding box coordinates).
        3. base_data: The unmodified input data passed from the previous component, including the original camera frame
        and metadata (e.g., dimensions, FPS).

        The component manages its lifecycle status and uses a face detection processor under the hood for the detection
        step.
        """

    def __init__(self, name):
        super().__init__(name)
        super().set_component_status(base_keys.COMPONENT_NOT_STARTED_STATUS)
        self.detector = FaceDetection()

    def run(self, raw_data):
        if super().get_component_status() != base_keys.COMPONENT_IS_RUNNING_STATUS:
            super().set_component_status(base_keys.COMPONENT_IS_RUNNING_STATUS)

        # OpenCV frame (numpy array)
        frame = raw_data[base_keys.CAMERA_FRAME]

        # Detect faces
        mediapipe_detection_result = self.detector.detect(frame)

        # Annotate
        annotated_image = visualize(frame, mediapipe_detection_result)

        # Convert to supported format
        detection_results = Faces.from_mediapipe(mediapipe_detection_result)

        super().send_to_component(
            face_frame=annotated_image,
            face_detection=detection_results,
            base_data=raw_data)

    def close(self):
        super().set_component_status(base_keys.COMPONENT_IS_STOPPED_STATUS)
        self.detector.close()
