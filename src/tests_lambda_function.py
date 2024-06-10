import unittest
from unittest.mock import patch
from lambda_function import current_time, get_weather_emoticon
from lambda_function import lambda_handler

class TestLambdaHandler(unittest.TestCase):

    @patch('lambda_function.requests.get')
    def test_lambda_handler_success(self, mock_get):
        mock_get.return_value.json.return_value = {
            'weather': [{'main': 'Clear'}],
            'main': {'temp': 25}
        }
        event = {}
        context = {}
        response = lambda_handler(event, context)
        self.assertEqual(response['statusCode'], 400)
        self.assertEqual(response['body'], {
            'weather': [{'main': 'Clear'}],
            'main': {'temp': 25}
        })

    @patch('lambda_function.requests.get')
    def test_lambda_handler_failure(self, mock_get):
        mock_get.return_value.json.return_value = {}
        event = {}
        context = {}
        response = lambda_handler(event, context)
        self.assertEqual(response['statusCode'], 200)
        self.assertEqual(response['body'], {})

class TestLambdaFunction(unittest.TestCase):
    def test_current_time(self):
        # Test that current_time returns a string
        self.assertIsInstance(current_time(), str)

    def test_get_weather_emoticon(self):
        # Test that get_weather_emoticon returns the correct emoticon for each weather condition
        self.assertEqual(get_weather_emoticon("Clear"), "☀️")
        self.assertEqual(get_weather_emoticon("Clouds"), "☁️")
        self.assertEqual(get_weather_emoticon("Rain"), "🌧️")
        self.assertEqual(get_weather_emoticon("Drizzle"), "🌦️")
        self.assertEqual(get_weather_emoticon("Thunderstorm"), "⛈️")
        self.assertEqual(get_weather_emoticon("Snow"), "❄️")
        self.assertEqual(get_weather_emoticon("Unknown"), "🤷")

if __name__ == '__main__':
    unittest.main()