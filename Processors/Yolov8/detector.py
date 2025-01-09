import base_keys
from base_component import BaseComponent
from Processors.Yolov8.video_detection import VideoDetection as video_detector


class Yolov8Detector(BaseComponent):
    """
    Sends 4 different key-value data pairs to the next component:
    1. last_detection
    2. yolo_frame : The annotated frame after yolov8 model has run on the raw camera frame
    3. class_labels : The class labels of detected objects in the raw camera frame
    4. base_data : The data sent through by the previous component (camera_widget) to this component, includes the raw
        camera frame as well as frame details
    """
    writer = None

    def __init__(self, name):
        super().__init__(name)

        self.detector = video_detector(exclude_class_ids=list(range(1,100)))

    def run(self, raw_data):
        super().set_component_status(base_keys.COMPONENT_IS_RUNNING_STATUS)

        frame = raw_data[base_keys.CAMERA_FRAME]
        yolo_frame = self.detector.run(frame)

        super().send_to_component(last_detection=self.detector.get_last_detection(),
                                  yolo_frame=yolo_frame,
                                  class_labels=self.detector.get_class_labels(),
                                  base_data=raw_data)

