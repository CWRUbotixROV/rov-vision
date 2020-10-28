import cv2
from vision.coral.coral_ui import Coral

test_image = cv2.imread("../images/coral/1/1.jpg", 1)

test = Coral(test_image)
test.crop_before_image(test_image)
test.display_changes(test.cropped_image)
