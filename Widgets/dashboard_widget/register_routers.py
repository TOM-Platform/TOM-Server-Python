import importlib
from Utilities import environment_utility


def register_routers(app):
    # Retrieve the API_ROUTERS environment variable
    routers = environment_utility.get_env_string('WEB_DASHBOARD_API_ROUTERS')

    if routers:
        # Split the comma-separated router paths into a list
        router_paths = routers.split(',')

        # Import and register each router with the FastAPI app
        for path in router_paths:
            module_path, router_name = path.rsplit('.', 1)
            module = importlib.import_module(module_path)
            router_instance = getattr(module, router_name)
            app.include_router(router_instance)
    else:
        # Raise an error if no API_ROUTERS environment variable is found
        raise ValueError("No API_ROUTERS found in environment variables.")
