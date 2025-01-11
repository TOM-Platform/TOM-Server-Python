Run FastAPI server with Python:

```bash
uvicorn hosting_local_llm:app --host 0.0.0.0 --port 5000 --reload

or 

python hosting_local_llm.py
```

Access the local LLM server with this command (without the history memory):

```bash
curl -X 'POST' \
  'http://127.0.0.1:5000/generate-answer' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "user_question": "What is the capital of France?",
  "system_prompt": "You are a friendly chatbot."
}'

```

Access the server with this command (with the history memory):

```bash
curl -X 'POST' \
  'http://127.0.0.1:5000/generate-answer-history' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "user_question": "I will travel to Singapore, how is the weather there?",
  "session_id": "user123"
}'

curl -X 'POST' \
  'http://127.0.0.1:5000/generate-answer-history' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "user_question": "Where will I travel to?",
  "session_id": "user123"
}'
```

