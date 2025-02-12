import socket
import ssl
import configparser
from typing import Optional


class Client:
    """
    Client class to handle communication with the server.

    This class is responsible for initializing the client, reading configuration settings,
    and sending messages to the server. It supports both plain and SSL-encrypted connections.

    Attributes:
        use_ssl (str): Indicates whether SSL should be used for the connection.
        cert_file (Optional[str]): Path to the SSL certificate file, if SSL is enabled.
        key_file (Optional[str]): Path to the SSL key file, if SSL is enabled.
        server_host (str): The host address of the server.
        server_port (int): The port number on which the server is listening.
    """

    def __init__(self) -> None:
        """
        Initialize the client by reading configuration settings from 'config.ini'.

        The configuration file is expected to contain settings for SSL usage, certificate files,
        and server connection details. If the configuration file is missing or incomplete,
        default values will be used.
        """
        # Read config.ini
        config = configparser.ConfigParser()
        config.read("config.ini")
        self.use_ssl: str = config.get("server", "use_ssl", fallback="False")
        self.cert_file: Optional[str] = config.get("server", "ssl_certfile", fallback=None)
        self.key_file: Optional[str] = config.get("server", "ssl_keyfile", fallback=None)
        self.server_host: str = "127.0.0.1"
        self.server_port: int = 65445


    def send_message(self, query: str, reread_flag: bool) -> None:
        """
        Send a message to the server and receive a response.

        This method establishes a connection to the server, sends a message, and waits for a response.
        The connection can be either plain or SSL-encrypted, depending on the configuration.

        Args:
            query (str): The query to send to the server.
            reread_flag (bool): Flag indicating whether to reread the data.

        Raises:
            Exception: If there is a connection error, it will be caught and printed.
        """
        message: str = f"{query},{str(reread_flag)}"

        # Create a socket object
        client_socket: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Enable SSL if configured
        if self.use_ssl.lower() == "true":
            context: ssl.SSLContext = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
            if self.cert_file:
                context.load_verify_locations(self.cert_file)
            client_socket = context.wrap_socket(
                client_socket, server_hostname=self.server_host
            )

        try:
            # Connect to the server
            client_socket.connect((self.server_host, self.server_port))

            # Send data
            client_socket.sendall(message.encode())

            # Receive response
            response: bytes = client_socket.recv(1024)
            print(f"Server says:\n {response.decode()}")

        except Exception as e:
            print(f"Connection error: {e}")

        finally:
            # Close the connection
            client_socket.close()


if __name__ == "__main__":
    """
    Main entry point for the client script.

    This block initializes the client and sends a sample message to the server.
    The `reread_flag` is set to False by default, but can be modified as needed.
    """
    reread_flag: bool = False

    client: Client = Client()
    client.send_message("11011101630", reread_flag)
