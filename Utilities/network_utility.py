# coding=utf-8

import requests
from Utilities import logging_utility

_REQUEST_TIMEOUT_SECONDS = 3  # 3 seconds

_logger = logging_utility.setup_logger(__name__)


# return True if success else False
def send_post_request(url, data, credentials=None):
    _logger.debug('POST Request: {url}, {data}', url=url, data=data)

    try:
        if credentials is None:
            x = requests.post(url, data=str(data).encode('ascii', 'ignore'),
                              timeout=_REQUEST_TIMEOUT_SECONDS, verify=False)
        else:
            x = requests.post(url, data=str(data).encode('ascii', 'ignore'),
                              timeout=_REQUEST_TIMEOUT_SECONDS, verify=False,
                              auth=(credentials['username'], credentials['password']))
        _logger.debug("status_code: {status_code}", status_code=x.status_code)
        return True
    except Exception as e:
        _logger.warning('Failed POST request', e)
        return False


def send_get_request(url, credentials=None):
    '''

    ref: https://requests.readthedocs.io/en/latest/user/quickstart/

    :param url:
    :param credentials:
    :return: json objects if success else None
    '''
    _logger.info('GET Request: {url}', url=url)

    try:
        if credentials is None:
            x = requests.get(url, timeout=_REQUEST_TIMEOUT_SECONDS, verify=False)
        else:
            x = requests.get(url, timeout=_REQUEST_TIMEOUT_SECONDS, verify=False,
                             auth=(credentials['username'], credentials['password']))
        _logger.debug("status_code: {status_code}", status_code=x.status_code)
        return x.json()
    except Exception as e:
        _logger.warning('Failed GET request', e)
        return None
