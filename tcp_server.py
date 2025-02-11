import socket
import ssl
import threading
import configparser
import time
import logging
from datetime import datetime
from typing import Optional, Tuple, Dict
from big_int_search import SetSearch


# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.DEBUG  # Enable DEBUG level logs
)
logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)




class TCPServer:
    """
    A TCP server that listens for client connections and processes integer search queries.

    This server:
    - Accepts client connections over TCP.
    - Optionally supports SSL/TLS encryption.
    - Handles client queries using the `SetSearch` class.
    - Supports a reread mode that determines whether data is reloaded for each query.
    - Runs each client connection in a separate thread for concurrent handling.

    Attributes:
        host (str): The IP address where the server listens for connections.
        port (int): The port number for the server.
        server_socket (socket.socket): The main server socket.
        use_ssl (str): Whether SSL/TLS is enabled (read from `config.ini`).
        ssl_certfile (str): Path to the SSL certificate file (if SSL is enabled).
        ssl_keyfile (str): Path to the SSL key file (if SSL is enabled).
    """

    def __init__(self) -> None:
        """
        Initializes the TCP server with default settings and reads configuration parameters.

        - Creates a socket for listening to client connections.
        - Reads SSL configuration from `config.ini`.

        Raises:
            FileNotFoundError: If `config.ini` is missing or does not contain required settings.
            socket.error: If the server fails to bind to the specified host and port.
        """
        self.host: str = "127.0.0.1"
        self.port: int = 65445
        self.server_socket: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)

        # Read SSL settings from config.ini
        config: configparser.ConfigParser = configparser.ConfigParser()
        config.read("config.ini")
        self.use_ssl: str = config.get("server", "use_ssl", fallback="false")
        self.ssl_certfile: str = config.get("server", "ssl_certfile", fallback="")
        self.ssl_keyfile: str = config.get("server", "ssl_keyfile", fallback="")



    def handle_client(self, client_socket: socket.socket, client_address: Tuple[str, int]) -> None:
        """
        Handles an individual client connection, processes queries, and sends responses.

        - Optionally wraps the connection in SSL/TLS if enabled.
        - Receives query data in the format `integer,mode` (e.g., `123,on`).
        - Uses the `SetSearch` class to process search requests.
        - Supports two search modes: 
            - `reread on` (reloads data each time)
            - `reread off` (uses stored data for efficiency)

        Args:
            client_socket (socket.socket): The socket representing the client connection.
            client_address (Tuple[str, int]): The client's IP address and port number.

        Exceptions:
            - ssl.SSLError: If SSL setup fails.
            - ValueError: If the input format is invalid.
            - TypeError: If the query is performed with an empty data store.
        """
        print(f"DEBUG - Connected to {client_address}")

        # Wrap socket in SSL if enabled
        if self.use_ssl.lower() == "true":
            try:
                context: ssl.SSLContext = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
                context.load_cert_chain(certfile=self.ssl_certfile, keyfile=self.ssl_keyfile)
                client_socket = context.wrap_socket(client_socket, server_side=True)
                logging.debug(" SSL connection established")
            except ssl.SSLError as e:
                print(f"SSL error: {e}")
                client_socket.close()
                return
        else:
            logging.debug(" SSL connection disabled")

        # Handle the client request
        try:
            while True:
                data: bytes = client_socket.recv(1024)
                if not data:  # Client disconnected
                    break
                
                # Parse the received query
                query_token, reread_mode_string = data.decode().split(",")
                print(f"DEBUG - Received from {client_address}")
                print(f"DEBUG - Query token: {query_token} and reread mode: {reread_mode_string}")

                # Process data using SetSearch
                search_instance: SetSearch = SetSearch(data)
                re_read_mode: str = search_instance.decode_user_input().get("reread_mode", "False")

                # Measure execution time
                start_time: float = time.time()
                if re_read_mode.lower() == "true":
                    response: str = search_instance.search_data_reread_on()
                else:
                    response = search_instance.search_data_reread_off()

                client_socket.sendall(response.encode())

                execution_time = (time.time() - start_time) * 1000
                print(f"DEBUG - Execution time: {execution_time:.2f}ms")
                logging.info("This is a log message.")

        except TypeError as e:
            response = "Please switch to READ_ON_QUERY=True, no data found in memory"
            client_socket.sendall(response.encode())
            logging.debug(f"Error with client {client_address}: {e}")

        except ValueError as e:
            response = "The search input must be a number or integer"
            client_socket.sendall(response.encode())
            logging.debug(f"Error with client {client_address}: {e}")

        finally:
            print(f"Closing connection to {client_address}\n")
            client_socket.close()



    def start(self) -> None:
        """
        Starts the TCP server and listens for client connections.

        - Runs in an infinite loop to accept new connections.
        - Spawns a new thread for each client connection to allow concurrent processing.

        Exceptions:
            - socket.error: If the server fails to accept connections.
        """
        print(f"Server started on {self.host}:{self.port}")

        while True:
            try:
                client_socket: socket.socket
                client_address: Tuple[str, int]
                client_socket, client_address = self.server_socket.accept()
                
                # Create a thread for handling the client
                client_thread: threading.Thread = threading.Thread(
                    target=self.handle_client, args=(client_socket, client_address)
                )
                client_thread.daemon = True  # Allows the program to exit even if threads are running
                client_thread.start()
            except socket.error as e:
                print(f"Socket error: {e}")
                break  # Exit if the socket encounters an unrecoverable error


if __name__ == "__main__":
    server: TCPServer = TCPServer()
    server.start()
