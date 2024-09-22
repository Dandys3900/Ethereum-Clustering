# Function for handling UI events
# Imports
import customtkinter as ct
from Helpers import Out
from GUI import *

# Class handling UI events from App class
class EventHandler():
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
                info_window = creator.createWindow(ttle="Project Information")
                # Construct project text
                text = (
                    "Project Name: Ethereum Clustering Tool \n"
                    "Author: Tomas Daniel \n"
                    "Version: 1.0.0 \n"
                    "Description: This tool is a result of Bachelor final thesis of 2024 conducted at Brno University of Technology. \n"
                )
                # Create label with project text and logo
                creator.createElement(ct.CTkLabel, info_window, "transparent", (300, 280), "Logo.png", (300, 280), text, frameGrid={
                    "row"    : 0,
                    "column" : 0,
                    "padx"   : 10,
                    "pady"   : 10,
                    "sticky" : "nsew"
                })

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
