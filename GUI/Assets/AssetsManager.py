# Provide functions for managing stored assets
# Imports
import os
import customtkinter as ct
from PIL import Image

# Loads given icon and return resized CTkImage
def loadIcon(iconName="", size:tuple=None):
    # Load icon
    icon = Image.open(
        os.path.join("GUI", "Assets", "Icons", iconName)
    )
    # Return icon
    return ct.CTkImage(icon, size=size)
