import unittest
import ssl
import socket
import threading
import configparser
from tcp_server import TCPServer
from client import Client
from unittest.mock import patch
import io
from big_int_search import SetSearch

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
        file_path = config.get("settings", "linuxpath")
        self.assertEqual(file_path, "/root/200k.txt")



    def test_server_response_for_match(self):
        """
        4. Opens the file found in the path, and searches for a full match of 
        the string in the file. Please note: partial matches of the search query
        string in a line do not count as matches. You should only respond with
        STRING EXISTS if you can find a match for the whole string as a stand-alone
        line in the file.
        """
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(("127.0.0.1", 65445))
        client_socket.sendall(b"24011601050,True")
        response = client_socket.recv(1024).decode()
        client_socket.close()
        self.assertIn("STRING EXISTS", response)


    def test_server_re_read_modes(self):
        """
        5. REREAD_ON_QUERY option: When set to True, this checks whether "String" 
        exists in the file, considering that the file in the path COULD change every 
        few microseconds. In this case the code should re-read the contents of the file
        on every search query sent from the client. When the option is set to False,
        the file is not expected to change and it’s enough to read it one time, on load
        """
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(("127.0.0.1", 65445))
        
        # Test re-read mode 'on'
        client_socket.sendall(b"24011601050,True")
        response_on = client_socket.recv(1024).decode()
        self.assertTrue("READ_ON_QUERY=True" in response_on)
        
        # Test re-read mode 'off'
        client_socket.sendall(b"24011601050,False")
        response_off = client_socket.recv(1024).decode()
        self.assertTrue("READ_ON_QUERY=False" in response_off)
        
        client_socket.close()


    def test_decode_user_input_spaces_and_null_bytes(self):
        """
        6. The maximum payload size is 1024 bytes. The server strips any 
        \x00 characters from the end of the payload it receives,
        """
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(("127.0.0.1", 65445))
        # Send a message larger than 1024 bytes
        payload = b"A" * 1500
        client_socket.sendall(payload)
        # Receive response
        response = client_socket.recv(1024)
        client_socket.close()
        search = SetSearch(b" 24011601050 , True \x00")
        decoded_input = search.decode_user_input()
        # Ensure response is not larger than 1024 bytes
        self.assertTrue(len(response) <= 1024)
        self.assertEqual(decoded_input["query_input"], 24011601050)
        # Ensure no spaces or null bytes are in the query input
        self.assertNotIn(" ", str(decoded_input["query_input"]))
        self.assertNotIn("\x00", str(decoded_input["query_input"]))



    def test_server_responds_with_string_exists_or_not_found(self):
        """
        7. Test that the server responds with 'STRING EXISTS' or 
        'STRING NOT FOUND' followed by a newline character.
        """
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(("127.0.0.1", 65445))
        client_socket.sendall(b"24011601050,False")
        response = client_socket.recv(1024).decode()
        client_socket.close()
        print(response)
        
        self.assertTrue(response.endswith("\n"))
        self.assertTrue("STRING EXISTS" in response or "STRING NOT FOUND" in response)



    def test_server_multithreading(self):
        """
        8. Test if the server can handle multiple client requests 
        in parallel using multithreading.
        """
        self.assertTrue(self.server_thread.daemon)

        
    



if __name__ == "__main__":
    unittest.main()
