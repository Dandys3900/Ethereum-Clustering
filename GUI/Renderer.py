# Imports
import os
from tkinter import Canvas
from GUI import ct

# Default colors
COLOR_WHITE = "#FFFFFF"
COLOR_GOLD  = "#D6AD60"

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
        # Set minimum window size
        self.minsize(640, 360)
        # Set window title
        self.title("Ethereum Address Clustering")
        # Set window icon
        self.iconbitmap(os.path.join("GUI", "Assets", "Images", "AppIcon.png"))

        # Set default theme
        ct.set_appearance_mode("dark")
        # Create grid for application widgets
        self.configureGrid()
        # Create widgets
        self.constructWidgets()

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
        # Create project logo element
        self.createProjectLogo()
        # Create menu bar
        self.createMenu()
        # Create info button
        self.createInfoButton()
        # Create result area
        self.createResultsArea()

    # Creates elements forming search bar
    def createSearchBar(self):
        # Create entry
        self.search_bar = self.creator.createEntry(self, "Insert target address", "white", ("Helvetica", 20, "bold"), COLOR_GOLD, (500, 50), {
            "row"        : 0,
            "column"     : 0,
            "columnspan" : 2,
            "padx"       : 20,
            "pady"       : (20, 20),
            "sticky"     : "w"
        })
        # Create button and frame with search icon
        self.creator.createButton(self.search_bar, COLOR_GOLD, (40, 40), "Search.png", frameGrid={
            "row"    : 0,
            "column" : 0,
            "padx"   : (0, 10),
            "sticky" : "e"
        })

    # Creates project logo element
    def createProjectLogo(self):
        # Create label with project logo
        self.creator.createLabel(self, size=(170, 90), image="Logo.png", imageSize=(140, 65), grid={
            "row"    : 0,
            "column" : 1,
            "sticky" : "se"
        })

    # Creates vertical menu
    def createMenu(self):
        # Create frame
        self.menu_frame = self.creator.createFrame(self, COLOR_GOLD, {
            "row"    : 1,
            "column" : 0,
            "padx"   : 20,
            "pady"   : 0,
            "sticky" : "nw"
        })
        # Create and add buttons to menu with icons
        for icon in ["GitlabRepo.png", "Donate.png", "Refresh.png"]:
            self.creator.createButton(self.menu_frame, COLOR_GOLD, (40, 40), icon, frameGrid={
                "padx" : 10,
                "pady" : 10
            })

    # Creates info button
    def createInfoButton(self):
        # Create button and frame with info icon
        self.creator.createButton(self, size=(40, 40), image="Info.png", frameGrid={
            "row"    : 1,
            "column" : 0,
            "padx"   : (30, 10),
            "pady"   : 10,
            "sticky" : "ws"
        })

    # Creates element for displaying clustering results:
        # Clustered addresses list
        # Addresses graph
    def createResultsArea(self):
        # Create main frame
        main_frame = self.creator.createFrame(self, COLOR_WHITE, {
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
            fg_color         = COLOR_WHITE,
            border_color     = COLOR_WHITE,
            label_anchor     = "w",
            label_text       = "Controlled addresses",
            label_font       = ("Helvetica", 20, "bold"),
            label_text_color = COLOR_GOLD,
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
        self.creator.createEntry(main_frame, "Find address", COLOR_GOLD, ("Helvetica", 20), COLOR_WHITE, (200, 30), grid={
            "row"    : 0,
            "column" : 0,
            "padx"   : (250, 0),
            "pady"   : 5,
            "sticky" : "nw"
        }).configure(border_color=COLOR_GOLD)
        # Create frame for results operations
        results_opt_frame = self.creator.createFrame(main_frame, grid={
            "row"    : 0,
            "column" : 0,
            "padx"   : 10,
            "pady"   : 5,
            "sticky" : "ne"
        })
        # Add export button with icon
        self.creator.createButton(results_opt_frame, size=(30, 30), image="Export.png", imageSize=(22, 22))
        # Create canvas for addresses graph
        self.graph = Canvas(main_frame)
        self.graph.grid(
            row    = 1,
            column = 0,
            padx   = 10,
            pady   = 10,
            sticky ="nsew"
        )
        # Create maximize graph button
        self.creator.createButton(self.graph, size=(30, 30), image="Maximize.png", imageSize=(22, 22), frameGrid={
            "sticky" : "nw"
        })

    # Adds clustered address record to output list
    def addResultAddress(self, entities=[]):
        for entity in entities:
            self.creator.createLabel(self.scroll_bar, image="Entity.png", text=entity)
# End of App class

# Main function triggering application rendering
def render():
    app = App()
    app.mainloop()
