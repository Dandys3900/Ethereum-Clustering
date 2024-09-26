# Function for handling UI events
# Imports
from Helpers import Out
from GUI import tk

# Class handling UI events from App class
class EventHandler():
    from GUI import ElementCreator
    def __init__(self, creator:ElementCreator=None):
        # Store ElementCreator instance
        self.creator = creator
        # Remember current donate label status
        self.donateLabelShown = False
        # Create donate label
        self.donateLabel = self.creator.createLabel(color="red", size=(500, 20), text="Feel free to donate some Ether: 0x81E11145Fc60Da6ebD43eee7c19e18Ce9e21Bfd5", grid={
            "row"        : 2,
            "columnspan" : 2,
            "sticky"     : "sw"
        })
        # Bind click on label with copying donate address to user clipboard
        self.donateLabel.bind("<Button-1>", lambda _: self.handleEvent("Copy"))
        # Hide donate label by default
        self.donateLabel.grid_remove()
        # Remember current graph status
        self.graphMaxed = False

    # Main event handling function
    def handleEvent(self, elementName=""):
        match elementName:
            case "Search":
                pass
            case "GitlabRepo":
                import webbrowser
                # Open web browser with repo
                webbrowser.open("https://github.com/Dandys3900/Ethereum-Clustering")
            case "Donate":
                if self.donateLabelShown:
                    # Hide it
                    self.donateLabel.grid_remove()
                    self.donateLabelShown = False
                else:
                    # Show it
                    self.donateLabel.grid()
                    self.donateLabelShown = True
            case "Info":
                # Create info window with project details
                info_window = self.creator.createWindow(title="Project Information")
                # Construct project text
                text = (
                    "Project Name: Ethereum Clustering Tool \n"
                    "Author: Tomas Daniel \n"
                    "Version: 1.0.0 \n"
                    "Description: This tool is a result of Bachelor final thesis of 2024 conducted at Brno University of Technology. \n"
                )
                # Create label with project text
                self.creator.createLabel(info_window, size=(350, 100), text=text, grid={
                    "padx"   : 10,
                    "pady"   : 10,
                    "sticky" : "w"
                })
                # Create label with project logo
                self.creator.createLabel(info_window, size=(350, 120), image="Logo.png", imageSize=(170, 90), grid={
                    "pady"   : (0, 10),
                    "sticky" : "sw"
                })
            case "Export":
                pass
            case "Maximize":
                if self.graphMaxed:
                    # Collapse graph back
                    self.creator.parent.scroll_bar.grid()
                    self.graphMaxed = False
                else:
                    # Expand graph
                    self.creator.parent.scroll_bar.grid_remove()
                    self.graphMaxed = True
            case "RefreshConStatus":
                pass
            case "Copy":
                # Create tkinter instance
                tkinter = tk.Tk()
                # Copy donate address to clipboard
                tkinter.clipboard_append("0x81E11145Fc60Da6ebD43eee7c19e18Ce9e21Bfd5")
                # Destroy instance
                tkinter.destroy()
            # Default case
            case _:
                Out.error(f"Unknown elementName provided: {elementName}")
# End of EventHandler class
