import requests
import json

def emotion_detector(text_to_analyze):
    """Send text to Watson NLP EmotionPredict endpoint and return formatted emotion scores.

    Args:
        text_to_analyze (str): The text to analyze for emotions.

    Returns:
        dict: Formatted dictionary with emotion scores and dominant emotion, or None values for invalid input.
    """
    url = "https://sn-watson-emotion.labs.skills.network/v1/watson.runtime.nlp.v1/NlpService/EmotionPredict"
    headers = {"grpc-metadata-mm-model-id": "emotion_aggregated-workflow_lang_en_stock"}
    input_json = {"raw_document": {"text": text_to_analyze}}
    
    # Send POST request
    response = requests.post(url, headers=headers, json=input_json)
    
    # Handle blank input (status code 400)
    if response.status_code == 400:
        return {
            "anger": None,
            "disgust": None,
            "fear": None,
            "joy": None,
            "sadness": None,
            "dominant_emotion": None
        }
    
    # Parse response text to dictionary
    response_dict = json.loads(response.text)
    
    # Extract emotion scores
    emotions = response_dict["emotionPredictions"][0]["emotion"]
    anger_score = emotions.get("anger", 0.0)
    disgust_score = emotions.get("disgust", 0.0)
    fear_score = emotions.get("fear", 0.0)
    joy_score = emotions.get("joy", 0.0)
    sadness_score = emotions.get("sadness", 0.0)
    
    # Find dominant emotion
    emotion_scores = {
        "anger": anger_score,
        "disgust": disgust_score,
        "fear": fear_score,
        "joy": joy_score,
        "sadness": sadness_score
    }
    dominant_emotion = max(emotion_scores, key=emotion_scores.get)
    
    # Format output
    output = {
        "anger": anger_score,
        "disgust": disgust_score,
        "fear": fear_score,
        "joy": joy_score,
        "sadness": sadness_score,
        "dominant_emotion": dominant_emotion
    }
    
    return output