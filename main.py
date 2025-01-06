import multiprocessing
import signal
from dotenv import load_dotenv
import base_keys
from Memory import Memory
from Utilities import config_utility, endpoint_utility, environment_utility, time_utility, logging_utility, file_utility

import asyncio


# from APIs.hololens import hololens_portal
_logger = None

def _load_environment(env):
    print(f"Running in {env} environment")

    env_file = f".env.{env}"

    if not file_utility.is_file_exists(env_file):
        raise FileNotFoundError(f"The environment file '{env_file}' was not found.")

    # load ENVIRONMENT variables
    load_dotenv(f".env.{env}")


def setup_environment():
    global _logger

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
    global _logger

    # NOTE: Parse all config
    config_utility.get_config()

    # NOTE: Set up and start memory
    Memory.init()

    # NOTE: Start widgets
    entrypoints = config_utility.get_channel_entrypoints()

    # Add sigterm handler to end program and cleanup elegantly
    loop = asyncio.get_event_loop()
    # TODO: Commented as add_signal_handler is not supported in Windows
    # for sig in (signal.SIGTERM, signal.SIGINT):
    #     loop.add_signal_handler(sig, _sigterm_handler, sig)

    tasks = []

    for component in entrypoints.keys():
        component_type = component.split(":")[0]
        if component_type == "input":
            instance = endpoint_utility.get_component_instance(component)
            entry_func = endpoint_utility.get_entry_func_of(component)
            entry_func = getattr(instance, entry_func)

            if (component == base_keys.CAMERA_WIDGET) or (component == base_keys.WEBSOCKET_WIDGET):
                task = entry_func()
                if task is not None:
                    tasks.append(task)
            else:
                # TODO: For multiprocessing tasks, this could be moved to their entry_func
                multiprocessing.Process(target=entry_func).start()
        elif component_type == "service":
            # Instantiate service first
            endpoint_utility.get_component_instance(component)

    loop.run_until_complete(asyncio.gather(*tasks))

    # Main loop that will run until the program is terminated.
    # TODO: We need to trap uncaught exceptions as they will cause the task to exit prematurely
    loop.run_forever()

    # Program ended ----- this is reached when sigterm_handler --> loop.stop()
    _logger.info("Shutting down --- ")

    # NOTE: close the shared memory
    Memory.close()


def _sigterm_handler(sig):
    global _logger

    loop = asyncio.get_running_loop()
    for task in asyncio.all_tasks(loop=loop):
        task.cancel()
    _logger.info(f'Got signal: {sig!s}, shutting down.')

    loop.remove_signal_handler(signal.SIGTERM)
    loop.add_signal_handler(signal.SIGINT, lambda: None)

    loop.stop()


if __name__ == "__main__":
    setup_environment()
    start_processing()
