import requests

_API_URL_BASE = "http://localhost:5000"


def generate_answer(user_prompt, system_prompt="You are a friendly chatbot.", temperature=0.1):
    url = _API_URL_BASE + "/generate-answer"
    data = {
        "user_prompt": user_prompt,
        "system_prompt": system_prompt,
        "temperature": temperature
    }
    answer_response = requests.post(url, json=data)
    return answer_response.json()


def generate_answer_with_history(user_prompt, system_prompt="You are a friendly chatbot.", session_id=None,
                                 temperature=0.1):
    url = _API_URL_BASE + "/generate-answer-history"
    data = {
        "user_prompt": user_prompt,
        "system_prompt": system_prompt,
        "session_id": session_id,
        "temperature": temperature
    }
    answer_with_history_response = requests.post(url, json=data)
    return answer_with_history_response.json()


if __name__ == "__main__":
    _user_prompt = "What is the capital of France?"
    _system_prompt = "You are a friendly chatbot."
    result = generate_answer_with_history(_user_prompt, _system_prompt)
    print(result)
