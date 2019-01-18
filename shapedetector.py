import cv2, imutils


class ShapeDetector:
    def __init__(self):
        pass

    def detect(self, c):
        shape = 'unidentified'
        peri = cv2.arcLength(c, True)   # perimeter
        approx = cv2.approxPolyDP(c, 0.04*peri, True)   # use RDP algorithm to simplify shape

        print(len(approx))
        if len(approx)==2:
            shape = 'line'
        elif len(approx)==3:
            shape = 'triangle'
        elif len(approx)==4:    # could be square or line
            (x, y, w, h) = cv2.boundingRect(approx)
            area = cv2.contourArea(c)
            if area/float(w*h) >=0.4:
                shape = 'square'
            else:
                shape = 'line'
        else:
            shape = 'circle'    # shapes can only be square, triangle, line, or circle

        return shape


def detect_shapes():
    image = cv2.imread('/home/sam/Documents/shapes.jpg', cv2.IMREAD_COLOR)
    resized = imutils.resize(image, width=300)  # resize to simplify shapes
    ratio = image.shape[0] / float(resized.shape[0])

    gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    thresh = cv2.threshold(blurred, 60, 255, cv2.THRESH_BINARY)[1]

    cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[1]
    sd = ShapeDetector()

    for c in cnts:
        # compute centroid of the contour as it would be on the original image
        M = cv2.moments(c)
        cx = int((M["m10"] / M["m00"]) * ratio)
        cy = int((M["m01"] / M["m00"]) * ratio)
        shape = sd.detect(c)

        c = c.astype(float)
        c = c*ratio
        c = c.astype(int)
        cv2.drawContours(image, [c], -1, (0, 255, 0), 2)
        cv2.putText(image, shape, (cx, cy), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

        cv2.imshow("Image", image)
        cv2.waitKey(0)

detect_shapes()
