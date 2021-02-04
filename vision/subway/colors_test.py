import cv2
from vision.images import get_image, show_debug
from vision.colors import get_colors
from vision.subway.colors import *
from vision import config
config.debug = False

image = get_image("subway", "1cropped", "front", "2.jpg")

# show_debug(crop_edge(image, Edge.left), name="Left", wait=False)
# show_debug(crop_edge(image, Edge.top), name="Top", wait=False)
# show_debug(crop_edge(image, Edge.right), name="Right", wait=False)

back = get_image("subway", "1cropped", "back", "5.jpg")
front = get_image("subway", "1cropped", "front", "2.jpg")
left = get_image("subway", "1cropped", "left", "4.jpg")
right = get_image("subway", "1cropped", "right", "4.jpg")
top = get_image("subway", "1cropped", "top", "9.jpg")

arrangement = match([left, right], [back, front, top])
cv2.imshow("Front", arrangement[Face.front].image)
cv2.imshow("right", arrangement[Face.right].image)
cv2.imshow("back", arrangement[Face.back].image)
cv2.imshow("left", arrangement[Face.left].image)

print(arrangement[Face.front].image is front)
print(arrangement[Face.back].image is back)

cv2.waitKey(0)