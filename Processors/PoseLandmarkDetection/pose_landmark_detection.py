import cv2
import mediapipe as mp
import numpy as np
from mediapipe import solutions
from mediapipe.framework.formats import landmark_pb2
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

from Utilities import environment_utility, file_utility

_MODEL_ASSET_PATH = environment_utility.get_env_string("POSE_LANDMARK_MODEL")


class PoseLandmark:
    """
    Represents a single pose landmark with position and visibility.
    """

    def __init__(self, x: float, y: float, z: float, visibility: float):
        self.x = x
        self.y = y
        self.z = z
        self.visibility = visibility

    def to_dict(self):
        return {
            "x": self.x,
            "y": self.y,
            "z": self.z,
            "visibility": self.visibility
        }


class Poses:
    """
    Stores pose detection results (for multiple people) in a picklable format.
    """

    def __init__(self, all_landmarks: list[list[PoseLandmark]]):
        self.all_landmarks = all_landmarks  # Each item is a list of landmarks for one person

    @classmethod
    def from_mediapipe(cls, mp_result):
        """
        Converts a MediaPipe PoseLandmarkerResult to a picklable PoseDetection.
        See: https://ai.google.dev/edge/mediapipe/solutions/vision/pose_landmarker/python#handle_and_display_results

        Args:
            mp_result: MediaPipe PoseLandmarkerResult object

        Returns:
            PoseDetection instance with all landmarks
        """
        all_landmarks = []

        for person_landmarks in mp_result.pose_landmarks:
            landmarks = [
                PoseLandmark(
                    x=lm.x,
                    y=lm.y,
                    z=lm.z,
                    visibility=lm.visibility
                )
                for lm in person_landmarks
            ]
            all_landmarks.append(landmarks)

        return cls(all_landmarks)


class PoseLandmarkDetection:
    """
       Use MediaPipe for face detection with OpenCV frames

       Details: https://ai.google.dev/edge/mediapipe/solutions/vision/pose_landmarker
       """

    def __init__(self):
        model_absolute_path = file_utility.get_path_with_filename(file_utility.get_project_root(), _MODEL_ASSET_PATH)
        base_options = python.BaseOptions(model_asset_path=model_absolute_path)
        options = vision.PoseLandmarkerOptions(base_options=base_options,
                                               output_segmentation_masks=True,
                                               running_mode=vision.RunningMode.IMAGE,
                                               num_poses=1,
                                               min_pose_detection_confidence=0.6,
                                               min_pose_presence_confidence=0.5,
                                               min_tracking_confidence=0.5)
        self.detector = vision.PoseLandmarker.create_from_options(options)

    def detect(self, frame: np.ndarray):
        """
        Detect pose landmarks in a frame

        Args:
            frame: OpenCV frame (BGR format)

        Returns:
            MediaPipe detection result
        """

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # Convert BGR to RGB for MediaPipe
        image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        return self.detector.detect(image)

    def close(self):
        """Release resources if needed"""
        # MediaPipe detector doesn't require explicit closing


def draw_landmarks_on_image(frame, detection_result):
    """
    Draw pose landmarks on the input frame

    Args:
        frame: OpenCV frame (BGR format)
        detection_result: MediaPipe pose detection result

    Returns:
        Annotated image with landmarks
    """
    pose_landmarks_list = detection_result.pose_landmarks
    if not pose_landmarks_list:
        return frame  # Return original frame if no landmarks detected

    annotated_image = np.copy(frame)

    # Loop through the detected poses to visualize
    for idx in range(len(pose_landmarks_list)):
        pose_landmarks = pose_landmarks_list[idx]

        # Draw the pose landmarks
        pose_landmarks_proto = landmark_pb2.NormalizedLandmarkList()
        pose_landmarks_proto.landmark.extend([
            landmark_pb2.NormalizedLandmark(x=landmark.x, y=landmark.y, z=landmark.z) for landmark in pose_landmarks
        ])
        solutions.drawing_utils.draw_landmarks(
            annotated_image,
            pose_landmarks_proto,
            solutions.pose.POSE_CONNECTIONS,
            solutions.drawing_styles.get_default_pose_landmarks_style())

    return annotated_image
