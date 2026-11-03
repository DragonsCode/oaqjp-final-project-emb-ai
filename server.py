"""Flask web application for emotion detection using Watson NLP."""
from flask import Flask, jsonify, render_template, request

from EmotionDetection import emotion_detector
from EmotionDetection.emotion_detection import EmotionServiceError

app = Flask(__name__)

@app.route('/')
def index():
    """Render the index.html template for the web interface.

    Returns:
        str: Rendered HTML content from index.html.
    """
    return render_template('index.html')

@app.route('/emotionDetector', methods=['GET'])
def emotion_detector_route():
    """Process text input and return formatted emotion analysis or error message.

    Expects a url parameter with a 'textToAnalyze' field. Returns a JSON response with
    either the formatted emotion analysis or an error message for invalid input.

    Returns:
        dict: JSON response containing the formatted emotion analysis or error message.
    """
    text = request.args.get('textToAnalyze')
    try:
        result = emotion_detector(text)
    except EmotionServiceError:
        return jsonify({"response": "Emotion service unavailable. Please try again later."}), 503

    # Check for invalid input (dominant_emotion is None)
    if result['dominant_emotion'] is None:
        return jsonify({'response': 'Invalid text! Please try again!'})

    # Format the response as specified
    response_text = (
        f"For the given statement, the system response is "
        f"'anger': {result['anger']}, "
        f"'disgust': {result['disgust']}, "
        f"'fear': {result['fear']}, "
        f"'joy': {result['joy']} and "
        f"'sadness': {result['sadness']}. "
        f"The dominant emotion is {result['dominant_emotion']}."
    )
    return jsonify({'response': response_text})

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=False)
