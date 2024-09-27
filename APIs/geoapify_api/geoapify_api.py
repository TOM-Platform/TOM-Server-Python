# source: https://apidocs.geoapify.com/

import json
from io import BytesIO
import requests
from PIL import Image

import base_keys
from Utilities import file_utility, logging_utility
from Utilities.file_utility import get_credentials_file_path

GEOAPIFY_CREDENTIAL_FILE = get_credentials_file_path(base_keys.GEOAPIFY_CREDENTIAL_FILE_KEY_NAME)
KEY_MAP_API = 'map_api_key'
api_key = None

GEOAPIFY_BASE_STATIC_MAP_URL = "https://maps.geoapify.com/v1/staticmap"

_logger = logging_utility.setup_logger(__name__)


def read_geoapify_credential():
    '''
    This method reads the Geoapify credentials from the file.
    :return: {"map_api_key": "YYY"}
    '''
    _logger.info('Reading Geoapify credentials')
    return file_utility.read_json_file(GEOAPIFY_CREDENTIAL_FILE)


def get_geoapify_credential(key, credential=None):
    _credential = credential
    if _credential is None:
        _credential = read_geoapify_credential()
    else:
        _credential = credential

    return _credential[key]


async def find_static_maps_geoapify(coordinates, size):
    global api_key
    if api_key is None:
        api_key = get_geoapify_credential(KEY_MAP_API)

    base_url = GEOAPIFY_BASE_STATIC_MAP_URL
    start_coordinate = coordinates[0]
    markers_str = f"lonlat:{start_coordinate[1]},{start_coordinate[0]};" \
                  "color:%230000ff;type:material;" \
                  "size:small;iconsize:small"

    if len(coordinates) > 1:
        end_coordinate = coordinates[-1]
        markers_str += f"|lonlat:{end_coordinate[1]},{end_coordinate[0]};" \
                       "color:%23ff0000;type:material;" \
                       "size:small;iconsize:small"

    path_str = "polyline:" + ",".join(f"{lng},{lat}" for lat, lng in coordinates) + ";linecolor:%23ff0000"

    url = f"{base_url}?apiKey={api_key}&width={size[0]}&height={size[1]}&marker={markers_str}&geometry={path_str}"

    # successful response just returns the image of origin to destination encoded as bytes
    response = requests.get(url)

    if response.status_code == 200:
        # Uncomment to show/save image in a jpg file
        image = Image.open(BytesIO(response.content))
        image.show()
        # image.save("static_map_1.jpeg", format="JPEG", quality=100)
        return response.content

    error_data = json.loads(response.content)
    error_message = error_data.get("message", "Unknown error")
    raise Exception(error_message)
