import math
import unittest
from unittest.mock import Mock, patch

import requests

from EmotionDetection import emotion_detector


def response(status=200, scores=None):
    result = Mock(status_code=status)
    result.json.return_value = {
        "emotionPredictions": [{"emotion": scores or {
            "anger": 0.1, "disgust": 0.1, "fear": 0.1,
            "joy": 0.6, "sadness": 0.1,
        }}]
    }
    # The old implementation parses .text; keep the same fixture for both paths.
    import json
    result.text = json.dumps(result.json.return_value)
    return result


class ServiceSafetyTests(unittest.TestCase):
    @patch("EmotionDetection.emotion_detection.requests.post")
    def test_blank_input_never_calls_provider(self, post):
        post.return_value = response()
        for value in (None, "", "   "):
            with self.subTest(value=value):
                result = emotion_detector(value)
                self.assertIsNone(result["dominant_emotion"])
        post.assert_not_called()

    @patch("EmotionDetection.emotion_detection.requests.post")
    def test_success_preserves_scores_and_bounds_network_wait(self, post):
        post.return_value = response()
        result = emotion_detector("Example")
        self.assertEqual(result["dominant_emotion"], "joy")
        self.assertEqual(result["joy"], 0.6)
        self.assertEqual(post.call_args.kwargs["json"], {"raw_document": {"text": "Example"}})
        timeout = post.call_args.kwargs.get("timeout")
        self.assertIsNotNone(timeout)
        self.assertTrue(all(value > 0 for value in timeout))

    @patch("EmotionDetection.emotion_detection.requests.post")
    def test_provider_400_preserves_invalid_input_contract(self, post):
        post.return_value = response(status=400)
        self.assertIsNone(emotion_detector("Example")["dominant_emotion"])

    @patch("EmotionDetection.emotion_detection.requests.post")
    def test_unavailable_service_has_safe_http_response(self, post):
        import server
        server.app.config["TESTING"] = True
        for failure in (requests.Timeout("synthetic-provider-detail"), requests.ConnectionError("synthetic-provider-detail")):
            with self.subTest(failure=type(failure).__name__):
                post.side_effect = failure
                result = server.app.test_client().get("/emotionDetector?textToAnalyze=Example")
                self.assertEqual(result.status_code, 503)
                self.assertIn("response", result.json)
                self.assertNotIn("synthetic-provider-detail", result.get_data(as_text=True))

    @patch("EmotionDetection.emotion_detection.requests.post")
    def test_non_success_and_invalid_payloads_are_not_predictions(self, post):
        import server
        server.app.config["TESTING"] = True
        invalid = []
        for status in (401, 429, 500):
            invalid.append(response(status=status))
        for payload in ({}, {"emotionPredictions": []}, {"emotionPredictions": [{"emotion": {}}]}):
            item = response()
            item.json.return_value = payload
            item.text = __import__("json").dumps(payload)
            invalid.append(item)
        item = response()
        item.json.side_effect = ValueError("synthetic-private-response")
        item.text = "not-json"
        invalid.append(item)
        for item in invalid:
            with self.subTest(status=item.status_code, payload=item.text[:20]):
                post.return_value = item
                result = server.app.test_client().get("/emotionDetector?textToAnalyze=Example")
                self.assertEqual(result.status_code, 503)
                self.assertNotIn("synthetic-private-response", result.get_data(as_text=True))

    @patch("EmotionDetection.emotion_detection.requests.post")
    def test_scores_must_be_finite_probabilities(self, post):
        import server
        server.app.config["TESTING"] = True
        for value in (math.nan, math.inf, -0.1, 1.1, True, "0.5"):
            with self.subTest(value=value):
                item = response()
                item.json.return_value["emotionPredictions"][0]["emotion"]["joy"] = value
                item.text = __import__("json").dumps(item.json.return_value)
                post.return_value = item
                result = server.app.test_client().get("/emotionDetector?textToAnalyze=Example")
                self.assertEqual(result.status_code, 503)

    @patch("EmotionDetection.emotion_detection.requests.post")
    def test_route_success_and_blank_input_contract(self, post):
        import server
        post.return_value = response()
        client = server.app.test_client()
        result = client.get("/emotionDetector?textToAnalyze=Example")
        self.assertEqual(result.status_code, 200)
        self.assertIn("dominant emotion is joy", result.json["response"])
        post.reset_mock()
        result = client.get("/emotionDetector")
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.json["response"], "Invalid text! Please try again!")
        post.assert_not_called()

    @patch("EmotionDetection.emotion_detection.requests.post")
    def test_every_emotion_can_be_dominant(self, post):
        names = ("anger", "disgust", "fear", "joy", "sadness")
        for dominant in names:
            with self.subTest(dominant=dominant):
                scores = {name: 0.8 if name == dominant else 0.05 for name in names}
                post.return_value = response(scores=scores)
                result = emotion_detector("Synthetic example")
                self.assertEqual(result, {**scores, "dominant_emotion": dominant})
