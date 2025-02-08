import time
import configparser
from typing import Optional, Set, Dict, Any

config = configparser.ConfigParser()

class SetSearch:
    """
    A class to handle searching for integer values in a data set based on user input.

    This class reads a set of integer values from a file specified in a configuration file,
    decodes user input received in a specific format, and searches for the input within the data set.
    It supports two search modes: `reread on` (which reloads the data every time) and `reread off`
    (which uses a stored data set for efficiency).

    Attributes:
        data_store (Optional[Set[int]]): A class-level attribute to store the data set,
                                         shared across instances to optimize search operations.
        user_input (bytes): The raw user input, expected in a comma-separated byte format (e.g., b"123, on").

    Methods:
        load_data() -> Set[int]: Loads the integer data set from a file specified in `config.ini`.
        decode_user_input() -> Dict[str, Any]: Decodes the user input, extracting the query integer and mode.
        search_data_reread_on() -> str: Searches the data set with reread mode enabled (reloads data every search).
        search_data_reread_off() -> str: Searches the data set with reread mode disabled (uses stored data).
    """

    data_store: Optional[Set[int]] = None  # Stores the loaded dataset for reuse

    def __init__(self, user_input: bytes) -> None:
        """
        Initializes the SetSearch class with user input.

        Args:
            user_input (bytes): The raw user input as bytes, expected in the format "integer, mode"
                                where `mode` is either "on" (reloads data) or "off" (uses stored data).
        """
        self.user_input = user_input

    def load_data(self) -> Set[int]:
        """
        Reads and loads a set of integers from a file specified in `config.ini`.

        The function retrieves the file path from the `[settings]` section in the configuration file
        and reads integer values from it, stripping out unnecessary characters like semicolons.

        Returns:
            Set[int]: A set containing all the integer values loaded from the file.

        Raises:
            FileNotFoundError: If the data file specified in `config.ini` does not exist.
            ValueError: If any line in the file contains non-integer data.
        """
        config.read("config.ini")
        data_file: str = config.get("settings", "DATA_FILE")
        
        with open(data_file, "r") as file:
            lines: Set[int] = {
                int(line.strip().replace(";", "")) for line in file if line.strip()
            }
        return lines

    def decode_user_input(self) -> Dict[str, Any]:
        """
        Decodes the user input and extracts the query value and reread mode.

        The input is expected to be a comma-separated string of the form: "integer, mode".
        The integer represents the query, and `mode` is either "on" or "off", determining
        whether to reload the data set for each search.

        Returns:
            Dict[str, Any]: A dictionary containing:
                - "query_input" (int): The integer value to search for.
                - "reread_mode" (str): Either "on" or "off", indicating the search mode.

        Raises:
            ValueError: If the input is not in the expected format or cannot be properly decoded.
        """
        data: str = self.user_input.decode()
        parts: list[str] = data.split(",")

        if len(parts) != 2:
            raise ValueError("Invalid input format. Expected 'integer, mode'.")

        query_input_str, reread_flag = parts
        query_input: int = int(query_input_str.strip())
        reread_mode: str = reread_flag.strip()

        return {
            "query_input": query_input,
            "reread_mode": reread_mode,
        }

    def search_data_reread_on(self) -> str:
        """
        Searches for the query integer in the data set with reread mode enabled.

        This method reloads the data set from the file every time it is called,
        ensuring it always operates on the most up-to-date data.

        Returns:
            str: A message indicating whether the queried integer exists in the data set.

        Possible Outputs:
            - "STRING EXISTS\n READ_ON_QUERY=True"
            - "STRING NOT FOUND\n READ_ON_QUERY=True"
        """
        query_input: int = self.decode_user_input()["query_input"]
        SetSearch.data_store = self.load_data()  # Reloads data each time

        if query_input in SetSearch.data_store:
            return "STRING EXISTS\n READ_ON_QUERY=True"
        else:
            return "STRING NOT FOUND\n READ_ON_QUERY=True"

    def search_data_reread_off(self) -> str:
        """
        Searches for the query integer in the stored data set with reread mode disabled.

        This method does not reload the data but instead uses the class-level `data_store`
        to perform the search, making it more efficient when multiple queries are performed.

        Returns:
            str: A message indicating whether the queried integer exists in the stored data set.

        Possible Outputs:
            - "STRING EXISTS\n READ_ON_QUERY=False"
            - "STRING NOT FOUND\n READ_ON_QUERY=False"

        Note:
            - If `data_store` is empty or None, this method may fail.
              Ensure `data_store` is populated before calling this method.
        """
        query_input: int = self.decode_user_input()["query_input"]

        if SetSearch.data_store and query_input in SetSearch.data_store:
            return "STRING EXISTS\n READ_ON_QUERY=False"
        else:
            return "STRING NOT FOUND\n READ_ON_QUERY=False"
