import os

import pytest
from dotenv import load_dotenv, find_dotenv

from Memory import Memory
from Utilities import file_utility


def get_integration_path():
    current_dir = os.getcwd()
    root = file_utility.get_project_root()
    if current_dir == root:
        return os.path.relpath(os.path.join(root, 'Tests', 'Integration'), start=root)

    while not os.path.isdir(os.path.join(current_dir, 'Integration')):
        parent = os.path.dirname(current_dir)
        if parent == current_dir:
            break
        current_dir = parent

    return os.path.relpath(os.path.join(current_dir, 'Integration'), start=os.getcwd())


def setup_env_variables():
    os.environ['ENV'] = "test"


def setup_test_database_parameters():
    integration = get_integration_path()

    os.environ['DATABASE_URL'] = f"sqlite:///{integration}"
    os.environ['DATABASE_NAME'] = "Test"
    os.environ['MODELS_FILE_PATH'] = os.path.join(integration, "Models") if integration != "." else "Models"
    os.environ['MODELS_FILE_EXT'] = ".json"


def remove_test_database():
    integration = get_integration_path()
    db_file = os.path.join(integration, "Test.db") if integration != "." else "Test.db"

    if os.path.exists(db_file):
        try:
            os.remove(db_file)
        except OSError:
            print(f'Failed to remove {db_file}')


@pytest.fixture(scope='session', autouse=True)
def configure_db():
    yield  # <-- all tests run here

    remove_test_database()


def initialize_test_env():
    env = os.environ['ENV']

    print(f"-------Enabling '{env}' environment--------")
    # reading ENVIRONMENT variables
    load_dotenv(find_dotenv(f".env.{env}"))


def pytest_configure():
    setup_env_variables()
    initialize_test_env()

    setup_test_database_parameters()

    # initialize shared memory
    Memory.init()
