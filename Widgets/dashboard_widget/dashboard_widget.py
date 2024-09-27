import threading
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from Utilities import logging_utility, environment_utility
from Database import database
from base_component import BaseComponent
from Widgets.dashboard_widget.register_routers import register_routers

_logger = logging_utility.setup_logger(__name__)


class DashboardWidget(BaseComponent):
    """
    DashboardWidget is responsible for setting up and running a FastAPI web server in a separate thread.
    It dynamically registers routers based on paths provided in the environment configuration and initializes the
    database connection.
    This class should not be modified directly; any changes should be made through the `.env` file.
    """

    def __init__(self, name) -> None:
        super().__init__(name)
        self.app = None
        self.web_server_thread = None

        self.server_url = None
        self.server_port = None

    # Method to run the FastAPI server
    def run_server(self):
        self.server_url = environment_utility.get_env_string('WEB_DASHBOARD_SERVER_URL')
        self.server_port = environment_utility.get_env_int('WEB_DASHBOARD_SERVER_PORT')
        _logger.info("Starting FastAPI server...")
        uvicorn.run(self.app, host=self.server_url, port=self.server_port, log_level="info")

    # Method to start the DashboardWidget
    def start(self):
        # Initialize the database connection
        database.init()
        # Create a FastAPI application instance
        self.app = FastAPI()
        # Enable CORS middleware
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],  # Update with your allowed origins
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        # Register routers (routes) with the FastAPI app
        register_routers(self.app)
        # Start the web server in a new thread
        self.web_server_thread = threading.Thread(target=self.run_server)
        self.web_server_thread.start()
        _logger.info("FastAPI server started in a new thread.")
