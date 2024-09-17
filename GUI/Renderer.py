# Imports
from tkinter import *
import customtkinter as ct
import os
from Helpers import Out

# Class encapsulating application elements
# NOTE: Events handling emthods are located in EventHandler.py file
class App(ct.CTk):
    def __init__(self):
        super().__init__()
        # Set initial window size
        self.geometry("910x680")
        # Set window title
        self.title("Ethereum Address Clustering")
        # Set window icon using relative path
        iconPath = os.path.join("GUI", "Assets", "Icons", "AppIcon.ico")
        print(iconPath)
        self.iconbitmap(iconPath)

        # Setup application grid
        # ----------- Window -----------
        # | (Row 0) SEARCH-BAR         |
        # | (Row 1) CONTENT-AREA:      |
        # | (Column 0) | (Column 1)    |
        # | MENU       | MAIN-CONTENT  |
        # ------------------------------
        # Search bar row, non-expandable
        self.grid_rowconfigure(0, weight=0)
        # Content area row, expandable
        self.grid_rowconfigure(1, weight=1)
        # Left menu column
        self.grid_columnconfigure(0, weight=1)
        # Right column for clustering results, with columns ratio 1:3
        self.grid_columnconfigure(1, weight=3)

        # Default value for corner radiuses
        self.cornerRad = 6

        # Create widgets
        self.constructWidgets()

    # Called from constructor to create all necessary widgets
    def constructWidgets(self):
        ## Create search bar ##
        search_bar = ct.CTkEntry(
            self,
            placeholder_text="Insert address...",
            corner_radius=self.cornerRad,
            width=600
        )
        # Place it in grid
        search_bar.grid(
            row=0,
            column=0,
            padx=10,
            pady=10,
            sticky="nw"
        )

    # Setter for application theme
    def setTheme(self, themeScheme="blue", colorScheme="system"):
        if themeScheme not in ["light", "dark", "system"]:
            Out.error(f"Invalid theme scheme choice: {themeScheme}")
        elif colorScheme not in ["blue", "green", "dark-blue"]:
            Out.error(f"Invalid color scheme choice: {colorScheme}")
        else:
            # Apply theme choice
            ct.set_appearance_mode(themeScheme)
            # Apply color theme choice
            ct.set_default_color_theme(colorScheme)
# End of App class

# Main function triggering application rendering
def render():

    app = App()
    app.mainloop()
