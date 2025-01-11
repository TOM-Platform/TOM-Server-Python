import importlib

from . import config_utility

component_instances = {}

component_base_dir_map = {
    "input": "Widgets",
    "processing": "Processors",
    "service": "Services",
    "output": "Outputs"
}


def get_entry_func_of(component, component_type=None):
    '''

    :param component: Format in configuration file, i.e., processing:Yolov8
    :param component_type:  i.e., processing
    :return:
    '''
    entrypoints = config_utility.get_channel_entrypoints()
    if component_type is None:
        component_type = component_base_dir_map[component.split(":")[0]]

    for name, entrypoint in entrypoints.items():
        if name == component:
            return entrypoint.split(".")[-1]

    return None


def get_exit_func_of(component, component_type=None):
    '''

    :param component: Format in configuration file, i.e., processing:Yolov8
    :param component_type: i.e., processing
    :return:
    '''
    exitpoints = config_utility.get_channel_exitpoints()

    if component_type is None:
        component_type = component_base_dir_map[component.split(":")[0]]

    for name, exitpoint in exitpoints.items():
        if name == component:
            return exitpoint.split(".")[-1]

    return None


def get_class_of(component, component_type=None):
    '''

    :param component: Format in configuration file, i.e., processing:Yolov8
    :param component_type: i.e., processing
    :return:
    '''
    entrypoints = config_utility.get_channel_entrypoints()
    if component_type is None:
        component_type = component_base_dir_map[component.split(":")[0]]

    for name, entrypoint in entrypoints.items():
        if name == component:
            return entrypoint.split(".")[-2]

    return None


def get_entrypoint_of(component):
    '''

    :param component: Format in configuration file, i.e., processing:Yolov8
    :return:
    '''
    result = ""
    entrypoints = config_utility.get_channel_entrypoints()
    component_type = component_base_dir_map[component.split(":")[0]]

    for name, entrypoint in entrypoints.items():
        if name == component:
            result = f"{component_type}.{entrypoint}"

    result = ".".join(result.split(".")[:-2])

    return result


def get_component_instance(component):
    '''

    :param component: Format in configuration file, i.e., processing:Yolov8
    :return:
    '''
    if component not in component_instances:
        entrypoint = get_entrypoint_of(component)
        class_name = get_class_of(component)

        submod = importlib.import_module(entrypoint)
        instance = getattr(submod, class_name)(component)

        component_instances[component] = instance

    return component_instances[component]
