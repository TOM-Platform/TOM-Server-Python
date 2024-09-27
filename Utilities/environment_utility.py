# coding=utf-8

# This file contains utility functions to get environment variables, /
# from the OS or from a .env file (e.g., ".env.dev") using `python-dotenv` package.

from os import environ
import re


def get_env_variable(key):
    return environ[key]


def get_env_variable_or_default(key, default):
    return environ.get(key, default)


def get_env_string(key):
    return get_env_variable(key)


def get_env_int(key):
    return int(get_env_variable(key))


def get_env_bool(key):
    return get_env_variable(key).lower() == "true"


def get_env_float(key):
    return float(get_env_variable(key))


def get_env_int_or_string(key):
    value = get_env_variable(key)
    if re.match(r"^\d+$", value):  # Check if value is a number
        return int(value)
    return value


def set_env_variable(key, value):
    environ[key] = value
    return environ[key]
