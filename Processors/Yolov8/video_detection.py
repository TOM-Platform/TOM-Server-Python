import supervision as sv
from ultralytics import YOLO
import numpy as np

from Utilities import environment_utility
from .object_detection_counter import ObjectDetectionCounter

_YOLO_MODEL = environment_utility.get_env_string("YOLO_MODEL")
_YOLO_CONFIDENCE_LEVEL = environment_utility.get_env_float("YOLO_CONFIDENCE_LEVEL")
_YOLO_INFERENCE = environment_utility.get_env_bool("YOLO_INFERENCE")
_YOLO_DETECTION_REGION = None
_YOLO_VERBOSE = environment_utility.get_env_bool("YOLO_VERBOSE")

_YOLO_OBJECT_DETECTION_COUNTER_DURATION = 0


class VideoDetection:
    """
    This class performs object detection on video frames using YOLO models,  with optional object counting and
    region-specific detection.
    """

    def __init__(
            self,
            model=_YOLO_MODEL,
            confidence_level=_YOLO_CONFIDENCE_LEVEL,
            inference=_YOLO_INFERENCE,  # set False, to hide object detection boxes
            detection_region=_YOLO_DETECTION_REGION,  # set to None to detect objects in the whole frame
            verbose=_YOLO_VERBOSE,  # set to True to show verbose output
            object_counter_duration=_YOLO_OBJECT_DETECTION_COUNTER_DURATION,  # set 0 to disable
    ):

        self.model = model
        self.confidenceLevel = confidence_level
        self.inference = inference
        self.detection_region = detection_region
        self.verbose = verbose

        if object_counter_duration > 0:
            self.object_detection_counter = ObjectDetectionCounter(object_counter_duration)
        else:
            self.object_detection_counter = None

        self.last_detection = None
        self.class_labels = None

    def get_detect_object_percentage(self):
        if self.object_detection_counter:
            return self.object_detection_counter.get_detected_object_percentage()

        return None

    def run(self, frame):
        # specify the model
        model = YOLO(self.model)

        # customize the bounding box
        box_annotator = sv.BoxAnnotator(
            thickness=2,
            text_thickness=2,
            text_scale=1
        )

        #  iou=0.45, max_det=50, verbose=False
        result = model(frame, agnostic_nms=True, conf=self.confidenceLevel, verbose=self.verbose)[0]

        # [[bounding_boxes, mask, confidence, class_id, tracker_id]
        detections = sv.Detections.from_yolov8(result)

        self.class_labels = model.model.names

        if self.detection_region is not None:
            detections = self.get_detection_in_region(detections, self.detection_region)

        if self.inference:
            labels = [f'{self.class_labels[class_id]} {confidence:0.2f}' for _, _, confidence, class_id, _ in
                      detections]

            frame = box_annotator.annotate(scene=frame, detections=detections, labels=labels)

        if self.object_detection_counter:
            self.object_detection_counter.infer_counting(detections, self.class_labels)

        self.last_detection = detections

        return frame

    # return the class labels of the model, [name1, name2, ...]
    def get_class_labels(self):
        return self.class_labels

    # return the last detection results in the format of [[bounding_boxes, mask, confidence, class_id, tracker_id], ...]
    def get_last_detection(self):
        last_detection = {
            'xyxy': self.last_detection.xyxy,
            'mask': self.last_detection.mask,
            'confidence': self.last_detection.confidence,
            'class_id': self.last_detection.class_id,
            'tracker_id': self.last_detection.tracker_id,
        }

        return last_detection

    @staticmethod
    def get_detection_in_region(detections, detection_region, exclude_class_ids=None):
        if exclude_class_ids is None:
            exclude_class_ids = []

        # initialize an instance of Detection class with empty values
        detections_in_specified_region = sv.Detections(xyxy=np.empty((0, 4)), mask=None,
                                                       confidence=np.empty((0,)),
                                                       class_id=np.empty((0,)),
                                                       tracker_id=None)
        # create temporary lists to store the values of xyxy, class_id and confidence of the objects in given region
        tmp_xyxy = []
        tmp_class_id = []
        tmp_confidence = []

        num_detections = len(detections['xyxy'])

        for i in range(0, num_detections):
            bounding_boxes = detections['xyxy'][i]
            class_id = detections['class_id'][i]
            confidence = detections['confidence'][i]

            # add to detection_results only if the object is in the specified region and not in exclude_class_ids
            if class_id not in exclude_class_ids and VideoDetection.intersects(bounding_boxes, detection_region):
                tmp_xyxy.append(bounding_boxes)
                tmp_class_id.append(class_id)
                tmp_confidence.append(confidence)

        detections_in_specified_region.xyxy = np.array(tmp_xyxy)
        detections_in_specified_region.class_id = np.array(tmp_class_id)
        detections_in_specified_region.confidence = np.array(tmp_confidence)

        return detections_in_specified_region

    @staticmethod
    def intersects(xyxy, xyxy_bounds):
        return not (xyxy[2] < xyxy_bounds[0] or xyxy[0] > xyxy_bounds[2] or xyxy[3] < xyxy_bounds[1]
                    or xyxy[1] > xyxy_bounds[3])

    @staticmethod
    def is_inside(xy, xyxy):
        p_x, p_y = xy
        min_x, min_y, max_x, max_y = xyxy
        return min_x < p_x < max_x and min_y < p_y < max_y
