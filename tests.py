import unittest
from unittest.mock import patch, mock_open, MagicMock
from big_int_search import SetSearch
from client import Client
import socket

class TestSetSearch(unittest.TestCase):
    def test_decode_user_input_valid(self):
        search = SetSearch(b"123, on")
        result = search.decode_user_input()
        self.assertEqual(result, {"query_input": 123, "reread_mode": "on"})

    def test_decode_user_input_invalid(self):
        search = SetSearch(b"invalid input")
        with self.assertRaises(ValueError):
            search.decode_user_input()

    @patch("builtins.open", new_callable=mock_open, read_data="100\n200\n300\n")
    @patch("configparser.ConfigParser.get", return_value="data.txt")
    def test_search_data_reread_on_exists(self, mock_config, mock_file):
        search = SetSearch(b"200, on")
        response = search.search_data_reread_on()
        self.assertEqual(response, "STRING EXISTS\n READ_ON_QUERY=True")
    
    @patch("builtins.open", new_callable=mock_open, read_data="100\n200\n300\n")
    @patch("configparser.ConfigParser.get", return_value="data.txt")
    def test_search_data_reread_on_not_exists(self, mock_config, mock_file):
        search = SetSearch(b"400, on")
        response = search.search_data_reread_on()
        self.assertEqual(response, "STRING NOT FOUND\n READ_ON_QUERY=True")

class TestClient(unittest.TestCase):
    @patch("socket.socket.connect")
    @patch("socket.socket.sendall")
    @patch("socket.socket.recv", return_value=b"STRING EXISTS\n READ_ON_QUERY=True")
    @patch("socket.socket.close")
    def test_send_message(self, mock_connect, mock_sendall, mock_recv, mock_close):
        client = Client()
        with patch("builtins.print") as mock_print:
            client.send_message("200", True)
            mock_sendall.assert_called_with(b"200,True")
            mock_print.assert_called_with("Server says:\n STRING EXISTS\n READ_ON_QUERY=True")

if __name__ == "__main__":
    unittest.main()
