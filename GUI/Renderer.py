# Imports
from tkinter import *
import customtkinter as ct
import os
from .Assets import *
from .EventHandler import handleEvent

# TODO:
    # Chovani buttonu - maximalizace canvasu, otevreni menu atd

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
        self.iconbitmap(
            os.path.join("GUI", "Assets", "Icons", "AppIcon.ico")
        )
        # Default value for corner radiuses
        self.cornerRadius = 10
        # Default colors
        self.FITBlue = "#00ABE3"
        self.FITRed  = "#FF0028"
        # Set default white theme
        ct.set_appearance_mode("light")

        # Create grid for application widgets
        self.configureGrid()
        # Create widgets
        self.constructWidgets()
        # Create result area
        self.createResultsElement()

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
    def createElement(self, target=None, parent=None, color="", size:tuple=(0, 0), image="", imageSize:tuple=(28, 28), text="", pack:dict={}, frameGrid:dict=None):
        # Create frame if grid is specified
        if frameGrid:
            parent = self.createFrame(parent, color, frameGrid)
        # Create element
        element = target(
            master   = parent,
            image    = loadIcon(image, imageSize),
            text     = text,
            fg_color = color,
            width    = size[0],
            height   = size[1]
        )
        # Pack it with parent widget
        element.pack(**pack)
        # Bind left mouse click if button
        if isinstance(target, ct.CTkButton):
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
        # Create button and frame with search icon
        self.createElement(ct.CTkButton, search_bar, self.FITBlue, (40, 40), "Search.png", frameGrid={
            "row"    : 0,
            "column" : 0,
            "padx"   : (0, 10),
            "sticky" : "e"
        })

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
        # Create and add buttons to menu with icons
        for icon in ["Settings.png", "Charts.png", "GitlabRepo.png", "Donate.png"]:
            self.createElement(ct.CTkButton, menu_frame, self.FITRed, (40, 40), icon, pack={
                "padx" : 10,
                "pady" : 10
            })

    # Creates info button
    def createInfoElement(self):
        # Create button and frame with info icon
        self.createElement(ct.CTkButton, self, self._fg_color, (40, 40), "Info.png", frameGrid={
            "row"    : 1,
            "column" : 0,
            "padx"   : (30, 10),
            "pady"   : 10,
            "sticky" : "ws"
        })

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
        # Create label within frame with refresh icon
        self.createElement(ct.CTkButton, frame, self._fg_color, (30, 30), "RefreshConStatus.png", (22, 22))

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
        # Set list row non-expandable since scrollable
        main_frame.grid_rowconfigure(0, weight=0)
        # Set graph row expandable
        main_frame.grid_rowconfigure(1, weight=1)
        # Set main frame (only used) column to take all space
        main_frame.grid_columnconfigure(0, weight=1)

        # Create frame for clustered addresses with title
        self.scroll_bar = ct.CTkScrollableFrame(
            master           = main_frame,
            fg_color         = self.FITBlue,
            border_color     = self.FITBlue,
            label_anchor     = "w",
            label_text       = "Controlled addresses",
            label_font       = ("Helvetica", 20, "bold"),
            label_text_color = "white",
            label_fg_color   = "transparent",
        )
        # Place it to grid
        self.scroll_bar.grid(
            row    = 0,
            column = 0,
            padx   = 10,
            pady   = 0,
            sticky = "nsew"
        )
        # Create search bar to search through result addresses
        self.createEntry(main_frame, "Find address", self.FITBlue, ("Helvetica", 20), "white", (200, 30), grid={
            "row"    : 0,
            "column" : 0,
            "pady"   : 5,
            "sticky" : "n"
        })
        # Create frame for results operations
        results_opt_frame = self.createFrame(main_frame, "transparent", {
            "row"    : 0,
            "column" : 0,
            "padx"   : 10,
            "pady"   : 5,
            "sticky" : "ne"
        })
        # Add export button with icon
        self.createElement(ct.CTkButton, results_opt_frame, "transparent", (30, 30), "Export.png", (22, 22))
        # Create canvas for addresses graph
        self.graph = Canvas(main_frame)
        self.graph.grid(
            row    = 1,
            column = 0,
            padx   = 10,
            pady   = 10,
            sticky ="nsew"
        )
        # Create maximiza graph button
        self.createElement(ct.CTkButton, self.graph, "transparent", (30, 30), "Maximize.png", (22, 22), frameGrid={
            "sticky" : "nw"
        })

    # Adds clustered address record to output list
    def addResultAddress(self, text=""):
        self.createElement(ct.CTkLabel, self.scroll_bar, "transparent", image="Entity.png", text=text)

    # Updates connection status element icon
    def connectionStatusChanged(self, status="ON"):
        # Update label icon according to connection status
        self.connectionElement.update(image=f"Connection_{status}.png")

# End of App class

# Main function triggering application rendering
def render():
    app = App()
    app.mainloop()
