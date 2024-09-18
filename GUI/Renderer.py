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
        self.grid_columnconfigure(0, weight=1)
        # Right column for clustering results, with columns ratio 1:3
        self.grid_columnconfigure(1, weight=3)

    # Creates frame and placed it to application grid
    def createFrame(self, parent=None, color="", grid:dict=None):
        frame = ct.CTkFrame(
            master  =parent,
            fg_color=color
        )
        # Place into grid
        if grid:
            frame.grid(**grid)
        # Return constructed frame
        return frame

    # Creates button and place it to application grid
    def createButton(self, parent=None, color="", size:list=[], image="", text=""):
        button = ct.CTkButton(
            master      =parent,
            image       =loadIcon(image),
            text        =text,
            fg_color    =color,
            border_color=color,
            width       =size[0],
            height      =size[1]
        )
        # Pack button with parent widget
        button.pack()
        # Bind left mouse click
        button.bind("<Button-1>", handleEvent)
        # Return constructed button
        return button

    # Creates entry and place it to application grid
    def createEntry(self, parent=None, text="", textColor="", font:tuple=(), color="", size:list=[0, 0], grid:dict=None):
        entry = ct.CTkEntry(
            master                =parent,
            placeholder_text      =text,
            placeholder_text_color=textColor,
            text_color            =textColor,
            font                  =font,
            fg_color              =color,
            border_color          =color,
            corner_radius         =self.cornerRadius,
            width                 =size[0],
            height                =size[1]
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

    # Creates elements forming search bar
    def createSearchBar(self):
        # Create entry
        search_bar = self.createEntry(self, "Insert address...", "white", ("Helvetica", 20, "bold"), self.FITBlue, [500, 50], {
            "row"       : 0,
            "column"    : 0,
            "columnspan": 2,
            "padx"      : 20,
            "pady"      : 40,
            "sticky"    : "w"
        })
        # Create frame for search icon
        icon_frame = self.createFrame(search_bar, self.FITBlue, {
            "row"   : 0,
            "column": 0,
            "padx"  : (0, 10),
            "sticky": "e"
        })
        # Create button within frame with search icon
        self.createButton(icon_frame, self.FITBlue, [40, 40], "Search.png")

    # Creates vertical menu
    def createMenu(self):
        # Create frame
        menu_frame = self.createFrame(self, self.FITRed, {
            "row"   : 1,
            "column": 0,
            "padx"  : 20,
            "pady"  : 0,
            "sticky": "nw"
        })
        # List all icons used in menu
        icons = ["Settings.png", "Charts.png", "GitlabRepo.png", "Donate.png"]
        # Create and add buttons to menu
        for icon in icons:
            button = self.createButton(menu_frame, self.FITRed, [40, 40], icon)
            # Set padding between each button in menu
            button.pack(pady=10, padx=10)
# End of App class

# Main function triggering application rendering
def render():
    app = App()
    app.mainloop()
