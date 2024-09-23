# Functions hadling creation of UI elements needed in App() class
# Imports
import os
from .Assets import loadImage
from GUI import ct

class ElementCreator():
    from GUI.Renderer import App
    def __init__(self, app:App):
        # Default parent
        self.parent = app
        # Default value for corner radiuses
        self.cornerRadius = 10

    # Creates frame and placed it to application grid
    def createFrame(self, parent=None, color="", grid:dict=None):
        frame = ct.CTkFrame(
            master        = parent or self.parent,
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
        from GUI.Event_Handler import EventHandler
        # Create frame if grid is specified
        if frameGrid:
            parent = self.createFrame(parent, color, frameGrid)
        # Create element
        element = target(
            master   = parent or self.parent,
            image    = loadImage(image, imageSize),
            text     = text,
            fg_color = color,
            width    = size[0],
            height   = size[1]
        )
        # Pack it with parent widget
        element.pack(**pack)
        # Bind left mouse click if button
        if isinstance(element, ct.CTkButton):
            # As element identifier use used icon name (without trailing file type)
            element.bind("<Button-1>", lambda event: EventHandler.handleEvent(event, image.split(".")[0], self))
        # Return constructed element
        return element

    # Creates entry and place it to application grid
    def createEntry(self, parent=None, text="", textColor="", font:tuple=(), color="", size:tuple=(0, 0), grid:dict=None):
        entry = ct.CTkEntry(
            master                 = parent or self.parent,
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

    # Creates top-level window
    def createWindow(self, parent=None, title="", geometry="400x300"):
        window = ct.CTkToplevel(
            master = parent or self.parent
        )
        # Apply window options
        window.title(title)
        window.geometry(geometry)
        window.iconbitmap(os.path.join("GUI", "Assets", "Images", "AppIcon.ico"))
        # Return constructed window
        return window
# End of ElementCreator class
