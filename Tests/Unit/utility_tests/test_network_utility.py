from unittest.mock import patch, MagicMock

import pytest

from Utilities.network_utility import send_post_request, send_get_request


# Mock the logger to avoid actual logging during tests
@pytest.fixture(autouse=True)
def mock_logger():
    with patch('Utilities.logging_utility.setup_logger') as mock_logger:
        yield mock_logger


# Mock the requests.post and requests.get methods
@pytest.fixture
def mock_requests():
    with patch('requests.post') as mock_post, patch('requests.get') as mock_get:
        yield mock_post, mock_get


def test_send_post_request_success(mock_requests: MagicMock):
    # Set up mock post request
    mock_post, _ = mock_requests
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_post.return_value = mock_response

    url: str = 'http://example.com'
    data: dict[str, str] = {'key': 'value'}

    # Send post request
    result: bool = send_post_request(url, data)

    # Check that the result is True and the post method was called with the correct arguments
    assert result == True
    mock_post.assert_called_once_with(
        url,
        data=str(data).encode('ascii', 'ignore'),
        timeout=3,
        verify=False
    )


def test_send_post_request_with_credentials(mock_requests: MagicMock):
    # Set up mock post request (with credentials)
    mock_post, _ = mock_requests
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_post.return_value = mock_response

    url: str = 'http://example.com'
    data: dict[str, str] = {'key': 'value'}
    credentials: dict[str, str] = {'username': 'user', 'password': 'pass'}

    # Send post request
    result: bool = send_post_request(url, data, credentials)

    # Check that the result is True and the post method was called with the correct arguments
    assert result == True
    mock_post.assert_called_once_with(
        url,
        data=str(data).encode('ascii', 'ignore'),
        timeout=3,
        verify=False,
        auth=(credentials['username'], credentials['password'])
    )


def test_send_post_request_failure(mock_requests: MagicMock):
    # Set up mock post request (with exception)
    mock_post, _ = mock_requests
    mock_post.side_effect = Exception('Network error')

    url: str = 'http://example.com'
    data: dict[str, str] = {'key': 'value'}

    # Send post request
    result: bool = send_post_request(url, data)

    # Check that the result is False (request failed due to exception)
    assert result == False


def test_send_get_request_success(mock_requests: MagicMock):
    # Set up mock get request
    _, mock_get = mock_requests
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {'key': 'value'}
    mock_get.return_value = mock_response

    url: str = 'http://example.com'

    # Send get request
    result: dict[str, str] = send_get_request(url)

    # Check that the result is the expected JSON object and the get method was called with the correct arguments
    assert result == {'key': 'value'}
    mock_get.assert_called_once_with(
        url,
        timeout=3,
        verify=False
    )


def test_send_get_request_with_credentials(mock_requests: MagicMock):
    # Set up mock get request (with credentials)
    _, mock_get = mock_requests
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {'key': 'value'}
    mock_get.return_value = mock_response

    url: str = 'http://example.com'
    credentials: dict[str, str] = {'username': 'user', 'password': 'pass'}

    # Send get request
    result: dict[str, str] = send_get_request(url, credentials)

    # Check that the result is the expected JSON object and the get method was called with the correct arguments
    assert result == {'key': 'value'}
    mock_get.assert_called_once_with(
        url,
        timeout=3,
        verify=False,
        auth=(credentials['username'], credentials['password'])
    )


def test_send_get_request_failure(mock_requests: MagicMock):
    # Set up mock get request (with exception)
    _, mock_get = mock_requests
    mock_get.side_effect = Exception('Network error')

    url: str = 'http://example.com'

    # Send get request
    result = send_get_request(url)

    # Check that the result is None (request failed due to exception)
    assert result is None
