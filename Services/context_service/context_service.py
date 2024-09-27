import base_keys
from base_component import BaseComponent
from Utilities import config_utility, endpoint_utility


class ContextService(BaseComponent):
    """
    This service stops all currently running services and starts the one service  provided in the 'detail' field of the
    websocket message.
    """

    def run(self, raw_data):
        super().set_component_status(base_keys.COMPONENT_IS_RUNNING_STATUS)

        new_service = raw_data[base_keys.WEBSOCKET_MESSAGE]["detail"]

        component_instance = endpoint_utility.get_component_instance(new_service)
        entry_func = endpoint_utility.get_entry_func_of(new_service)
        entry_func = getattr(component_instance, entry_func)

        all_component_status = super().get_memory_data(base_keys.MEMORY_COMPONENT_STATUS_KEY)

        exitpoints = config_utility.get_channel_exitpoints()

        for component_name, status in all_component_status.items():
            # If component is a service and is currently running, stop it
            if (component_name.split(":")[0] == "service" and status == base_keys.COMPONENT_IS_RUNNING_STATUS
                    and component_name in exitpoints):
                temp_component_instance = endpoint_utility.get_component_instance(component_name)
                exit_func = endpoint_utility.get_exit_func_of(component_name)
                exit_func = getattr(temp_component_instance, exit_func)
                exit_func()

        super().set_component_status(base_keys.COMPONENT_IS_STOPPED_STATUS)

        # TODO: Data to be passed into service to be started? Will this be provided as part of the message details?
        data = None
        entry_func(data)
