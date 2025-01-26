# Imports
import json
from termcolor import colored

# Static class for terminal output messages
class Out:
    # Success messages output
    @staticmethod
    def success(message):
        print(colored(message, 'green'))

    # Error messages output
    @staticmethod
    def error(message):
        print(colored(message, 'red'))

    # Warning messages output
    @staticmethod
    def warning(message):
        print(colored(message, 'yellow'))

    # JSON formatted output
    @staticmethod
    def json(message):
        print(json.dumps(message, indent=2))

    # Default messages output
    @staticmethod
    def blank(message):
        print(message)
# End of Out class
