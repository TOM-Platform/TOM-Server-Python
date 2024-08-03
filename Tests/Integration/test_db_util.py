from os import environ
import os

from Utilities.file_utility import get_project_root


def get_integration_path():
    # Get the current working directory
    current_dir = os.getcwd()
    
    if current_dir == get_project_root():
        return os.path.relpath(os.path.join(current_dir, 'Tests', 'Integration'), start=os.getcwd())

    # Navigate up the directory tree until finding the 'Integration' folder
    while not os.path.isdir(os.path.join(current_dir, 'Integration')):
        current_dir = os.path.dirname(current_dir)
        if current_dir == os.path.dirname(current_dir):
            break
    
    # Construct the relative path to the 'Integration' folder
    relative_path = os.path.relpath(os.path.join(current_dir, 'Integration'), start=os.getcwd())

    return relative_path


def set_test_db_environ():
    # Set the environment variables for the database
    relative_path = get_integration_path()
    environ['DATABASE_URL'] = f"sqlite:///{relative_path}"
    if relative_path == ".":
        relative_path = ""
    environ['DATABASE_NAME'] = "Test"
    environ['MODELS_FILE_PATH'] = os.path.join(relative_path, "Models")
    environ['MODELS_FILE_EXT'] = ".json"
    environ['ENV'] = "dev"
