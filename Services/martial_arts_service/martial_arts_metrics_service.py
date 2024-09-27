from collections import defaultdict

from google.protobuf.json_format import MessageToDict

from DataFormat.ProtoFiles.MartialArts import ma_post_session_metrics_pb2
from Database import tables
from . import martial_arts_const
from .martial_arts_keys import MA_POST_SESSION_METRICS_DATA


class MartialArtsMetricsService:
    """
    MartialArtsMetricsService handles recording, processing, and saving the metrics data generated during a martial
    arts session. It provides real-time feedback and generates post-session reports for the user.
    """

    def __init__(self, martial_arts_service) -> None:
        self.martial_arts_service = martial_arts_service

        # just store the metrics that were sent over, once session ends can do processing of these data and saving to DB
        self.metrics_data_list = []

    def reset(self) -> None:
        self.metrics_data_list = []

    def record_metrics(self, decoded_data, feedback_category) -> None:
        if not decoded_data:
            return

        # convert protobuf to dict to allow assignment of feedback category
        data_dict = MessageToDict(decoded_data)
        data_dict["feedback_category"] = feedback_category

        self.metrics_data_list.append(data_dict)

    # Process metrics for user to see post-session feedback and save to DB
    def process_save_metrics(self, end_session_data) -> None:
        # process raw metrics data
        processed_metrics = self.process_metrics(end_session_data)
        post_session_metrics_data = self.get_post_session_metrics(processed_metrics, end_session_data)
        # send to user some post-session metrics
        self.martial_arts_service.send_to_component(websocket_message=post_session_metrics_data,
                                                    websocket_datatype=MA_POST_SESSION_METRICS_DATA)
        # # save to DB
        tables.insert_rows_to_table(
            martial_arts_const.METRICS_TABLE_NAME, processed_metrics)

    def get_post_session_metrics(self, processed_metrics, end_session_data) \
            -> ma_post_session_metrics_pb2.MaPostSessionMetrics:
        post_session_metrics_data = ma_post_session_metrics_pb2.MaPostSessionMetrics()
        post_session_metrics_data.total_punches = processed_metrics[martial_arts_const.TOTAL_PUNCHES_KEY]
        post_session_metrics_data.correct_punches = processed_metrics[martial_arts_const.GOOD_PUNCH]
        post_session_metrics_data.off_target_punches = processed_metrics[martial_arts_const.OFF_TARGET]
        post_session_metrics_data.bad_angle_punches = processed_metrics[martial_arts_const.BAD_ANGLE]

        if processed_metrics[martial_arts_const.TOTAL_PUNCHES_KEY] > 0:
            post_session_metrics_data.avg_reaction_time = processed_metrics[
                                                              martial_arts_const.TOTAL_REACTION_TIME_KEY] / \
                                                          processed_metrics[martial_arts_const.TOTAL_PUNCHES_KEY]
        else:
            post_session_metrics_data.avg_reaction_time = 0

        post_session_metrics_data.session_duration = end_session_data.session_duration
        return post_session_metrics_data

    def process_metrics(self, end_session_data) -> dict:
        processed_metrics = {
            martial_arts_const.TOTAL_REACTION_TIME_KEY: 0,
            martial_arts_const.RAW_DATA_KEY: self.metrics_data_list,
            martial_arts_const.PUNCH_DICT_KEY: defaultdict(int),
            martial_arts_const.GOOD_PUNCH: 0,
            martial_arts_const.OFF_TARGET: 0,
            martial_arts_const.BAD_ANGLE: 0,
            martial_arts_const.TOTAL_PUNCHES_KEY: 0,
            martial_arts_const.UNCATEGORIZED_PUNCHES_KEY: 0,
            martial_arts_const.DATETIME: end_session_data.datetime,
            martial_arts_const.SESSION_DURATION: end_session_data.session_duration,
            martial_arts_const.INTERVAL_DURATION: end_session_data.interval_duration,
        }
        total_punches = 0

        for metrics_data in self.metrics_data_list:
            total_punches += 1

            processed_metrics[martial_arts_const.TOTAL_REACTION_TIME_KEY] += metrics_data['reactionTime']

            if metrics_data["punchData"]:
                punch_type = metrics_data["punchData"]["punchType"]
                if punch_type in processed_metrics[martial_arts_const.PUNCH_DICT_KEY]:
                    processed_metrics[martial_arts_const.PUNCH_DICT_KEY][punch_type] += 1
                else:
                    processed_metrics[martial_arts_const.PUNCH_DICT_KEY][punch_type] = 1
            if metrics_data["feedback_category"]:
                category = metrics_data["feedback_category"]
                processed_metrics[category] += 1
            else:
                processed_metrics[martial_arts_const.UNCATEGORIZED_PUNCHES_KEY] += 1

        processed_metrics[martial_arts_const.TOTAL_PUNCHES_KEY] = total_punches

        return processed_metrics
