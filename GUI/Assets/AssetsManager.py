# Provide functions for managing stored assets
# Imports
import os
import customtkinter as ct
from PIL import Image

# Loads given icon and return resized CTkImage
def loadIcon(iconName="", iconWidth=32, iconHeight=32):
    # Load icon
    icon = Image.open(
        os.path.join("GUI", "Assets", "Icons", iconName)
    )
    # Resize icon
    icon = icon.resize(
        (iconWidth, iconHeight)
    )
    # Return icon
    return ct.CTkImage(icon)
