from unittest.mock import patch
import unittest
from lambda_function import get_user_city, set_user_city
from decimal import Decimal



class TestDynamoDBFunctions(unittest.TestCase):

    @patch('lambda_function.table.get_item')
    def test_get_user_city_success(self, mock_get_item):
        # Mock DynamoDB response
        mock_get_item.return_value = {'Item': {'chat_id': '123', 'city': 'London', 'lat': 51.5074, 'lon': -0.1278}}
        
        # Call the function
        result = get_user_city('123')
        
        # Check the result
        self.assertEqual(result, {'chat_id': '123', 'city': 'London', 'lat': 51.5074, 'lon': -0.1278})

    @patch('lambda_function.table.get_item')
    def test_get_user_city_dynamodb_error(self, mock_get_item):
        mock_get_item.side_effect = Exception("DynamoDB error")
        
        result = get_user_city('123')
        
        self.assertIsNone(result)

    @patch('lambda_function.table.get_item')
    def test_get_user_city_valid_user(self, mock_get_item):
        mock_get_item.return_value = {
            'Item': {
                'chat_id': '123',
                'city': 'New York',
                'lat': 40.7128,
                'lon': -74.0060
            }
        }
        
        result = get_user_city('123')
        
        self.assertEqual(result['city'], 'New York')
        self.assertEqual(result['lat'], 40.7128)
        self.assertEqual(result['lon'], -74.0060)

    @patch('lambda_function.table.get_item')
    def test_get_user_city_non_existent_user(self, mock_get_item):
        mock_get_item.return_value = {}

        result = get_user_city('999')
        
        self.assertIsNone(result)

    @patch('lambda_function.get_city_coordinates')
    @patch('lambda_function.table.put_item')
    def test_set_user_city_success(self, mock_put_item, mock_get_city_coordinates):
        mock_get_city_coordinates.return_value = (40.7128, -74.0060)  # New York coordinates
        
        result = set_user_city('123', 'New York')
        
        self.assertTrue(result)
        mock_put_item.assert_called_once_with(
            Item={
                'chat_id': '123',
                'city': 'New York',
                'lat': Decimal('40.7128'),
                'lon': Decimal('-74.0060')
            }
        )

    @patch('lambda_function.get_city_coordinates')
    def test_set_user_city_invalid_city(self, mock_get_city_coordinates):
        mock_get_city_coordinates.return_value = (None, None)
        
        result = set_user_city('123', 'InvalidCity')
        
        self.assertFalse(result)


if __name__ == '__main__':
    unittest.main()