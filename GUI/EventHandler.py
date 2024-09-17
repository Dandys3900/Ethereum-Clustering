# Function for handling UI events
# Imports
from Helpers import Out

def handleEvent(event="", element=""):
    match event:
        case "click":
            print(f"{element} {event}")
            # Nested switch for determining source element
            match element:
                case "search":
                    print("search icon pressed")
                case _:
                    Out.error(f"Unknown element received: {element}")
        case _:
            Out.error(f"Unknown event received: {event}")
