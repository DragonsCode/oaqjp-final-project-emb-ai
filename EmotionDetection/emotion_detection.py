"""Validated, bounded access to the external Watson teaching endpoint."""

import math

import requests

EMOTIONS = ("anger", "disgust", "fear", "joy", "sadness")
URL = "https://sn-watson-emotion.labs.skills.network/v1/watson.runtime.nlp.v1/NlpService/EmotionPredict"


class EmotionServiceError(RuntimeError):
    """The provider is unavailable or did not return a valid prediction."""


def emotion_detector(text_to_analyze):
    """Return five scores and their maximum; blank/400 inputs retain None values.

    Network failures, non-200/400 statuses and invalid provider data raise
    EmotionServiceError without exposing submitted text or upstream responses.
    """
    invalid = dict.fromkeys((*EMOTIONS, "dominant_emotion"))
    if not isinstance(text_to_analyze, str) or not text_to_analyze.strip():
        return invalid
    try:
        response = requests.post(
            URL,
            headers={"grpc-metadata-mm-model-id": "emotion_aggregated-workflow_lang_en_stock"},
            json={"raw_document": {"text": text_to_analyze}},
            timeout=(3.05, 10),
        )
    except requests.RequestException:
        raise EmotionServiceError("Emotion service unavailable") from None
    if response.status_code == 400:
        return invalid
    if response.status_code != 200:
        raise EmotionServiceError("Emotion service unavailable")
    try:
        emotions = response.json()["emotionPredictions"][0]["emotion"]
        scores = {name: emotions[name] for name in EMOTIONS}
        if any(
            isinstance(value, bool)
            or not isinstance(value, (int, float))
            or not math.isfinite(value)
            or not 0 <= value <= 1
            for value in scores.values()
        ):
            raise ValueError("Invalid score")
    except (ValueError, KeyError, IndexError, TypeError):
        raise EmotionServiceError("Invalid emotion service response") from None
    return {**scores, "dominant_emotion": max(scores, key=scores.get)}
