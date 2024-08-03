# coding=utf-8
from APIs.local_llm.local_llm_web_api import generate_answer, generate_answer_with_history
from unittest.mock import patch, MagicMock


@patch('APIs.local_llm.local_llm_web_api.requests.post')
def test_local_llm_web_api_generate_answer(mock_post: MagicMock):
    # Set up the mock response from the llm api
    mock_response = MagicMock()
    mock_response.json.return_value = "The capital of France is Paris."
    mock_post.return_value = mock_response

    # Call the function and assert the result
    answer: str = generate_answer("What is the capital of France?")
    assert answer == "The capital of France is Paris."

    # Verify that request was called with the correct arguments
    mock_post.assert_called_once_with(
        "http://localhost:5000/generate-answer",
        json={
            "user_prompt": "What is the capital of France?",
            "system_prompt": "You are a friendly chatbot.",
            "temperature": 0.1
        }
    )

@patch('APIs.local_llm.local_llm_web_api.requests.post')
def test_local_llm_web_api_generate_answer_with_history(mock_post: MagicMock):
    # Set up the mock responses from the llm api
    mock_responses = [
        MagicMock(json=lambda: "The capital of France is Paris."), # First response
        MagicMock(json=lambda: 'Your previous question was: "What is the capital of France?"') # Second response
    ]
    mock_post.side_effect = mock_responses

    # Call the functions
    answer1: str = generate_answer_with_history("What is the capital of France?")
    answer2: str = generate_answer_with_history("What was my previous question?")

    # Check if the answers are correct
    assert answer1 == "The capital of France is Paris."
    assert answer2 == 'Your previous question was: "What is the capital of France?"'

    # Verify that requests were called with the correct arguments
    assert mock_post.call_count == 2
    mock_post.assert_any_call(
        "http://localhost:5000/generate-answer-history",
        json={
            "user_prompt": "What is the capital of France?",
            "system_prompt": "You are a friendly chatbot.",
            "session_id": None,
            "temperature": 0.1
        }
    )
    mock_post.assert_any_call(
        "http://localhost:5000/generate-answer-history",
        json={
            "user_prompt": "What was my previous question?",
            "system_prompt": "You are a friendly chatbot.",
            "session_id": None,
            "temperature": 0.1
        }
    )
