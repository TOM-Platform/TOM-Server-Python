import time
from collections import Counter
from Utilities import logging_utility

_logger = logging_utility.setup_logger(__name__)

class ObjectDetectionCounter:
    def __init__(
            self,
            counter_window_duration=1,  # window duration to keep track of objects in seconds
    ):
        self.counter_window_duration = counter_window_duration
        self.detected_objects = []
        self.detected_times = []

    # detection = [[bounding_boxes, mask, confidence, class_id, tracker_id], ...], class_labels = [name1, name2, ...]
    def infer_counting(self, detections, class_labels):
        current_time = time.time()
        self.detected_times.append(current_time)

        objects = [class_labels[class_id] for _, _, _, class_id, _ in detections]
        self.detected_objects.append(objects)

        index = 0
        for i in range(len(self.detected_times)):
            if self.detected_times[i] < current_time - self.counter_window_duration:
                index += 1
            else:
                break

        self.detected_times = self.detected_times[index:]
        self.detected_objects = self.detected_objects[index:]

        return self

    def get_detected_objects(self):
        return self.detected_objects.copy()

    def get_detected_object_percentage(self):
        detected_objects = self.detected_objects
        detected_objects_instances = len(detected_objects)
        detected_objects_flat = [j for sub in detected_objects for j in sub]
        counts = Counter(detected_objects_flat)
        percentage = {}
        for i, count in counts.most_common():
            # _logger.debug(i, counts[i], count, detected_objects_instances)
            percentage[i] = count / detected_objects_instances

        return percentage
