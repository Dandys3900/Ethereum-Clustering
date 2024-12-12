# Provide functions for managing stored assets
# Imports
import os
import customtkinter as ct
from PIL import Image

# Loads given image and return resized CTkImage object
def loadImage(imageName="", size:tuple=None):
    # No image name given to load
    if imageName == "":
        return None
    # Load image
    img = Image.open(os.path.join("GUI", "Assets", "Images", imageName))
    # Return image
    return ct.CTkImage(img, size=size)
