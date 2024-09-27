# coding=utf-8

# Ref:
# - https://docs.microsoft.com/en-us/windows/mixed-reality/develop/advanced-concepts/device-portal-api-reference
# - https://docs.microsoft.com/en-us/windows/uwp/debug-test-perf/device-portal-api-core


import base_keys
from Utilities import network_utility, file_utility, environment_utility, logging_utility
from Utilities.file_utility import get_credentials_file_path

# Note: Need to disable SSL connection (System->Preference)
DEVICE_STREAM_SETTINGS = "holo=true&pv=true&mic=false&loopback=true"

CREDENTIALS = None
HOLOLENS_IP = None
DEVICE_PORTAL_USERNAME = None
DEVICE_PORTAL_PASSWORD = None

API_BASE = None
# POST
API_START_RECORDING = None
API_STOP_RECORDING = None
API_GET_RECORDINGS = None
API_GET_RECORDING_STATUS = None
API_TAKE_PHOTO = None

API_STREAM_VIDEO = None

_logger = logging_utility.setup_logger(__name__)


def read_hololens_credential():
    _logger.info('Reading HoloLens credentials')
    hololens_credential_file = get_credentials_file_path(base_keys.HOLOLENS_CREDENTIALS_FILE_KEY_NAME)
    return file_utility.read_json_file(hololens_credential_file)


def set_api_credentials():
    """
    Set the API credentials before calling the rest of functions
    :return:
    """
    global CREDENTIALS, HOLOLENS_IP, DEVICE_PORTAL_USERNAME, DEVICE_PORTAL_PASSWORD, \
        API_BASE, API_START_RECORDING, API_STOP_RECORDING, API_GET_RECORDINGS, API_GET_RECORDING_STATUS, \
        API_TAKE_PHOTO, API_STREAM_VIDEO

    CREDENTIALS = read_hololens_credential()
    HOLOLENS_IP = CREDENTIALS['ip']
    DEVICE_PORTAL_USERNAME = CREDENTIALS['username']
    DEVICE_PORTAL_PASSWORD = CREDENTIALS['password']

    _logger.info('HOLOLENS_IP: {ip}', ip=HOLOLENS_IP)

    API_BASE = f'https://{HOLOLENS_IP}/api'

    # POST
    API_START_RECORDING = f'{API_BASE}/holographic/mrc/video/control/start?' \
                          'holo=true&pv=true&mic=true&loopback=true&RenderFromCamera=true'
    API_STOP_RECORDING = f'{API_BASE}/holographic/mrc/video/control/stop'  # POST
    API_GET_RECORDINGS = f'{API_BASE}/holographic/mrc/files'  # GET
    API_GET_RECORDING_STATUS = f'{API_BASE}/holographic/mrc/status'  # GET
    API_TAKE_PHOTO = f'{API_BASE}/holographic/mrc/photo?holo=true&pv=true'  # POST

    API_STREAM_VIDEO = f'https://{DEVICE_PORTAL_USERNAME}:{DEVICE_PORTAL_PASSWORD}@{HOLOLENS_IP}/' \
                       f'api/holographic/stream/live_med.mp4?{DEVICE_STREAM_SETTINGS}'


def set_hololens_as_camera():
    environment_utility.set_env_variable(base_keys.CAMERA_VIDEO_SOURCE, API_STREAM_VIDEO)


# return True if success else False
def start_recording():
    return network_utility.send_post_request(API_START_RECORDING, "", CREDENTIALS)


# return True if success else False
def stop_recording():
    return network_utility.send_post_request(API_STOP_RECORDING, "", CREDENTIALS)


def take_photo():
    return network_utility.send_post_request(API_TAKE_PHOTO, "", CREDENTIALS)


# return list of files ([{'CreationTime': xx, 'FileName': 'xx.mp4', 'FileSize': xx}])
def get_saved_recordings():
    res = network_utility.send_get_request(API_GET_RECORDINGS, CREDENTIALS)
    if res is None or not res:
        return []

    return res['MrcRecordings']


# return True if recording
def get_recording_status():
    res = network_utility.send_get_request(API_GET_RECORDING_STATUS, CREDENTIALS)
    if res is None:
        return False

    return res['IsRecording']
