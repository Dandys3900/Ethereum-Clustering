# Imports
from tkinter import *
import customtkinter as ct
import os
from Helpers import Out
from .Assets import *
from .EventHandler import handleEvent

# Class encapsulating application elements
# NOTE: Events handling emthods are located in EventHandler.py file
class App(ct.CTk):
    def __init__(self):
        super().__init__()
        # Set initial window size
        self.geometry("910x680")
        # Set window title
        self.title("Ethereum Address Clustering")
        # Set window icon
        iconPath = os.path.join("GUI", "Assets", "Icons", "AppIcon.ico")
        self.iconbitmap(iconPath)
        # Default value for corner radiuses
        self.cornerRadius = 10
        # Default colors
        self.FITBlue = "#00ABE3"
        self.FITRed  = "#FF0028"

        # Set white theme
        self.setTheme(themeScheme="light")
        # Create grid for application widgets
        self.configureGrid()
        # Create widgets
        self.constructWidgets()
        # Create result area
        self.createResultsElement()

    # Setter for application theme
    def setTheme(self, themeScheme="system", colorScheme="blue"):
        if themeScheme not in ["light", "dark", "system"]:
            Out.error(f"Invalid theme scheme choice: {themeScheme}")
        elif colorScheme not in ["blue", "green", "dark-blue"]:
            Out.error(f"Invalid color scheme choice: {colorScheme}")
        else:
            # Apply theme choice
            ct.set_appearance_mode(themeScheme)
            # Apply color theme choice
            ct.set_default_color_theme(colorScheme)

    # Setup application grid
    # ----------- Window -----------
    # | (Row 0) SEARCH-BAR         |
    # | (Row 1) CONTENT-AREA:      |
    # | (Column 0) | (Column 1)    |
    # | MENU       | MAIN-CONTENT  |
    # ------------------------------
    def configureGrid(self):
        # Search bar row, non-expandable
        self.grid_rowconfigure(0, weight=0)
        # Content area row, expandable
        self.grid_rowconfigure(1, weight=1)
        # Left menu column
        self.grid_columnconfigure(0, weight=0)
        # Right column for clustering results
        self.grid_columnconfigure(1, weight=1)

    # Creates frame and placed it to application grid
    def createFrame(self, parent=None, color="", grid:dict=None):
        frame = ct.CTkFrame(
            master        = parent,
            fg_color      = color,
            corner_radius = self.cornerRadius
        )
        # Place into grid
        if grid:
            frame.grid(**grid)
        # Return constructed frame
        return frame

    # Creates element of given target class (button/label)
    def createElement(self, target=None, parent=None, color="", size:tuple=(), image="", imageSize:tuple=(28, 28)):
        element = target(
            master   = parent,
            image    = loadIcon(image, imageSize),
            text     = "",
            fg_color = color,
            width    = size[0],
            height   = size[1]
        )
        # Pack it with parent widget
        element.pack()
        # Bind left mouse click if button
        if isinstance(target, ct.CTkButton):
            print("button")
            element.bind("<Button-1>", handleEvent)
        # Return constructed element
        return element

    # Creates entry and place it to application grid
    def createEntry(self, parent=None, text="", textColor="", font:tuple=(), color="", size:tuple=(0, 0), grid:dict=None):
        entry = ct.CTkEntry(
            master                 = parent,
            placeholder_text       = text,
            placeholder_text_color = textColor,
            text_color             = textColor,
            font                   = font,
            fg_color               = color,
            border_color           = color,
            corner_radius          = self.cornerRadius,
            width                  = size[0],
            height                 = size[1]
        )
        # Place into grid
        if grid:
            entry.grid(**grid)
         # Return constructed button
        return entry

    # Called from constructor to create all necessary widgets
    def constructWidgets(self):
        # Create search bar
        self.createSearchBar()
        # Create menu bar
        self.createMenu()
        # Create info button
        self.createInfoElement()
        # Create connection status element
        self.createConnectionElement()

    # Creates elements forming search bar
    def createSearchBar(self):
        # Create entry
        search_bar = self.createEntry(self, "Insert address", "white", ("Helvetica", 20, "bold"), self.FITBlue, (500, 50), {
            "row"        : 0,
            "column"     : 0,
            "columnspan" : 2,
            "padx"       : 20,
            "pady"       : (40, 20),
            "sticky"     : "w"
        })
        # Create frame for search icon
        icon_frame = self.createFrame(search_bar, self.FITBlue, {
            "row"    : 0,
            "column" : 0,
            "padx"   : (0, 10),
            "sticky" : "e"
        })
        # Create button within frame with search icon
        self.createElement(ct.CTkButton, icon_frame, self.FITBlue, (40, 40), "Search.png")

    # Creates vertical menu
    def createMenu(self):
        # Create frame
        menu_frame = self.createFrame(self, self.FITRed, {
            "row"    : 1,
            "column" : 0,
            "padx"   : 20,
            "pady"   : 0,
            "sticky" : "nw"
        })
        # List all icons used in menu
        icons = ["Settings.png", "Charts.png", "GitlabRepo.png", "Donate.png"]
        # Create and add buttons to menu
        for icon in icons:
            button = self.createElement(ct.CTkButton, menu_frame, self.FITRed, (40, 40), icon)
            # Set padding between each button in menu
            button.pack(pady=10, padx=10)

    # Creates info button
    def createInfoElement(self):
        # Create frame
        info_frame = self.createFrame(self, "transparent", {
            "row"    : 1,
            "column" : 0,
            "padx"   : 20,
            "pady"   : 10,
            "sticky" : "ws"
        })
        # Create button within frame with info icon
        self.createElement(ct.CTkButton, info_frame, self._fg_color, (40, 40), "Info.png")

    # Creates current connection status element
    def createConnectionElement(self):
        # Create frame
        frame = self.createFrame(self, "transparent", {
            "row"    : 0,
            "column" : 1,
            "padx"   : 15,
            "pady"   : 15,
            "sticky" : "ne"
        })
        # Create label within frame with connection status icon
        # Store this element for potencial connection updates
        self.connectionElement = self.createElement(ct.CTkLabel, frame, self._fg_color, (40, 40), "Connection_ON.png", (34, 30))

    # Creates element for displaying clustering results:
        # Clustered addresses list
        # Addresses graph
    def createResultsElement(self):
        # Create main frame
        main_frame = self.createFrame(self, self.FITBlue, {
            "row"    : 1,
            "column" : 1,
            "padx"   : (0, 20),
            "pady"   : (0, 10),
            "sticky" : "nsew"
        })
        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_rowconfigure(1, weight=4)
        main_frame.grid_columnconfigure(0, weight=1)
        # Create frame for clustered addresses
        self.scroll_bar = ct.CTkScrollableFrame(master=main_frame, fg_color=self.FITBlue, border_color=self.FITBlue)
        self.scroll_bar.grid(
            row    = 0,
            column = 0,
            padx   = 10,
            pady   = 0,
            sticky = "nsew"
        )
        # Create canvas for addresses graph
        self.graph = Canvas(main_frame)
        self.graph.grid(
            row    = 1,
            column = 0,
            padx   = 10,
            pady   = 10,
            sticky ="nsew"
        )

    # Updates connection status element icon
    def connectionStatusChanged(self, status="ON"):
        # Update label icon according to connection status
        self.connectionElement.update(image=f"Connection_{status}.png")

# End of App class

# Main function triggering application rendering
def render():
    app = App()
    app.mainloop()
