# Functions hadling creation of UI elements needed in App() class
# Imports
from .Assets import loadImage
from GUI import ct

class ElementCreator():
    from GUI.Renderer import App
    def __init__(self, app:App=None):
        from GUI.Event_Handler import EventHandler
        # Default parent
        self.parent = app
        # Default value for corner radiuses
        self.cornerRadius = 10
        # Init EventHandler class
        self.handle = EventHandler(self)

    # Creates frame and placed it to application grid
    def createFrame(self, parent=None, color="transparent", grid:dict=None):
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

    # Create button with given attributes
    def createButton(self, parent=None, color="transparent", size:tuple=(0, 0), image="", imageSize:tuple=(28, 28), text="", frameGrid:dict=None):
        # Create frame if grid is specified
        if frameGrid:
            parent = self.createFrame(parent, color, frameGrid)
        # Create element
        element = ct.CTkButton(
            master   = parent or self.parent,
            image    = loadImage(image, imageSize),
            text     = text,
            fg_color = color,
            width    = size[0],
            height   = size[1]
        )
        # Place it with parent widget
        element.grid()
        # Bind left mouse click if button
        # As element identifier use used icon name (without trailing file type)
        element.bind("<Button-1>", lambda _: self.handle.handleEvent(image.split(".")[0]))
        # Return constructed element
        return element

    # Create label with given attributes
    def createLabel(self, parent=None, color="transparent", size:tuple=(0, 0), image="", imageSize:tuple=(28, 28), text="", grid:dict={}):
        # Create element
        element = ct.CTkLabel(
            master        = parent or self.parent,
            image         = loadImage(image, imageSize),
            text          = text,
            text_color    = "#D6AD60", # COLOR_GOLD
            fg_color      = color,
            wraplength    = size[0],
            justify       = "left",
            corner_radius = self.cornerRadius,
            width         = size[0],
            height        = size[1],
        )
        # Place it with parent widget
        element.grid(**grid)
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
    def createWindow(self, parent=None, title="", geometry:tuple=(350, 220), content="", timer=None):
        window = ct.CTkToplevel(
            master = parent or self.parent
        )
        # Apply window options
        window.title(title)
        window.geometry(f"{geometry[0]}x{geometry[1]}")
        window.resizable(False, False)
        # Make sure window is at top level
        window.attributes('-topmost', True)
        # Add content to window
        self.createLabel(window, size=geometry, text=content, grid={
            "padx"   : 10,
            "pady"   : 10,
            "sticky" : "n"
        })
        # Add timer to close window if set
        if timer:
            window.after(timer, window.destroy)
        # Return constructed window
        return window
# End of ElementCreator class
