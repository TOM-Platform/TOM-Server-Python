import multiprocessing
from dotenv import load_dotenv
import base_keys
from Memory import Memory
from Utilities import config_utility, endpoint_utility, environment_utility, time_utility, logging_utility, file_utility


# from APIs.hololens import hololens_portal


def _load_environment(env):
    print(f"Running in {env} environment")

    env_file = f".env.{env}"

    if not file_utility.is_file_exists(env_file):
        raise FileNotFoundError(f"The environment file '{env_file}' was not found.")

    # load ENVIRONMENT variables
    load_dotenv(f".env.{env}")


def setup_environment():
    # get the environment
    env = environment_utility.get_env_string('ENV')
    _load_environment(env)

    # NOTE: Logging
    log_file_name = environment_utility.get_env_string('LOG_FILE')
    log_level = environment_utility.get_env_int('LOG_LEVEL')
    _logger = logging_utility.setup_logger(log_file=log_file_name, log_level=log_level)
    _logger.info("Starting Server")

    # Set HL2 camera: uncomment the two lines below if you want to set the HL2 camera
    # hololens_portal.set_api_credentials()
    # hololens_portal.set_hololens_as_camera()


def start_processing():
    # NOTE: Parse all config
    config_utility.get_config()
    # NOTE: Set up and start memory
    Memory.init()
    # NOTE: Start widgets
    entrypoints = config_utility.get_channel_entrypoints()
    camera_required = None

    for component in entrypoints.keys():
        if component.split(":")[0] == "input":
            instance = endpoint_utility.get_component_instance(component)
            entry_func = endpoint_utility.get_entry_func_of(component)
            entry_func = getattr(instance, entry_func)

            if component == base_keys.CAMERA_WIDGET:
                camera_required = entry_func
            else:
                multiprocessing.Process(target=entry_func).start()

    # camera needs to run in the main thread (due to OpenCV pickle limitations), so it will be started after all others have started.
    if camera_required is not None:
        camera_required()

    # NOTE: This section only runs if the Camera Widget is not enabled since the Camera Widget has its own while loop
    try:
        while True:
            time_utility.sleep_seconds(1)
    except KeyboardInterrupt:
        logging_utility.setup_logger().error("Keyboard Interrupt")

    # NOTE: close the shared memory
    Memory.close()


if __name__ == "__main__":
    setup_environment()
    start_processing()
