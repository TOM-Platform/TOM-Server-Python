# coding=utf-8

import glob
import json
import os
import time
from pathlib import Path
import yaml
from Utilities import logging_utility

_logger = logging_utility.setup_logger(__name__)


def append_data(file_name, data):
    os.makedirs(os.path.dirname(file_name), exist_ok=True)

    try:
        with open(file_name, "a") as file:
            file.write(data)
        return True
    except Exception:
        _logger.exception("Failed to write to {file_name}", file_name=file_name)
        return False


def is_yaml_file(file_name):
    return file_name.endswith(".yaml")


def is_file_exists(file_name):
    return os.path.isfile(file_name)


def create_directory(directory):
    try:
        os.makedirs(directory, exist_ok=True)
        return True
    except Exception:
        _logger.exception("Failed to create directory: {dir}", dir=directory)
        return False


# return lines
def read_file(file_name):
    with open(file_name) as f:
        return f.readlines()


def read_yaml_file(file_name):
    with open(file_name) as f:
        return yaml.safe_load(f)


def read_json_file(file_name):
    with open(file_name) as f:
        return json.load(f)


def read_prompt_file(file_name):
    with open(file_name, "r") as f:
        return f.read()


def write_data(file_name, lines):
    try:
        with open(file_name, "w") as file:
            file.writelines(lines)
        return True
    except Exception:
        _logger.exception("Failed to write to {file_name}", file_name=file_name)
        return False


# extension: extension with . (e.g. .csv)
def read_file_names(directory, extension, prefix=None):
    all_files_with_extension = list(glob.glob(f'{directory}/*{extension}'))
    all_files_with_extension.sort()
    # _logger.debug(all_files_with_extension)

    if prefix:
        return [file for file in all_files_with_extension if Path(file).stem.startswith(prefix)]
    return all_files_with_extension


# save the order info as {"order": <list>, "index": <index>}
def save_order_data(file_name, list_data, current_index):
    try:
        with open(file_name, 'w') as outfile:
            data = {'order': list_data, 'index': current_index}
            json.dump(data, outfile)
        return True
    except Exception:
        _logger.exception("Failed to save order data: {file_name}", file_name=file_name)
        return False


# return the <list>: order, <index>:index
def read_order_data(file_name, max_duration_minutes):
    if not os.path.exists(file_name):
        return None, None

    # if order data file is older than <max_duration_minutes> minutes ignore it
    if is_file_older_than(file_name, max_duration_minutes * 60):
        return None, None

    # read recent order data file
    try:
        with open(file_name) as json_file:
            data = json.load(json_file)
            return data['order'], data['index']
    except Exception:
        _logger.exception("Failed to read order data: {file_name}", file_name=file_name)
        return None, None


def is_file_older_than(file_name, seconds):
    file_time = os.path.getmtime(file_name)
    return (time.time() - file_time) > seconds


def get_project_root():
    current_dir = os.path.dirname(os.path.abspath(__file__))

    while not os.path.isfile(os.path.join(current_dir, 'main.py')):
        current_dir = os.path.dirname(current_dir)

    return current_dir


def get_path_from_project_root(folders):
    """
    Constructs a full directory path from the project root by traversing through the specified folders,
    creating each directory if it does not exist.

    Parameters
    ----------
    folders : list of str
        A list of folder names to traverse from the project root. The folder sequence should be
        ordered from left to right.

    Returns
    -------
    str
        The full path of the directory constructed from the project root with the specified folders.
    """
    current_directory = get_project_root()

    for folder in folders:
        current_directory = os.path.join(current_directory, folder)
        create_directory(current_directory)
    return current_directory


def get_path_with_filename(directory, filename):
    return os.path.join(directory, filename)


def delete_all_files_in_dir(dir_path):
    try:
        # List all items in the folder
        for item_name in os.listdir(dir_path):
            item_path = os.path.join(dir_path, item_name)
            os.remove(item_path)
        return True
    except Exception:
        _logger.exception(f"Error deleting files in {dir_path}")
        return False


def get_credentials_file_path(api_credentials_key):
    """
    return the path of the credentials file (which is stored in the `credential` folder)
    """
    try:
        credential_file_name = os.environ[api_credentials_key]
        return os.path.join(get_project_root(), "credential", credential_file_name)
    except KeyError as exc:
        _logger.exception("KeyError: {key} not found in os.environ", key=api_credentials_key)
        raise KeyError from exc
