from DataFormat.ProtoFiles.Dashboard import dashboard_live_running_data_pb2
from Services.running_service.running_service_params import BaseParams
from Utilities import time_utility
from Utilities.format_utility import convert_m_s_to_min_km


##############################################################################################################
############################################## running live data #############################################
##############################################################################################################


def build_real_running_data_for_dashboard(decoded_data):
    data = dashboard_live_running_data_pb2.DashboardLiveRunningData()
    data.timestamp = time_utility.get_current_millis()
    data.start_time = int(decoded_data["start_time"])
    data.calories = int(decoded_data["calories"])
    data.heart_rate = int(decoded_data["heart_rate"])
    data.distance = decoded_data["distance"] / 1000
    data.speed = -1.0
    if decoded_data["speed"] != -1.0:
        data.speed = convert_m_s_to_min_km(decoded_data["speed"])
    data.avg_speed = -1.0
    if data.distance != 0:
        data.avg_speed = BaseParams.total_sec / data.distance
    data.bearing = int(decoded_data["bearing"])
    data.curr_lat = float(decoded_data.get("curr_lat", 0.0))
    data.curr_lng = float(decoded_data.get("curr_lng", 0.0))
    return data
