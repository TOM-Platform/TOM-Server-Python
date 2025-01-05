import os
import base_keys
from Database import database, tables
from DataFormat import datatypes_helper
from Utilities import time_utility, endpoint_utility, config_utility, logging_utility
from Memory.Memory import update_shared_memory_item, get_shared_memory_item

CONFIG_CHANNEL_PIPES = "channel-pipes"
VALID_COMPONENT_STATUS = [base_keys.COMPONENT_NOT_STARTED_STATUS, base_keys.COMPONENT_IS_RUNNING_STATUS,
                          base_keys.COMPONENT_IS_STOPPED_STATUS]

_logger = logging_utility.setup_logger(__name__)


class BaseComponent:
    """
    BaseComponent serves as a foundational class for managing the status, data, 
    and communication between various components in the TOM server.

    Key functionalities include:
    - **Component Status Management**: Initialize, set, and get the status of a component.
    - **Shared Memory Operations**: Provides interfaces for reading and writing data to shared memory.
    - **Database Operations**: Simplifies inserting and querying data from the database.
    - **Message Sending**: Implements communication and data transfer between components.
    - **Logging**: Provides detailed logs for debugging and monitoring component behavior.
    """

    """
    Set of supported datatypes for the component. (to be overridden by subclasses)
    """
    SUPPORTED_DATATYPES = {}

    def __init__(self, name) -> None:
        self.name = name

        _logger.info("Initialising:: {name}, PID: {pid}", name=self.name, pid=os.getpid())
        # NOTE: Initialising 1 Database per BaseComponent Instance since we refer to a local .db file / a hosted DB.
        # The Database is only for interfacing with the .db file / hosted db
        database.init()

        self.component_status_name = f"{self.name}_STATUS"
        self.set_component_status(base_keys.COMPONENT_NOT_STARTED_STATUS)  # Default Status

    def send_to_component(self, **kwargs):
        if len(kwargs) <= 0:
            _logger.warning("No data found to be sent to component")
            return

        if base_keys.BASE_DATA_KEY in kwargs:
            message = self.__build_from_base_message(kwargs)
        else:
            message = self.__build_message(kwargs)

        all_subscribers = config_utility.get_config()[CONFIG_CHANNEL_PIPES][self.name]
        for subscriber in all_subscribers:
            entry_func = self.__get_subscriber_func(subscriber, message)

            if entry_func:
                entry_func(message)

    def is_supported_datatype(self, datatype) -> bool:
        """
        Check if the datatype is supported/handled by this component (by SUPPORTED_DATATYPES)
        :return: true if handled by the component, false otherwise
        """
        return datatype in self.SUPPORTED_DATATYPES

    def get_supported_datatypes(self) -> set[str]:
        """
        :return: Set of supported datatype names for the component
        """
        return self.SUPPORTED_DATATYPES

    def insert_data_to_db(self, table_name, data):
        tables.insert_rows_to_table(table_name, data)

    def get_data_from_db(self, table_name, query):
        return tables.get_rows_from_table(table_name, query).all()

    def set_memory_data(self, key_name, val):
        update_shared_memory_item(key_name, val)

    def get_memory_data(self, key_name):
        return get_shared_memory_item(key_name)

    def get_component_status(self):
        return self.get_memory_data(base_keys.MEMORY_COMPONENT_STATUS_KEY)[self.component_status_name]

    def set_component_status(self, new_status):
        all_component_status_keys = self.get_memory_data(base_keys.MEMORY_COMPONENT_STATUS_KEY)
        if all_component_status_keys is None:
            all_component_status_keys = {}  # Initialise with an empty dictionary

        if new_status in VALID_COMPONENT_STATUS:
            all_component_status_keys[self.component_status_name] = new_status

            self.set_memory_data(base_keys.MEMORY_COMPONENT_STATUS_KEY, all_component_status_keys)
        else:
            _logger.error("Invalid Component Status 'set_component_status()': {new_status}", new_status=new_status)

    def __build_message(self, args):
        message = {}

        message[base_keys.TIMESTAMP_KEY] = time_utility.get_iso_date_time_str()
        message[base_keys.ORIGIN_KEY] = self.name

        for key, val in args.items():
            message[key] = val

        return message

    def __build_from_base_message(self, args):
        new_message = args[base_keys.BASE_DATA_KEY]
        new_message[base_keys.ORIGIN_KEY] = self.name

        if base_keys.TIMESTAMP_KEY not in new_message:
            new_message[base_keys.TIMESTAMP_KEY] = time_utility.get_iso_date_time_str()

        for key, val in args.items():
            if key != base_keys.BASE_DATA_KEY:
                new_message[key] = val

        return new_message

    def __get_subscriber_func(self, subscriber, message):
        instance = endpoint_utility.get_component_instance(subscriber)

        # Send websocket data only if the subscriber is interested in the datatype
        if self.name == base_keys.WEBSOCKET_WIDGET:
            datatype = datatypes_helper.get_name_by_key(message[base_keys.WEBSOCKET_DATATYPE])
            if not instance.is_supported_datatype(datatype):
                # Subscriber not interested in messages of this datatype
                return None

        entry_func = endpoint_utility.get_entry_func_of(subscriber)
        entry_func = getattr(instance, entry_func)

        return entry_func
