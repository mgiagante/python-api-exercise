import unittest
from unittest.mock import patch, Mock

from app.core import is_valid

# from app import db  # Updated path for db module
# from app.core import MAX_RETRIES, MAX_WINNERS  # If constants were moved
import main  # For accessing functions in main.py

"""
These tests mock the API responses and verify that different parts of the
process of obtaining valid and unique winners for 25 different states work
as expected.
"""
class TestMainFunctions(unittest.TestCase):

    # Fetching users works when users have the basic attributes.
    @patch("main.requests.get")
    def test_fetch_winners_success(self, mock_get):
        mock_response = Mock()
        mock_response.json.return_value = [
                {"id": "1", "email": "test@example.com", "address": {"state": "New York"}},
                {"id": "2", "email": "test2@example.com", "address": {"state": "Ohio"}}
        ]
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        result = main.fetch_winners()
        self.assertEqual(result[0], {"id": "1", "email": "test@example.com", "address": {"state": "New York"}})
        self.assertEqual(result[1], {"id": "2", "email": "test2@example.com", "address": {"state": "Ohio"}})

    # Fetching users returns `None` when the API throws an error.
    @patch("main.requests.get")
    def test_fetch_winners_failure(self, mock_get):
        mock_get.side_effect = Exception("API error")
        result = main.fetch_winners()
        self.assertIsNone(result)

    # is_valid(user) returns true when user has all required attributes. 
    def test_is_valid_with_valid_user(self):
        valid_user = {"id": "1", "email": "test@example.com", "address": {"state": "NY"}}
        self.assertTrue(is_valid(valid_user))

    # is_valid(user) returns false when user lacks an id.
    def test_is_valid_with_invalid_user_no_id(self):
        invalid_user = {"email": "test@example.com", "address": {"state": "NY"}}
        self.assertFalse(is_valid(invalid_user))

    # is_valid(user) returns false when user lacks an address. 
    def test_is_valid_with_invalid_user_no_address(self):
        invalid_user = {"id": "1", "email": "test@example.com"}
        self.assertFalse(is_valid(invalid_user))

    # is_valid(user) returns false when user has an address field but its value is `None`. 
    def test_is_valid_with_address_not_dictionary():
        user = {"id": "1", "email": "test@example.com", "address": None}
        assert is_valid(user) is False

    # is_valid(user) returns false when user has an address field but there is no `state` field in it. 
    def test_is_valid_with_invalid_user_malformed(self):
        invalid_user = {"id": "1", "email": "test@example.com", "address": {}}
        self.assertFalse(is_valid(invalid_user))

if __name__ == "__main__":
    unittest.main()
