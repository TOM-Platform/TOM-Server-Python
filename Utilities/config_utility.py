from os import listdir, getcwd
from Utilities import file_utility, logging_utility

configuration = {}

CFG_TYPES = ["input", "processing", "service", "output"]
CONFIG_DIR = getcwd() + "/Config"

CONFIGURATION_CHANNELS_KEY = "channels"
CONFIGURATION_CHANNEL_PIPES_KEY = "channel-pipes"
CONFIGURATION_CHANNELS_ENTRYPOINTS_KEY = "channel-entrypoints"
CONFIGURATION_CHANNELS_EXITPOINTS_KEY = "channel-exitpoints"

BASE_CONFIGURATION_ENTRYPOINT_KEY = "entrypoint"
BASE_CONFIGURATION_EXITPOINT_KEY = "exitpoint"
BASE_CONFIGURATION_COMPONENT_NAME_KEY = "name"
BASE_CONFIGURATION_COMPONENT_SUBSCRIBER_KEY = "next"

_logger = logging_utility.setup_logger(__name__)


def parse_all_config():
    config_files = [f for f in listdir(
        CONFIG_DIR) if file_utility.is_yaml_file(f)]

    if len(config_files) <= 0:
        raise Exception("No Configuration File detected in ./Config")

    configuration[CONFIGURATION_CHANNELS_KEY] = []
    configuration[CONFIGURATION_CHANNEL_PIPES_KEY] = {}
    configuration[CONFIGURATION_CHANNELS_ENTRYPOINTS_KEY] = {}
    configuration[CONFIGURATION_CHANNELS_EXITPOINTS_KEY] = {}

    for filename in config_files:
        filepath = f"{CONFIG_DIR}/{filename}"
        cfg = file_utility.read_yaml_file(filepath)

        for cfg_type in CFG_TYPES:
            if cfg_type in cfg:
                parse_config(cfg[cfg_type], cfg_type, filename)


def parse_config(cfg, cfg_type, filename):
    try:
        for component in cfg:
            cfg_key = f"{cfg_type}:{component[BASE_CONFIGURATION_COMPONENT_NAME_KEY]}"

            add_channel_to_configuration(cfg_key)
            add_entrypoint_to_configuration(component, cfg_key)
            add_exitpoint_to_configuration(component, cfg_key)
            add_pipe_to_configuration(component, cfg_key)
    except Exception as exc:
        raise Exception(f"Error parsing Configuration File: {filename}") from exc


def add_channel_to_configuration(channel_name):
    if channel_name not in configuration[CONFIGURATION_CHANNELS_KEY]:
        configuration[CONFIGURATION_CHANNELS_KEY].append(channel_name)


def add_entrypoint_to_configuration(component, cfg_key):
    if BASE_CONFIGURATION_ENTRYPOINT_KEY not in component:
        error_msg = (f"{BASE_CONFIGURATION_ENTRYPOINT_KEY} not in {component}, "
                     f"unable to save {BASE_CONFIGURATION_ENTRYPOINT_KEY}")
        _logger.error(error_msg)
        raise Exception(error_msg)

    if cfg_key not in configuration[CONFIGURATION_CHANNELS_ENTRYPOINTS_KEY]:
        configuration[CONFIGURATION_CHANNELS_ENTRYPOINTS_KEY][cfg_key] = component[BASE_CONFIGURATION_ENTRYPOINT_KEY]


def add_exitpoint_to_configuration(component, cfg_key):
    if BASE_CONFIGURATION_EXITPOINT_KEY not in component:
        _logger.warning("{cfg_key} not in {component}, unable to save {cfg_key}",
                        cfg_key=BASE_CONFIGURATION_EXITPOINT_KEY, component=component)
        return

    if cfg_key not in configuration[CONFIGURATION_CHANNELS_EXITPOINTS_KEY]:
        configuration[CONFIGURATION_CHANNELS_EXITPOINTS_KEY][cfg_key] = component[BASE_CONFIGURATION_EXITPOINT_KEY]


def add_pipe_to_configuration(component, cfg_key):
    if BASE_CONFIGURATION_COMPONENT_SUBSCRIBER_KEY in component:
        if cfg_key not in configuration[CONFIGURATION_CHANNEL_PIPES_KEY]:
            configuration[CONFIGURATION_CHANNEL_PIPES_KEY][cfg_key] = []

            for subscriber in component[BASE_CONFIGURATION_COMPONENT_SUBSCRIBER_KEY]:
                configuration[CONFIGURATION_CHANNEL_PIPES_KEY][cfg_key].append(
                    subscriber)
        else:
            for subscriber in component[BASE_CONFIGURATION_COMPONENT_SUBSCRIBER_KEY]:
                if subscriber not in configuration[CONFIGURATION_CHANNEL_PIPES_KEY][cfg_key]:
                    configuration[CONFIGURATION_CHANNEL_PIPES_KEY][cfg_key].append(
                        subscriber)
    elif cfg_key not in configuration[CONFIGURATION_CHANNEL_PIPES_KEY]:
        configuration[CONFIGURATION_CHANNEL_PIPES_KEY][cfg_key] = []


def get_config():
    if not configuration:
        parse_all_config()

    return configuration


def get_channel_entrypoints():
    return configuration[CONFIGURATION_CHANNELS_ENTRYPOINTS_KEY]


def get_channel_exitpoints():
    return configuration[CONFIGURATION_CHANNELS_EXITPOINTS_KEY]


def get_channel_pipes():
    return configuration[CONFIGURATION_CHANNEL_PIPES_KEY]
