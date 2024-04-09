import unittest
from unittest.mock import patch
from main import generate_dates, write_to_csv, push_to_database, check_database_connection, make_api_calls, main
from testing.postgresql import Postgresql
from unittest.mock import mock_open

class TestMain(unittest.TestCase):
    
    def test_generate_dates(self):
        # Test generate_dates function
        start_date = '2022-01-01'
        end_date = '2022-01-03'
        expected_dates = ['2022-01-01', '2022-01-02']
        self.assertEqual(generate_dates(start_date, end_date), expected_dates)

def test_write_to_csv(self):
    # Test write_to_csv function
    data = [
        {'date': '2022-01-01', 'base': 'EUR', 'USD': 1.2, 'GBP': 0.8, 'EUR': 1.0},
        {'date': '2022-01-02', 'base': 'EUR', 'USD': 1.3, 'GBP': 0.9, 'EUR': 1.1}
    ]
    filename = 'test_output.csv'

    # Create mock file object to simulate writing to file
    mock_file = mock_open()

    # Patch the open function to return the mock file object
    with patch('builtins.open', mock_file):
        # Call the function under test
        write_to_csv(data, filename)

        # Retrieve the call arguments for the open function
        _, args = mock_file.call_args

        # Ensure that the file is opened with the correct filename and mode
        self.assertEqual(args[0], 'output/' + filename)
        self.assertEqual(args[1], 'w')

        # Retrieve the mock file object and check the number of lines written
        mock_file().write.assert_called_once()
        handle = mock_file()
        handle.write.assert_called_once()
        handle.writelines.assert_called_once()

        # Retrieve the lines written to the file and check the number of lines
        lines_written = handle.writelines.call_args[0][0]
        self.assertEqual(len(lines_written), 3)  # Header + 2 data rows



    @patch('main.psycopg2.connect')
    def test_push_to_database(self, mock_connect):
        # Test push_to_database function
        mock_cursor = mock_connect.return_value.cursor.return_value
        mock_cursor.execute.side_effect = [None, None]  # Mock successful execution

        # Mocking PostgreSQL connection
        with Postgresql.Postgresql() as postgresql:
            database_url = postgresql.url()
            push_to_database(database_url)
            mock_connect.assert_called_once_with(database_url)
            self.assertEqual(mock_cursor.execute.call_count, 2)  # One for table creation, one for data insertion

    @patch.dict('os.environ', {'DATABASE_URL': 'postgresql:///dummy_database.db'})
    def test_check_database_connection(self, mock_getenv):
        # Test check_database_connection function
        self.assertTrue(check_database_connection())  # Pass no arguments to let it fetch from environment variable

    @patch('main.make_api_calls')
    @patch('main.write_to_csv')
    def test_main(self, mock_write_to_csv, mock_make_api_calls):
        # Mock the return value of make_api_calls
        mock_make_api_calls.return_value = [{'date': '2022-01-01', 'base': 'EUR', 'rates': {'USD': 1.2, 'GBP': 0.8, 'EUR': 1.0}}]

        # Call the main function
        main()

        # Assert that make_api_calls and write_to_csv are called once
        mock_make_api_calls.assert_called_once()
        mock_write_to_csv.assert_called_once()

        # Additional assertion: Check the arguments passed to write_to_csv
        expected_data = [{'date': '2022-01-01', 'base': 'EUR', 'USD': 1.2, 'GBP': 0.8, 'EUR': 1.0}]
        mock_write_to_csv.assert_called_once_with(expected_data)

if __name__ == '__main__':
    unittest.main()
