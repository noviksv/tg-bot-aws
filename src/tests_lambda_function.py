import unittest
from unittest.mock import patch, MagicMock
import json
from lambda_function import (
    extract_chat_id,
    get_weather_emoticon,
    send_tg_msg,
    get_current_weather,
    get_forecast_weather,
    get_city_coordinates,
    get_user_city,
    set_user_city,
    lambda_handler
)

class TestLambdaFunctions(unittest.TestCase):

    @patch('lambda_function.json.loads')
    def test_extract_chat_id_success(self, mock_json_loads):
        mock_json_loads.return_value = {'message': {'chat': {'id': '12345'}}}
        payload = json.dumps({'message': {'chat': {'id': '12345'}}})
        chat_id = extract_chat_id(payload)
        self.assertEqual(chat_id, '12345')

    @patch('lambda_function.json.loads')
    def test_extract_chat_id_failure(self, mock_json_loads):
        mock_json_loads.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)
        chat_id = extract_chat_id("Invalid JSON")
        self.assertIsNone(chat_id)

    def test_get_weather_emoticon(self):
        self.assertEqual(get_weather_emoticon("Clear"), "☀️")
        self.assertEqual(get_weather_emoticon("Clouds"), "☁️")
        self.assertEqual(get_weather_emoticon("Rain"), "🌧️")
        self.assertEqual(get_weather_emoticon("Drizzle"), "🌦️")
        self.assertEqual(get_weather_emoticon("Thunderstorm"), "⛈️")
        self.assertEqual(get_weather_emoticon("Snow"), "❄️")
        self.assertEqual(get_weather_emoticon("Unknown"), "🤷")

    @patch('lambda_function.requests.get')
    def test_send_tg_msg(self, mock_requests_get):
        mock_response = MagicMock()
        mock_response.json.return_value = {'ok': True}
        mock_response.raise_for_status = MagicMock()
        mock_requests_get.return_value = mock_response

        response = send_tg_msg("Hello", "12345")
        self.assertEqual(response['ok'], True)
        mock_requests_get.assert_called_once()

    @patch('lambda_function.requests.get')
    def test_get_current_weather_success(self, mock_requests_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'main': {'temp': 20},
            'weather': [{'main': 'Clear'}]
        }
        mock_requests_get.return_value = mock_response

        weather_data = get_current_weather(51.5074, -0.1278)
        self.assertEqual(weather_data['main']['temp'], 20)
        self.assertEqual(weather_data['weather'][0]['main'], 'Clear')

    @patch('lambda_function.requests.get')
    def test_get_current_weather_failure(self, mock_requests_get):
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_requests_get.return_value = mock_response

        weather_data = get_current_weather(51.5074, -0.1278)
        self.assertIsNone(weather_data)

    @patch('lambda_function.requests.get')
    def test_get_city_coordinates_success(self, mock_requests_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [{'lat': 51.5074, 'lon': -0.1278}]
        mock_requests_get.return_value = mock_response

        lat, lon = get_city_coordinates("London")
        self.assertEqual(lat, 51.5074)
        self.assertEqual(lon, -0.1278)

    @patch('lambda_function.requests.get')
    def test_get_city_coordinates_failure(self, mock_requests_get):
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_requests_get.return_value = mock_response

        lat, lon = get_city_coordinates("InvalidCity")
        self.assertIsNone(lat)
        self.assertIsNone(lon)

    @patch('lambda_function.table.get_item')
    def test_get_user_city_success(self, mock_get_item):
        mock_get_item.return_value = {
            'Item': {
                'chat_id': '12345',
                'city': 'London',
                'lat': 51.5074,
                'lon': -0.1278
            }
        }

        user_city = get_user_city('12345')
        self.assertEqual(user_city['city'], 'London')

    @patch('lambda_function.table.get_item')
    def test_get_user_city_failure(self, mock_get_item):
        mock_get_item.return_value = {}
        user_city = get_user_city('12345')
        self.assertIsNone(user_city)

    @patch('lambda_function.get_city_coordinates')
    @patch('lambda_function.table.put_item')
    def test_set_user_city_success(self, mock_put_item, mock_get_city_coordinates):
        mock_get_city_coordinates.return_value = (51.5074, -0.1278)
        mock_put_item.return_value = None  # Simulate successful put_item

        result = set_user_city('12345', 'London')
        self.assertTrue(result)

    @patch('lambda_function.get_city_coordinates')
    def test_set_user_city_failure(self, mock_get_city_coordinates):
        mock_get_city_coordinates.return_value = (None, None)

        result = set_user_city('12345', 'InvalidCity')
        self.assertFalse(result)

    @patch('lambda_function.send_tg_msg')
    @patch('lambda_function.get_user_city')
    @patch('lambda_function.get_current_weather')
    def test_lambda_handler_weather(self, mock_get_current_weather, mock_get_user_city, mock_send_tg_msg):
        mock_get_user_city.return_value = {
            'chat_id': '12345',
            'city': 'London',
            'lat': 51.5074,
            'lon': -0.1278
        }
        mock_get_current_weather.return_value = {
            'main': {'temp': 20},
            'weather': [{'main': 'Clear'}]
        }

        event = {
            "body": json.dumps({
                "message": {
                    "text": "/weather",
                    "chat": {"id": "12345"}
                }
            })
        }
        response = lambda_handler(event, {})
        self.assertEqual(response['statusCode'], 200)
        self.assertIn('body', response)
        self.assertIn('Clear', response['body'])

    @patch('lambda_function.send_tg_msg')
    @patch('lambda_function.get_user_city')
    def test_lambda_handler_no_city_set(self, mock_get_user_city, mock_send_tg_msg):
        mock_get_user_city.return_value = None

        event = {
            "body": json.dumps({
                "message": {
                    "text": "/weather",
                    "chat": {"id": "12345"}
                }
            })
        }
        response = lambda_handler(event, {})
        self.assertEqual(response['statusCode'], 200)
        self.assertIn("", response['body'])

if __name__ == '__main__':
    unittest.main()
