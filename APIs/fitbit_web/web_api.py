# wrapper for https://github.com/orcasgit/python-fitbit
import datetime
import json

import fitbit
import pandas as pd

import base_keys
from Utilities import file_utility, logging_utility
from Utilities.file_utility import get_credentials_file_path
from . import gather_keys_oauth2 as Oauth2

# DO NOT CHANGE FOLLOWING
DATA_TYPE_HEART_RATE = 'activities/heart'
DATA_TYPE_STEPS = 'activities/steps'
DATA_TYPE_DISTANCE = 'activities/distance'
DATA_TYPE_ELEVATION = 'activities/elevation'
DATA_TYPE_CALORIES = 'activities/calories'
# DATA_TYPE_SPO2 = 'spo2'
# DATA_TYPE_BREATHING_RATE = 'br'

DETAIL_LEVEL_1SEC = '1sec'
DETAIL_LEVEL_1MIN = '1min'
DETAIL_LEVEL_5MIN = '5min'
DETAIL_LEVEL_15MIN = '15min'

KEY_CLIENT_ID = 'client_id'
KEY_CLIENT_SECRET = 'client_secret'

# has the 'access_token' and 'refresh_token'
FITBIT_TOKEN_FILE = 'credential/fitbit_token.json'
KEY_ACCESS_TOKEN = 'access_token'
KEY_REFRESH_TOKEN = 'refresh_token'
FITBIT_CREDENTIAL_FILE = get_credentials_file_path(base_keys.FITBIT_CREDENTIAL_FILE_KEY_NAME)

# how long the token is valid for 8 hours
FITBIT_TOKEN_TOKEN_AGE_SECONDS = 8 * 60 * 60

TODAY = str(datetime.datetime.now().strftime("%Y-%m-%d"))  # 'yyyy-MM-dd'

_logger = logging_utility.setup_logger(__name__)


# return {'client_id': XX, 'client_secret': XX}
def read_fitbit_credential():
    _logger.info('Reading Fitbit credentials')
    return file_utility.read_json_file(FITBIT_CREDENTIAL_FILE)


def read_fitbit_token():
    _logger.info('Reading Fitbit token')

    if not file_utility.is_file_exists(FITBIT_TOKEN_FILE):
        return None

    if file_utility.is_file_older_than(FITBIT_TOKEN_FILE, FITBIT_TOKEN_TOKEN_AGE_SECONDS):
        return None

    return file_utility.read_json_file(FITBIT_TOKEN_FILE)


def save_fitbit_token(token):
    try:
        with open(FITBIT_TOKEN_FILE, 'w') as outfile:
            json.dump(token, outfile)
    except Exception as e:
        _logger.error('Failed to save order data: {fitbit_file}, {e_class}',
                      e_class=e.__class__, fitbit_file=FITBIT_TOKEN_FILE)


def get_authorize_token(credential):
    '''

    :param credential:
    :return: {'access_token': XX, 'refresh_token': XX}
    '''
    server = Oauth2.OAuth2Server(credential[KEY_CLIENT_ID], credential[KEY_CLIENT_SECRET])
    server.browser_authorize()
    return {KEY_ACCESS_TOKEN: str(server.fitbit.client.session.token['access_token']),
            KEY_REFRESH_TOKEN: str(server.fitbit.client.session.token['refresh_token'])}


def get_auth_client(credential, token):
    return fitbit.Fitbit(credential[KEY_CLIENT_ID], credential[KEY_CLIENT_SECRET], oauth2=True,
                         access_token=token[KEY_ACCESS_TOKEN],
                         refresh_token=token[KEY_REFRESH_TOKEN])


# see https://dev.fitbit.com/build/reference/web-api/intraday/get-activity-intraday-by-interval/ for data format
# date = <yyyy-MM-dd>, type = <DATA_TYPE_...>, detail_level = <DETAIL_LEVEL_...>, time = <HH:mm>,
def get_json_data(auth_client, date, data_type, detail_level, start_time=None, end_time=None):
    return auth_client.intraday_time_series(data_type, base_date=date, detail_level=detail_level,
                                            start_time=start_time, end_time=end_time)


# "activities-steps": [
#     {
#         "dateTime": "2019-01-01",
#         "value": "0"
#     }
# ],
# return 'date' (YYYY-MM-DD), 'count'
def get_date_and_count(json_data, data_type):
    type_key = data_type.replace("/", "-")
    data = json_data[type_key]
    return data['dateTime'], data['value']


# "activities-steps-intraday": {
#     "dataset": [
#         {
#             "time": "08:00:00",
#             "value": 0
#         },
#         {
#             "time": "08:01:00",
#             "value": 0
#         },
#         {
#             "time": "08:02:00",
#             "value": 0
#         },
# return data_frame with 'time' and 'value'
def get_data_frame(json_data, data_type):
    type_key = data_type.replace("/", "-") + "-intraday"
    return pd.DataFrame(json_data[type_key]['dataset'])
