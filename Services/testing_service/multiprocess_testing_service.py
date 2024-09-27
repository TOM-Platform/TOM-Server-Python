import base_keys
from DataFormat import datatypes_helper
from DataFormat.ProtoFiles.Common import request_data_pb2
from base_component import BaseComponent
from Utilities import time_utility

_KEY_LAST_DETECTION_TIME = "LAST_DETECTION_TIME"


class TestingService(BaseComponent):
    """
    This service processes data from different sources (YOLOv8 and WebSocket) and manages memory data related to
    detections. It handles both camera detection  data and WebSocket messages, performing actions based on the
    source of the data.
    """

    def run(self, raw_data):
        super().set_component_status(base_keys.COMPONENT_IS_RUNNING_STATUS)

        origin = raw_data[base_keys.ORIGIN_KEY]

        if origin == base_keys.YOLOV8_PROCESSOR:
            self._handle_camera_data(raw_data)

        if origin == base_keys.WEBSOCKET_WIDGET:
            datatype = raw_data[base_keys.WEBSOCKET_DATATYPE]
            data = raw_data[base_keys.WEBSOCKET_MESSAGE]

            data = datatypes_helper.convert_json_to_protobuf(datatype, data)

            self._handle_websocket_data(datatype, data)

    def _handle_camera_data(self, raw_data):
        super().set_memory_data(base_keys.YOLOV8_LAST_DETECTION,
                                raw_data[base_keys.YOLOV8_LAST_DETECTION])
        super().set_memory_data(base_keys.YOLOV8_CLASS_LABELS,
                                raw_data[base_keys.YOLOV8_CLASS_LABELS])

        super().set_memory_data(_KEY_LAST_DETECTION_TIME, time_utility.get_time_string())

    def _handle_websocket_data(self, socket_data_type, decoded_data):
        print(f"Socket data type: {socket_data_type}, Decoded data: {decoded_data}")

        frame_detections = super().get_memory_data(base_keys.YOLOV8_LAST_DETECTION)
        class_labels = super().get_memory_data(base_keys.YOLOV8_CLASS_LABELS)

        last_detection_time = super().get_memory_data(_KEY_LAST_DETECTION_TIME)

        print(f"Last camera detection time: {last_detection_time}")

        if not frame_detections:
            print("No memory camera data")
        else:
            unique_objects = self._get_unique_objects(frame_detections, class_labels)
            print(f'Objects[{len(unique_objects)}]: {unique_objects}')

            if len(unique_objects) > 0:
                # build websocket data
                request_data_proto = request_data_pb2.RequestData(
                    detail=unique_objects[0],
                )
                # send to websocket output
                super().send_to_component(websocket_message=request_data_proto)

    @staticmethod
    def _get_unique_objects(detections, class_labels):
        confidence_threshold = 0.30
        class_ids = []
        confidences = []

        num_detections = len(detections['xyxy'])

        for i in range(0, num_detections):
            class_id = detections['class_id'][i]
            confidence = detections['confidence'][i]
            if confidence > confidence_threshold:
                class_ids.append(class_id)
                confidences.append(confidence)

        if len(class_ids) == 0:
            return []

        # TODO: sort by confidence
        unique_objects = [class_labels[class_id] for class_id in set(class_ids)]
        return unique_objects
