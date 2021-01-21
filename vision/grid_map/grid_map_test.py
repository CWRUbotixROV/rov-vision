from vision.grid_map.grid_map import *
from vision.colors import *
from vision.images import *

config.debug = True

video = get_video("transect", "transect.MOV")
video2 = get_video("transect", "transect2.mp4")

# Tests square detection
start_mapping(video)

# Tests color and line detection
# find_blue_poles(video)


# # Tests image stitching
# image_stitching()
#
# # Check if stitched_img exists
# stitched_img = get_image("transect", "stitched_img.jpg")
#
# if stitched_img is not None:
#     # Use k means color clustering on stitched_img
#     get_colors(stitched_img, 20, True)
# else:
#     print("Could not find stitched image")
