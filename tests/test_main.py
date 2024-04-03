import unittest
from unittest.mock import patch

from src.main import get_birthdays_db

class TestGetBirthdaysDb(unittest.TestCase):

    @patch("src.main.psycopg2")
    @patch("src.main.initialize_config") 
    def test_get_birthdays_db_returns_string_with_birthdays(self, mock_config, mock_psycopg2):
        mock_cursor = mock_psycopg2.connect().cursor()
        mock_cursor.fetchall.return_value = [("01-01", "John"), ("01-01", "Jane")]
        result = get_birthdays_db()
        expected = "День рождения у 🎂: \nJohn\nJane"
        self.assertEqual(result, expected)

    @patch("src.main.psycopg2")
    @patch("src.main.initialize_config")
    def test_get_birthdays_db_returns_empty_string_if_no_birthdays(self, mock_config, mock_psycopg2):
        mock_cursor = mock_psycopg2.connect().cursor()
        mock_cursor.fetchall.return_value = []
        result = get_birthdays_db()
        expected = ""
        self.assertEqual(result, expected)

    @patch("src.main.psycopg2")
    @patch("src.main.initialize_config")
    def test_get_birthdays_db_returns_none_on_error(self, mock_config, mock_psycopg2):
        mock_psycopg2.connect.side_effect = Exception("DB error")
        result = get_birthdays_db()
        self.assertIsNone(result)

