# Function for handling UI events
# Imports
from Helpers import Out
from GUI import ct

# Class handling UI events from App class
class EventHandler():
    from GUI import ElementCreator
    @staticmethod
    # Main event handling function
    def handleEvent(event=None, elementName="", creator:ElementCreator=None):
        print(event, elementName)
        match elementName:
            case "Search":
                pass
            case " Settings":
                pass
            case "Charts":
                pass
            case "GitlabRepo":
                pass
            case "Donate":
                pass
            case "Info":
                # Create info window with project details
                info_window = creator.createWindow(title="Project Information")
                # Construct project text
                text = (
                    "Project Name: Ethereum Clustering Tool \n"
                    "Author: Tomas Daniel \n"
                    "Version: 1.0.0 \n"
                    "Description: This tool is a result of Bachelor final thesis of 2024 conducted at Brno University of Technology. \n"
                )
                # Create label with project text and logo
                creator.createElement(ct.CTkLabel, info_window, "transparent", (300, 280), "Logo.png", (200, 100), text)

            case "Export":
                pass
            case "Maximize":
                pass
            case "RefreshConStatus":
                pass
            # Default case
            case _:
                Out.error(f"Unknown elementName provided: {elementName}")
# End of EventHandler class
