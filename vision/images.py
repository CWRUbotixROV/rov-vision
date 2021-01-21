"""Contains methods to get testing images from the images directory"""

import cv2
import os
from os import path, walk
from vision import images_path, config

def get_image(*paths):
    """Returns the image at the specified path with each folder as a separate argument.
    For example: `get_image("coral", "1", "1.jpg")`"""
    return cv2.imread(path.join(images_path, *paths))

def show_image(*paths):
    """Behaves the same as get_image but also displays the image"""
    image = get_image(*paths)
    cv2.imshow("Test image", image)
    cv2.waitKey(0)
    return image

def get_all_images(*paths):
    """Returns a list of all images found at the specified path.
    For example: `get_all_images("coral", "1")`"""
    images = []
    (dirpath, _, filenames) = next(walk(path.join(images_path, *paths)))
    for file in filenames:
        try:
            images.append(cv2.imread(path.join(dirpath, file)))
        except:
            pass
    return images

def get_video(*paths):
    """Returns a VideoCapture object from a video file at the specified path with each folder as a separate argument."""
    return cv2.VideoCapture(path.join(images_path, *paths))

def get_folder(*paths):
    """Returns the path of the specified folder
    For example: 'get_folder("transect", "frames")'"""
    return path.join(images_path, *paths)

def clear_folder(*paths):
    """Deletes all files in a folder.
    For example: `clear_folder("transect", "frames")`"""
    (dirpath, _, filenames) = next(walk(path.join(images_path, *paths)))
    for file in filenames:
        try:
            os.remove(path.join(dirpath, file))
        except:
            pass

def show_debug(image, name="Image", wait=True):
    """
    If it is running in debug mode, then the given image will be displayed.
    Parameters:
    image: The image to display
    name (str): The name of the window (Default "Image")
    wait (bool): If true, code will stop execution until a key is pressed (Default True)
    """
    if config.debug:
        cv2.imshow(name, image)
        if wait:
            cv2.waitKey(0)
