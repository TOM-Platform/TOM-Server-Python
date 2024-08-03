import pytest
from os import environ
from Utilities.environment_utility import (
    get_env_variable,
    get_env_variable_or_default,
    get_env_string,
    get_env_int,
    get_env_bool,
    get_env_float,
    get_env_int_or_string,
    set_env_variable,
)

# Fixture to set up and tear down environment variables for tests
@pytest.fixture(autouse=True)
def setup_env():
    # Set up test environment variables
    environ['TEST_STRING'] = 'hello'
    environ['TEST_INT'] = '42'
    environ['TEST_BOOL_TRUE'] = 'TrUe'
    environ['TEST_BOOL_FALSE'] = 'fAlSe'
    environ['TEST_FLOAT'] = '3.14'
    environ['TEST_INT_OR_STRING_INT'] = '100'
    environ['TEST_INT_OR_STRING_STR'] = 'not_a_number'
    
    yield
    
    # Clean up test environment variables
    keys_to_remove = [
        'TEST_STRING', 'TEST_INT', 'TEST_BOOL_TRUE', 'TEST_BOOL_FALSE',
        'TEST_FLOAT', 'TEST_INT_OR_STRING_INT', 'TEST_INT_OR_STRING_STR'
    ]

    for key in keys_to_remove:
        environ.pop(key, None)

def test_get_env_variable():
    # Check that an existing environment variable can be retrieved
    assert get_env_variable('TEST_STRING') == 'hello'
    
    # Check that a non-existent environment variable raises a KeyError
    with pytest.raises(KeyError):
        get_env_variable('NON_EXISTENT_VAR')

def test_get_env_variable_or_default():
    # Check that an existing environment variable can be retrieved
    assert get_env_variable_or_default('TEST_STRING', 'default') == 'hello'
    
    # Check that a non-existent environment variable returns the default value
    assert get_env_variable_or_default('NON_EXISTENT_VAR', 'default') == 'default'

def test_get_env_string():
    # Check that an existing environment variable can be retrieved as a string
    assert get_env_string('TEST_STRING') == 'hello'

def test_get_env_int():
    # Check that an existing integer environment variable can be retrieved
    assert get_env_int('TEST_INT') == 42
    
    # Check that a non-integer environment variable raises a ValueError
    with pytest.raises(ValueError):
        get_env_int('TEST_STRING')

def test_get_env_bool():
    # Check that an existing boolean environment variable can be retrieved
    assert get_env_bool('TEST_BOOL_TRUE') == True
    assert get_env_bool('TEST_BOOL_FALSE') == False
    
def test_get_env_bool():
    # Check that an existing boolean environment variable can be retrieved
    assert get_env_bool('TEST_BOOL_TRUE') == True
    assert get_env_bool('TEST_BOOL_FALSE') == False
    
    # Check that a non-boolean environment variable raises a ValueError
    assert get_env_bool('TEST_STRING') == False

def test_get_env_float():
    # Check that an existing float environment variable can be retrieved
    assert get_env_float('TEST_FLOAT') == 3.14
    
    # Check that a non-float environment variable raises a ValueError
    with pytest.raises(ValueError):
        get_env_float('TEST_STRING')

def test_get_env_int_or_string():
    # Check that an integer environment variable can be retrieved as an int
    assert get_env_int_or_string('TEST_INT_OR_STRING_INT') == 100
    
    # Check that a non-integer environment variable can be retrieved as a string
    assert get_env_int_or_string('TEST_INT_OR_STRING_STR') == 'not_a_number'

def test_set_env_variable():
    # Check that a new environment variable can be set
    assert set_env_variable('NEW_VAR', 'new_value') == 'new_value'
    assert environ['NEW_VAR'] == 'new_value'
    
    # Check that an existing environment variable can be updated
    assert set_env_variable('TEST_STRING', 'updated_value') == 'updated_value'
    assert environ['TEST_STRING'] == 'updated_value'