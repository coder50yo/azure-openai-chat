import unittest
from app import app, chat  # Replace 'your_module' with the actual name of the module
from unittest.mock import patch, MagicMock
import json

class TestChatFunction(unittest.TestCase):

    @patch('app.client')
    def test_chat_success(self, mock_client):
        # Mock the client response
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content='Mock response'))]
        mock_client.chat.completions.create.return_value = mock_response

        # Make a test request
        with app.test_client() as client:
            response = client.post('/chat', data=json.dumps({'query': 'Test query'}), content_type='application/json')

        # Assert the response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['response'], 'Mock response')

    @patch('app.client')
    def test_chat_error(self, mock_client):
        # Mock the client to raise an exception
        mock_client.chat.completions.create.side_effect = Exception('Mock error')

        # Make a test request
        with app.test_client() as client:
            response = client.post('/chat', data=json.dumps({'query': 'Test query'}), content_type='application/json')

        # Assert the response
        self.assertEqual(response.status_code, 500)
        self.assertIn('Mock error', response.json['error'])

if __name__ == '__main__':
    unittest.main()