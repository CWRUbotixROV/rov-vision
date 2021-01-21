import cv2
from vision.coral.coral_ui import Coral
from vision.images import get_image
from vision import config

config.debug = True

test_image = get_image("coral", "1", "1.jpg")

test = Coral(test_image)
test.crop_before_image(test_image)
test.display_changes(test.cropped_image)
