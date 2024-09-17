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
        # Set window icon using relative path
        iconPath = os.path.join("GUI", "Assets", "Icons", "AppIcon.ico")
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
        self.cornerRad = 10
        # Default colors
        self.FITBlue = "#00ABE3"
        self.FITRed  = "#FF0028"

        # Set white theme
        self.setTheme(themeScheme="light")

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

    # Called from constructor to create all necessary widgets
    def constructWidgets(self):
        ## Create search bar ##
        search_bar = ct.CTkEntry(
            self,
            placeholder_text="Insert address...",
            placeholder_text_color="white",
            text_color="white",
            font=("Helvetica", 22, "bold"),
            fg_color=self.FITBlue,
            border_color=self.FITBlue,
            corner_radius=self.cornerRad,
            width=500,
            height=40
        )
        search_bar.grid(
            row=0,
            column=0,
            padx=20,
            pady=40,
            sticky="w"
        )
        frame = ct.CTkFrame(
            search_bar,
            corner_radius=self.cornerRad,
            fg_color=self.FITBlue,
            border_color=self.FITBlue
        )
        frame.grid(
            row=0,
            column=0,
            padx=(0, 10),
            sticky="e"
        )
        # Place search icon button into search bar
        searchIconButton = ct.CTkButton(
            frame,
            image=loadIcon("Search.png"),
            text="",
            command=handleEvent("click", "search"),
            fg_color=self.FITBlue,
            border_color=self.FITBlue,
            corner_radius=self.cornerRad,
            width=30,
            height=40
        )
        searchIconButton.pack()
# End of App class

# Main function triggering application rendering
def render():
    app = App()
    app.mainloop()
