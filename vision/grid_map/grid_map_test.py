from vision.grid_map.grid_map import *
from vision.colors import *
from vision.images import *

video = get_video("transect", "transect.MOV")

# Tests square detection
find_squares(video)

# Tests color and line detection
# start_mapping(video)

# Tests image stitching
# image_stitching()

# Check if stitched_img exists
# stitched_img = get_image("transect", "stitched_img.jpg")
#
# if stitched_img is not None:
#     # Use k means color clustering on stitched_img
#     get_colors(stitched_img, 20)
# else:
#     print("Could not find stitched image")