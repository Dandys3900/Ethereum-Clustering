# Imports
import os
from tkinter import Canvas
from GUI import ct

# Default colors
FITBlue = "#00ABE3"
FITRed  = "#FF0028"

# Class encapsulating application elements
# NOTE: Events handling emthods are located in EventHandler.py file
class App(ct.CTk):
    def __init__(self):
        from GUI import ElementCreator
        super().__init__()
        # Creator ElementCreator instance
        self.creator = ElementCreator(self)
        # Set initial window size
        self.geometry("910x680")
        # Set window title
        self.title("Ethereum Address Clustering")
        # Set window icon
        self.iconbitmap(os.path.join("GUI", "Assets", "Images", "AppIcon.ico"))

        # Set default white theme
        ct.set_appearance_mode("light")
        # Create grid for application widgets
        self.configureGrid()
        # Create widgets
        self.constructWidgets()
        # Create result area
        self.createResultsArea()

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

    # Called from constructor to create all necessary widgets
    def constructWidgets(self):
        # Create search bar
        self.createSearchBar()
        # Create menu bar
        self.createMenu()
        # Create info button
        self.createInfoButton()
        # Create connection status element
        self.createConnectionButton()

    # Creates elements forming search bar
    def createSearchBar(self):
        # Create entry
        search_bar = self.creator.createEntry(self, "Insert address", "white", ("Helvetica", 20, "bold"), FITBlue, (500, 50), {
            "row"        : 0,
            "column"     : 0,
            "columnspan" : 2,
            "padx"       : 20,
            "pady"       : (40, 20),
            "sticky"     : "w"
        })
        # Create button and frame with search icon
        self.creator.createElement(ct.CTkButton, search_bar, FITBlue, (40, 40), "Search.png", frameGrid={
            "row"    : 0,
            "column" : 0,
            "padx"   : (0, 10),
            "sticky" : "e"
        })

    # Creates vertical menu
    def createMenu(self):
        # Create frame
        menu_frame = self.creator.createFrame(self, FITRed, {
            "row"    : 1,
            "column" : 0,
            "padx"   : 20,
            "pady"   : 0,
            "sticky" : "nw"
        })
        # Create and add buttons to menu with icons
        for icon in ["Settings.png", "Charts.png", "GitlabRepo.png", "Donate.png"]:
            self.creator.createElement(ct.CTkButton, menu_frame, FITRed, (40, 40), icon, pack={
                "padx" : 10,
                "pady" : 10
            })

    # Creates info button
    def createInfoButton(self):
        # Create button and frame with info icon
        self.creator.createElement(ct.CTkButton, self, self._fg_color, (40, 40), "Info.png", frameGrid={
            "row"    : 1,
            "column" : 0,
            "padx"   : (30, 10),
            "pady"   : 10,
            "sticky" : "ws"
        })

    # Creates current connection status element
    def createConnectionButton(self):
        # Create frame
        frame = self.creator.createFrame(self, "transparent", {
            "row"    : 0,
            "column" : 1,
            "padx"   : 15,
            "pady"   : 15,
            "sticky" : "ne"
        })
        # Create label within frame with connection status icon
        # Store this element for potencial connection updates
        self.connectionElement = self.creator.createElement(ct.CTkLabel, frame, self._fg_color, (40, 40), "Connection_ON.png", (34, 30))
        # Create label within frame with refresh icon
        self.creator.createElement(ct.CTkButton, frame, self._fg_color, (30, 30), "RefreshConStatus.png", (22, 22))

    # Creates element for displaying clustering results:
        # Clustered addresses list
        # Addresses graph
    def createResultsArea(self):
        # Create main frame
        main_frame = self.creator.createFrame(self, FITBlue, {
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
            fg_color         = FITBlue,
            border_color     = FITBlue,
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
        self.creator.createEntry(main_frame, "Find address", FITBlue, ("Helvetica", 20), "white", (200, 30), grid={
            "row"    : 0,
            "column" : 0,
            "pady"   : 5,
            "sticky" : "n"
        })
        # Create frame for results operations
        results_opt_frame = self.creator.createFrame(main_frame, "transparent", {
            "row"    : 0,
            "column" : 0,
            "padx"   : 10,
            "pady"   : 5,
            "sticky" : "ne"
        })
        # Add export button with icon
        self.creator.createElement(ct.CTkButton, results_opt_frame, "transparent", (30, 30), "Export.png", (22, 22))
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
        self.creator.createElement(ct.CTkButton, self.graph, "transparent", (30, 30), "Maximize.png", (22, 22), frameGrid={
            "sticky" : "nw"
        })

    # Adds clustered address record to output list
    def addResultAddress(self, text=""):
        self.creator.createElement(ct.CTkLabel, self.scroll_bar, "transparent", image="Entity.png", text=text)

    # Updates connection status element icon
    def connectionStatusChanged(self, status="ON"):
        # Update label icon according to connection status
        self.connectionElement.update(image=f"Connection_{status}.png")
# End of App class

# Main function triggering application rendering
def render():
    app = App()
    app.mainloop()
