import unittest
import socket
import threading
import configparser
from tcp_server import TCPServer
from client import Client
from unittest.mock import patch
import io

class TestTCPServer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = TCPServer()
        cls.server_thread = threading.Thread(target=cls.server.start, daemon=True)
        cls.server_thread.start()
    
    def test_server_accepts_connections(self):
        """
        1. 
        Write a server script that binds a port and responds
        to connections (an unlimited amount of concurrent connections),
        """
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(("127.0.0.1", 65445))
        client_socket.close()

    def test_server_receives_and_sends_string(self):
        """
        2. Receives "String" in the connection in clear text
        """
        client = Client()
        with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
            client.send_message("24011601050", True)
            output = mock_stdout.getvalue()
        
        # Ensure response contains expected output
        self.assertTrue("STRING EXISTS" in output or "STRING NOT FOUND" in output)
    def test_configuration_file_path_extraction(self):
        """
        3. The path to find the file comes from the configuration file.
        The configuration file can have a large number of elements that are not relevant
        to your server script. The line with the path in it will start with
        "linuxpath=" and will have the path after it, e.g., "linuxpath=/root/200k.txt".
        Assume a config.ini file exists in the same directory.
        """
        config = configparser.ConfigParser()
        config.read("config.ini")
        file_path = config.get("server", "linuxpath", fallback=None)
        self.assertEqual(file_path, "/root/200k.txt")


if __name__ == "__main__":
    unittest.main()
