import cv2


class Coral:

    def __init__(self, before_image):
        self.before_image = before_image
        self.cropped_image = before_image

    def crop_before_image(self, image):
        cv2.namedWindow("Image")
        cv2.moveWindow("Image", 0, 0)

        # Have user crop image
        roi = cv2.selectROI("Image", image, False)  # selectROI(window name, image, showCrosshair)
        self.cropped_image = image[int(roi[1]):int(roi[1] + roi[3]), int(roi[0]):int(roi[0] + roi[2])]

        # Display cropped image
        cv2.imshow("Cropped Image", self.cropped_image)
        cv2.moveWindow("Cropped Image", 700, 0)
        cv2.waitKey(0)

    def display_changes(self, image):
        cv2.imshow("Image Changes", image)
        cv2.moveWindow("Image Changes", 0, 0)
        cv2.waitKey(0)
