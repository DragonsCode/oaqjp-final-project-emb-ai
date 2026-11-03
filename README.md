# Emotion detection with Watson NLP

A Flask teaching application that sends English text to the external IBM Skills Network Watson emotion endpoint and displays anger, disgust, fear, joy and sadness scores. This repository integrates a hosted model; it does not train or evaluate a new model.

## Run locally

Use Python 3.12:

```sh
python -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
python server.py
```

Open http://127.0.0.1:5000. The endpoint requires network access and may be restricted or unavailable outside the course environment. Do not submit sensitive text: input is sent to a third party and the teaching GET interface places it in a URL. The development server binds to loopback with debug disabled; public hosting needs a production WSGI server, HTTPS, request limits and an explicit privacy policy.

## Response behavior

`GET /emotionDetector?textToAnalyze=...` retains its JSON `response` field. Missing/blank input and provider HTTP 400 retain the original invalid-input message (HTTP 200). Valid predictions preserve all five scores. Network errors, other provider statuses, malformed data and invalid probabilities return a generic HTTP 503 message, also shown in the browser. Requests use 3.05-second connect and 10-second read timeouts; these are socket timeouts, not a total request deadline.

## Tests

```sh
python -m pip install -r requirements-dev.txt
python -m unittest discover -s tests -v
ruff check EmotionDetection server.py tests setup.py
node --test tests/test_frontend.cjs
```

Default tests use mocked provider responses and make no external requests. The five original provider examples remain available as explicit integration tests:

```sh
RUN_WATSON_INTEGRATION=1 python -m unittest discover -s tests -p test_emotion_detection.py -v
```

These opt-in tests send their example sentences to Watson and depend on its availability and model outputs. CI runs only offline tests; it does not establish prediction accuracy.
