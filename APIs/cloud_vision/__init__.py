import base_keys
from Utilities.environment_utility import set_env_variable
from Utilities.file_utility import get_credentials_file_path
from Utilities import logging_utility

_logger = logging_utility.setup_logger(__name__)


def _set_google_cloud_api_key():
    _logger.info('Setting Google credentials')
    # The Google Cloud Library looks for this "GOOGLE_APPLICATION_CREDENTIALS" in
    # the environment variable by default (source: https://cloud.google.com/docs/authentication/application-default-credentials)
    google_cloud_credentials_file = get_credentials_file_path(
        base_keys.GOOGLE_CLOUD_CREDENTIAL_FILE_KEY_NAME)
    set_env_variable("GOOGLE_APPLICATION_CREDENTIALS", google_cloud_credentials_file)


_set_google_cloud_api_key()
