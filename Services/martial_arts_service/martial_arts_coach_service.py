from DataFormat.ProtoFiles.Common import request_data_pb2
from .martial_arts_keys import MA_FEEDBACK_LIVE_DATA
from . import martial_arts_const


# Generates feedback for user
class MartialArtsCoachService:
    """
    The MartialArtsCoachService class is responsible for analyzing live data from martial arts sessions and generating
    real-time feedback for the user.
    """

    def __init__(self, martial_arts_service) -> None:
        self.martial_arts_service = martial_arts_service
        self.feedback_set = set()
        self.request_data = request_data_pb2.RequestData()

    def send_live_feedback(self, live_feedback) -> None:
        self.request_data.detail = live_feedback
        self.martial_arts_service.send_to_component(websocket_message=self.request_data,
                                                    websocket_datatype=MA_FEEDBACK_LIVE_DATA)
        self.feedback_set.add(live_feedback)
        # return

    def analyse_live_data(self, decoded_data) -> str:
        if not decoded_data or not decoded_data.collision_data:
            return ''

        collision_data = decoded_data.collision_data
        collision_point = collision_data.collision_point
        pad_position = collision_data.pad_position

        collision_x = collision_point.x
        collision_y = collision_point.y

        pad_x = pad_position.x
        pad_y = pad_position.y

        distance_to_target = collision_data.distance_to_target
        if distance_to_target and distance_to_target > martial_arts_const.DISTANCE_TO_TARGET_FEEDBACK_THRESHOLD:
            horizontal_distance = abs(collision_x - pad_x)
            vertical_distance = abs(collision_y - pad_y)

            if horizontal_distance > vertical_distance:
                if collision_x > pad_x:
                    return martial_arts_const.PUNCH_LEFT
                if collision_x < pad_x:
                    return martial_arts_const.PUNCH_RIGHT
            else:
                if collision_y > pad_y:
                    return martial_arts_const.PUNCH_LOWER
                if collision_y < pad_y:
                    return martial_arts_const.PUNCH_HIGHER

        angle = collision_data.angle
        if angle and (
                angle < martial_arts_const.ANGLE_FEEDBACK_THRESHOLD_LOWER or
                angle > martial_arts_const.ANGLE_FEEDBACK_THRESHOLD_HIGHER
        ):
            return martial_arts_const.PUNCH_NOT_STRAIGHT

        return martial_arts_const.GOOD

    def categorize_feedback(self, live_feedback) -> str:
        if live_feedback == martial_arts_const.GOOD:
            return martial_arts_const.GOOD_PUNCH

        if live_feedback in martial_arts_const.OFF_TARGET_FEEDBACK:
            return martial_arts_const.OFF_TARGET

        return martial_arts_const.BAD_ANGLE
