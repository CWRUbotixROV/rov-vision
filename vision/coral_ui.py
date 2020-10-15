import cv2

class Coral:

    def __init__(self, before_image):
        self.before_image = before_image

    def crop_before_image(self, image):
        cv2.namedWindow("Image")
        cv2.moveWindow("Image", 0, 0)

        # Have user crop image
        roi = cv2.selectROI("Image", image, False) # selectROI(window name, image, showCrosshair)
        image_cropped = image[int(roi[1]):int(roi[1] + roi[3]), int(roi[0]):int(roi[0] + roi[2])]

        # Display cropped image
        cv2.imshow("Cropped Image", image_cropped)
        cv2.moveWindow("Cropped Image", 700, 0)
        cv2.waitKey(0)
        self.before_image = image_cropped

    def display_changes(self, image):
        cv2.imshow("Image Changes", image)
        cv2.waitKey(0)

test_image = cv2.imread("/Users/georgiamartinez/Desktop/rov-vision/images/coral/1/1.jpg", 1)

test = Coral(test_image)
test.crop_before_image(test_image)
# test.display_changes(test_image)

