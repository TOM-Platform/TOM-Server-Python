from dotenv import load_dotenv, find_dotenv

from Memory import Memory


def initialize_test_env():
    env = 'test'
    print(f"-------Enabling '{env}' environment--------")
    # reading ENVIRONMENT variables
    load_dotenv(find_dotenv(f".env.{env}"))


def pytest_configure():
    initialize_test_env()

    # initialize shared memory
    Memory.init()
